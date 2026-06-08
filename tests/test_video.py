"""
Tests for video generation and compositing modules.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from video.screenshot import generate_code_image
from video.compositor import composite_video

@patch("video.screenshot.sync_playwright")
def test_generate_code_image_success(mock_playwright, tmp_path):
    """Test generating a code screenshot."""
    # Mock playwright Context manager
    mock_p = Mock()
    mock_playwright.return_value.__enter__.return_value = mock_p
    
    mock_browser = Mock()
    mock_p.chromium.launch.return_value = mock_browser
    
    mock_page = Mock()
    mock_browser.new_page.return_value = mock_page
    
    mock_element = Mock()
    mock_page.locator.return_value = mock_element
    
    out_path = tmp_path / "code.png"
    code = 'print("hello world")'
    
    result = generate_code_image(code, out_path)
    
    assert result == out_path
    
    # Verify playwright flow
    mock_browser.new_page.assert_called_once()
    mock_page.set_content.assert_called_once()
    mock_page.locator.assert_called_with("#capture-area")
    mock_element.screenshot.assert_called_once_with(path=str(out_path), omit_background=True)
    mock_browser.close.assert_called_once()

def test_generate_code_image_empty_code(tmp_path):
    """Test gracefully skipping empty code."""
    out_path = tmp_path / "code.png"
    result = generate_code_image("   ", out_path)
    assert result is None

@patch("video.compositor.CompositeVideoClip")
@patch("video.compositor.ImageClip")
@patch("video.compositor.AudioFileClip")
def test_composite_video_success(mock_audio_clip, mock_image_clip, mock_composite_clip, tmp_path):
    """Test compositing an image and audio into a video."""
    img_path = tmp_path / "code.png"
    audio_path = tmp_path / "voice.mp3"
    out_path = tmp_path / "final.mp4"
    
    img_path.write_text("fake img")
    audio_path.write_text("fake audio")
    
    # Mock audio
    mock_audio = Mock()
    mock_audio.duration = 5.0
    mock_audio_clip.return_value = mock_audio
    
    # Mock image
    mock_img = Mock()
    mock_image_clip.return_value = mock_img
    mock_img.with_duration.return_value = mock_img
    mock_img.resized.return_value = mock_img
    mock_img.with_position.return_value = mock_img
    
    # Mock composite
    mock_final = Mock()
    mock_composite_clip.return_value = mock_final
    mock_final.with_audio.return_value = mock_final
    
    result = composite_video(img_path, audio_path, out_path)
    
    assert result == out_path
    
    mock_audio_clip.assert_called_once_with(str(audio_path))
    mock_image_clip.assert_called_once_with(str(img_path))
    mock_composite_clip.assert_called_once()
    
    mock_final.write_videofile.assert_called_once()
    
    # Check cleanup
    mock_audio.close.assert_called_once()
    mock_img.close.assert_called_once()
    mock_final.close.assert_called_once()
