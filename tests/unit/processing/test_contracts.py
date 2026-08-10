from aire_archeotech.processing.base import ExtractedText, ExtractionStatus


def test_extracted_text_records_engine_identity() -> None:
    result = ExtractedText(
        text="finding",
        status=ExtractionStatus.EXTRACTED,
        engine="pypdf",
        engine_version="5.0",
    )

    assert result.text == "finding"
    assert result.engine == "pypdf"
