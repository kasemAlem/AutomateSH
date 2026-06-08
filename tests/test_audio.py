"""
Tests for audio generation module.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from audio.tts import generate_voice

def test_generate_voice_no_api_key(monkeypatch, tmp_path):
    """Test that voice generation skips gracefully if no API key is set."""
    def mock_settings():
        class Settings:
            openai_api_key = None
        return Settings()
        
    monkeypatch.setattr("audio.tts.get_settings", mock_settings)
    
    out_path = tmp_path / "out.mp3"
    result = generate_voice("Hello world", out_path)
    
    assert result is None
    assert not out_path.exists()

@patch("audio.tts.OpenAI")
def test_generate_voice_success(mock_openai, monkeypatch, tmp_path):
    """Test successful voice generation."""
    def mock_settings():
        class Settings:
            openai_api_key = "fake_key"
            tts_voice = "echo"
            tts_model = "tts-1"
        return Settings()
        
    monkeypatch.setattr("audio.tts.get_settings", mock_settings)
    
    # Mock the OpenAI client response
    mock_client = Mock()
    mock_openai.return_value = mock_client
    
    mock_response = Mock()
    mock_response.content = b"fake_mp3_data"
    mock_client.audio.speech.create.return_value = mock_response
    
    out_path = tmp_path / "out.mp3"
    result = generate_voice("Hello world", out_path)
    
    assert result == out_path
    assert out_path.exists()
    assert out_path.read_bytes() == b"fake_mp3_data"
    
    # Verify the client was called with correct args
    mock_client.audio.speech.create.assert_called_once_with(
        model="tts-1",
        voice="echo",
        input="Hello world"
    )

@patch("audio.tts.OpenAI")
def test_generate_voice_api_error(mock_openai, monkeypatch, tmp_path):
    """Test error handling when API fails."""
    def mock_settings():
        class Settings:
            openai_api_key = "fake_key"
            tts_voice = "echo"
            tts_model = "tts-1"
        return Settings()
        
    monkeypatch.setattr("audio.tts.get_settings", mock_settings)
    
    # Mock the OpenAI client to raise an exception
    mock_client = Mock()
    mock_openai.return_value = mock_client
    mock_client.audio.speech.create.side_effect = Exception("API Error")
    
    out_path = tmp_path / "out.mp3"
    result = generate_voice("Hello world", out_path)
    
    assert result is None
    assert not out_path.exists()
