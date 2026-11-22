"""
Main Application Module
Orchestrates the multimodal behavioral-signal analysis pipeline.

The pipeline extracts face/eye/audio signals from a video, compares them
against the speaker's own baseline (first N seconds), and produces a
deviation report.  The output is a signal-consistency report, NOT a
"truth/lie" label.
"""

import json
import sys

import cv2
import numpy as np

from audio_analysis.acoustic_features import AcousticFeatureExtractor
from audio_analysis.emotion_analysis import EmotionAnalyzer
from audio_analysis.speech_to_text import SpeechToTextConverter
from eye_tracking.eye_tracker import EyeTracker
from eye_tracking.pupil_analysis import PupilAnalyzer
from face_analysis.face_detector import FaceDetector
from face_analysis.micro_expression import MicroExpressionDetector
from fusion.multimodal_fusion import MultimodalFusion
from gemini.gemini_reasoning import GeminiReasoning


class LieDetectionPipeline:
    """
    Main pipeline for multimodal behavioral-signal analysis.

    Despite the class name (kept for backward compatibility), this pipeline
    produces a *deviation index*, not a lie/truth verdict.
    """

    DEFAULT_BASELINE_SECONDS = 20
    DEFAULT_WINDOW_SECONDS = 5

    def __init__(self, baseline_seconds=None, window_seconds=None):
        """Initialize all components of the pipeline."""
        self.baseline_seconds = baseline_seconds or self.DEFAULT_BASELINE_SECONDS
        self.window_seconds = window_seconds or self.DEFAULT_WINDOW_SECONDS
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

    @staticmethod
    def _windows(n_items, items_per_window):
        """Yield (start, stop) index pairs of consecutive windows."""
        step = max(int(items_per_window), 1)
        for start in range(0, n_items, step):
            yield start, min(start + step, n_items)

    @staticmethod
    def _numeric(value):
        return isinstance(value, (int, float)) and not np.isnan(value)

    @classmethod
    def _mean_of_windows(cls, window_features):
        """Average each signal over a list of per-window feature dicts."""
        out = {}
        keys = {k for wf in window_features for k in wf}
        for k in keys:
            vals = [wf[k] for wf in window_features if cls._numeric(wf.get(k))]
            if vals:
                out[k] = float(np.mean(vals))
        return out

    @classmethod
    def _stack_windows(cls, window_features):
        """Turn a list of per-window dicts into signal -> list of values."""
        out = {}
        for wf in window_features:
            for k, v in wf.items():
                if cls._numeric(v):
                    out.setdefault(k, []).append(float(v))
        return out

    def _visual_windows(self, landmarks, fps, start_frame, stop_frame):
        """Per-window visual features for frames in [start_frame, stop_frame)."""
        frames_per_window = self.window_seconds * fps
        result = []
        for ws, we in self._windows(stop_frame - start_frame, frames_per_window):
            window = [lm for lm in landmarks[start_frame + ws:start_frame + we] if lm is not None]
            # Require at least half the window to contain a detected face
            if len(window) < max(2, 0.5 * (we - ws)):
                continue
            result.append(self._visual_features(window, fps))
        return result

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

    def _load_audio(self, audio_path, video_path):
        """Load a separate audio file, or fall back to the video's audio track."""
        for path in (audio_path, video_path):
            if not path:
                continue
            try:
                y, sr = self.acoustic_extractor.load_audio(path)
            except Exception:
                continue
            if len(y) > 0:
                return y, sr, path
        return None, None, None

    def _audio_windows(self, y, sr, start_s, stop_s):
        """Per-window acoustic features for the span [start_s, stop_s)."""
        start, stop = int(start_s * sr), min(int(stop_s * sr), len(y))
        if stop <= start:
            return []
        result = []
        win = int(self.window_seconds * sr)
        for ws, we in self._windows(stop - start, win):
            chunk = y[start + ws:start + we]
            if len(chunk) < 0.5 * win:
                continue
            feats = self.acoustic_extractor.extract_features(chunk, sr)
            result.append({k: v for k, v in feats.items() if v is not None})
        return result

    # ---- Public API ----

    def process_video(self, video_path, audio_path=None):
        """
        Process a video (and optional separate audio) for behavioral signals.

        The first `baseline_seconds` of the recording are the speaker's
        baseline; the remainder is the segment compared against it. Both are
        split into `window_seconds` windows so the baseline has a spread
        (standard deviation) for z-scores.

        Args:
            video_path: Path to input video file.
            audio_path: Optional path to a separate audio file. If omitted,
                the video's own audio track is used when it can be decoded.

        Returns:
            dict with the deviation report and optional Gemini summary.
        """
        # 1. Video: landmarks per frame
        all_landmarks, fps = self._extract_landmarks_from_video(video_path)
        n_frames = len(all_landmarks)
        baseline_end = min(int(self.baseline_seconds * fps), n_frames)

        baseline_visual = self._visual_windows(all_landmarks, fps, 0, baseline_end)
        segment_visual = self._visual_windows(all_landmarks, fps, baseline_end, n_frames)

        # 2. Audio: separate file or the video's own track
        y, sr, audio_source = self._load_audio(audio_path, video_path)
        baseline_audio, segment_audio = [], []
        if y is not None:
            duration = len(y) / sr
            baseline_audio = self._audio_windows(y, sr, 0, self.baseline_seconds)
            segment_audio = self._audio_windows(y, sr, self.baseline_seconds, duration)

        # 3. Baseline = per-window values (gives a spread); segment = window mean
        baseline_all = {**self._stack_windows(baseline_visual), **self._stack_windows(baseline_audio)}
        segment_all = {**self._mean_of_windows(segment_visual), **self._mean_of_windows(segment_audio)}

        # 4. Fusion
        deviation = self.multimodal_fusion.compute_deviation(baseline_all, segment_all)

        # 5. Optional transcript (only when openai-whisper is installed)
        transcript = None
        if audio_source and self.speech_to_text.available:
            transcript = self.speech_to_text.transcribe_audio(audio_source).get('text')

        if audio_source is None:
            source_label = None
        elif audio_source == audio_path:
            source_label = 'separate_file'
        else:
            source_label = 'video_track'

        meta = {
            'video_duration_s': round(n_frames / fps, 2) if fps else None,
            'fps': round(fps, 2),
            'frames_with_face': sum(lm is not None for lm in all_landmarks),
            'total_frames': n_frames,
            'baseline_seconds': self.baseline_seconds,
            'window_seconds': self.window_seconds,
            'baseline_windows': {'face': len(baseline_visual), 'audio': len(baseline_audio)},
            'segment_windows': {'face': len(segment_visual), 'audio': len(segment_audio)},
            'audio_source': source_label,
            'face_landmarks_backend': ('mediapipe_face_mesh' if self.face_detector.use_mediapipe
                                       else 'unavailable (install mediapipe<0.10.30)'),
            'transcript': transcript,
        }

        # 6. Gemini summary (optional)
        return self.gemini_reasoning.generate_report(meta, deviation)

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
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
