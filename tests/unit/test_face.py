"""
Unit tests for face analysis module.
Uses synthetic landmarks and blank frames — no real images needed.
"""




from face_analysis.face_detector import FaceDetector
from face_analysis.micro_expression import MicroExpressionDetector


class TestFaceDetector:
    """Tests for FaceDetector."""

    def setup_method(self):
        # Use Haar cascade only (no MediaPipe) for deterministic tests
        self.detector = FaceDetector(use_mediapipe=False)

    def test_initialization(self):
        assert self.detector is not None
        assert self.detector.face_cascade is not None

    def test_blank_frame_no_faces(self, blank_frame):
        """A blank frame should detect 0 faces and not crash."""
        faces = self.detector.detect_faces(blank_frame)
        assert len(faces) == 0

    def test_none_frame(self):
        """None frame should return empty array."""
        faces = self.detector.detect_faces(None)
        assert len(faces) == 0

    def test_ear_open_vs_closed(
        self, synthetic_landmarks_open_eyes, synthetic_landmarks_closed_eyes
    ):
        """EAR for open eyes should be higher than for closed eyes."""
        open_ear = FaceDetector.eye_aspect_ratio(
            synthetic_landmarks_open_eyes[FaceDetector.LEFT_EYE_IDX]
        )
        closed_ear = FaceDetector.eye_aspect_ratio(
            synthetic_landmarks_closed_eyes[FaceDetector.LEFT_EYE_IDX]
        )
        assert open_ear > closed_ear, (
            f"Open EAR ({open_ear}) should be > closed EAR ({closed_ear})"
        )
        assert closed_ear < 0.1, f"Closed EAR should be near 0, got {closed_ear}"


class TestMicroExpressionDetector:
    """Tests for MicroExpressionDetector (simulated / rule-based)."""

    def setup_method(self):
        self.detector = MicroExpressionDetector()

    def test_initialization(self):
        assert self.detector is not None

    def test_stable_landmarks_no_events(self, synthetic_landmarks_open_eyes):
        """Identical landmarks across frames should produce no rapid-change events."""
        seq = [synthetic_landmarks_open_eyes.copy() for _ in range(10)]
        events = self.detector.detect_events(seq)
        assert len(events) == 0

    def test_large_displacement_detected(self, synthetic_landmarks_open_eyes):
        """A large landmark shift should be detected as an event."""
        seq = [synthetic_landmarks_open_eyes.copy() for _ in range(5)]
        # Create a sudden shift in frame 3
        shifted = synthetic_landmarks_open_eyes.copy()
        shifted += 50.0  # large displacement
        seq[3] = shifted
        events = self.detector.detect_events(seq)
        assert 3 in events


class TestBlinkCounter:
    """Test blink counting from synthetic landmark sequences."""

    def test_three_blinks(
        self, synthetic_landmarks_open_eyes, synthetic_landmarks_closed_eyes
    ):
        """Three synthetic dips should count as 3 blinks."""
        from eye_tracking.eye_tracker import EyeTracker
        tracker = EyeTracker(ear_threshold=0.15, min_blink_frames=1)

        # Build a sequence: open open CLOSED open open CLOSED open open CLOSED open
        o = synthetic_landmarks_open_eyes
        c = synthetic_landmarks_closed_eyes
        seq = [o, o, c, o, o, c, o, o, c, o]
        result = tracker.count_blinks(seq, fps=30.0)
        assert result['blink_count'] == 3, (
            f"Expected 3 blinks, got {result['blink_count']}"
        )
