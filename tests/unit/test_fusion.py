"""
Unit tests for multimodal fusion module.
"""


import json
import re

import pytest

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
        for z in result['per_signal'].values():
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

    def test_baseline_windows_give_true_z_score(self):
        """With several baseline windows, deviation = (segment - mean) / std."""
        baseline = {'pitch_mean': [190.0, 200.0, 210.0]}  # mean 200, sample std 10
        segment = {'pitch_mean': 230.0}
        result = self.fusion.compute_deviation(baseline, segment)
        assert result['methods']['pitch_mean'] == 'z_score'
        assert result['per_signal']['pitch_mean'] == pytest.approx(3.0)
        assert result['baseline_values']['pitch_mean'] == pytest.approx(200.0)

    def test_single_baseline_value_falls_back_to_relative_change(self):
        """A single baseline value has no spread, so relative change is used and labeled."""
        result = self.fusion.compute_deviation({'pitch_mean': 200.0}, {'pitch_mean': 300.0})
        assert result['methods']['pitch_mean'] == 'relative_change'
        assert result['per_signal']['pitch_mean'] == pytest.approx(0.5)

    def test_missing_modality_handled(self):
        """A missing modality is skipped and the remaining weights are renormalised."""
        fusion = MultimodalFusion(modality_weights={'blinks_per_minute': 1.0, 'pitch_mean': 3.0,
                                                     'pause_ratio': 1.0})
        baseline = {'blinks_per_minute': 15.0, 'pitch_mean': 200.0, 'pause_ratio': 0.2}
        segment = {'blinks_per_minute': 30.0, 'pause_ratio': 0.2}  # audio pitch missing
        result = fusion.compute_deviation(baseline, segment)
        assert 'pitch_mean' not in result['per_signal']
        assert set(result['available_signals']) == {'blinks_per_minute', 'pause_ratio'}
        assert sum(result['weights'].values()) == pytest.approx(1.0)
        assert result['weights']['blinks_per_minute'] == pytest.approx(0.5)
        # |1.0| * 0.5 + |0.0| * 0.5
        assert result['deviation_index'] == pytest.approx(0.5)

    def test_no_signals_returns_empty_report(self):
        result = self.fusion.compute_deviation({}, {})
        assert result['available_signals'] == []
        assert result['deviation_index'] is None

    def test_no_lie_truth_label(self):
        """The output never contains a lie/truth label or a deception score."""
        baseline = {'blinks_per_minute': [12.0, 14.0, 16.0], 'pitch_mean': 200.0}
        segment = {'blinks_per_minute': 30.0, 'pitch_mean': 260.0}
        result = self.fusion.compute_deviation(baseline, segment)
        forbidden_keys = {'lie', 'truth', 'is_lying', 'verdict', 'deception', 'deception_score', 'score'}
        assert not forbidden_keys & set(result)
        text = json.dumps(result).lower()
        assert not re.search(r'\b(lie|lying|liar|truth|truthful)\b', text)
