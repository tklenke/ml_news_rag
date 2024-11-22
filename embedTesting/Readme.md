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


### TestEmbeddingsRev2
Perhaps a better way to test than gut feel of quality of anwsers, is to look at how well the embedding model finds relevant chunks. Made assumption that a shorter distance from a question to document that has essentiall the same text means the embedding model is working better.

Run all models against 10 newsletters and measureed the time to embed all.  And then for three queries that are made from looking at the text in three newsletters, checked the vector distances.

Subtracted distance from 1 to get a score where higher is better (arbitrary but easier for my brain!)

Results:
`
| Avg Dist |    Ratio of Distance/Embed Time	|
| 0.51 |	0.83 |	Model: all-minilm |		
| 0.62 |	0.60 |	Model: bge-m3 |
| 0.69 |	0.69 |	Model: bge-large |
| 0.69 |	0.64 |	Model: mxbai-embed-large |		
| 0.70 |	0.69 |	Model: snowflake-arctic-embed |		
| 0.67 | 	0.91 |	Model: nomic-embed-text |
`
Seems that nomic-embed-text provides much faster embedding (a consideration) for only marginal loss of distance.  Note that the distance winner (snowflake) did very poorly in picking the right chunks...so really should be disqualified.