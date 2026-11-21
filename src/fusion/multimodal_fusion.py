"""
Multimodal Fusion Module
Combines per-signal features using per-speaker baseline z-score normalisation.

The output is a **deviation index** — how far the current segment's signals
deviate from the speaker's own baseline — not a "deception probability".
"""

import numpy as np


class MultimodalFusion:
    """
    Fuse face, eye and audio features using baseline-normalised z-scores.

    Workflow:
        1. Extract features from a "baseline" segment (e.g. the first 20 s).
        2. Extract features from subsequent segments.
        3. Call compute_deviation() to get per-signal z-scores and an
           aggregate deviation index.
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

    def __init__(self, modality_weights=None):
        """
        Args:
            modality_weights: Optional dict mapping signal names to weights.
                If None, all signals are weighted equally.
        """
        self.modality_weights = modality_weights  # None → equal weights

    def compute_deviation(self, baseline_features, segment_features):
        """
        Compute per-signal z-score deviations and an aggregate index.

        Args:
            baseline_features: dict of signal_name → float (from baseline).
            segment_features:  dict of signal_name → float (from segment).

        Returns:
            dict with:
                'per_signal': {signal: z_score, …}
                'deviation_index': weighted mean of absolute z-scores
                'available_signals': list of signals that had data
                'explanation': human-readable summary
        """
        per_signal = {}
        available = []

        for key in self.SIGNAL_KEYS:
            bl = baseline_features.get(key)
            sg = segment_features.get(key)
            if bl is None or sg is None:
                continue
            if isinstance(bl, (int, float)) and isinstance(sg, (int, float)):
                if np.isnan(bl) or np.isnan(sg):
                    continue
                # Simple z-score: deviation = (segment − baseline) / max(|baseline|, ε)
                denom = max(abs(bl), 1e-6)
                z = (sg - bl) / denom
                per_signal[key] = round(float(z), 4)
                available.append(key)

        # Aggregate: weighted mean of |z|
        if not available:
            return {
                'per_signal': {},
                'deviation_index': 0.0,
                'available_signals': [],
                'explanation': 'No signals available for comparison.',
            }

        weights = self._get_weights(available)
        abs_z = np.array([abs(per_signal[k]) for k in available])
        w = np.array([weights[k] for k in available])
        deviation_index = float(np.average(abs_z, weights=w))

        explanation = self._explain(per_signal, deviation_index)

        return {
            'per_signal': per_signal,
            'deviation_index': round(deviation_index, 4),
            'available_signals': available,
            'explanation': explanation,
        }

    def _get_weights(self, available_keys):
        """Return normalised weight dict for the available signals."""
        if self.modality_weights:
            raw = {k: self.modality_weights.get(k, 1.0) for k in available_keys}
        else:
            raw = {k: 1.0 for k in available_keys}
        total = sum(raw.values()) or 1.0
        return {k: v / total for k, v in raw.items()}

    @staticmethod
    def _explain(per_signal, deviation_index):
        """Generate a plain-English explanation of the deviation."""
        lines = []
        for key, z in per_signal.items():
            direction = 'higher' if z > 0 else 'lower'
            mag = abs(z)
            if mag < 0.5:
                lines.append(f"  - {key}: within normal range (z={z:+.2f})")
            else:
                lines.append(f"  - {key}: {mag:.1f}× {direction} than baseline (z={z:+.2f})")
        summary = (
            f"Aggregate deviation index: {deviation_index:.2f}. "
            "This measures how far the speaker's current signals deviate "
            "from their own baseline, NOT a deception probability.\n"
        )
        return summary + '\n'.join(lines)


if __name__ == "__main__":
    print("Multimodal Fusion Module Loaded")
