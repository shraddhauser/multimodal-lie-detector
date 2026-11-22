"""
Acoustic Features Extraction Module
Extracts pitch (F0), jitter, shimmer, speech rate and pause ratio
from audio signals using librosa.
"""

import numpy as np

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False


class AcousticFeatureExtractor:
    """Extract acoustic features from audio using librosa."""

    def __init__(self, target_sr=16000):
        """
        Args:
            target_sr: Target sample rate.  Audio at other rates is
                       resampled automatically by librosa.load().
        """
        self.target_sr = target_sr

    def load_audio(self, path):
        """
        Load an audio file and return (signal, sr).

        Stereo is mixed to mono. Sample rate is resampled to self.target_sr.
        """
        if not LIBROSA_AVAILABLE:
            raise ImportError("librosa is required for audio analysis")
        y, sr = librosa.load(path, sr=self.target_sr, mono=True)
        return y, sr

    def extract_features(self, y, sr=None):
        """
        Extract acoustic features from an audio waveform.

        Args:
            y: 1-D numpy array (mono audio).
            sr: Sample rate (defaults to self.target_sr).

        Returns:
            dict with pitch_mean, pitch_std, jitter, shimmer,
            speech_rate, pause_ratio.
        """
        if sr is None:
            sr = self.target_sr

        y = np.asarray(y, dtype=np.float64)

        # --- Pitch (F0) via pyin ---
        f0, voiced_flag, _ = librosa.pyin(
            y, fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'), sr=sr,
        )
        voiced_f0 = f0[~np.isnan(f0)] if f0 is not None else np.array([])

        pitch_mean = float(np.mean(voiced_f0)) if len(voiced_f0) > 0 else float('nan')
        pitch_std = float(np.std(voiced_f0)) if len(voiced_f0) > 0 else float('nan')

        # --- Jitter (cycle-to-cycle pitch variation) ---
        jitter = self._jitter(voiced_f0)

        # --- Shimmer (cycle-to-cycle amplitude variation, approximated) ---
        shimmer = self._shimmer(y, sr)

        # --- Speech rate (onsets per second) ---
        onsets = librosa.onset.onset_detect(y=y, sr=sr, units='time')
        duration_s = len(y) / sr
        speech_rate = len(onsets) / duration_s if duration_s > 0 else 0.0

        # --- Pause ratio ---
        pause_ratio = self._pause_ratio(y, sr)

        return {
            'pitch_mean': round(pitch_mean, 2) if not np.isnan(pitch_mean) else None,
            'pitch_std': round(pitch_std, 2) if not np.isnan(pitch_std) else None,
            'jitter': round(jitter, 6) if jitter is not None else None,
            'shimmer': round(shimmer, 6) if shimmer is not None else None,
            'speech_rate': round(speech_rate, 2),
            'pause_ratio': round(pause_ratio, 4),
        }

    # ---- helpers ----

    @staticmethod
    def _jitter(voiced_f0):
        """Relative jitter: mean absolute period-to-period difference / mean period."""
        if len(voiced_f0) < 2:
            return None
        periods = 1.0 / voiced_f0
        diffs = np.abs(np.diff(periods))
        mean_period = np.mean(periods)
        if mean_period == 0:
            return None
        return float(np.mean(diffs) / mean_period)

    @staticmethod
    def _shimmer(y, sr):
        """Approximate shimmer from RMS energy of short frames."""
        frame_length = int(0.025 * sr)  # 25 ms
        hop_length = int(0.010 * sr)    # 10 ms
        if frame_length < 1 or len(y) < frame_length:
            return None
        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
        rms = rms[rms > 0]
        if len(rms) < 2:
            return None
        diffs = np.abs(np.diff(rms))
        return float(np.mean(diffs) / np.mean(rms))

    @staticmethod
    def _pause_ratio(y, sr, threshold_db=-40, min_pause_s=0.15):
        """
        Fraction of audio duration that is silence (below threshold).
        """
        frame_length = int(0.025 * sr)
        hop_length = int(0.010 * sr)
        if frame_length < 1 or len(y) < frame_length:
            return 1.0
        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
        ref = np.max(rms) if np.max(rms) > 0 else 1e-9
        db = 20 * np.log10(rms / ref + 1e-12)
        silent_frames = np.sum(db < threshold_db)
        return float(silent_frames / max(len(rms), 1))


if __name__ == "__main__":
    print("Acoustic Feature Extractor Module Loaded")
    print(f"librosa available: {LIBROSA_AVAILABLE}")
