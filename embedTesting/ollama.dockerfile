FROM ollama/ollama
# Install required dependencies
RUN echo "getting embed models"
# Install the models
# Install embed models (note will install in a new image basically)
RUN nohup bash -c "ollama serve &" \
   && sleep 2 \
   && ollama pull mxbai-embed-large \
   && ollama pull all-minilm \
   && ollama pull snowflake-arctic-embed \
   && ollama pull bge-m3 \
   && ollama pull bge-large \
   && ollama pull nomic-embed-text
#   && ollama pull llama3 \  add back if running TestEmbeddingsRev1.py

