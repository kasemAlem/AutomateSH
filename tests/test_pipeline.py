"""
Tests for pipeline nodes and graph routing.
"""

import pytest
from pathlib import Path


class TestNormalizeTopic:
    """Test topic normalization node."""

    def test_basic_capitalization(self):
        from engine.nodes import node_normalize_topic
        result = node_normalize_topic({"topic": "github actions cache", "audience": "developers"})
        assert result["normalized_topic"] == "Github Actions Cache"

    def test_preserves_all_caps_acronyms(self):
        from engine.nodes import node_normalize_topic
        result = node_normalize_topic({"topic": "CI/CD with YAML", "audience": "developers"})
        # CI and YAML are all-caps so they should be preserved
        assert "CI/CD" in result["normalized_topic"] or "Ci/Cd" in result["normalized_topic"]

    def test_strips_whitespace(self):
        from engine.nodes import node_normalize_topic
        result = node_normalize_topic({"topic": "  fzf  linux  ", "audience": "developers"})
        assert not result["normalized_topic"].startswith(" ")
        assert not result["normalized_topic"].endswith(" ")


class TestQualityReview:
    """Test quality review node parsing."""

    def test_parses_high_score(self, mock_llm_response):
        from engine.nodes import node_quality_review
        mock_llm_response("SCORE: 9\nSTRENGTHS:\n- Great hook\nISSUES:\nNone\nSUGGESTION:\nNone")

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("engine.nodes._call_llm", lambda p: "SCORE: 9\nSTRENGTHS:\n- Great hook\nISSUES:\nNone\nSUGGESTION:\nNone")
            result = node_quality_review({
                "normalized_topic": "GitHub Cache",
                "selected_title": "Speed Up CI",
                "script": "Your CI is slow. Use cache. Three lines of YAML. Builds go 8x faster. Follow us.",
                "code_example": "- uses: actions/cache@v4",
                "quality_passed": False,
                "retry_count": 0,
                "errors": [],
            })

        assert result["quality_score"] == 9
        assert result["quality_passed"] is True

    def test_parses_low_score_fails(self):
        from engine.nodes import node_quality_review
        import unittest.mock as mock

        with mock.patch("engine.nodes._call_llm", return_value="SCORE: 4\nSTRENGTHS:\n- ok\nISSUES:\n- too short\nSUGGESTION:\nRewrite hook"):
            result = node_quality_review({
                "normalized_topic": "Topic",
                "selected_title": "Title",
                "script": "Short.",
                "code_example": "pass",
                "quality_passed": False,
                "retry_count": 0,
                "errors": [],
            })

        assert result["quality_score"] == 4
        assert result["quality_passed"] is False
        assert result["retry_count"] == 1  # Incremented because it failed

    def test_retry_count_increments_on_failure(self):
        from engine.nodes import node_quality_review
        import unittest.mock as mock

        with mock.patch("engine.nodes._call_llm", return_value="SCORE: 3"):
            result = node_quality_review({
                "normalized_topic": "Topic",
                "selected_title": "Title",
                "script": "Bad script.",
                "code_example": "pass",
                "quality_passed": False,
                "retry_count": 1,  # Already had one retry
                "errors": [],
            })

        assert result["retry_count"] == 2  # Incremented again


class TestQualityRouting:
    """Test the quality gate routing logic."""

    def test_routes_to_export_when_passed(self):
        from engine.graph import route_quality_check
        state = {"quality_passed": True, "retry_count": 0, "quality_score": 8}
        assert route_quality_check(state) == "markdown_export"

    def test_routes_to_retry_when_failed_and_under_limit(self):
        from engine.graph import route_quality_check
        state = {"quality_passed": False, "retry_count": 0, "quality_score": 5}
        assert route_quality_check(state) == "script_writer"

    def test_routes_to_export_at_max_retries(self):
        from engine.graph import route_quality_check
        state = {"quality_passed": False, "retry_count": 2, "quality_score": 4}
        assert route_quality_check(state) == "markdown_export"


class TestMarkdownExport:
    """Test the markdown export node."""

    def test_creates_file(self, sample_state, tmp_path, monkeypatch):
        from engine.nodes import node_export_markdown

        monkeypatch.chdir(tmp_path)
        output_path = str(tmp_path / "output")

        def fake_settings():
            class S:
                output_dir = output_path
            return S()

        monkeypatch.setattr("engine.nodes.get_settings", fake_settings)

        result = node_export_markdown(sample_state)

        assert "markdown_path" in result
        filepath = Path(result["markdown_path"])
        assert filepath.exists()

    def test_file_contains_script(self, sample_state, tmp_path, monkeypatch):
        from engine.nodes import node_export_markdown

        monkeypatch.chdir(tmp_path)
        output_path = str(tmp_path / "output")

        def fake_settings():
            class S:
                output_dir = output_path
            return S()

        monkeypatch.setattr("engine.nodes.get_settings", fake_settings)

        result = node_export_markdown(sample_state)
        content = Path(result["markdown_path"]).read_text()

        assert sample_state["script"] in content
        assert sample_state["selected_title"] in content
        assert "#github" in content.lower()


class TestHashtagParsing:
    """Test hashtag parsing helper."""

    def test_parses_space_separated(self):
        from engine.nodes import _parse_hashtags
        result = _parse_hashtags("#github #devops #linux")
        assert "#github" in result
        assert "#devops" in result

    def test_adds_hash_if_missing(self):
        from engine.nodes import _parse_hashtags
        result = _parse_hashtags("github devops linux")
        assert "#github" in result

    def test_deduplicates(self):
        from engine.nodes import _parse_hashtags
        result = _parse_hashtags("#github #github #devops")
        assert result.count("#github") == 1

    def test_limits_to_15(self):
        from engine.nodes import _parse_hashtags
        tags = " ".join(f"#tag{i}" for i in range(30))
        result = _parse_hashtags(tags)
        assert len(result) <= 15


class TestVideoAssetsExport:
    """Test the video assets generation node."""
    
    def test_creates_files(self, tmp_path):
        from engine.nodes import node_export_video_assets
        
        md_path = tmp_path / "2024-01-01-test-topic.md"
        md_path.write_text("fake md content")
        
        state = {
            "markdown_path": str(md_path),
            "script": "**bold** and *italic* and __underline__ [Camera zooms]\n(Happy tone) Hey guys!  \n",
            "selected_title": "Test Title",
            "thumbnail_text": "WOW TEST",
            "code_example": "print('hello')"
        }
        
        node_export_video_assets(state)
        
        base_name = md_path.stem
        
        voice_path = tmp_path / f"{base_name}-voice.txt"
        thumb_path = tmp_path / f"{base_name}-thumbnail.txt"
        rec_path = tmp_path / f"{base_name}-recording_notes.md"
        
        assert voice_path.exists()
        assert thumb_path.exists()
        assert rec_path.exists()
        
        # Test voice stripping
        voice_text = voice_path.read_text()
        assert "bold" in voice_text
        assert "**" not in voice_text
        assert "italic" in voice_text
        assert "*" not in voice_text
        assert "underline" in voice_text
        assert "__" not in voice_text
        assert "Camera zooms" not in voice_text
        assert "Happy tone" not in voice_text
        assert "Hey guys!" in voice_text
        
        # Test thumbnail
        thumb_text = thumb_path.read_text()
        assert "Test Title" in thumb_text
        assert "WOW TEST" in thumb_text
        
        # Test recording notes
        rec_text = rec_path.read_text()
        assert "print('hello')" in rec_text
        assert "Test Title" in rec_text
