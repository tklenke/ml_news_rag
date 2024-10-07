FROM ollama/ollama
# Install required dependencies
RUN echo "getting embed models"
# Install the models
# Install embed models (note will install in a new image basically)
RUN nohup bash -c "ollama serve &" \
   && sleep 2 \
<<<<<<< HEAD
   && ollama pull all-minilm \
   && ollama run llama3.2:3b \
   && ollama pull ALIENTELLIGENCE/engineeringtechnicalmanuals \
   && ollama run gemma2:2b \
   && ollama run phi3.5:3.8b
=======
   && ollama pull mxbai-embed-large \
   && ollama pull all-minilm \
   && ollama pull snowflake-arctic-embed \
   && ollama pull bge-m3 \
   && ollama pull bge-large \
   && ollama pull nomic-embed-text \
   && ollama pull llama3
>>>>>>> 048e69d3858afa223cce80f777b73162c6d8639a
