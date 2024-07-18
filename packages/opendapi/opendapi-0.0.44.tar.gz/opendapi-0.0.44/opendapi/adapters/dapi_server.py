# pylint: disable=too-many-instance-attributes, too-many-locals, broad-exception-caught
""""Adapter to interact with the DAPI Server."""

import itertools
import time
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from importlib.metadata import version
from typing import Callable, Dict, List, Optional, Set, Tuple, Type
from urllib.parse import urljoin

import requests
from deepmerge import always_merger
from requests.adapters import HTTPAdapter
from snakemd import Document as MDDocument
from urllib3.util.retry import Retry

from opendapi.adapters.file import OpenDAPIFileContents
from opendapi.adapters.git import ChangeTriggerEvent
from opendapi.config import OpenDAPIConfig
from opendapi.defs import HTTPMethod
from opendapi.logging import LogCounterKey, LogDistKey, Timer, increment_counter
from opendapi.utils import make_api_w_query_and_body

TOTAL_RETRIES = 5
RETRY_BACKOFF_FACTOR = 10


def _simple_iter_chunks(data, size=1):
    """Helper for chunking data into lists of size `size`."""
    iterator = iter(data)
    for _ in range(0, len(data), size):
        yield list(itertools.islice(iterator, size))


def _chunks(data, size=1):
    """Helper for splicing a dictionary into smaller dictionaries of size `size`."""
    iterator = iter(data)
    for _ in range(0, len(data), size):
        yield {k: data[k] for k in itertools.islice(iterator, size)}


@dataclass
class DAPIServerConfig:
    """Configuration for the DAPI Server."""

    server_host: str
    api_key: str
    mainline_branch_name: str
    register_on_merge_to_mainline: bool = True
    suggest_changes: bool = True
    enrich_batch_size: int = 1
    ignore_suggestions_cache: bool = False
    register_batch_size: int = 30
    analyze_impact_batch_size: int = 15


@dataclass
class DAPIServerMeta:
    """Metadata about the DAPI server"""

    name: str
    url: str
    github_user_name: str
    github_user_email: str
    logo_url: Optional[str] = None
    suggestions_cta_url: Optional[str] = None


class DAPIServerRequestType(Enum):
    """Enum for DAPI Server Request Types."""

    VALIDATE = "/v1/registry/validate"
    REGISTER = "/v1/registry/register"
    UNREGISTER = "/v1/registry/unregister"
    ANALYZE_IMPACT = "/v1/registry/impact"


@dataclass
class PersistedPullRequestEntity:
    """
    A PullRequestEntity that was persisted and associated with a PR
    in the DAPI server
    """

    pr_link: str
    id: str
    filepath: str
    previous_content: Optional[dict]
    new_blob_sha: str
    new_content: Dict
    new_generated_by: str
    entity: str
    changed_from_current: bool
    commit_data: str

    def get_metadata_for_upsert(self) -> dict:
        """Get the metadata for the upsert request."""
        return {
            "id": self.id,
            "commit_data": self.commit_data,
        }


@dataclass
class PersistedGithubPullRequest:
    """A GithubPullRequest that was persisted to the DAPI server."""

    repo_name: str
    number: int
    link: str
    woven_comment_id: Optional[int]
    branch: str
    branch_head_commit_sha: str
    base_commit_sha: str
    head_commit_sha: str
    pull_request_entity_ids: Set[str]
    state: str
    title: str


