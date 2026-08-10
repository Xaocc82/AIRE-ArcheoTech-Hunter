from aire_archeotech.processing.base import ExtractedText, ExtractionStatus
from aire_archeotech.processing.queue import InMemoryProcessingQueue, ProcessingJobStatus


def test_claimed_job_cannot_be_claimed_twice() -> None:
    queue = InMemoryProcessingQueue()
    submitted = queue.submit(b"pdf bytes")

    claimed = queue.claim_next()

    assert claimed is not None
    assert claimed.id == submitted.id
    assert claimed.status is ProcessingJobStatus.RUNNING
    assert queue.claim_next() is None


def test_completion_stores_extraction_result() -> None:
    queue = InMemoryProcessingQueue()
    job = queue.submit(b"pdf bytes")
    claimed = queue.claim_next()
    assert claimed is not None
    result = ExtractedText(
        text="NACA report",
        status=ExtractionStatus.EXTRACTED,
        engine="pypdf",
        engine_version="6.15.0",
    )

    completed = queue.complete(job.id, result)

    assert completed.status is ProcessingJobStatus.COMPLETED
    assert completed.result == result
