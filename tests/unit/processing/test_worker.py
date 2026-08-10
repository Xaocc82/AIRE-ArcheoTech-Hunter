from aire_archeotech.processing.base import ExtractedText, ExtractionStatus
from aire_archeotech.processing.queue import InMemoryProcessingQueue, ProcessingJobStatus
from aire_archeotech.processing.worker import ProcessingWorker


class FixedExtractor:
    def extract(self, document: bytes) -> ExtractedText:
        assert document == b"PDF"
        return ExtractedText(
            text="NACA report",
            status=ExtractionStatus.EXTRACTED,
            engine="test",
            engine_version="1",
        )


def test_worker_processes_one_claimed_document() -> None:
    queue = InMemoryProcessingQueue()
    queue.submit(b"PDF")

    processed = ProcessingWorker(queue=queue, extractor=FixedExtractor()).run_once()

    assert processed is not None
    assert processed.status is ProcessingJobStatus.COMPLETED
    assert processed.result is not None
    assert processed.result.text == "NACA report"
