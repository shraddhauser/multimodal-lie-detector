"""
Main Application Module
Orchestrates the multimodal behavioral-signal analysis pipeline.

The pipeline extracts face/eye/audio signals from a video, compares them
against the speaker's own baseline (first N seconds), and produces a
deviation report.  The output is a signal-consistency report, NOT a
"truth/lie" label.
"""

import sys
import os
import cv2
import numpy as np

from face_analysis.face_detector import FaceDetector
from face_analysis.micro_expression import MicroExpressionDetector
from eye_tracking.eye_tracker import EyeTracker
from eye_tracking.pupil_analysis import PupilAnalyzer
from audio_analysis.acoustic_features import AcousticFeatureExtractor
from audio_analysis.emotion_analysis import EmotionAnalyzer
from audio_analysis.speech_to_text import SpeechToTextConverter
from fusion.multimodal_fusion import MultimodalFusion
from gemini.gemini_reasoning import GeminiReasoning


class LieDetectionPipeline:
    """
    Main pipeline for multimodal behavioral-signal analysis.

    Despite the class name (kept for backward compatibility), this pipeline
    produces a *deviation index*, not a lie/truth verdict.
    """

    DEFAULT_BASELINE_SECONDS = 20

    def __init__(self, baseline_seconds=None):
        """Initialize all components of the pipeline."""
        self.baseline_seconds = baseline_seconds or self.DEFAULT_BASELINE_SECONDS
        self.face_detector = FaceDetector()
        self.micro_expression_detector = MicroExpressionDetector()
        self.eye_tracker = EyeTracker()
        self.head_analyzer = PupilAnalyzer()
        self.acoustic_extractor = AcousticFeatureExtractor()
        self.emotion_analyzer = EmotionAnalyzer()
        self.speech_to_text = SpeechToTextConverter()
        self.multimodal_fusion = MultimodalFusion()
        self.gemini_reasoning = GeminiReasoning()

    # ---- Video processing ----

    def _extract_landmarks_from_video(self, video_path):
        """
        Read a video and return a list of per-frame landmark arrays
        (or None for frames with no face), plus the fps.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise FileNotFoundError(f"Cannot open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        all_landmarks = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            lm = self.face_detector.get_landmarks(frame)
            all_landmarks.append(lm)

        cap.release()
        return all_landmarks, fps

    def _split_baseline_segment(self, landmarks, fps):
        """Split landmarks into baseline and segment lists."""
        baseline_frames = int(self.baseline_seconds * fps)
        # Only keep frames where landmarks were detected
        valid = [(i, lm) for i, lm in enumerate(landmarks) if lm is not None]
        baseline = [lm for i, lm in valid if i < baseline_frames]
        segment = [lm for i, lm in valid if i >= baseline_frames]
        return baseline, segment

    def _visual_features(self, landmark_list, fps):
        """Extract visual features from a list of landmark arrays."""
        if not landmark_list:
            return {}
        blinks = self.eye_tracker.count_blinks(landmark_list, fps)
        gaze = self.eye_tracker.gaze_aversion_ratio(landmark_list)
        head = self.head_analyzer.head_movement_variance(landmark_list)
        return {
            'blinks_per_minute': blinks['blinks_per_minute'],
            'aversion_ratio': gaze['aversion_ratio'],
            'head_movement_variance': head['total_variance'],
        }

    # ---- Audio processing ----

    def _audio_features(self, audio_path):
        """Extract audio features from a file."""
        if not audio_path:
            return {}
        try:
            y, sr = self.acoustic_extractor.load_audio(audio_path)
        except Exception:
            return {}
        feats = self.acoustic_extractor.extract_features(y, sr)
        return {k: v for k, v in feats.items() if v is not None}

    # ---- Public API ----

    def process_video(self, video_path, audio_path=None):
        """
        Process a video (and optional separate audio) for behavioral signals.

        Args:
            video_path: Path to input video file.
            audio_path: Optional path to a separate audio file.

        Returns:
            dict with the deviation report and optional Gemini summary.
        """
        print(f"Processing video: {video_path}")

        # 1. Extract landmarks
        all_landmarks, fps = self._extract_landmarks_from_video(video_path)
        baseline_lm, segment_lm = self._split_baseline_segment(all_landmarks, fps)

        # 2. Visual features (baseline vs segment)
        baseline_visual = self._visual_features(baseline_lm, fps)
        segment_visual = self._visual_features(segment_lm, fps)

        # 3. Audio features (whole file — split not implemented yet)
        audio_feats = self._audio_features(audio_path)

        # 4. Merge features
        baseline_all = {**baseline_visual}
        segment_all = {**segment_visual}
        # Audio goes into segment only (baseline audio split is TODO)
        if audio_feats:
            segment_all.update(audio_feats)
            baseline_all.update(audio_feats)  # same baseline for now

        # 5. Fusion
        deviation = self.multimodal_fusion.compute_deviation(baseline_all, segment_all)

        # 6. Gemini summary (optional)
        report = self.gemini_reasoning.generate_report({}, deviation)

        return report

    def process_interview(self, video_path, audio_path=None):
        """
        Process complete interview (video + optional audio).

        Alias for process_video().
        """
        return self.process_video(video_path, audio_path)


def main():
    """Main entry point."""
    print("Multimodal Behavioral-Signal Analysis Pipeline")
    print("=" * 50)

    pipeline = LieDetectionPipeline()
    print("Pipeline initialized successfully")

    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        audio_path = sys.argv[2] if len(sys.argv) > 2 else None
        result = pipeline.process_video(video_path, audio_path)
        print("\nResult:")
        import json
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
