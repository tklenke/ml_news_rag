# Embed Technical Corpus

Script will embed a corpus of test data via one embedding model and store 
the vector data into a ChromaDB. Script will build a list of documents to embed and start
embedding each file.  the order of files will be random, but a list will be kept such
that the script can be stopped and restarted saving progress.

## Workflow

### Set up Docker Containers

Build two docker containers required.  One for the ChromaDB and one for Ollama and the embedding models.
ChromaDB will store data persistantly and Ollama will download relevant models for embedding and 
answer testing.  Start docker desktop. Run the docker-compose from the parent directory using Windows Command prompt. 

```
docker-compose build
docker-compose up -d
docker-compose ps
docker exec modeltesting-ollama-1 ollama list
```
*might need to confirm the name of the ollama container for the list*

### Ensure python has required libraries
```
pip install -r requirements. txt
```

### Run the Embedder
```
python embedder.py
```



