from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Extra

from classiq.interface.jobs import JobStatus


class ExecutionJobDetailsV1(BaseModel, extra=Extra.ignore):
    id: str

    name: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]

    provider: Optional[str]
    backend_name: Optional[str]

    status: JobStatus

    num_shots: Optional[int]
    program_id: Optional[str]

    error: Optional[str]


class ExecutionJobsQueryResultsV1(BaseModel, extra=Extra.ignore):
    results: List[ExecutionJobDetailsV1]
