import json
import typing
import urllib.parse
from langfuse.api.resources.trace.client import TraceClient
from langfuse.api.core import pydantic_v1, RequestOptions, jsonable_encoder, remove_none_from_dict
from langfuse.api import Error, UnauthorizedError, AccessDeniedError, MethodNotAllowedError, NotFoundError

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore

from olangfuse.utils import handle_jsonerror, get_cookies, BASE_URL, COOKIE_AUTH


class OpenTraceClient(TraceClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        cookie = COOKIE_AUTH
        if not cookie:
            cookie = get_cookies(BASE_URL)
        self._next_auth = f"__Secure-next-auth.session-token={cookie.get('__Secure-next-auth.session-token', '')}"

    def delete(
        self,
        trace_ids: typing.List[str],
        project_id: str,
        batch_size: int = 1,
        *,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> str:
        """
        Delete a specific trace

        Args:
            trace_id (str): The unique langfuse identifier of a trace,
            project_id (str): The unique langfuse identifier of a project,
        """
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(
                f"{self._client_wrapper.get_base_url()}/",
                f"api/trpc/traces.deleteMany?batch={batch_size}",
            ),
            params=jsonable_encoder(
                request_options.get("additional_query_parameters") if request_options is not None else None
            ),
            headers=jsonable_encoder(
                remove_none_from_dict(
                    {
                        **self._client_wrapper.get_headers(),
                        "Cookie": self._next_auth,
                        **(request_options.get("additional_headers", {}) if request_options is not None else {}),
                    }
                )
            ),
            data=json.dumps({"0": {"json": {"traceIds": trace_ids, "projectId": project_id}}}),
            timeout=request_options.get("timeout_in_seconds")
            if request_options is not None and request_options.get("timeout_in_seconds") is not None
            else self._client_wrapper.get_timeout(),
            retries=0,
            max_retries=request_options.get("max_retries") if request_options is not None else 0,
        )
        if 200 <= _response.status_code < 300:
            return "Trace deleted successfully"
        if _response.status_code == 400:
            raise Error(pydantic_v1.parse_obj_as(typing.Any, _response.json()))  # type: ignore
        if _response.status_code == 401:
            raise UnauthorizedError(pydantic_v1.parse_obj_as(typing.Any, _response.json()))  # type: ignore
        if _response.status_code == 403:
            raise AccessDeniedError(pydantic_v1.parse_obj_as(typing.Any, _response.json()))  # type: ignore
        if _response.status_code == 405:
            raise MethodNotAllowedError(pydantic_v1.parse_obj_as(typing.Any, _response.json()))  # type: ignore
        if _response.status_code == 404:
            raise NotFoundError(pydantic_v1.parse_obj_as(typing.Any, _response.json()))  # type: ignore

        handle_jsonerror(_response)
