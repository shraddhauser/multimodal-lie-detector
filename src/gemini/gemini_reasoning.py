"""
Gemini Reasoning Module (optional)
Turns a signal-deviation report into a plain-English summary with an
explicit ethical caveat.  The API key comes from the environment only.

When no API key is set or the library is unavailable, the module degrades
gracefully: generate_summary() returns None and the report omits the
AI summary.
"""

import json
import os

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

CAVEAT = (
    "IMPORTANT: There is no scientifically validated physiological or "
    "behavioral 'lie signature'. These signals reflect cognitive load, "
    "stress, or individual differences — not deception. This tool must "
    "not be used for hiring, policing, legal proceedings, or any "
    "high-stakes decision."
)


class GeminiReasoning:
    """Use Google Gemini for multi-step reasoning (optional, mocked in tests)."""

    def __init__(self, api_key=None):
        """
        Args:
            api_key: Gemini API key.  If None, reads from GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        self.model_name = "gemini-2.0-flash"
        self._model = None

    def _get_model(self):
        if self._model is None:
            if not GENAI_AVAILABLE or not self.api_key:
                return None
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(self.model_name)
        return self._model

    def generate_summary(self, deviation_report):
        """
        Generate a plain-English summary of the deviation report.

        Args:
            deviation_report: dict returned by MultimodalFusion.compute_deviation().

        Returns:
            str summary, or None if the API is unavailable.
        """
        model = self._get_model()
        if model is None:
            return None

        prompt = self._build_prompt(deviation_report)
        response = model.generate_content(prompt)
        return response.text

    def _build_prompt(self, deviation_report):
        """Build the Gemini prompt including the ethical caveat."""
        report_json = json.dumps(deviation_report, indent=2, default=str)
        return (
            "You are a behavioral-signal analysis assistant. "
            "Summarise the following deviation report in plain English. "
            "Explain which signals deviated most from the speaker's baseline "
            "and what that might indicate (e.g. increased cognitive load, "
            "stress, discomfort). "
            f"\n\n{CAVEAT}\n\n"
            "Always include the above caveat in your summary.\n\n"
            f"Report:\n{report_json}"
        )

    def generate_report(self, analysis_meta, deviation_report):
        """
        Assemble the final report.

        Args:
            analysis_meta: dict of pipeline metadata (durations, window counts...).
            deviation_report: dict returned by MultimodalFusion.compute_deviation().
        """
        summary = None
        if deviation_report.get('available_signals'):
            try:
                summary = self.generate_summary(deviation_report)
            except Exception:
                summary = None  # network/API errors must not break the report
        return {
            'title': 'Multimodal Behavioral-Signal Analysis Report',
            'analysis': analysis_meta or {},
            'deviation_report': deviation_report,
            'ai_summary': summary,
            'caveat': CAVEAT,
        }


if __name__ == "__main__":
    print("Gemini Reasoning Module Loaded")
    print(f"GenAI available: {GENAI_AVAILABLE}")
    print(f"API key set: {bool(os.environ.get('GEMINI_API_KEY'))}")
