## Project Overview

ml_news_rag is a Retrieval-Augmented Generation (RAG) system for answering questions about amateur-built experimental aircraft, specifically focusing on Cozy aircraft builders. The system ingests content from newsgroups, websites, and PDFs, embeds them into a vector database, and provides intelligent question-answering capabilities using local LLM models.

### Purpose

Provide expert-level answers to aircraft builders by querying a comprehensive knowledge base of:
- Cozy Builders Google Groups discussions (historical message threads)
- Aeroelectric Connection articles and documentation
- Canard Pusher newsletters and technical content
- Other relevant amateur aircraft building resources

## Project Structure

### Data Pipeline Modules

- `msgGetter/` - Scrape Google Groups messages using Selenium + ChromeDriver
  - Runs on Windows due to Chrome/Selenium dependencies
  - Converts raw HTML messages to markdown format
  - Maintains message ID tracking to avoid duplicates

- `webGetter/` - Scrape website content and convert to markdown
  - Processes HTML and PDF files from specific websites
  - Includes canard_pusher_chunker.py for handling long newsletter text

- `extractPDFs/` - Extract text from PDF documents
  - Convert PDFs to text and markdown formats
  - Specialized extractors for Aeroelectric Connection and newsletters

- `embedder/` - Embed documents into ChromaDB vector database
  - Processes corpus of markdown documents
  - Uses Ollama embedding models (default: all-minilm)
  - Tracks embedding progress in embedstatus.txt for resume capability
  - Runs on Linux/WSL to leverage Docker infrastructure

- `asker/` - Query interface for RAG system
  - Takes natural language questions
  - Retrieves relevant context from ChromaDB
  - Generates answers using local LLM models via Ollama
  - Configurable relevance thresholds and document limits

### Testing and Evaluation

- `embedTesting/` - Test different embedding models and configurations
- `modelTesting/` - Evaluate various LLM models for answer quality

### Data Storage

- `data/` - Document corpus and message archives
  - `msgs/` - Raw messages from Google Groups
  - `msgs_md/` - Messages converted to markdown
  - `cozybuilders/` - Cozy builders specific content
  - `aeroelectric/` - Aeroelectric Connection content
  - `news/` - Newsletter and web content
  - `test/`, `test_min/` - Test datasets

### Infrastructure

- **ChromaDB**: Vector database for document embeddings (port 8000)
  - Persistent storage at `../site_2024/data/chroma`
  - Version: 1.1.1

- **Ollama**: Local LLM and embedding model server (port 11434)
  - Requires NVIDIA GPU support
  - Runs embedding models (all-minilm, etc.)
  - Runs inference models (gemma2:2b, etc.)

- **Docker Compose**: Orchestrates ChromaDB and Ollama containers

### Dependencies

Core Python libraries:
- `chromadb` - Vector database client
- `ollama` - LLM model interface
- `selenium` - Web scraping for Google Groups (Windows only)

## Project Status

### Current Capabilities

- Data ingestion pipeline functional for Google Groups, websites, and PDFs
- Embedding pipeline operational with progress tracking
- RAG query system working with configurable parameters
- Docker infrastructure deployed with GPU support

### Module Organization

- Each major module (`msgGetter`, `webGetter`, `embedder`, etc.) is self-contained
- Most modules include their own README.md and requirements.txt
- Shared utilities in modules like `chroma_functions.py` and `embed_functions.py`

### Current Structure

- `asker/` - Query interface modules
- `msgGetter/` - Google Groups scraping (Windows-based)
- `webGetter/` - Website scraping tools
- `embedder/` - Document embedding pipeline
- `extractPDFs/` - PDF text extraction
- `embedTesting/` - Embedding model evaluation
- `modelTesting/` - LLM model evaluation
- `newsGetter/` - [DEPRECATED] Old news scraping (use msgGetter)
- `data/` - Document corpus storage
- `docs/plans/` - Design specifications and implementation plans
  - `required_from_tom.md` - Items such as test fixtures needed from Tom
  - `architect_todo.md` - Place for Programmer or Tom to give feedback to the architect
  - `programmer_todo.md` - Place where architect gives direction to programmer on what steps to tackle next
- `docs/acronyms.md` - Domain terminology and acronyms
- `docs/references/` - Reference materials (READ ONLY)
- `venv/` - Python virtual environment

## Documentation Management

### Reference Materials
- All files in `docs/references/` are READ ONLY. NEVER modify these files.
- These contain source materials and documentation references.

### Working Documentation
- Update `docs/acronyms.md` as new domain terminology is introduced
- Update this file as the project structure evolves or new modules are added
