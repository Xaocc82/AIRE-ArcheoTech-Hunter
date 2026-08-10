from aire_archeotech.screening.records import ScreeningChannel, ScreeningRecord, ScreeningVerdict


def test_screening_record_preserves_bounded_research_verdict() -> None:
    record = ScreeningRecord(
        candidate_id="candidate-naca-123",
        channel=ScreeningChannel.PATENT,
        verdict=ScreeningVerdict.HOLD,
        reviewer="researcher@example.test",
        rationale="Requires a jurisdiction-specific human review.",
    )

    assert record.verdict is ScreeningVerdict.HOLD
    assert record.channel is ScreeningChannel.PATENT
