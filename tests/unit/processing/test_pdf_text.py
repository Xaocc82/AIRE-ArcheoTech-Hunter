from io import BytesIO

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from aire_archeotech.processing.base import ExtractionStatus
from aire_archeotech.processing.pdf_text import PypdfTextExtractor


def _pdf_with_text(text: str) -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=200, height=200)
    font = writer._add_object(
        DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type1"),
                NameObject("/BaseFont"): NameObject("/Helvetica"),
            }
        )
    )
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})}
    )
    content = DecodedStreamObject()
    content.set_data(f"BT /F1 12 Tf 20 100 Td ({text}) Tj ET".encode())
    page[NameObject("/Contents")] = writer._add_object(content)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def test_extracts_embedded_text_from_pdf() -> None:
    result = PypdfTextExtractor().extract(_pdf_with_text("NACA report"))

    assert result.text == "NACA report"
    assert result.status is ExtractionStatus.EXTRACTED
    assert result.engine == "pypdf"


def test_marks_pdf_without_embedded_text_for_ocr() -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    output = BytesIO()
    writer.write(output)

    result = PypdfTextExtractor().extract(output.getvalue())

    assert result.text == ""
    assert result.status is ExtractionStatus.OCR_REQUIRED
