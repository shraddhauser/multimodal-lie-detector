"""
Unit tests for Gemini reasoning module.
Tests use mocking — no API key or internet required.
"""

import os
from unittest.mock import MagicMock, patch

from gemini.gemini_reasoning import CAVEAT, GeminiReasoning


class TestGeminiReasoning:
    """Tests for GeminiReasoning."""

    def test_no_api_key_graceful(self):
        """Without an API key, generate_summary should return None."""
        # Clear the env var so no key can leak in from the developer's machine
        with patch.dict(os.environ, {}, clear=True):
            reasoning_clean = GeminiReasoning(api_key=None)
            result = reasoning_clean.generate_summary({'deviation_index': 0.5})
            assert result is None

    def test_prompt_includes_caveat(self):
        """The prompt sent to Gemini should include the ethical caveat."""
        reasoning = GeminiReasoning(api_key='fake-key')
        report = {'deviation_index': 0.5, 'per_signal': {'pitch_mean': 1.2}}
        prompt = reasoning._build_prompt(report)
        assert CAVEAT in prompt

    @patch('gemini.gemini_reasoning.GENAI_AVAILABLE', True)
    def test_generate_summary_with_mock(self):
        """With a mocked Gemini client, generate_summary should return text."""
        reasoning = GeminiReasoning(api_key='fake-key')

        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a mocked summary with caveat."
        mock_model.generate_content.return_value = mock_response

        reasoning._model = mock_model

        report = {'deviation_index': 0.5, 'per_signal': {'pitch_mean': 1.2}}
        result = reasoning.generate_summary(report)
        assert result == "This is a mocked summary with caveat."
        mock_model.generate_content.assert_called_once()

    def test_api_error_degrades_gracefully(self):
        """A Gemini/network error must not break the report; it just has no summary."""
        reasoning = GeminiReasoning(api_key='fake-key')
        reasoning._model = MagicMock()
        reasoning._model.generate_content.side_effect = RuntimeError('network down')
        report = reasoning.generate_report({}, {'deviation_index': 0.5, 'available_signals': ['pitch_mean']})
        assert report['ai_summary'] is None
        assert report['caveat'] == CAVEAT

    def test_report_structure(self):
        """generate_report should include the caveat even without API."""
        with patch.dict(os.environ, {}, clear=True):
            reasoning = GeminiReasoning(api_key=None)
            report = reasoning.generate_report(
                {},
                {'deviation_index': 0.3, 'per_signal': {}}
            )
        assert 'caveat' in report
        assert report['ai_summary'] is None  # no key → no summary
        assert 'deviation_report' in report
