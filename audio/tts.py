"""
Text-To-Speech (TTS) module using edge-tts (Microsoft Edge TTS).
"""

import asyncio
import edge_tts
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)

# Very popular high-quality English voice 
DEFAULT_VOICE = "en-US-ChristopherNeural"

def generate_voice(text: str, output_path: Path) -> Path | None:
    """
    Generate an MP3 from text using edge-tts API.
    
    Args:
        text: The clean text to be spoken.
        output_path: Path where the resulting .mp3 should be saved.
        
    Returns:
        The path to the saved audio file, or None if generation failed.
    """
    try:
        logger.info("Generating TTS audio via edge-tts", voice=DEFAULT_VOICE)
        
        async def _generate():
            communicate = edge_tts.Communicate(text, DEFAULT_VOICE)
            await communicate.save(str(output_path))
            
        # Run the async generation block
        asyncio.run(_generate())
        
        logger.info("Saved TTS audio", path=str(output_path))
        return output_path
        
    except Exception as e:
        logger.error("Failed to generate TTS audio", error=str(e))
        return None
