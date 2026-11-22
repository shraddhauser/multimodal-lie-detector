"""
Eye Tracking Module
Tracks blink rate and gaze-aversion ratio from MediaPipe Face Mesh landmarks.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from face_analysis.face_detector import FaceDetector


class EyeTracker:
    """
    Track blink rate and gaze-aversion ratio using MediaPipe landmarks.

    Blink detection uses the Eye Aspect Ratio (EAR): when the EAR drops
    below *ear_threshold* for at least *min_blink_frames* consecutive frames,
    one blink is counted.

    Gaze aversion is estimated from the iris-centre position relative to
    the eye corners: when the horizontal ratio falls outside
    [0.5 − aversion_margin, 0.5 + aversion_margin], the frame is counted
    as "averted".
    """

    def __init__(self, ear_threshold=0.21, min_blink_frames=2, aversion_margin=0.15):
        self.ear_threshold = ear_threshold
        self.min_blink_frames = min_blink_frames
        self.aversion_margin = aversion_margin

    # ---- Blink counting ----

    @staticmethod
    def _ear(landmarks, indices):
        """Compute EAR for one eye from full-face landmarks."""
        pts = landmarks[indices]
        return FaceDetector.eye_aspect_ratio(pts)

    def count_blinks(self, landmarks_sequence, fps=30.0):
        """
        Count blinks in a sequence of landmark arrays.

        Args:
            landmarks_sequence: list of (478, 2) arrays.
            fps: Frames per second (used to compute blinks/min).

        Returns:
            dict with 'blink_count', 'blinks_per_minute', 'ear_values'.
        """
        ear_values = []
        blink_count = 0
        below_count = 0

        for lm in landmarks_sequence:
            left_ear = self._ear(lm, FaceDetector.LEFT_EYE_IDX)
            right_ear = self._ear(lm, FaceDetector.RIGHT_EYE_IDX)
            avg_ear = (left_ear + right_ear) / 2.0
            ear_values.append(avg_ear)

            if avg_ear < self.ear_threshold:
                below_count += 1
            else:
                if below_count >= self.min_blink_frames:
                    blink_count += 1
                below_count = 0

        # Catch blink at end of sequence
        if below_count >= self.min_blink_frames:
            blink_count += 1

        duration_min = len(landmarks_sequence) / max(fps, 1e-9) / 60.0
        bpm = blink_count / duration_min if duration_min > 0 else 0.0

        return {
            'blink_count': blink_count,
            'blinks_per_minute': round(bpm, 2),
            'ear_values': ear_values,
        }

    # ---- Gaze aversion ----

    def gaze_aversion_ratio(self, landmarks_sequence):
        """
        Compute the fraction of frames where gaze is averted.

        Uses the horizontal position of the iris centre relative to the
        inner and outer eye corners.

        Returns:
            dict with 'aversion_ratio' (0–1) and 'gaze_ratios' per frame.
        """
        gaze_ratios = []
        averted_count = 0

        for lm in landmarks_sequence:
            ratios = []
            for iris_idx, corner_inner, corner_outer in [
                (FaceDetector.LEFT_IRIS_IDX, 133, 33),
                (FaceDetector.RIGHT_IRIS_IDX, 362, 263),
            ]:
                iris = lm[iris_idx]
                inner = lm[corner_inner]
                outer = lm[corner_outer]
                width = np.linalg.norm(inner - outer)
                if width < 1e-6:
                    ratios.append(0.5)
                    continue
                ratio = np.linalg.norm(iris - outer) / width
                ratios.append(ratio)

            avg_ratio = float(np.mean(ratios))
            gaze_ratios.append(avg_ratio)

            if abs(avg_ratio - 0.5) > self.aversion_margin:
                averted_count += 1

        aversion = averted_count / max(len(landmarks_sequence), 1)
        return {
            'aversion_ratio': round(aversion, 4),
            'gaze_ratios': gaze_ratios,
        }


if __name__ == "__main__":
    print("Eye Tracker Module Loaded")
