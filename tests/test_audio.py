"""
Tests for audio generation module.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from audio.tts import generate_voice

@patch("audio.tts.edge_tts.Communicate")
def test_generate_voice_success(mock_communicate, tmp_path):
    """Test successful voice generation."""
    out_path = tmp_path / "out.mp3"
    
    # Mock the async save method
    mock_instance = Mock()
    mock_instance.save = AsyncMock()
    mock_communicate.return_value = mock_instance
    
    result = generate_voice("Hello world", out_path)
    
    assert result == out_path
    mock_communicate.assert_called_once_with("Hello world", "en-US-ChristopherNeural")
    mock_instance.save.assert_called_once_with(str(out_path))

@patch("audio.tts.edge_tts.Communicate")
def test_generate_voice_api_error(mock_communicate, tmp_path):
    """Test error handling when TTS fails."""
    out_path = tmp_path / "out.mp3"
    
    # Mock the async save method to raise an exception
    mock_instance = Mock()
    mock_instance.save = AsyncMock(side_effect=Exception("Edge TTS Error"))
    mock_communicate.return_value = mock_instance
    
    result = generate_voice("Hello world", out_path)
    
    assert result is None

