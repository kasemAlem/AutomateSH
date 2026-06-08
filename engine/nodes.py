"""
LangGraph pipeline nodes.
Each node is a pure function: (ContentState) -> dict[str, Any]
The returned dict contains only the fields this node updates.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog

from app.config import get_settings
from engine.state import ContentState
from providers.factory import get_provider
from audio.tts import generate_voice
from video.screenshot import generate_code_image
from video.compositor import composite_video

logger = structlog.get_logger(__name__)

# Prompts directory is always relative to the project root
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


# ── Helpers ────────────────────────────────────────────────────────────────────


def _load_prompt(name: str) -> str:
    """Load a prompt template from the prompts directory."""
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def _call_llm(prompt: str) -> str:
    """Call the configured LLM and return the response as a string."""
    provider = get_provider()
    return provider.generate(prompt)


def _parse_score(text: str, default: int = 5) -> int:
    """Extract 'SCORE: N' from quality review output."""
    match = re.search(r"SCORE:\s*(\d+)", text, re.IGNORECASE)
    if match:
        return max(1, min(10, int(match.group(1))))
    return default


def _parse_list_items(text: str) -> list[str]:
    """Parse numbered or bulleted list items from LLM output."""
    items = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        # Strip leading numbering/bullets: "1.", "-", "*", "•"
        cleaned = re.sub(r"^[\d]+[\.\)]\s*|^[-*•]\s*", "", line).strip()
        if cleaned:
            items.append(cleaned)
    return items


def _parse_hashtags(text: str) -> list[str]:
    """Extract and normalize hashtags from LLM output."""
    # Split on whitespace and commas
    tokens = re.split(r"[\s,]+", text.strip())
    hashtags: list[str] = []
    seen: set[str] = set()

    for token in tokens:
        token = token.strip().lower().rstrip(",.")
        if not token:
            continue
        tag = token if token.startswith("#") else f"#{token}"
        # Remove non-alphanumeric except #
        tag = re.sub(r"[^#\w]", "", tag)
        if tag not in seen and len(tag) > 1:
            seen.add(tag)
            hashtags.append(tag)

    return hashtags[:15]


# ── Node 0: Normalize Topic ────────────────────────────────────────────────────


def node_normalize_topic(state: ContentState) -> dict[str, Any]:
    """Clean and normalize the raw topic string."""
    raw = state["topic"].strip()
    # Title-case each word, preserve existing acronyms (all-caps words)
    normalized = " ".join(
        word if word.isupper() and len(word) > 1 else word.capitalize()
        for word in raw.split()
    )
    logger.info("Topic normalized", raw=raw, normalized=normalized)
    return {"normalized_topic": normalized}


# ── Node 1: Research Agent ────────────────────────────────────────────────────


def node_research(state: ContentState) -> dict[str, Any]:
    """Research the topic and extract developer pain points and best practices."""
    template = _load_prompt("research")
    prompt = template.format(
        topic=state["normalized_topic"],
        audience=state.get("audience", "developers"),
    )

    logger.info("Running research agent", topic=state["normalized_topic"])
    research = _call_llm(prompt)
    return {"research": research}


# ── Node 2: Script Writer ─────────────────────────────────────────────────────


def node_write_script(state: ContentState) -> dict[str, Any]:
    """Write a 20-40 second video script (HOOK → PROBLEM → SOLUTION → DEMO → CTA)."""
    template = _load_prompt("script")
    retry = state.get("retry_count", 0)
    feedback = state.get("quality_feedback", "")

    # Inject previous feedback when retrying
    feedback_section = (
        f"\n\nPREVIOUS REVIEW FEEDBACK (address these issues):\n{feedback}"
        if retry > 0 and feedback
        else ""
    )

    prompt = template.format(
        topic=state["normalized_topic"],
        research=state["research"],
        audience=state.get("audience", "developers"),
        feedback=feedback_section,
    )

    logger.info("Writing script", topic=state["normalized_topic"], retry=retry)
    script = _call_llm(prompt)
    return {"script": script.strip()}


# ── Node 3: Code Generator ────────────────────────────────────────────────────


def node_generate_code(state: ContentState) -> dict[str, Any]:
    """Generate a production-quality code example for the video."""
    template = _load_prompt("code")
    prompt = template.format(
        topic=state["normalized_topic"],
        script=state["script"],
        research=state["research"],
    )

    logger.info("Generating code example")
    code = _call_llm(prompt)

    # Strip surrounding markdown fences if the LLM wrapped the response
    code = re.sub(r"^```[\w]*\n?", "", code.strip())
    code = re.sub(r"\n?```$", "", code.strip())

    return {"code_example": code.strip()}


# ── Node 4: Title Generator ───────────────────────────────────────────────────


def node_generate_titles(state: ContentState) -> dict[str, Any]:
    """Generate 5 viral title options and select the best one."""
    template = _load_prompt("title")
    prompt = template.format(
        topic=state["normalized_topic"],
        script=state["script"],
        research=state["research"],
    )

    logger.info("Generating titles")
    raw = _call_llm(prompt)

    titles = _parse_list_items(raw)
    if not titles:
        # Fallback: use raw output as single title
        titles = [raw.strip()]

    selected = titles[0] if titles else state["normalized_topic"]
    logger.info("Titles generated", count=len(titles), selected=selected)
    return {"titles": titles, "selected_title": selected}


# ── Node 5: Thumbnail Generator ──────────────────────────────────────────────


def node_generate_thumbnail(state: ContentState) -> dict[str, Any]:
    """Generate thumbnail text (max 5 words, high contrast and readable)."""
    template = _load_prompt("thumbnail")
    prompt = template.format(
        title=state["selected_title"],
        topic=state["normalized_topic"],
    )

    logger.info("Generating thumbnail text")
    raw = _call_llm(prompt)

    # Strictly enforce 5-word maximum
    words = raw.strip().split()[:5]
    thumbnail_text = " ".join(words).upper()  # Uppercase for thumbnail impact
    return {"thumbnail_text": thumbnail_text}


# ── Node 6: Hashtag Generator ─────────────────────────────────────────────────


def node_generate_hashtags(state: ContentState) -> dict[str, Any]:
    """Generate 15 relevant hashtags for platform distribution."""
    template = _load_prompt("hashtags")
    prompt = template.format(
        topic=state["normalized_topic"],
        title=state["selected_title"],
    )

    logger.info("Generating hashtags")
    raw = _call_llm(prompt)
    hashtags = _parse_hashtags(raw)

    # Always ensure core brand hashtag is present
    if "#automatesh" not in hashtags:
        hashtags = ["#automatesh"] + hashtags[:14]

    return {"hashtags": hashtags}


# ── Node 7: Description Generator ────────────────────────────────────────────


def node_generate_description(state: ContentState) -> dict[str, Any]:
    """Generate a 100-word SEO-optimized video description."""
    template = _load_prompt("description")
    prompt = template.format(
        topic=state["normalized_topic"],
        title=state["selected_title"],
        script=state["script"],
        research=state["research"],
    )

    logger.info("Generating description")
    description = _call_llm(prompt)

    # Hard-cap at 100 words
    words = description.strip().split()
    if len(words) > 100:
        description = " ".join(words[:100]) + "..."

    return {"description": description.strip()}


# ── Node 8: Quality Reviewer (Gap #2 fix) ────────────────────────────────────


def node_quality_review(state: ContentState) -> dict[str, Any]:
    """
    Review content quality and score it 1-10.
    If score < threshold, the graph retries from script_writer.
    """
    template = _load_prompt("quality_review")
    script = state["script"]
    word_count = len(script.split())

    prompt = template.format(
        topic=state["normalized_topic"],
        title=state["selected_title"],
        script=script,
        code_example=state["code_example"],
        word_count=word_count,
    )

    logger.info("Running quality review", word_count=word_count)
    review = _call_llm(prompt)

    score = _parse_score(review)
    threshold = get_settings().quality_threshold
    passed = score >= threshold

    # Increment retry_count only when failing (used by router to prevent infinite loops)
    retry_count = state.get("retry_count", 0)
    new_retry = retry_count + (1 if not passed else 0)

    logger.info(
        "Quality review complete",
        score=score,
        threshold=threshold,
        passed=passed,
        retry=retry_count,
    )

    return {
        "quality_score": score,
        "quality_feedback": review.strip(),
        "quality_passed": passed,
        "retry_count": new_retry,
    }


# ── Node 9: Markdown Export ───────────────────────────────────────────────────


def node_export_markdown(state: ContentState) -> dict[str, Any]:
    """Export all generated content to a structured Markdown file."""
    settings = get_settings()
    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build filename: YYYY-MM-DD-topic-slug.md
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = re.sub(r"[^\w\s-]", "", state["normalized_topic"].lower())
    slug = re.sub(r"[-\s]+", "-", slug).strip("-")
    filename = f"{date_str}-{slug}.md"
    filepath = output_dir / filename

    hashtags_str = " ".join(state.get("hashtags", []))
    titles_section = "\n".join(
        f"{i + 1}. {title}" for i, title in enumerate(state.get("titles", []))
    )

    quality_badge = "🟢" if state.get("quality_score", 0) >= 7 else "🟡"

    content = f"""# {state["selected_title"]}

