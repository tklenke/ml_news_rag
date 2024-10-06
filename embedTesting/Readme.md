# Embedding Model Testing on Technical Corpus

Script will embed a corpus of test data via several embedding models and store the vector
data into a ChromaDB. Then will ask three questions and pull relevant data from the 
ChromaDB to be used in generating the response.  Model is llama3 for question responses.
Each embedding model is tracked for the time to embed the corpus and store the results
in the vector database, and how long each of the test questions takes to answer.

## Workflow

### Set up Docker Containers

Two docker containers are built.  One for the ChromaDB and one for Ollama and the embedding models.
Both Docker images will store data (chroma database and downloaded models) within the docker container
**Dockerfile** will build the embedtesting-ollama-rag image

```
docker-compose build
docker-compose up -d
docker-compose ps
docker exec embedtesting-ollama-1 ollama list
```
*might need to confirm the name of the ollama container for the list*

### Ensure python has required libraries
```
pip install -r requirements. txt
```

### Run the Embedding Tests
```
python TestEmbeddings.py
```
*may want to edit Constants section of TestEmbeddings.py*


