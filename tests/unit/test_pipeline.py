"""
Tests for the end-to-end pipeline (src/main.py) on synthetic media.
A short baseline (1 s) and window (0.5 s) keep the tests fast.
"""

import json
import re

import pytest

from main import LieDetectionPipeline


@pytest.fixture(scope='module')
def pipeline():
    return LieDetectionPipeline(baseline_seconds=1, window_seconds=0.5)


def test_report_structure_on_synthetic_video(pipeline, synthetic_face_video_path, steady_pitch_wav_path):
    """A drawn-face video plus audio runs end to end without crashing."""
    report = pipeline.process_video(synthetic_face_video_path, steady_pitch_wav_path)
    assert {'title', 'analysis', 'deviation_report', 'ai_summary', 'caveat'} <= set(report)
    meta = report['analysis']
    assert meta['total_frames'] == 30
    assert meta['video_duration_s'] == pytest.approx(2.0, abs=0.1)
    assert meta['audio_source'] == 'separate_file'
    json.dumps(report)  # must be JSON-serialisable for the API


def test_steady_audio_has_near_zero_deviation(pipeline, synthetic_face_video_path, steady_pitch_wav_path):
    """If nothing changes after the baseline, the pitch deviation is about 0."""
    dev = pipeline.process_video(synthetic_face_video_path, steady_pitch_wav_path)['deviation_report']
    assert 'pitch_mean' in dev['per_signal']
    assert abs(dev['per_signal']['pitch_mean']) < 0.05


def test_pitch_shift_after_baseline_is_detected(pipeline, synthetic_face_video_path, pitch_shift_wav_path):
    """220 Hz baseline then 330 Hz: the pitch deviation must be clearly positive."""
    dev = pipeline.process_video(synthetic_face_video_path, pitch_shift_wav_path)['deviation_report']
    assert dev['segment_values']['pitch_mean'] == pytest.approx(330, abs=10)
    assert dev['baseline_values']['pitch_mean'] == pytest.approx(220, abs=10)
    assert dev['per_signal']['pitch_mean'] > 0.3


def test_report_has_no_lie_truth_label(pipeline, synthetic_face_video_path, pitch_shift_wav_path):
    report = pipeline.process_video(synthetic_face_video_path, pitch_shift_wav_path)
    text = json.dumps(report['deviation_report']).lower()
    assert not re.search(r'\b(lie|lying|liar|truth|truthful)\b', text)


def test_unreadable_video_raises(pipeline, tmp_path):
    bad = tmp_path / 'not_a_video.mp4'
    bad.write_bytes(b'\x00' * 100)
    with pytest.raises(FileNotFoundError):
        pipeline.process_video(str(bad))
