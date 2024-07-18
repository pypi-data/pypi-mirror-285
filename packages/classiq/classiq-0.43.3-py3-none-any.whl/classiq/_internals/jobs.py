import json
import logging
from typing import Callable, Dict, Iterable, Optional, Set, TypeVar

import httpx
import pydantic

from classiq.interface.jobs import JobDescription, JobID, JSONObject

from classiq._internals.async_utils import poll_for
from classiq._internals.client import client, try_again_on_failure
from classiq._internals.config import SDKMode
from classiq.exceptions import ClassiqAPIError

_URL_PATH_SEP = "/"
GeneralJobDescription = JobDescription[JSONObject]
_logger = logging.getLogger(__name__)
T = TypeVar("T")


def _join_url_path(*parts: str) -> str:
    if not parts:
        return ""
    prepend_slash = parts[0].startswith(_URL_PATH_SEP)
    append_slash = parts[-1].endswith(_URL_PATH_SEP)
    joined = _URL_PATH_SEP.join(part.strip(_URL_PATH_SEP) for part in parts)

    return "".join(
        [
            ("/" if prepend_slash else ""),
            joined,
            ("/" if append_slash else ""),
        ]
    )


def _general_job_description_parser(
    json_response: JSONObject,
) -> Optional[GeneralJobDescription]:
    job_description = GeneralJobDescription.parse_obj(json_response)
    if job_description.status.is_final():
        return job_description
    return None


class JobPoller:
    INITIAL_INTERVAL_SEC = 1
    INTERVAL_FACTOR = 2
    FINAL_INTERVAL_SEC = INITIAL_INTERVAL_SEC * INTERVAL_FACTOR**5  # 32 secs
    DEV_INTERVAL = 0.05

    def __init__(
        self,
        base_url: str,
        required_headers: Optional[Set[str]] = None,
        use_versioned_url: bool = True,
        additional_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self._required_headers = required_headers or set()
        self._additional_headers = additional_headers
        client_instance = client()
        self._base_url = (
            client_instance.make_versioned_url(base_url)
            if use_versioned_url
            else base_url
        )
        self._async_client = client_instance.async_client()
        self._mode = client_instance.config.mode

    def _parse_job_id_response(self, response: httpx.Response) -> JobID:
        return JobID.parse_obj(response.json())

    def _make_poll_url(self, job_id: JobID) -> str:
        return _join_url_path(self._base_url, job_id.job_id)

    @staticmethod
    def _make_cancel_url(poll_url: str) -> str:
        return _join_url_path(poll_url, "cancel")

    def _update_headers(self, response: httpx.Response) -> None:
        for header in self._required_headers:
            try:
                self._async_client.headers[header] = response.headers[header]
            except KeyError as exc:
                raise ClassiqAPIError(
                    f"Response to {self._base_url} is missing header {header}"
                ) from exc

    @try_again_on_failure
    async def _request(
        self, http_method: str, url: str, body: Optional[Dict] = None
    ) -> httpx.Response:
        # Update headers in case they change
        self._async_client.headers.update(client().get_headers())
        response = await self._async_client.request(
            method=http_method, url=url, json=body, headers=self._additional_headers
        )
        client().handle_response(response)
        return response

    async def _submit(self, body: Dict) -> httpx.Response:
        return await self._request(http_method="POST", url=self._base_url, body=body)

    def _interval_sec(self) -> Iterable[float]:
        if self._mode == SDKMode.DEV:
            while True:
                yield self.DEV_INTERVAL
        else:
            for _ in range(10):
                yield self.INITIAL_INTERVAL_SEC
            interval = self.INITIAL_INTERVAL_SEC
            while True:
                yield interval
                interval = min(interval * self.INTERVAL_FACTOR, self.FINAL_INTERVAL_SEC)

    async def _poll(
        self,
        poll_url: str,
        timeout_sec: Optional[float],
        response_parser: Callable[[JSONObject], Optional[T]] = _general_job_description_parser,  # type: ignore[assignment]
    ) -> T:
        async def poller() -> JSONObject:
            nonlocal self, poll_url
            raw_response = await self._request(http_method="GET", url=poll_url)
            return raw_response.json()

        async for json_response in poll_for(
            poller, timeout_sec=timeout_sec, interval_sec=self._interval_sec()
        ):
            parsed = response_parser(json_response)
            if parsed is not None:
                return parsed
        raise ClassiqAPIError("API request timed out")

    async def poll(
        self,
        job_id: JobID,
        timeout_sec: Optional[float],
        response_parser: Callable[[JSONObject], Optional[T]] = _general_job_description_parser,  # type: ignore[assignment]
    ) -> T:
        poll_url = self._make_poll_url(job_id=job_id)
        async with self._async_client:
            return await self._poll(
                poll_url=poll_url,
                response_parser=response_parser,
                timeout_sec=timeout_sec,
            )

    async def _cancel(self, poll_url: str) -> None:
        _logger.info("Cancelling job %s", poll_url, exc_info=True)
        cancel_url = self._make_cancel_url(poll_url)
        await self._request(http_method="PUT", url=cancel_url)

    async def run(
        self, body: Dict, timeout_sec: Optional[float]
    ) -> GeneralJobDescription:
        async with self._async_client:
            submit_response = await self._submit(body=body)
            job_id = self._parse_job_id_response(response=submit_response)
            poll_url = self._make_poll_url(job_id=job_id)
            self._update_headers(response=submit_response)
            try:
                return await self._poll(poll_url=poll_url, timeout_sec=timeout_sec)
            except Exception:
                await self._cancel(poll_url=poll_url)
                raise

    async def run_pydantic(
        self, model: pydantic.BaseModel, timeout_sec: Optional[float]
    ) -> GeneralJobDescription:
        # TODO: we can't use model.dict() - it doesn't serialize complex class.
        # This was added because JSON serializer doesn't serialize complex type, and pydantic does.
        # We should add support for smarter json serialization.
        body = json.loads(model.json())
        return await self.run(body, timeout_sec)
