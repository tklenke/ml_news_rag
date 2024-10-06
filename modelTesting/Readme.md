=Embedding Model Testing on Technical Corpus=

==Workflow==

===Set up Docker Containers===

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

===Run the Embedding Tests===




