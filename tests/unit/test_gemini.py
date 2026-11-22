"""
Unit tests for Gemini reasoning module.
Tests use mocking — no API key or internet required.
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from gemini.gemini_reasoning import GeminiReasoning, CAVEAT


class TestGeminiReasoning:
    """Tests for GeminiReasoning."""

    def test_no_api_key_graceful(self):
        """Without an API key, generate_summary should return None."""
        reasoning = GeminiReasoning(api_key=None)
        # Also clear the env var
        with patch.dict(os.environ, {}, clear=True):
            reasoning_clean = GeminiReasoning(api_key=None)
            result = reasoning_clean.generate_summary({'deviation_index': 0.5})
            assert result is None

    def test_prompt_includes_caveat(self):
        """The prompt sent to Gemini should include the ethical caveat."""
        reasoning = GeminiReasoning(api_key='fake-key')
        report = {'deviation_index': 0.5, 'per_signal': {'pitch_mean': 1.2}}
        prompt = reasoning._build_prompt(report)
        assert 'no scientifically validated' in prompt.lower() or \
               'no reliable physiological' in prompt.lower() or \
               CAVEAT[:30] in prompt

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

    def test_report_structure(self):
        """generate_report should include the caveat even without API."""
        reasoning = GeminiReasoning(api_key=None)
        report = reasoning.generate_report(
            {},
            {'deviation_index': 0.3, 'per_signal': {}}
        )
        assert 'caveat' in report
        assert report['ai_summary'] is None  # no key → no summary
        assert 'deviation_report' in report


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
