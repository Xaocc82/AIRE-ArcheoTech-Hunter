"""Deterministic in-memory queue used by the first processing worker."""

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from aire_archeotech.processing.base import ExtractedText


class ProcessingJobStatus(StrEnum):
    """Lifecycle states for a queued document-processing job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"


@dataclass(frozen=True)
class ProcessingJob:
    """An immutable snapshot of one queued document-processing job."""

    id: UUID
    document: bytes
    status: ProcessingJobStatus
    submitted_at: datetime
    result: ExtractedText | None = None


class InMemoryProcessingQueue:
    """FIFO queue with explicit single-claim and completion transitions."""

    def __init__(self) -> None:
        self._jobs: dict[UUID, ProcessingJob] = {}
        self._pending_job_ids: list[UUID] = []

    def submit(self, document: bytes) -> ProcessingJob:
        """Add a document to the tail of the pending queue."""
        job = ProcessingJob(
            id=uuid4(),
            document=document,
            status=ProcessingJobStatus.PENDING,
            submitted_at=datetime.now(UTC),
        )
        self._jobs[job.id] = job
        self._pending_job_ids.append(job.id)
        return job

    def claim_next(self) -> ProcessingJob | None:
        """Atomically transition the oldest pending job to running in this process."""
        if not self._pending_job_ids:
            return None
        job_id = self._pending_job_ids.pop(0)
        job = self._jobs[job_id]
        claimed = replace(job, status=ProcessingJobStatus.RUNNING)
        self._jobs[job_id] = claimed
        return claimed

    def complete(self, job_id: UUID, result: ExtractedText) -> ProcessingJob:
        """Store a result for a running job and transition it to completed."""
        job = self._jobs[job_id]
        if job.status is not ProcessingJobStatus.RUNNING:
            raise ValueError(f"Job {job_id} is not running")
        completed = replace(job, status=ProcessingJobStatus.COMPLETED, result=result)
        self._jobs[job_id] = completed
        return completed
