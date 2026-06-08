"""
Face Detection Module
Detects faces in video frames using computer vision techniques.
"""

import cv2
import numpy as np


class FaceDetector:
    """Face detection using OpenCV and pre-trained models."""
    
    def __init__(self, model_path=None):
        """Initialize the face detector."""
        self.model_path = model_path
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def detect_faces(self, frame):
        """
        Detect faces in a frame.
        
        Args:
            frame: Input video frame
            
        Returns:
            List of detected faces with bounding boxes
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        return faces
    
    def extract_face_roi(self, frame, face_bbox):
        """Extract Region of Interest for detected face."""
        x, y, w, h = face_bbox
        roi = frame[y:y+h, x:x+w]
        return roi


if __name__ == "__main__":
    print("Face Detector Module Loaded")
