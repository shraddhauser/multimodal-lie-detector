"""
Shared pytest fixtures for the multimodal behavioral-signal analysis test suite.
All fixtures are synthetic and generated into pytest's tmp_path:
no real recordings, no internet, no GPU, no API keys.

`src/` and `web/` are put on the import path by `pythonpath` in pytest.ini.
"""

import wave

import cv2
import numpy as np
import pytest


def _write_wav(path, samples, sr=16000, channels=1):
    """Write a numpy array of float samples to a 16-bit WAV file."""
    samples = np.clip(samples, -1.0, 1.0)
    int_samples = (samples * 32767).astype(np.int16)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(int_samples.tobytes())


@pytest.fixture
def sine_wav_path(tmp_path):
    """Create a 3-second 220 Hz sine wave WAV at 16 kHz."""
    sr = 16000
    duration = 3.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    samples = 0.5 * np.sin(2 * np.pi * 220 * t)
    path = str(tmp_path / 'sine_220hz.wav')
    _write_wav(path, samples, sr)
    return path


@pytest.fixture
def silent_wav_path(tmp_path):
    """Create a 2-second silent WAV."""
    sr = 16000
    duration = 2.0
    samples = np.zeros(int(sr * duration))
    path = str(tmp_path / 'silence.wav')
    _write_wav(path, samples, sr)
    return path


@pytest.fixture
def stereo_wav_path(tmp_path):
    """Create a 1-second stereo 440 Hz sine wave WAV."""
    sr = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    left = 0.5 * np.sin(2 * np.pi * 440 * t)
    right = 0.3 * np.sin(2 * np.pi * 440 * t)
    stereo = np.column_stack([left, right]).flatten()
    path = str(tmp_path / 'stereo_440hz.wav')
    _write_wav(path, stereo, sr, channels=2)
    return path


@pytest.fixture
def blank_frame():
    """A 480×640 black (blank) BGR frame."""
    return np.zeros((480, 640, 3), dtype=np.uint8)


@pytest.fixture
def synthetic_landmarks_open_eyes():
    """
    Synthetic (478, 2) landmark array with open-eye geometry.
    Only the 6 EAR-relevant points per eye + iris + nose tip are
    geometrically meaningful; the rest are zeros.
    """
    lm = np.zeros((478, 2), dtype=np.float64)
    # Left eye (open): EAR ≈ 0.3
    lm[33] = [100, 100]   # outer corner
    lm[160] = [110, 95]   # top-1
    lm[158] = [120, 95]   # top-2
    lm[133] = [130, 100]  # inner corner
    lm[153] = [120, 105]  # bottom-2
    lm[144] = [110, 105]  # bottom-1
    # Right eye (open)
    lm[362] = [200, 100]
    lm[385] = [210, 95]
    lm[387] = [220, 95]
    lm[263] = [230, 100]
    lm[373] = [220, 105]
    lm[380] = [210, 105]
    # Iris centres
    lm[468] = [115, 100]  # left iris
    lm[473] = [215, 100]  # right iris
    # Nose tip
    lm[1] = [165, 200]
    return lm


@pytest.fixture
def synthetic_landmarks_closed_eyes(synthetic_landmarks_open_eyes):
    """Same as open-eye landmarks but with top/bottom points collapsed (EAR → ~0)."""
    lm = synthetic_landmarks_open_eyes.copy()
    # Close left eye
    lm[160] = [110, 100]
    lm[158] = [120, 100]
    lm[153] = [120, 100]
    lm[144] = [110, 100]
    # Close right eye
    lm[385] = [210, 100]
    lm[387] = [220, 100]
    lm[373] = [220, 100]
    lm[380] = [210, 100]
    return lm


@pytest.fixture
def sine_44k_wav_path(tmp_path):
    """A 1-second 220 Hz sine at 44.1 kHz (wrong rate: must be resampled to 16 kHz)."""
    sr = 44100
    t = np.linspace(0, 1.0, sr, endpoint=False)
    path = str(tmp_path / 'sine_44k.wav')
    _write_wav(path, 0.5 * np.sin(2 * np.pi * 220 * t), sr)
    return path


def _sine(freq, seconds, sr=16000):
    t = np.linspace(0, seconds, int(sr * seconds), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * freq * t)


@pytest.fixture
def steady_pitch_wav_path(tmp_path):
    """3 s at a constant 220 Hz: after the baseline, nothing changes."""
    path = str(tmp_path / 'steady.wav')
    _write_wav(path, _sine(220, 3.0))
    return path


@pytest.fixture
def pitch_shift_wav_path(tmp_path):
    """1 s at 220 Hz (baseline) followed by 2 s at 330 Hz (shifted)."""
    path = str(tmp_path / 'shift.wav')
    _write_wav(path, np.concatenate([_sine(220, 1.0), _sine(330, 2.0)]))
    return path


@pytest.fixture
def synthetic_face_video_path(tmp_path):
    """
    A 2-second, 15 fps, 320x240 synthetic video of a drawn cartoon face
    (no real person). Generated on the fly, so nothing is committed.
    """
    path = str(tmp_path / 'drawn_face.mp4')
    fps, w, h = 15, 320, 240
    writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
    assert writer.isOpened(), 'OpenCV could not open an mp4 writer'
    for i in range(2 * fps):
        frame = np.full((h, w, 3), 200, dtype=np.uint8)
        cx = 160 + int(5 * np.sin(i / 3))           # gentle head sway
        cv2.ellipse(frame, (cx, 120), (60, 80), 0, 0, 360, (150, 180, 230), -1)
        eye_h = 2 if i % 10 == 0 else 8              # periodic "blink"
        for ex in (cx - 22, cx + 22):
            cv2.ellipse(frame, (ex, 100), (12, eye_h), 0, 0, 360, (255, 255, 255), -1)
            cv2.circle(frame, (ex, 100), 4, (40, 40, 40), -1)
        cv2.ellipse(frame, (cx, 155), (25, 8), 0, 0, 180, (60, 60, 160), 3)
        writer.write(frame)
    writer.release()
    return path
