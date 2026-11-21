"""
Pupil / Head-Movement Analysis Module
Analyses head-movement variance from face-mesh nose-tip landmark.
"""

import numpy as np

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from face_analysis.face_detector import FaceDetector


class PupilAnalyzer:
    """
    Analyse head movement using the nose-tip landmark (index 1 in
    MediaPipe Face Mesh).  Pupil-dilation estimation from a webcam is
    unreliable (lighting confound), so this module focuses on
    head-movement variance as a proxy for restlessness.
    """

    NOSE_TIP_IDX = 1

    def __init__(self):
        pass

    def head_movement_variance(self, landmarks_sequence):
        """
        Compute variance of the nose-tip position across frames.

        Args:
            landmarks_sequence: list of (478, 2) arrays.

        Returns:
            dict with 'x_variance', 'y_variance', 'total_variance'.
        """
        if not landmarks_sequence:
            return {'x_variance': 0.0, 'y_variance': 0.0, 'total_variance': 0.0}

        positions = np.array([lm[self.NOSE_TIP_IDX] for lm in landmarks_sequence])
        x_var = float(np.var(positions[:, 0]))
        y_var = float(np.var(positions[:, 1]))
        return {
            'x_variance': round(x_var, 4),
            'y_variance': round(y_var, 4),
            'total_variance': round(x_var + y_var, 4),
        }


if __name__ == "__main__":
    print("Pupil / Head-Movement Analyzer Module Loaded")