@dataclass
class DAPIServerResponse:
    """DAPI server Response formatted"""

    request_type: DAPIServerRequestType
    status_code: int
    server_meta: DAPIServerMeta
    suggestions: Optional[dict] = None
    info: Optional[dict] = None
    errors: Optional[dict] = None
    text: Optional[str] = None
    markdown: Optional[str] = None

    @property
    def error(self) -> bool:
        """Check if there is an error in the response."""
        return self.errors is not None and len(self.errors) > 0

    @property
    def compiled_markdown(self) -> str:
        """Get the compiled markdown."""
        if (
            self.request_type is DAPIServerRequestType.ANALYZE_IMPACT
            and self.info
            and len(self.info)
        ):
            impact_md = MDDocument()
            impact_md.add_heading(":exclamation: Impact analysis", 2)
            impact_md.add_paragraph(
                "The schema change in this PR might impact an analytics use case. "
                "Please reach out to affected users.\n"
            )
            impact_md.add_table(
                header=[
                    "Dataset",
                    "Datastore",
                    "Impacted Users",
                    "Impacted Tables",
                ],
                data=[
                    [
                        dapi_urn,
                        datastore_urn,
                        (
                            f":warning: <b>{len(compiled_impact['impacted_users'])} users</b>"
                            f"<br>{', '.join(compiled_impact['impacted_users'])}"
                            if compiled_impact["impacted_users"]
                            else ":white_check_mark: No users"
                        ),
                        (
                            f":warning: <b>{len(compiled_impact['impacted_tables'])} tables</b>"
                            f"<br>{', '.join(compiled_impact['impacted_tables'])}"
                            if compiled_impact["impacted_tables"]
                            else ":white_check_mark: No tables"
                        ),
                    ]
                    for dapi_urn, datastore_impact in self.info.items()
                    for datastore_urn, compiled_impact in datastore_impact.items()
                ],
            )
            return str(impact_md)
        return self.markdown

    @property
    def compiled_text(self) -> str:
        """Get the compiled text."""
        return self.text

    def merge(self, other: "DAPIServerResponse") -> "DAPIServerResponse":
        """Merge two responses."""

        def merge_text_fn(this_text, other_text):
            if not this_text or not other_text:
                return other_text or this_text

            return (
                "\n\n".join([this_text, other_text])
                if this_text != other_text
                else other_text
            )

        def merge_dict(this_dict, other_dict):
            if not this_dict or not other_dict:
                return other_dict or this_dict

            return always_merger.merge(this_dict, other_dict)

        if self.request_type != other.request_type:
            raise ValueError(
                f"Cannot merge responses of different types: {self.request_type} and {other.request_type}"
            )

        return DAPIServerResponse(
            request_type=other.request_type or self.request_type,
            status_code=other.status_code or self.status_code,
            server_meta=other.server_meta or self.server_meta,
            errors=merge_dict(self.errors, other.errors),
            suggestions=merge_dict(self.suggestions, other.suggestions),
            info=merge_dict(self.info, other.info),
            text=merge_text_fn(self.text, other.text),
            markdown=merge_text_fn(self.markdown, other.markdown),
        )


