"""
Unit tests for multimodal fusion module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from fusion.multimodal_fusion import MultimodalFusion


class TestMultimodalFusion(unittest.TestCase):
    """Test cases for MultimodalFusion."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fusion = MultimodalFusion()
    
    def test_initialization(self):
        """Test MultimodalFusion initialization."""
        self.assertIsNotNone(self.fusion)
        self.assertEqual(self.fusion.fusion_method, 'weighted_average')
        self.assertIn('face', self.fusion.modality_weights)
        self.assertIn('eyes', self.fusion.modality_weights)
        self.assertIn('audio', self.fusion.modality_weights)
    
    def test_modality_weights_sum(self):
        """Test that modality weights sum to 1.0."""
        total_weight = sum(self.fusion.modality_weights.values())
        self.assertAlmostEqual(total_weight, 1.0, places=5)


if __name__ == '__main__':
    unittest.main()
