"""
Unit tests for audio analysis module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from audio_analysis.speech_to_text import SpeechToTextConverter
from audio_analysis.emotion_analysis import EmotionAnalyzer
from audio_analysis.acoustic_features import AcousticFeatureExtractor


class TestSpeechToText(unittest.TestCase):
    """Test cases for SpeechToTextConverter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.converter = SpeechToTextConverter()
    
    def test_initialization(self):
        """Test SpeechToTextConverter initialization."""
        self.assertIsNotNone(self.converter)
        self.assertEqual(self.converter.model_name, 'base')


class TestEmotionAnalyzer(unittest.TestCase):
    """Test cases for EmotionAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = EmotionAnalyzer()
    
    def test_initialization(self):
        """Test EmotionAnalyzer initialization."""
        self.assertIsNotNone(self.analyzer)
        self.assertGreater(len(self.analyzer.emotions), 0)


class TestAcousticFeatures(unittest.TestCase):
    """Test cases for AcousticFeatureExtractor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = AcousticFeatureExtractor()
    
    def test_initialization(self):
        """Test AcousticFeatureExtractor initialization."""
        self.assertIsNotNone(self.extractor)
        self.assertEqual(self.extractor.sample_rate, 16000)


if __name__ == '__main__':
    unittest.main()
