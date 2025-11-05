FROM ollama/ollama
# Install required dependencies
RUN echo "getting embed models"
# Install the models
# Install embed models (note will install in a new image basically)
RUN nohup bash -c "ollama serve &" \
   && sleep 2 \
#   && ollama run mistral-openorca:7b
#   && ollama run gemma3:1b \
  && ollama run gemma3:4b
#   && ollama pull nomic-embed-text 


