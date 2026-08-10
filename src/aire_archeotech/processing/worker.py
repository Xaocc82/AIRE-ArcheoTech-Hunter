"""Single-iteration document-processing worker."""

from aire_archeotech.processing.base import PdfTextExtractor
from aire_archeotech.processing.queue import InMemoryProcessingQueue, ProcessingJob


class ProcessingWorker:
    """Process pending documents through an injected embedded-text extractor."""

    def __init__(self, queue: InMemoryProcessingQueue, extractor: PdfTextExtractor) -> None:
        self._queue = queue
        self._extractor = extractor

    def run_once(self) -> ProcessingJob | None:
        """Process one pending document, or return ``None`` when the queue is empty."""
        job = self._queue.claim_next()
        if job is None:
            return None
        return self._queue.complete(job.id, self._extractor.extract(job.document))
