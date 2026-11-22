"""
Multimodal Fusion Module
Combines per-signal features using per-speaker baseline z-score normalisation.

The output is a **deviation index**: how far the current segment's signals
deviate from the speaker's own baseline. It is NOT a "deception probability".
"""

import numpy as np


def _is_number(value):
    return isinstance(value, (int, float, np.floating, np.integer)) and not np.isnan(value)


class MultimodalFusion:
    """
    Fuse face, eye and audio features using baseline-normalised z-scores.

    Workflow:
        1. Split the speaker's baseline period (e.g. the first 20 s) into
           short windows and extract features from each window.
        2. Extract features from the rest of the recording (the segment).
        3. Call compute_deviation() to get per-signal deviations and an
           aggregate deviation index.

    Per-signal deviation:
        * If the baseline provides >= 2 window values with non-zero spread,
          the deviation is a true z-score: (segment - mean) / std.
        * Otherwise (a single baseline value, or zero spread) it falls back
          to the relative change: (segment - baseline) / |baseline|.
          The method used for each signal is reported in 'methods'.
    """

    # Signals that the fusion engine understands.
    SIGNAL_KEYS = [
        'blinks_per_minute',
        'aversion_ratio',
        'head_movement_variance',
        'pitch_mean',
        'pitch_std',
        'speech_rate',
        'pause_ratio',
    ]

    MODALITY_OF = {
        'blinks_per_minute': 'face',
        'aversion_ratio': 'face',
        'head_movement_variance': 'face',
        'pitch_mean': 'audio',
        'pitch_std': 'audio',
        'speech_rate': 'audio',
        'pause_ratio': 'audio',
    }

    def __init__(self, modality_weights=None):
        """
        Args:
            modality_weights: Optional dict mapping signal names to weights.
                If None, all signals are weighted equally. Weights are
                renormalised over the signals that are actually available.
        """
        self.modality_weights = modality_weights

    @staticmethod
    def _baseline_stats(value):
        """Return (mean, std, n) for a scalar or a list of window values."""
        if isinstance(value, (list, tuple, np.ndarray)):
            vals = np.array([v for v in value if _is_number(v)], dtype=np.float64)
            if len(vals) == 0:
                return None
            std = float(np.std(vals, ddof=1)) if len(vals) >= 2 else 0.0
            return float(np.mean(vals)), std, len(vals)
        if _is_number(value):
            return float(value), 0.0, 1
        return None

    def compute_deviation(self, baseline_features, segment_features):
        """
        Compute per-signal deviations and an aggregate index.

        Args:
            baseline_features: dict of signal_name -> float, or
                signal_name -> list of per-window floats.
            segment_features: dict of signal_name -> float.

        Returns:
            dict with:
                'per_signal': {signal: deviation, ...}
                'methods': {signal: 'z_score' | 'relative_change', ...}
                'baseline_values': {signal: baseline mean, ...}
                'segment_values': {signal: segment value, ...}
                'deviation_index': weighted mean of absolute deviations
                'weights': normalised weight per available signal
                'available_signals': list of signals that had data
                'explanation': human-readable summary
        """
        per_signal, methods, baseline_values, segment_values = {}, {}, {}, {}

        for key in self.SIGNAL_KEYS:
            stats = self._baseline_stats(baseline_features.get(key))
            sg = segment_features.get(key)
            if stats is None or not _is_number(sg):
                continue
            mean, std, _ = stats
            if std > 1e-9:
                dev = (sg - mean) / std
                methods[key] = 'z_score'
            else:
                dev = (sg - mean) / max(abs(mean), 1e-6)
                methods[key] = 'relative_change'
            per_signal[key] = round(float(dev), 4)
            baseline_values[key] = round(mean, 4)
            segment_values[key] = round(float(sg), 4)

        available = list(per_signal)
        if not available:
            return {
                'per_signal': {},
                'methods': {},
                'baseline_values': {},
                'segment_values': {},
                'deviation_index': None,
                'weights': {},
                'available_signals': [],
                'explanation': 'No signals available for comparison '
                               '(no face detected and/or no usable audio after the baseline period).',
            }

        weights = self._get_weights(available)
        abs_dev = np.array([abs(per_signal[k]) for k in available])
        w = np.array([weights[k] for k in available])
        deviation_index = float(np.average(abs_dev, weights=w))

        return {
            'per_signal': per_signal,
            'methods': methods,
            'baseline_values': baseline_values,
            'segment_values': segment_values,
            'deviation_index': round(deviation_index, 4),
            'weights': {k: round(v, 4) for k, v in weights.items()},
            'available_signals': available,
            'explanation': self._explain(per_signal, methods, deviation_index),
        }

    def _get_weights(self, available_keys):
        """Return a normalised weight dict for the available signals."""
        if self.modality_weights:
            raw = {k: float(self.modality_weights.get(k, 1.0)) for k in available_keys}
        else:
            raw = {k: 1.0 for k in available_keys}
        total = sum(raw.values()) or 1.0
        return {k: v / total for k, v in raw.items()}

    @staticmethod
    def _explain(per_signal, methods, deviation_index):
        """Generate a plain-English explanation of the deviation."""
        lines = []
        for key, d in per_signal.items():
            direction = 'above' if d > 0 else 'below'
            if methods[key] == 'z_score':
                if abs(d) < 1.0:
                    lines.append(f"  - {key}: within the baseline's normal spread (z={d:+.2f})")
                else:
                    lines.append(f"  - {key}: {abs(d):.1f} standard deviations {direction} baseline (z={d:+.2f})")
            else:
                lines.append(f"  - {key}: {abs(d) * 100:.0f}% {direction} baseline (relative change)")
        summary = (
            f"Aggregate deviation index: {deviation_index:.2f}. "
            "This is the weighted mean of absolute per-signal deviations from the "
            "speaker's own baseline. It is NOT a deception probability.\n"
        )
        return summary + '\n'.join(lines)


if __name__ == "__main__":
    print("Multimodal Fusion Module Loaded")
