"""
Face Detection Module
Detects faces in video frames using MediaPipe Face Mesh with Haar cascade fallback.
"""

import cv2
import numpy as np

try:
    import mediapipe as mp
    # Newer MediaPipe releases removed the legacy `solutions` API; treat that
    # as "unavailable" so we fall back to the Haar cascade instead of crashing.
    MEDIAPIPE_AVAILABLE = hasattr(mp, 'solutions') and hasattr(mp.solutions, 'face_mesh')
except ImportError:
    MEDIAPIPE_AVAILABLE = False


class FaceDetector:
    """Face detection using MediaPipe Face Mesh (primary) or OpenCV Haar cascade (fallback)."""

    def __init__(self, model_path=None, use_mediapipe=True):
        """
        Initialize the face detector.

        Args:
            model_path: Optional path to a custom model (unused with MediaPipe).
            use_mediapipe: If True, prefer MediaPipe Face Mesh when available.
        """
        self.model_path = model_path
        self.use_mediapipe = use_mediapipe and MEDIAPIPE_AVAILABLE

        # Haar cascade fallback
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        # MediaPipe Face Mesh
        self._mp_face_mesh = None
        if self.use_mediapipe:
            self._mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )

    # ----- Eye Aspect Ratio (EAR) for blink detection -----

    @staticmethod
    def eye_aspect_ratio(eye_landmarks):
        """
        Compute the Eye Aspect Ratio (EAR).

        Args:
            eye_landmarks: Array of shape (6, 2) with the six eye-contour points
                           ordered as [P1, P2, P3, P4, P5, P6] where
                           P1-P4 are the horizontal endpoints and
                           P2-P3, P5-P6 are vertical pairs.

        Returns:
            Float EAR value.  Lower values indicate a more closed eye.
        """
        eye = np.asarray(eye_landmarks, dtype=np.float64)
        # vertical distances
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])
        # horizontal distance
        C = np.linalg.norm(eye[0] - eye[3])
        if C == 0:
            return 0.0
        return (A + B) / (2.0 * C)

    # ----- MediaPipe helpers -----

    def _get_mesh_landmarks(self, frame):
        """
        Run MediaPipe Face Mesh on *frame* and return the first face's
        normalised landmarks as a list of (x, y, z) tuples, or None.
        """
        if not self.use_mediapipe or self._mp_face_mesh is None:
            return None
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._mp_face_mesh.process(rgb)
        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0].landmark
        return None

    def get_landmarks(self, frame):
        """
        Return 478 (x, y) pixel-coordinate landmarks for the first detected
        face, or None.
        """
        raw = self._get_mesh_landmarks(frame)
        if raw is None:
            return None
        h, w = frame.shape[:2]
        return np.array([(lm.x * w, lm.y * h) for lm in raw], dtype=np.float64)

    # MediaPipe Face Mesh landmark indices for the left and right eye contour
    # (six-point EAR model).
    LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]

    # Iris centre landmarks (refine_landmarks=True required)
    LEFT_IRIS_IDX = 468
    RIGHT_IRIS_IDX = 473

    def detect_faces(self, frame):
        """
        Detect faces in a frame using the Haar cascade.

        Args:
            frame: Input BGR video frame.

        Returns:
            Numpy array of bounding boxes (x, y, w, h). Empty array if none.
        """
        if frame is None or frame.size == 0:
            return np.array([])
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces) == 0:
            return np.array([])
        return faces

    def extract_face_roi(self, frame, face_bbox):
        """Extract Region of Interest for detected face."""
        x, y, w, h = face_bbox
        roi = frame[y:y + h, x:x + w]
        return roi

    def close(self):
        """Release MediaPipe resources."""
        if self._mp_face_mesh is not None:
            self._mp_face_mesh.close()
            self._mp_face_mesh = None


if __name__ == "__main__":
    print("Face Detector Module Loaded")
    print(f"MediaPipe available: {MEDIAPIPE_AVAILABLE}")
