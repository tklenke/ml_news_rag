import sys, chromadb, ollama

chromaclient = chromadb.HttpClient(host="localhost", port=8000)
collection = chromaclient.get_or_create_collection(name="buildragwithpython")

#query = " ".join(sys.argv[1:])
query = "what are a few tips on protecting your skin"
print(f"embedding query {query}")
queryembed = ollama.embed(model="nomic-embed-text", input=query)['embeddings']

relateddocs = '\n\n'.join(collection.query(query_embeddings=queryembed, n_results=10)['documents'][0])
prompt = f"{query} - Answer that question using the following text as a resource: {relateddocs}"

print(f"asking without rag")
noragoutput = ollama.generate(model="llama3", prompt=query, stream=False)
print(f"Answered without RAG: {noragoutput['response']}")
print("---")
print(f"asking with rag")
ragoutput = ollama.generate(model="llama3", prompt=prompt, stream=False)

print(f"Answered with RAG: {ragoutput['response']}")
print("---")
print(f"{prompt}")