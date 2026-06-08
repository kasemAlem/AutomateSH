"""
LangGraph pipeline state definition.
ContentState is passed between all nodes in the content generation graph.
"""

from operator import add
from typing import Annotated

from typing_extensions import TypedDict


class ContentState(TypedDict):
    """
    Shared state flowing through the content generation pipeline.

    Fields are updated by each node. Fields annotated with `add` reducer
    accumulate values across nodes (used for error list).
    """

    # ── Input ──────────────────────────────────────────────────
    topic: str
    """Original topic as provided by the user."""

    normalized_topic: str
    """Cleaned and properly capitalized topic."""

    audience: str
    """Target audience (default: 'developers')."""

    generate_audio: bool
    """Flag to indicate if TTS audio should be generated."""

    generate_video: bool
    """Flag to indicate if final mp4 video should be composited."""

    publish_tiktok: bool
    """Flag to indicate if the final video should be uploaded and published to TikTok."""

    tiktok_publish_url: str
    """The URL or status of the published TikTok video."""

    # ── Research ───────────────────────────────────────────────
    research: str
    """Research output: problem, why it matters, best practice, hook idea."""

    # ── Generated Content ──────────────────────────────────────
    script: str
    """20-40 second video script with HOOK → PROBLEM → SOLUTION → DEMO → CTA."""

    code_example: str
    """Production-quality code example (max 15 lines)."""

    titles: list[str]
    """5 generated title options, ordered best-first."""

    selected_title: str
    """Primary title selected from titles list."""

    thumbnail_text: str
    """Thumbnail overlay text (max 5 words)."""

    hashtags: list[str]
    """15 relevant hashtags for platform distribution."""

    description: str
    """SEO-optimized video description (max 100 words)."""

    # ── Quality Control ────────────────────────────────────────
    quality_score: int
    """Quality score from 1-10 assigned by the Quality Reviewer."""

    quality_feedback: str
    """Full quality review text including strengths and improvement notes."""

    quality_passed: bool
    """True if quality_score >= threshold, False otherwise."""

    retry_count: int
    """Number of times the script has been retried due to quality failure."""

    # ── Output ─────────────────────────────────────────────────
    markdown_path: str
    """Path to the exported markdown file."""

    errors: Annotated[list[str], add]
    """List of non-fatal errors accumulated across nodes."""
