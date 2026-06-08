"""
Video compositing using MoviePy.
"""
from pathlib import Path
import structlog

from moviepy import ImageClip, AudioFileClip, CompositeVideoClip

logger = structlog.get_logger(__name__)

def composite_video(image_path: Path, audio_path: Path, output_path: Path) -> Path | None:
    """
    Composite a static image and audio into a final mp4 video.
    Applies a slow zoom effect to the image.
    """
    try:
        # Load audio to get duration
        audio = AudioFileClip(str(audio_path))
        duration = audio.duration
        
        # Load image
        img_clip = ImageClip(str(image_path)).with_duration(duration)
        
        # Target vertical resolution (Shorts/TikTok)
        W, H = 1080, 1920
        
        # Scale image to fit within width with some padding
        img_clip = img_clip.resized(width=W * 0.9)
        
        # Apply slow zoom (Ken Burns)
        # moviepy resize with a function resizes dynamically over time
        def zoom(t):
            return 1.0 + 0.1 * (t / duration)
            
        animated_img = img_clip.resized(zoom).with_position("center")
        
        # Composite on a dark grey background
        final_video = CompositeVideoClip([animated_img], size=(W, H), bg_color=(20, 20, 20))
        final_video = final_video.with_audio(audio)
        
        logger.info("Rendering video... This may take a moment", duration=duration)
        
        # Write file
        final_video.write_videofile(
            str(output_path),
            fps=30,
            codec="libx264",
            audio_codec="aac",
            logger=None,  # Disable stdout progress bar spam
            preset="ultrafast",
            threads=4
        )
        
        # Cleanup
        audio.close()
        img_clip.close()
        final_video.close()
        
        logger.info("Video rendered successfully", path=str(output_path))
        return output_path
        
    except Exception as e:
        logger.error("Failed to composite video", error=str(e))
        return None