> **Topic:** {state["normalized_topic"]}  
> **Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}  
> **Quality Score:** {quality_badge} {state.get("quality_score", "N/A")}/10  
> **Audience:** {state.get("audience", "developers")}

---

## 🎬 Video Script

> *Target: 20-40 seconds | {len(state["script"].split())} words*

{state["script"]}

---

## 💻 Code Example

```
{state["code_example"]}
```

---

## 📝 Description

{state["description"]}

---

## 🏷️ Hashtags

{hashtags_str}

---

## 🖼️ Thumbnail Text

> **{state["thumbnail_text"]}**

---

## 📋 All Title Options

{titles_section}

---

## 📊 Research Notes

{state.get("research", "")}

---

## 🔍 Quality Review

```
{state.get("quality_feedback", "Not reviewed")}
```

---

*Generated by [Automate.sh](https://automate.sh) Content Engine v1.0*
"""

    filepath.write_text(content, encoding="utf-8")
    logger.info("Markdown exported", path=str(filepath), quality=state.get("quality_score"))

    return {"markdown_path": str(filepath)}


# ── Node 10: Video Assets Export ──────────────────────────────────────────────


def node_export_video_assets(state: ContentState) -> dict[str, Any]:
    """Export supplementary files needed for video creation (voice, thumbnail, recording notes)."""
    if "markdown_path" not in state:
        logger.warning("No markdown_path found, skipping video asset generation")
        return {}
        
    md_path = Path(state["markdown_path"])
    base_dir = md_path.parent
    base_name = md_path.stem
    
    # 1. Voice script (strip markdown and stage directions)
    script_text = state["script"]
    # Strip markdown bold/italic (**text**, *text*, __text__, _text_)
    script_text = re.sub(r"[*_]{1,3}([^*_]+)[*_]{1,3}", r"\1", script_text)
    # Strip bracketed/parenthetical actions like [Camera pans] or (Happy tone)
    script_text = re.sub(r"\[.*?\]|\(.*?\)", "", script_text)
    # Clean up double spaces
    script_text = re.sub(r"[ \t]+", " ", script_text)
    # Clean up empty lines
    script_text = "\n".join(line.strip() for line in script_text.splitlines() if line.strip())
    
    voice_path = base_dir / f"{base_name}-voice.txt"
    voice_path.write_text(script_text, encoding="utf-8")
    
    # 2. Thumbnail text prompt
    thumbnail_text = f"TITLE: {state['selected_title']}\nTHUMBNAIL: {state.get('thumbnail_text', '')}"
    thumb_path = base_dir / f"{base_name}-thumbnail.txt"
    thumb_path.write_text(thumbnail_text, encoding="utf-8")
    
    # 3. Recording notes
    recording_notes = f"""# Recording Notes for: {state['selected_title']}

## Code to Record
```
{state.get('code_example', '')}
```

## Original Script (with visual cues)
{state.get('script', '')}
"""
    rec_path = base_dir / f"{base_name}-recording_notes.md"
    rec_path.write_text(recording_notes, encoding="utf-8")
    
    # 4. Optional TTS generation
    audio_path = None
    if state.get("generate_audio", False) or state.get("generate_video", False):
        audio_path = base_dir / f"{base_name}-voice.mp3"
        logger.info("Generating voiceover audio...")
        generate_voice(script_text, audio_path)
        
    # 5. Optional Video Compositing
    if state.get("generate_video", False):
        if audio_path and audio_path.exists():
            image_path = base_dir / f"{base_name}-code.png"
            video_path = base_dir / f"{base_name}-final.mp4"
            
            logger.info("Generating code screenshot...")
            generate_code_image(state.get("code_example", ""), image_path)
            
            if image_path.exists():
                logger.info("Compositing video...")
                composite_video(image_path, audio_path, video_path)
            else:
                logger.error("Failed to create code screenshot, skipping compositing")
        else:
            logger.error("No audio file found, skipping compositing")
    
    logger.info("Video assets exported", base_name=base_name, dir=str(base_dir))
    
    return {}


# ── Node 11: Publish TikTok ───────────────────────────────────────────────────


def node_publish_tiktok(state: ContentState) -> dict[str, Any]:
    """Upload and publish the generated video to TikTok via Composio."""
    if not state.get("generate_video", False) or not state.get("publish_tiktok", False):
        logger.info("Skipping TikTok publish (flags not set)")
        return {}
        
    if "markdown_path" not in state:
        logger.warning("No markdown_path found, skipping TikTok publish")
        return {}
        
    md_path = Path(state["markdown_path"])
    base_dir = md_path.parent
    base_name = md_path.stem
    video_path = base_dir / f"{base_name}-final.mp4"
    
    if not video_path.exists():
        logger.error("Final video not found for publishing", path=str(video_path))
        return {}
        
    from social.tiktok import upload_and_publish_video
    
    logger.info("Initiating TikTok publishing process...")
    url = upload_and_publish_video(
        video_path=video_path,
        title=state.get("selected_title", "Automated Video"),
        hashtags=state.get("hashtags", [])
    )
    
    if url:
        logger.info("Successfully published to TikTok", url=url)
        return {"tiktok_publish_url": url}
    else:
        logger.error("Failed to publish to TikTok")
        return {}
