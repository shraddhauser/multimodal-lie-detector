"""
Micro Expression Detection Module (simulated)

Analyses facial landmarks over time to detect rapid changes in
facial-action-unit–like signals. This is a *rule-based heuristic*,
not a trained classifier — see docs/DECISIONS.md ADR-003.

Label: simulated / rule-based.
"""

import numpy as np


class MicroExpressionDetector:
    """
    Detect rapid landmark-displacement events that *approximate*
    facial action units.

    This detector is **simulated / rule-based**: it measures frame-to-frame
    landmark displacement and flags frames where the displacement exceeds a
    threshold.  It does *not* use a trained model and should not be treated
    as a validated micro-expression classifier.
    """

    def __init__(self, displacement_threshold=2.0, min_frames=1):
        """
        Args:
            displacement_threshold: Mean landmark displacement (in pixels)
                above which a frame is flagged as a rapid-change event.
            min_frames: Minimum consecutive flagged frames to count as one
                event.
        """
        self.displacement_threshold = displacement_threshold
        self.min_frames = min_frames
        self._prev_landmarks = None

    def reset(self):
        """Reset internal state between clips."""
        self._prev_landmarks = None

    def update(self, landmarks):
        """
        Feed one frame's landmarks and return the displacement from the
        previous frame.

        Args:
            landmarks: (N, 2) array of landmark pixel coordinates.

        Returns:
            Float mean displacement, or 0.0 on the first frame.
        """
        landmarks = np.asarray(landmarks, dtype=np.float64)
        if self._prev_landmarks is None:
            self._prev_landmarks = landmarks
            return 0.0
        displacement = np.mean(np.linalg.norm(landmarks - self._prev_landmarks, axis=1))
        self._prev_landmarks = landmarks
        return float(displacement)

    def detect_events(self, landmark_sequence):
        """
        Scan a full sequence and return indices of rapid-change events.

        Args:
            landmark_sequence: list of (N, 2) arrays, one per frame.

        Returns:
            List of frame indices where displacement exceeded the threshold.
        """
        self.reset()
        events = []
        for i, lm in enumerate(landmark_sequence):
            d = self.update(lm)
            if d > self.displacement_threshold:
                events.append(i)
        self.reset()
        return events


if __name__ == "__main__":
    print("Micro Expression Detector Module Loaded (simulated / rule-based)")
