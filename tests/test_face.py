"""
Unit tests for face analysis module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from face_analysis.face_detector import FaceDetector
from face_analysis.micro_expression import MicroExpressionDetector


class TestFaceDetector(unittest.TestCase):
    """Test cases for FaceDetector."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = FaceDetector()
    
    def test_initialization(self):
        """Test FaceDetector initialization."""
        self.assertIsNotNone(self.detector)
        self.assertIsNotNone(self.detector.face_cascade)


class TestMicroExpressionDetector(unittest.TestCase):
    """Test cases for MicroExpressionDetector."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = MicroExpressionDetector()
    
    def test_initialization(self):
        """Test MicroExpressionDetector initialization."""
        self.assertIsNotNone(self.detector)
        self.assertGreater(self.detector.sensitivity, 0)


if __name__ == '__main__':
    unittest.main()
