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
        """Test graceful error handling when LLM fails (non-model errors)."""
        message = "Installing firewall"

        # Mock LLM to raise non-model exception (e.g., connection error)
        with patch.object(tagger, 'ollamaclient') as mock_client:
            mock_client.generate.side_effect = Exception("Connection timeout")

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

    def test_categorize_message_single_chapter(self, tagger):
        """Test categorizing message with single chapter match."""
        message = "Working on firewall installation"

        with patch.object(tagger, 'ollamaclient') as mock_client:
            mock_response = {'response': '23'}
            mock_client.generate.return_value = mock_response

            chapters, raw_response = tagger.categorize_message(message)

            assert isinstance(chapters, list)
            assert chapters == [23]
            assert raw_response == '23'

    def test_categorize_message_multiple_chapters(self, tagger):
        """Test categorizing message with multiple chapter matches."""
        message = "Installing fuselage bulkheads, firewall, and engine mount"

        with patch.object(tagger, 'ollamaclient') as mock_client:
            mock_response = {'response': '4, 15, 23'}
            mock_client.generate.return_value = mock_response

            chapters, raw_response = tagger.categorize_message(message)

            assert isinstance(chapters, list)
            assert chapters == [4, 15, 23]  # Should be sorted
            assert raw_response == '4, 15, 23'

    def test_categorize_message_verbose_format(self, tagger):
        """Test parsing verbose chapter format."""
        message = "Working on fuselage and firewall"

        with patch.object(tagger, 'ollamaclient') as mock_client:
            mock_response = {'response': 'Chapter 4, Chapter 15'}
            mock_client.generate.return_value = mock_response

            chapters, raw_response = tagger.categorize_message(message)

            assert isinstance(chapters, list)
            assert chapters == [4, 15]
            assert raw_response == 'Chapter 4, Chapter 15'

    def test_categorize_message_none_response(self, tagger):
        """Test parsing 'NONE' response for categorization."""
        message = "Weather delays this week"

        with patch.object(tagger, 'ollamaclient') as mock_client:
            mock_response = {'response': 'NONE'}
            mock_client.generate.return_value = mock_response

            chapters, raw_response = tagger.categorize_message(message)

            assert isinstance(chapters, list)
            assert len(chapters) == 0
            assert raw_response == 'NONE'

    def test_categorize_message_invalid_chapters(self, tagger):
        """Test filtering out invalid chapter numbers."""
        message = "Various work"

        with patch.object(tagger, 'ollamaclient') as mock_client:
            mock_response = {'response': '0, 4, 26, 100'}
            mock_client.generate.return_value = mock_response

            chapters, raw_response = tagger.categorize_message(message)

            assert isinstance(chapters, list)
            assert chapters == [4]  # Only valid chapter (1-25)
            assert raw_response == '0, 4, 26, 100'

    def test_categorize_message_empty_message(self, tagger):
        """Test categorizing empty message."""
        chapters, raw_response = tagger.categorize_message("")

        assert isinstance(chapters, list)
        assert len(chapters) == 0
        assert raw_response == ""

    def test_categorize_message_error_handling(self, tagger):
        """Test graceful error handling when LLM fails during categorization (non-model errors)."""
        message = "Working on firewall"

        with patch.object(tagger, 'ollamaclient') as mock_client:
            mock_client.generate.side_effect = Exception("Connection timeout")

            chapters, raw_response = tagger.categorize_message(message)

            assert isinstance(chapters, list)
            assert len(chapters) == 0
            assert "ERROR" in raw_response

    def test_categorize_message_removes_duplicates(self, tagger):
        """Test removing duplicate chapter numbers."""
        message = "Multiple references to same chapters"

        with patch.object(tagger, 'ollamaclient') as mock_client:
            mock_response = {'response': '4, 4, 15, 15, 23'}
            mock_client.generate.return_value = mock_response

            chapters, raw_response = tagger.categorize_message(message)

            assert isinstance(chapters, list)
            assert chapters == [4, 15, 23]  # No duplicates, sorted
            assert raw_response == '4, 4, 15, 15, 23'

    def test_tag_message_model_not_found_raises_error(self, tagger, keywords):
        """Test that model not found error terminates immediately."""
        message = "Installing firewall"

        with patch.object(tagger, 'ollamaclient') as mock_client:
            mock_client.generate.side_effect = Exception("model 'gemma3:1b' not found (status code: 404)")

            # Should raise RuntimeError, not return empty list
            with pytest.raises(RuntimeError, match="LLM model not found"):
                tagger.tag_message(message, keywords)

    def test_categorize_message_model_not_found_raises_error(self, tagger):
        """Test that model not found error terminates immediately during categorization."""
        message = "Working on firewall"

        with patch.object(tagger, 'ollamaclient') as mock_client:
            mock_client.generate.side_effect = Exception("model 'llama3:8b' not found")

            # Should raise RuntimeError, not return empty list
            with pytest.raises(RuntimeError, match="LLM model not found"):
                tagger.categorize_message(message)
