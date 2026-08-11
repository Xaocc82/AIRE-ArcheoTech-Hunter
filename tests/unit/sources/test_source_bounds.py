import pytest

from aire_archeotech.sources.base import MAX_SOURCE_RECORDS, SourceQuery


def test_source_query_rejects_a_request_above_the_hard_cap() -> None:
    with pytest.raises(ValueError, match="must not exceed"):
        SourceQuery("NACA", max_records=MAX_SOURCE_RECORDS + 1)
