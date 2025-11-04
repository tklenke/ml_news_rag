"""Tests for LLM keyword tagger."""

import pytest
from unittest.mock import Mock, patch
from llm_tagger import KeywordTagger


class TestKeywordTagger:
    """Test KeywordTagger class."""

    @pytest.fixture
    def tagger(self):
        """Create KeywordTagger instance."""
        return KeywordTagger()

    @pytest.fixture
    def keywords(self):
        """Sample keyword list."""
        return ["firewall", "cowling", "canard", "engine", "fuel", "electrical", "panel"]

    @pytest.mark.skip(reason="Requires Ollama running - integration test")
    def test_tag_message_exact_match(self, tagger, keywords):
        """Test tagging message with exact keyword match."""
        message = "I'm installing the firewall today"
        result, raw_response = tagger.tag_message(message, keywords)

        assert isinstance(result, list)
        assert isinstance(raw_response, str)
        assert "firewall" in result

    @pytest.mark.skip(reason="Requires Ollama running - integration test")
    def test_tag_message_synonym_match(self, tagger, keywords):
        """Test tagging message with synonym (cowl -> cowling)."""
        message = "Working on the cowl attachment"
        result, raw_response = tagger.tag_message(message, keywords)

        assert isinstance(result, list)
        assert isinstance(raw_response, str)
        assert "cowling" in result

    @pytest.mark.skip(reason="Requires Ollama running - integration test")
    def test_tag_message_context_match(self, tagger, keywords):
        """Test semantic understanding (Rotax -> engine)."""
        message = "Rotax 916is installation complete"
        result, raw_response = tagger.tag_message(message, keywords)

        assert isinstance(result, list)
        assert isinstance(raw_response, str)
        assert "engine" in result

    @pytest.mark.skip(reason="Requires Ollama running - integration test")
    def test_tag_message_no_match(self, tagger, keywords):
        """Test message with no matching keywords."""
        message = "Weather delays this week"
        result, raw_response = tagger.tag_message(message, keywords)

        assert isinstance(result, list)
        assert isinstance(raw_response, str)
        assert len(result) == 0

    @pytest.mark.skip(reason="Requires Ollama running - integration test")
    def test_tag_message_multiple_keywords(self, tagger, keywords):
        """Test message matching multiple keywords."""
        message = "Firewall and cowling installation with new panel"
        result, raw_response = tagger.tag_message(message, keywords)

        assert isinstance(result, list)
        assert isinstance(raw_response, str)
        assert len(result) >= 2
        assert "firewall" in result
        assert "cowling" in result or "panel" in result

    def test_tag_message_validates_against_master_list(self, tagger, keywords):
        """Test that LLM responses are validated against master keyword list."""
        message = "Installing firewall"

        # Mock LLM to return invalid keyword not in master list
        with patch.object(tagger, 'ollamaclient') as mock_client:
            mock_response = {'response': 'firewall, fake_keyword_not_in_list'}
            mock_client.generate.return_value = mock_response

            result, raw_response = tagger.tag_message(message, keywords)

            # Should only return valid keywords
            assert "firewall" in result
            assert "fake_keyword_not_in_list" not in result
            assert raw_response == 'firewall, fake_keyword_not_in_list'

    def test_tag_message_empty_message(self, tagger, keywords):
        """Test tagging empty message."""
        result, raw_response = tagger.tag_message("", keywords)

        assert isinstance(result, list)
        assert isinstance(raw_response, str)
        assert len(result) == 0
        assert raw_response == ""

    def test_tag_message_empty_keywords(self, tagger):
        """Test tagging with empty keyword list."""
        message = "Installing firewall"
        result, raw_response = tagger.tag_message(message, [])

        assert isinstance(result, list)
        assert isinstance(raw_response, str)
        assert len(result) == 0
        assert raw_response == ""

    def test_llm_error_handling(self, tagger, keywords):
        """Test graceful error handling when LLM fails."""
        message = "Installing firewall"

        # Mock LLM to raise exception
        with patch.object(tagger, 'ollamaclient') as mock_client:
            mock_client.generate.side_effect = Exception("LLM connection error")

            # Should not crash, should return empty list and error message
            result, raw_response = tagger.tag_message(message, keywords)

            assert isinstance(result, list)
            assert isinstance(raw_response, str)
            assert len(result) == 0
            assert "ERROR" in raw_response

    def test_llm_timeout_handling(self, tagger, keywords):
        """Test timeout handling."""
        message = "Installing firewall"

        # Mock LLM to timeout
        with patch.object(tagger, 'ollamaclient') as mock_client:
            mock_client.generate.side_effect = TimeoutError("Request timed out")

            # Should not crash, should return empty list and error message
            result, raw_response = tagger.tag_message(message, keywords)

            assert isinstance(result, list)
            assert isinstance(raw_response, str)
            assert len(result) == 0
            assert "ERROR" in raw_response

    def test_custom_ollama_host(self):
        """Test initializing with custom Ollama host."""
        custom_host = "http://custom:11434"
        tagger = KeywordTagger(ollamahost=custom_host)

        assert tagger.host == custom_host

    def test_custom_model(self, tagger, keywords):
        """Test using custom model parameter."""
        message = "Installing firewall"
        custom_model = "gemma2:2b"

        with patch.object(tagger, 'ollamaclient') as mock_client:
            mock_response = {'response': 'firewall'}
            mock_client.generate.return_value = mock_response

            result, raw_response = tagger.tag_message(message, keywords, model=custom_model)

            # Verify custom model was used
            mock_client.generate.assert_called_once()
            call_kwargs = mock_client.generate.call_args[1]
            assert call_kwargs['model'] == custom_model
            assert raw_response == 'firewall'

    def test_parse_none_response(self, tagger, keywords):
        """Test parsing 'NONE' response from LLM."""
        message = "Weather delays"

        with patch.object(tagger, 'ollamaclient') as mock_client:
            mock_response = {'response': 'NONE'}
            mock_client.generate.return_value = mock_response

            result, raw_response = tagger.tag_message(message, keywords)

            assert isinstance(result, list)
            assert len(result) == 0
            assert raw_response == 'NONE'

    def test_parse_comma_separated_response(self, tagger, keywords):
        """Test parsing comma-separated response."""
        message = "Installing firewall and cowling"

        with patch.object(tagger, 'ollamaclient') as mock_client:
            mock_response = {'response': 'firewall, cowling'}
            mock_client.generate.return_value = mock_response

            result, raw_response = tagger.tag_message(message, keywords)

            assert "firewall" in result
            assert "cowling" in result
            assert raw_response == 'firewall, cowling'

    def test_parse_response_with_extra_whitespace(self, tagger, keywords):
        """Test parsing response with extra whitespace."""
        message = "Installing firewall"

        with patch.object(tagger, 'ollamaclient') as mock_client:
            mock_response = {'response': '  firewall  ,  cowling  '}
            mock_client.generate.return_value = mock_response

            result, raw_response = tagger.tag_message(message, keywords)

            # Whitespace should be stripped
            assert "firewall" in result
            assert "cowling" in result
            # No whitespace-padded entries
            assert "  firewall  " not in result
            assert raw_response == '  firewall  ,  cowling  '
