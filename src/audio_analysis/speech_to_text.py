"""
Speech to Text Module (optional — requires openai-whisper)

Uses Whisper tiny/base for offline transcription.  When the library
is not installed, transcribe_audio() returns an empty string gracefully.
"""

try:
    import whisper as openai_whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class SpeechToTextConverter:
    """Convert speech audio to text using OpenAI Whisper."""

    def __init__(self, model_name='base'):
        """
        Args:
            model_name: Whisper model size ('tiny', 'base', 'small', …).
        """
        self.model_name = model_name
        self.confidence_threshold = 0.5
        self._model = None

    def _load_model(self):
        if self._model is None and WHISPER_AVAILABLE:
            self._model = openai_whisper.load_model(self.model_name)

    def transcribe_audio(self, audio_file):
        """
        Transcribe an audio file to text.

        Args:
            audio_file: Path to audio file.

        Returns:
            dict with 'text' and 'confidence'.
        """
        if not WHISPER_AVAILABLE:
            return {'text': '', 'confidence': 0.0}
        self._load_model()
        result = self._model.transcribe(audio_file)
        return {
            'text': result.get('text', ''),
            'confidence': 1.0,  # Whisper does not expose per-segment confidence
        }

    def transcribe_with_timestamps(self, audio_file):
        """Transcribe audio with word-level timestamps."""
        if not WHISPER_AVAILABLE:
            return []
        self._load_model()
        result = self._model.transcribe(audio_file, word_timestamps=True)
        segments = []
        for seg in result.get('segments', []):
            segments.append({
                'start': seg['start'],
                'end': seg['end'],
                'text': seg['text'],
            })
        return segments


if __name__ == "__main__":
    print("Speech to Text Module Loaded")
    print(f"Whisper available: {WHISPER_AVAILABLE}")
