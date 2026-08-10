from pathlib import Path


def test_source_policy_prohibits_uncontrolled_crawling() -> None:
    policy_path = Path("docs/SOURCE_POLICY.md")
    assert policy_path.is_file()

    policy = policy_path.read_text(encoding="utf-8")

    assert "uncontrolled crawling" in policy