class DAPIRequests:
    """Class to handle requests to the DAPI Server."""

    def __init__(
        self,
        dapi_server_config: DAPIServerConfig,
        opendapi_config: OpenDAPIConfig,
        trigger_event: ChangeTriggerEvent,
        error_msg_handler: Optional[Callable[[str], None]] = None,
        error_exception_cls: Optional[Type[Exception]] = None,
        txt_msg_handler: Optional[Callable[[str], None]] = None,
        markdown_msg_handler: Optional[Callable[[str], None]] = None,
    ):  # pylint: disable=too-many-arguments
        self.dapi_server_config = dapi_server_config
        self.opendapi_config = opendapi_config
        self.trigger_event = trigger_event
        self.error_msg_handler = error_msg_handler
        self.error_exception_cls = error_exception_cls or Exception
        self.txt_msg_handler = txt_msg_handler
        self.markdown_msg_handler = markdown_msg_handler

        self.session = requests.Session()
        # Add retry once after 60s for 500, 502, 503, 504
        # This is to handle the case where the server is starting up
        # or when any AI per-minute token limits are hit
        kwargs = {
            "total": TOTAL_RETRIES,
            "backoff_factor": RETRY_BACKOFF_FACTOR,
            "status_forcelist": [500, 502, 503, 504],
            "allowed_methods": ["POST"],
        }

        # Add some more options for urllib3 2.0.0 and above
        urllib3_version = version("urllib3").split(".")
        if int(urllib3_version[0]) >= 2:  # pragma: no cover
            kwargs.update(
                {
                    "backoff_jitter": 15,
                    "backoff_max": 360,  # Default is 120
                }
            )

        retries = Retry(**kwargs)
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def handle_server_message(self, message: str, should_print: bool = True) -> None:
        """Handle a message from the server."""
        # Show the messages
        if message.get("errors"):
            if self.error_msg_handler:
                self.error_msg_handler("There were errors")

        if should_print:
            if message.get("md") and self.markdown_msg_handler:
                self.markdown_msg_handler(
                    f'<br>{message.get("md", message.get("text"))}'
                )

            if message.get("text") and self.txt_msg_handler:
                self.txt_msg_handler(f'\n{message.get("text")}')

    def raw_send_request_to_dapi_server(
        self,
        request_path: str,
        method: HTTPMethod,
        query_params: Optional[dict] = None,
        body_json: Optional[dict] = None,
    ) -> Tuple[requests.Response, Dict]:
        headers = {
            "Content-Type": "application/json",
            "X-DAPI-Server-API-Key": self.dapi_server_config.api_key,
        }
        # measure the time it takes to get a response from the server in milliseconds
        metrics_tags = {
            "request_path": request_path,
            "org_name": self.opendapi_config.org_name_snakecase,
        }

        with Timer(LogDistKey.ASK_DAPI_SERVER) as _timer:
            response, _ = make_api_w_query_and_body(
                urljoin(self.dapi_server_config.server_host, request_path),
                headers=headers,
                query_params=query_params,
                body_json=body_json,
                method=method,
                timeout=60,
                req_session=self.session,
            )
            metrics_tags["status_code"] = response.status_code
            _timer.set_tags(metrics_tags)

        return response, metrics_tags

    def _handle_api_error(self, request_path: str, status_code: int) -> None:
        """Handle an error message."""
        msg = f"Something went wrong! API failure with {status_code} for {request_path}"
        if self.error_msg_handler:
            self.error_msg_handler(msg)
        raise self.error_exception_cls(msg)

    def ask_dapi_server(
        self,
        request_type: DAPIServerRequestType,
        payload: dict,
        print_txt_markdown: bool = True,
    ) -> DAPIServerResponse:
        """Ask the DAPI Server for something."""
        request_path = request_type.value
        payload["client_context"] = {
            "meta": {
                "type": "opendapi",
                "version": f"opendapi-{version('opendapi')}",
            },
            "change_trigger_event": {
                "where": self.trigger_event.where,
                "event_type": self.trigger_event.event_type,
                "before_change_sha": self.trigger_event.before_change_sha,
                "after_change_sha": self.trigger_event.after_change_sha,
                "repo_html_url": self.trigger_event.repo_html_url,
                "pull_request_number": self.trigger_event.pull_request_number,
            },
        }
        response, metrics_tags = self.raw_send_request_to_dapi_server(
            request_path=request_path,
            body_json=payload,
            method=HTTPMethod.POST,
        )
        for payload_type in ["teams", "datastores", "purposes", "dapis"]:
            if payload_type in payload:
                increment_counter(
                    key=LogCounterKey.ASK_DAPI_SERVER_PAYLOAD_ITEMS,
                    value=len(payload[payload_type]),
                    tags=always_merger.merge(
                        metrics_tags, {"payload_type": payload_type}
                    ),
                )
        # Server responds with a detailed error on 400, so only error when status > 400
        if response.status_code > 400:
            self._handle_api_error(request_path, response.status_code)

        message = response.json()

        server_meta = message.get("server_meta", {})

        self.handle_server_message(
            message, (print_txt_markdown or response.status_code >= 400)
        )

        return DAPIServerResponse(
            request_type=request_type,
            status_code=response.status_code,
            server_meta=DAPIServerMeta(
                name=server_meta.get("name", "DAPI Server"),
                url=server_meta.get("url", "https://opendapi.org"),
                github_user_name=server_meta.get("github_user_name", "github-actions"),
                github_user_email=server_meta.get(
                    "github_user_email", "github-actions@github.com"
                ),
                logo_url=server_meta.get("logo_url"),
                suggestions_cta_url=server_meta.get("suggestions_cta_url"),
            ),
            errors=message.get("errors"),
            suggestions=message.get("suggestions"),
            info=message.get("info"),
            markdown=message.get("md"),
            text=message.get("text"),
        )

    def validate(
        self,
        all_files: OpenDAPIFileContents,
        changed_files: OpenDAPIFileContents,
        commit_hash: str,
        suggest_changes_override: Optional[bool] = None,
        ignore_suggestions_cache: bool = False,
        notify_function: Optional[Callable[[int], None]] = None,
    ) -> DAPIServerResponse:
        """Validate OpenDAPI files with the DAPI Server."""
        all_files = all_files.for_server()
        changed_files = changed_files.for_server()
        chunk_size = self.dapi_server_config.enrich_batch_size
        suggest_changes = (
            self.dapi_server_config.suggest_changes
            if suggest_changes_override is None
            else suggest_changes_override
        )

        def _build_validate_payload(updates: dict) -> dict:
            base_validate_payload = {
                "dapis": {},
                "teams": {},
                "datastores": {},
                "purposes": {},
                "suggest_changes": suggest_changes,
                "commit_hash": commit_hash,
                "ignore_suggestions_cache": ignore_suggestions_cache,
            }
            result = base_validate_payload.copy()
            result.update(updates)
            return result

        # First, we validate the non-dapi files
        payload = _build_validate_payload(
            {
                "teams": all_files["teams"],
                "datastores": all_files["datastores"],
                "purposes": all_files["purposes"],
            }
        )
        resp = self.ask_dapi_server(
            DAPIServerRequestType.VALIDATE, payload, print_txt_markdown=False
        )
        # Then we validate the dapi files in batches
        for dapi_chunk in _chunks(changed_files["dapis"], chunk_size):
            for dapi_loc in dapi_chunk:
                all_files["dapis"].pop(dapi_loc, None)
            try:
                payload = _build_validate_payload({"dapis": dapi_chunk})
                this_resp = self.ask_dapi_server(
                    DAPIServerRequestType.VALIDATE, payload, print_txt_markdown=False
                )
                resp = resp.merge(this_resp)
            except self.error_exception_cls:
                # In case of errors (likely from AI timeouts), validate one by one
                # but first sleep for RETRY_BACKOFF_FACTOR to give the server time to recover
                time.sleep(RETRY_BACKOFF_FACTOR)
                for loc, item in dapi_chunk.items():
                    payload = _build_validate_payload({"dapis": {loc: item}})
                    this_resp = self.ask_dapi_server(
                        DAPIServerRequestType.VALIDATE,
                        payload,
                        print_txt_markdown=False,
                    )
                    resp = resp.merge(this_resp)

            if notify_function is not None:
                notify_function(chunk_size)

        # Finally, we validate the remaining files without suggestions
        if all_files["dapis"]:
            for dapi_chunk in _chunks(all_files["dapis"], chunk_size):
                payload = _build_validate_payload(
                    {"dapis": dapi_chunk, "suggest_changes": False}
                )
                this_resp = self.ask_dapi_server(
                    DAPIServerRequestType.VALIDATE,
                    payload,
                    print_txt_markdown=False,
                )
                resp = resp.merge(this_resp)

                if notify_function is not None:
                    notify_function(chunk_size)

        return resp

    def analyze_impact(
        self,
        changed_files: OpenDAPIFileContents,
        notify_function: Optional[Callable[[int], None]] = None,
    ) -> DAPIServerResponse:
        """Analyze the impact of changes on the DAPI Server."""
        server_files = changed_files.for_server()
        chunk_size = self.dapi_server_config.analyze_impact_batch_size
        resp: DAPIServerResponse = self.ask_dapi_server(
            DAPIServerRequestType.ANALYZE_IMPACT,
            {
                "dapis": {},
                "teams": server_files["teams"],
                "datastores": server_files["datastores"],
                "purposes": server_files["purposes"],
            },
        )

        for dapi_chunk in _chunks(server_files["dapis"], chunk_size):
            this_resp = self.ask_dapi_server(
                DAPIServerRequestType.ANALYZE_IMPACT,
                {
                    "dapis": dapi_chunk,
                    "teams": {},
                    "datastores": {},
                    "purposes": {},
                },
            )
            resp = resp.merge(this_resp) if resp else this_resp
            if notify_function is not None:
                notify_function(chunk_size)
        return resp

    def register(
        self,
        all_files: OpenDAPIFileContents,
        commit_hash: str,
        source: str,
        notify_function: Optional[Callable[[int], None]] = None,
    ) -> Optional[DAPIServerResponse]:
        """Register OpenDAPI files with the DAPI Server."""
        all_files = all_files.for_server()
        chunk_size = self.dapi_server_config.register_batch_size
        resp: DAPIServerResponse = self.ask_dapi_server(
            DAPIServerRequestType.REGISTER,
            {
                "dapis": {},
                "teams": all_files["teams"],
                "datastores": all_files["datastores"],
                "purposes": all_files["purposes"],
                "commit_hash": commit_hash,
                "source": source,
            },
        )

        for dapi_chunk in _chunks(all_files["dapis"], chunk_size):
            this_resp = self.ask_dapi_server(
                DAPIServerRequestType.REGISTER,
                {
                    "dapis": dapi_chunk,
                    "teams": {},
                    "datastores": {},
                    "purposes": {},
                    "commit_hash": commit_hash,
                    "source": source,
                },
            )
            resp = resp.merge(this_resp) if resp else this_resp
            if notify_function is not None:
                notify_function(chunk_size)
        return resp

    def unregister(self, source: str, except_dapi_urns: List[str]):
        """Unregister missing DAPIs from the DAPI Server."""
        return self.ask_dapi_server(
            DAPIServerRequestType.UNREGISTER,
            {
                "source": source,
                "except_dapi_urns": except_dapi_urns,
            },
        )

    def get_or_create_gh_pull_request(self) -> PersistedGithubPullRequest:
        """Get or create a GithubPullRequest entity from the DAPI Server"""
        response, _ = self.raw_send_request_to_dapi_server(
            request_path="/v1/github/pull-requests",
            query_params={
                "repo_name": self.trigger_event.repo_full_name,
                "number": self.trigger_event.pull_request_number,
            },
            method=HTTPMethod.GET,
        )

        if response.status_code == 200:
            return PersistedGithubPullRequest(**response.json()["pull_request"])

        elif response.status_code == 404:
            response, _ = self.raw_send_request_to_dapi_server(
                request_path="/v1/github/pull-requests",
                query_params={
                    "repo_name": self.trigger_event.repo_full_name,
                    "number": self.trigger_event.pull_request_number,
                },
                body_json={
                    "link": self.trigger_event.pull_request_link,
                    "base_commit_sha": self.trigger_event.before_change_sha,
                    "head_commit_sha": self.trigger_event.after_change_sha,
                },
                method=HTTPMethod.POST,
            )

        # no validation here, so anything 400 and above is an error
        if response.status_code >= 400:
            self._handle_api_error("/v1/github/pull-requests", response.status_code)

        return PersistedGithubPullRequest(**response.json()["pull_request"])

    def create_gh_pull_request_entities(
        self,
        current_commit_files: OpenDAPIFileContents,
        changed_files_from_base: OpenDAPIFileContents,
        changed_files: OpenDAPIFileContents,
        enriched_files: Optional[OpenDAPIFileContents],
        notify_function: Optional[Callable[[int], None]] = lambda _: None,
    ) -> List[PersistedPullRequestEntity]:
        """Register OpenDAPI files with the DAPI Server."""
        current_commit_files = current_commit_files.for_server(writeable_location=True)
        changed_files_from_base = changed_files_from_base.for_server(
            writeable_location=True
        )
        changed_files = changed_files.for_server(writeable_location=True)
        enriched_files = (
            enriched_files.for_server(writeable_location=True) if enriched_files else {}
        )

        OPENDAPI_TYPE_TO_BODY_KEY = {
            "teams": "teams_pr_entities",
            "datastores": "datastores_pr_entities",
            "purposes": "purposes_pr_entities",
            "dapis": "dapi_pr_entities",
        }

        # iterate over files from base, since want to be able to show all changed files
        # in the portal, even though we default to toggling only the changed from current
        body_key_w_filepath_w_raw_md_tuples = []
        for (
            opendapi_type,
            changed_json_by_file_from_base,
        ) in changed_files_from_base.items():
            current_json_by_file = current_commit_files[opendapi_type]
            changed_json_by_file = changed_files[opendapi_type]
            # may have been the empty dict if initially was None, so safe access
            enriched_json_by_file = enriched_files.get(opendapi_type, {})
            body_key = OPENDAPI_TYPE_TO_BODY_KEY[opendapi_type]

            # we only want to add the the GithubPullRequest opendapi entities that
            # were changed in this PR, which are the ones with changes from base
            for (
                filepath,
                changed_json_from_base,
            ) in changed_json_by_file_from_base.items():
                # if a file that was changed from base is changed from current, it means
                # that the user is not up to date merging the metadata changes.
                changed_from_current = filepath in changed_json_by_file

                # for us to say that changes were generated by AI, the file must have been
                # enriched and it still must be different than the current state, since if the
                # current state is not different it means that a human committed it,
                # meaning that the AI suggestion was accepted, at which point it is owned
                # by the user
                maybe_enriched_json = enriched_json_by_file.get(filepath)
                generated_by_ai = maybe_enriched_json and changed_from_current

                # the portal will only diff against the current content if there was a change,
                # and the PREntity only stores the previous content if there was a change,
                # since it only needs it in that event. Therefore,
                # we only need to store the current content if there was a change, otherwise
                # send None
                current_content = (
                    current_json_by_file.get(filepath) if changed_from_current else None
                )

                # if the file was enriched, we use that state, but otherwise the state should
                # not be different (the only time we yaml dump after generate is for enrich)
                # and so we default to the state after generate which is changed_json_from_base
                new_content = maybe_enriched_json or changed_json_from_base

                raw_pr_entity_metadata = {
                    "previous_content": current_content,
                    "new_content": new_content,
                    "changed_from_current": changed_from_current,
                    "new_generated_by": "ai" if generated_by_ai else "user",
                }
                body_key_w_filepath_w_raw_md_tuples.append(
                    (body_key, filepath, raw_pr_entity_metadata)
                )

        persisted_pr_entities = []
        chunk_size = self.dapi_server_config.register_batch_size

        for chunked_files in _simple_iter_chunks(
            body_key_w_filepath_w_raw_md_tuples, chunk_size
        ):
            body = defaultdict(dict)
            for body_key, file_path, raw_pr_entity_metadata in chunked_files:
                body[body_key][file_path] = raw_pr_entity_metadata

            response, _ = self.raw_send_request_to_dapi_server(
                request_path="/v1/github/pull-requests/entities",
                query_params={
                    "repo_name": self.trigger_event.repo_full_name,
                    "number": self.trigger_event.pull_request_number,
                },
                body_json=body,
                method=HTTPMethod.POST,
            )

            if response.status_code == 200:
                persisted_pr_entities.extend(
                    (
                        PersistedPullRequestEntity(**entity)
                        for entity in response.json()["pull_request_entities"]
                    )
                )
            # even though we return validation errors as a 400, they should not happen at
            # this point in the flow, since we already validated. This would therefore be
            # a hard failure
            if response.status_code >= 400:
                self._handle_api_error(
                    "/v1/github/pull-requests/entities", response.status_code
                )

            notify_function(chunk_size)

        return persisted_pr_entities

    def upsert_gh_pull_request(
        self,
        woven_comment_id: Optional[int],
        persisted_pr_entities_to_upsert: List[PersistedPullRequestEntity],
    ) -> PersistedGithubPullRequest:
        """Upsert a GithubPullRequest entity to the DAPI Server"""
        response, _ = self.raw_send_request_to_dapi_server(
            request_path="/v1/github/pull-requests/upsert",
            query_params={
                "repo_name": self.trigger_event.repo_full_name,
                "number": self.trigger_event.pull_request_number,
            },
            body_json={
                "link": self.trigger_event.pull_request_link,
                "woven_comment_id": woven_comment_id,
                "base_commit_sha": self.trigger_event.before_change_sha,
                "head_commit_sha": self.trigger_event.after_change_sha,
                "persisted_entities": [
                    entity.get_metadata_for_upsert()
                    for entity in persisted_pr_entities_to_upsert
                ],
            },
            method=HTTPMethod.POST,
        )

        if response.status_code >= 400:
            self._handle_api_error("/v1/github/pull-requests", response.status_code)

        return PersistedGithubPullRequest(**response.json()["pull_request"])
