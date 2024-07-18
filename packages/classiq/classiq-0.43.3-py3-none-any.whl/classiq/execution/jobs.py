import webbrowser
from datetime import datetime
from typing import List, Optional, Union
from urllib.parse import urljoin

from classiq.interface.execution.jobs import ExecutionJobDetailsV1
from classiq.interface.executor.execution_request import ExecutionJobDetails
from classiq.interface.executor.execution_result import ResultsCollection
from classiq.interface.jobs import JobStatus, JSONObject
from classiq.interface.server.routes import EXECUTION_JOBS_NON_VERSIONED_FULL_PATH

from classiq._internals.api_wrapper import CLASSIQ_ACCEPT_HEADER, ApiWrapper
from classiq._internals.async_utils import syncify_function
from classiq._internals.client import client
from classiq._internals.jobs import JobID, JobPoller
from classiq.exceptions import ClassiqAPIError

_JobDetails = Union[ExecutionJobDetails, ExecutionJobDetailsV1]

_JOB_DETAILS_VERSION = "v1"
_JOB_RESULT_VERSION = "v1"


class ExecutionJob:
    _details: _JobDetails
    _result: Optional[ResultsCollection]

    def __init__(self, details: _JobDetails) -> None:
        self._details = details
        self._result = None

    @property
    def id(self) -> str:
        return self._details.id

    @property
    def name(self) -> Optional[str]:
        return self._details.name

    @property
    def start_time(self) -> datetime:
        return self._details.start_time

    @property
    def end_time(self) -> Optional[datetime]:
        return self._details.end_time

    @property
    def provider(self) -> Optional[str]:
        return self._details.provider

    @property
    def backend_name(self) -> Optional[str]:
        return self._details.backend_name

    @property
    def status(self) -> JobStatus:
        return self._details.status

    @property
    def num_shots(self) -> Optional[int]:
        return self._details.num_shots

    @property
    def program_id(self) -> Optional[str]:
        return self._details.program_id

    @property
    def error(self) -> Optional[str]:
        return self._details.error

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        if self.name is None:
            return f"{class_name}(id={self.id!r})"
        else:
            return f"{class_name}(name={self.name!r}, id={self.id!r})"

    @classmethod
    async def from_id_async(cls, id: str) -> "ExecutionJob":
        details = await ApiWrapper.call_get_execution_job_details(JobID(job_id=id))
        return cls(details)

    @classmethod
    def from_id(cls, id: str) -> "ExecutionJob":
        return syncify_function(cls.from_id_async)(id)

    @property
    def _job_id(self) -> JobID:
        return JobID(job_id=self.id)

    async def result_async(
        self, timeout_sec: Optional[float] = None
    ) -> ResultsCollection:
        await self.poll_async(timeout_sec=timeout_sec)

        if self.status == JobStatus.FAILED:
            raise ClassiqAPIError(self.error or "")
        if self.status == JobStatus.CANCELLED:
            raise ClassiqAPIError("Job has been cancelled.")

        if self._result is None:
            self._result = (
                await ApiWrapper.call_get_execution_job_result(
                    job_id=self._job_id, version=_JOB_RESULT_VERSION
                )
            ).results
        return self._result

    result = syncify_function(result_async)

    async def poll_async(self, timeout_sec: Optional[float] = None) -> None:
        if not self.status.is_final():
            await self._poll_job(timeout_sec=timeout_sec)

    poll = syncify_function(poll_async)

    async def _poll_job(self, timeout_sec: Optional[float] = None) -> None:
        def response_parser(json_response: JSONObject) -> Optional[bool]:
            self._details = ExecutionJobDetails.parse_obj(json_response)
            if self.status.is_final():
                return True
            return None

        poller = JobPoller(
            base_url=EXECUTION_JOBS_NON_VERSIONED_FULL_PATH,
            use_versioned_url=False,
            additional_headers={CLASSIQ_ACCEPT_HEADER: _JOB_DETAILS_VERSION},
        )
        await poller.poll(
            job_id=self._job_id,
            response_parser=response_parser,
            timeout_sec=timeout_sec,
        )

    async def rename_async(self, name: str) -> None:
        self._details = await ApiWrapper.call_patch_execution_job(self._job_id, name)

    rename = syncify_function(rename_async)

    @property
    def ide_url(self) -> str:
        base_url = client().config.ide
        return urljoin(base_url, f"jobs/{self.id}")

    def open_in_ide(self) -> None:
        webbrowser.open_new_tab(self.ide_url)


async def get_execution_jobs_async(
    offset: int = 0, limit: int = 50
) -> List[ExecutionJob]:
    result = await ApiWrapper().call_query_execution_jobs(offset=offset, limit=limit)
    return [ExecutionJob(details) for details in result.results]


get_execution_jobs = syncify_function(get_execution_jobs_async)
