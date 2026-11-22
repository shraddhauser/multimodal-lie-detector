"""
Unit tests for audio analysis module.
Uses synthetic WAV fixtures — no real data, no internet, no GPU.
"""

import sys
import os
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from audio_analysis.acoustic_features import AcousticFeatureExtractor


class TestAcousticFeatureExtractor:
    """Tests for AcousticFeatureExtractor."""

    def setup_method(self):
        self.extractor = AcousticFeatureExtractor(target_sr=16000)

    def test_initialization(self):
        assert self.extractor.target_sr == 16000

    def test_sine_pitch(self, sine_wav_path):
        """The pitch of a 220 Hz sine wave should be within ±5 Hz."""
        y, sr = self.extractor.load_audio(sine_wav_path)
        feats = self.extractor.extract_features(y, sr)
        assert feats['pitch_mean'] is not None
        assert abs(feats['pitch_mean'] - 220) < 5, (
            f"Expected ≈220 Hz, got {feats['pitch_mean']}"
        )

    def test_silence_pause_ratio(self, silent_wav_path):
        """Silence should give a high pause ratio."""
        y, sr = self.extractor.load_audio(silent_wav_path)
        feats = self.extractor.extract_features(y, sr)
        assert feats['pause_ratio'] > 0.8, (
            f"Expected high pause_ratio for silence, got {feats['pause_ratio']}"
        )

    def test_silence_pitch_is_nan_safe(self, silent_wav_path):
        """Silence should give None pitch (NaN-safe), not crash."""
        y, sr = self.extractor.load_audio(silent_wav_path)
        feats = self.extractor.extract_features(y, sr)
        # pitch_mean may be None if no voiced frames
        assert feats['pitch_mean'] is None or isinstance(feats['pitch_mean'], float)

    def test_stereo_becomes_mono(self, stereo_wav_path):
        """Stereo input should be loaded and processed without error."""
        y, sr = self.extractor.load_audio(stereo_wav_path)
        assert y.ndim == 1, "Audio should be mono after loading"
        feats = self.extractor.extract_features(y, sr)
        assert isinstance(feats, dict)

    def test_feature_keys(self, sine_wav_path):
        """All expected feature keys should be present."""
        y, sr = self.extractor.load_audio(sine_wav_path)
        feats = self.extractor.extract_features(y, sr)
        for key in ['pitch_mean', 'pitch_std', 'jitter', 'shimmer',
                     'speech_rate', 'pause_ratio']:
            assert key in feats


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
