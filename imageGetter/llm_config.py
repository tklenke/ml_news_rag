# ABOUTME: LLM configuration for keyword extraction and tagging
# ABOUTME: Defines Ollama host, model settings, and prompt templates

# LLM Configuration
OLLAMA_HOST = "http://localhost:11434"
LLM_MODEL = "gemma3:1b"  # Tom can edit this as needed

# Prompt template for keyword extraction (Phase 4a)
KEYWORD_EXTRACTION_PROMPT = """You are a very exact librarian tasked with analyzing aircraft builder messages to build a keyword vocabulary.

The existing list of keywords is: {keywords}

Extract all aircraft-building related keywords from this message.

Message: {message}

Return keywords as a comma-separated list. Focus on:
- Aircraft parts (firewall, cowling, canard, etc.)
- Tools and materials (epoxy, aluminum, fiberglass, etc.)
- Processes (layup, installation, painting, etc.)
- Systems (engine, fuel, electrical, etc.)

Return only the keywords, no explanations. If there is an error, return a blank line."""

# Prompt template for keyword tagging (Phase 4b)
KEYWORD_TAGGING_PROMPT = """You are analyzing aircraft builder messages. Given this list of keywords, return ONLY the keywords that are relevant to the message below.

Keywords: {keywords}

Message: {message}

Return the matching keywords as a comma-separated list. If no keywords match, return "NONE". Do not include explanations or extra text."""
