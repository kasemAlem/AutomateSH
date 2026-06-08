"""
Pytest configuration and shared fixtures.
"""

import pytest
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def reset_caches():
    """Clear lru_cache singletons between tests to prevent state leakage."""
    from app.config import get_settings
    from providers.factory import get_provider
    from database.connection import get_engine

    get_settings.cache_clear()
    get_provider.cache_clear()

    yield

    get_settings.cache_clear()
    get_provider.cache_clear()


@pytest.fixture
def mock_llm_response(monkeypatch):
    """Patch call_llm to return a fixed response."""
    def _patch(response: str):
        monkeypatch.setattr("engine.nodes._call_llm", lambda prompt: response)
    return _patch


@pytest.fixture
def sample_state() -> dict:
    """Complete ContentState with realistic sample data."""
    return {
        "topic": "GitHub Actions Cache",
        "normalized_topic": "Github Actions Cache",
        "audience": "developers",
        "research": (
            "PROBLEM: Developers waste 5-10 minutes per CI run re-downloading dependencies.\n"
            "WHY IT MATTERS: A 10-person team loses 100+ developer-hours per month to slow CI.\n"
            "BEST PRACTICE: Use actions/cache@v4 with a hash of your lockfile as the key.\n"
            "INTERESTING FACT: GitHub provides 10GB of free cache storage per repository.\n"
            "HOOK IDEA: Your CI pipeline re-downloads the same 500MB of packages every single run."
        ),
        "script": (
            "Your CI re-downloads the same packages every single run. "
            "That's minutes of wasted time on every push. "
            "GitHub Actions cache fixes it with three lines of YAML. "
            "Add actions/cache and point it at your node_modules. "
            "Your builds go from 8 minutes to under 2. "
            "Follow Automate.sh for daily dev shortcuts."
        ),
        "code_example": (
            "- uses: actions/cache@v4\n"
            "  with:\n"
            "    path: ~/.npm\n"
            "    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}\n"
            "    restore-keys: |\n"
            "      ${{ runner.os }}-node-  # Partial cache fallback"
        ),
        "titles": [
            "Your CI Is Wasting 8 Minutes Every Run",
            "GitHub Actions Cache: The Secret Nobody Uses",
            "Speed Up CI With Three Lines of YAML",
            "Stop Re-Downloading NPM Packages in CI",
            "GitHub Actions Cache Tutorial 2024",
        ],
        "selected_title": "Your CI Is Wasting 8 Minutes Every Run",
        "thumbnail_text": "STOP SLOW CI",
        "hashtags": ["#automatesh", "#github", "#githubactions", "#devops", "#cicd"],
        "description": (
            "Learn how to use GitHub Actions cache to eliminate redundant dependency "
            "downloads in your CI pipeline. This simple three-line YAML snippet can "
            "cut your build time from 8 minutes to under 2. Follow for daily automation shortcuts."
        ),
        "quality_score": 8,
        "quality_feedback": "SCORE: 8\nSTRENGTHS:\n- Strong hook\n- Specific numbers\nISSUES:\nNone\nSUGGESTION:\nNone",
        "quality_passed": True,
        "retry_count": 0,
        "markdown_path": "",
        "errors": [],
    }
