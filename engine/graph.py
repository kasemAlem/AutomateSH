"""
LangGraph content generation graph.
Defines the pipeline topology with conditional retry edge for quality control.

Pipeline flow:
    normalize_topic → research → script_writer → code_generator
    → title_generator → thumbnail_generator → hashtag_generator
    → description_generator → quality_review
                                    ↓ passed / max retries
                              markdown_export
                                    ↓ failed (retry)
                              script_writer  (back to improve script)
"""

import structlog
from langgraph.graph import END, START, StateGraph

from engine.nodes import (
    node_export_markdown,
    node_export_video_assets,
    node_generate_code,
    node_generate_description,
    node_generate_hashtags,
    node_generate_thumbnail,
    node_generate_titles,
    node_normalize_topic,
    node_quality_review,
    node_research,
    node_write_script,
    node_publish_tiktok,
)
from engine.state import ContentState

logger = structlog.get_logger(__name__)


# ── Routing Logic ──────────────────────────────────────────────────────────────


def route_quality_check(state: ContentState) -> str:
    """
    After quality review: decide whether to export or retry the script.

    Returns:
        "markdown_export" → quality passed or max retries reached
        "script_writer"   → quality failed, retry with feedback
    """
    from app.config import get_settings
    max_retries = get_settings().max_retries

    if state.get("quality_passed", False):
        logger.info("Quality passed — exporting", score=state.get("quality_score"))
        return "markdown_export"

    retry_count = state.get("retry_count", 0)
    if retry_count >= max_retries:
        logger.warning(
            "Max retries reached — exporting anyway",
            retries=retry_count,
            score=state.get("quality_score"),
        )
        return "markdown_export"

    logger.info(
        "Quality failed — retrying script",
        score=state.get("quality_score"),
        retry=retry_count,
    )
    return "script_writer"


# ── Graph Builder ──────────────────────────────────────────────────────────────


def build_graph() -> StateGraph:
    """
    Build and compile the content generation StateGraph.

    Returns a compiled LangGraph graph ready to invoke.
    """
    graph = StateGraph(ContentState)

    # Register all nodes
    graph.add_node("normalize_topic", node_normalize_topic)
    graph.add_node("research", node_research)
    graph.add_node("script_writer", node_write_script)
    graph.add_node("code_generator", node_generate_code)
    graph.add_node("title_generator", node_generate_titles)
    graph.add_node("thumbnail_generator", node_generate_thumbnail)
    graph.add_node("hashtag_generator", node_generate_hashtags)
    graph.add_node("description_generator", node_generate_description)
    graph.add_node("quality_review", node_quality_review)
    graph.add_node("markdown_export", node_export_markdown)
    graph.add_node("video_assets_export", node_export_video_assets)
    graph.add_node("publish_tiktok", node_publish_tiktok)

    # Linear pipeline edges
    graph.add_edge(START, "normalize_topic")
    graph.add_edge("normalize_topic", "research")
    graph.add_edge("research", "script_writer")
    graph.add_edge("script_writer", "code_generator")
    graph.add_edge("code_generator", "title_generator")
    graph.add_edge("title_generator", "thumbnail_generator")
    graph.add_edge("thumbnail_generator", "hashtag_generator")
    graph.add_edge("hashtag_generator", "description_generator")
    graph.add_edge("description_generator", "quality_review")

    # Conditional edge: quality gate with retry loop
    graph.add_conditional_edges(
        "quality_review",
        route_quality_check,
        {
            "script_writer": "script_writer",   # retry
            "markdown_export": "markdown_export",  # export
        },
    )

    # Final edges
    graph.add_edge("markdown_export", "video_assets_export")
    graph.add_edge("video_assets_export", "publish_tiktok")
    graph.add_edge("publish_tiktok", END)

    return graph.compile()


# ── Public API ────────────────────────────────────────────────────────────────


def run_pipeline(topic: str, audience: str = "developers", generate_audio: bool = False, generate_video: bool = False, publish_tiktok: bool = False) -> dict:
    """
    Run the full content generation pipeline.

    Args:
        topic: The topic to generate content for.
        audience: The target audience.
        generate_audio: If True, generate TTS audio.
        generate_video: If True, composite final MP4.

    Returns:
        The final state dict.
    """
    logger.info("Starting pipeline", topic=topic, audience=audience, generate_audio=generate_audio, generate_video=generate_video)
    pipeline = build_graph()

    initial_state: ContentState = {
        "topic": topic,
        "normalized_topic": "",
        "audience": audience,
        "generate_audio": generate_audio,
        "generate_video": generate_video,
        "publish_tiktok": publish_tiktok,
        "tiktok_publish_url": "",
        "research": "",
        "script": "",
        "code_example": "",
        "titles": [],
        "selected_title": "",
        "thumbnail_text": "",
        "hashtags": [],
        "description": "",
        "quality_score": 0,
        "quality_feedback": "",
        "quality_passed": False,
        "retry_count": 0,
        "markdown_path": "",
        "errors": [],
    }

    result = pipeline.invoke(initial_state)
    logger.info(
        "Pipeline complete",
        topic=topic,
        quality=result.get("quality_score"),
        path=result.get("markdown_path"),
    )
    return result
