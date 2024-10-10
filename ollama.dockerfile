FROM ollama/ollama AS ollama-huh
# Install required dependencies
RUN echo "getting embed models"
# Install the models
# Install embed models (note will install in a new image basically)
RUN nohup bash -c "ollama serve &" \
&& sleep 2 \
&& ollama pull all-minilm \
#&& ollama pull ALIENTELLIGENCE/engineeringtechnicalmanuals \
&& ollama run gemma2:2b \
#&& ollama run phi3.5:3.8b
eche "done"