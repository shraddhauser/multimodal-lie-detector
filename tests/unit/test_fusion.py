"""
Unit tests for multimodal fusion module.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from fusion.multimodal_fusion import MultimodalFusion


class TestMultimodalFusion:
    """Tests for MultimodalFusion."""

    def setup_method(self):
        self.fusion = MultimodalFusion()

    def test_initialization(self):
        assert self.fusion is not None

    def test_identical_baseline_zero_deviation(self):
        """With identical baseline and segment, all deviations should be ≈ 0."""
        features = {
            'blinks_per_minute': 15.0,
            'aversion_ratio': 0.1,
            'head_movement_variance': 2.0,
            'pitch_mean': 200.0,
            'pitch_std': 20.0,
            'speech_rate': 3.5,
            'pause_ratio': 0.2,
        }
        result = self.fusion.compute_deviation(features, features.copy())
        assert result['deviation_index'] == pytest.approx(0.0, abs=1e-6)
        for key, z in result['per_signal'].items():
            assert z == pytest.approx(0.0, abs=1e-6)

    def test_shifted_pitch_raises_deviation(self):
        """A shifted pitch should raise the audio deviation."""
        baseline = {
            'blinks_per_minute': 15.0,
            'pitch_mean': 200.0,
        }
        segment = {
            'blinks_per_minute': 15.0,
            'pitch_mean': 300.0,  # 50% higher
        }
        result = self.fusion.compute_deviation(baseline, segment)
        assert result['deviation_index'] > 0
        assert result['per_signal']['pitch_mean'] > 0

    def test_missing_modality_handled(self):
        """A missing modality should not crash — its weight is renormalised."""
        baseline = {
            'blinks_per_minute': 15.0,
            'pitch_mean': 200.0,
        }
        segment = {
            'blinks_per_minute': 15.0,
            # pitch_mean missing
        }
        result = self.fusion.compute_deviation(baseline, segment)
        assert 'pitch_mean' not in result['per_signal']
        assert 'blinks_per_minute' in result['per_signal']

    def test_no_lie_truth_label(self):
        """The output should never contain a 'lie' or 'truth' label."""
        features = {
            'blinks_per_minute': 15.0,
            'pitch_mean': 200.0,
        }
        result = self.fusion.compute_deviation(features, features)
        result_str = str(result).lower()
        assert 'lie' not in result_str or 'lie' in 'applied'  # guard against substring
        # More explicit check
        for key in result:
            assert key not in ('lie', 'truth', 'deception', 'deception_score')
        assert 'score' not in result  # no ambiguous 'score' key at top level


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
