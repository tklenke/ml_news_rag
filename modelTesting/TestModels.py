import ollama
import chromadb
import time
from chroma_functions import getclient, getcollection, importdocs

#--------- CONSTANTs -------------
embedModel = "all-minilm"
sourceDocPath = "../data/test"
chunck_size = 75

base_prompt ="""You are an aerospace engineer specializing in amatuer-built aircraft. Don't restate this. If you don't know the answer, 
    just say that you don't know, don't try to make up an answer. """

rag_prompt =""" Use the following pieces of context to answer the users question. -----"""

questions = [
    "How much angle should I have for the control stick to allow for sufficient clearance?",
    "Give me a list of engines that I should consider.  Include two sentences of pros and cons for each.",
    "Give me a list of tips to consider when installing the engine."
]


llmodels = [
	"phi3.5:3.8b",
	"gemma2:2b",
	"ALIENTELLIGENCE/engineeringtechnicalmanuals:latest",
	"llama3.2:3b"]

#-------------MAIN-------------------
print(f"Starting ModelTesting...")
chromaclient = getclient()
results=[]

#embed
t0 = time.time()
#get chromacollection
collection = getcollection(chromaclient,embedModel) 
importdocs(sourceDocPath, embedModel, collection, chunck_size)
embed_time = time.time()-t0

for llmodel in llmodels:
    stats = {}
    stats['Model'] = llmodel
    print(f"running llm {llmodel}...")

    print(f" asking questions...")
    #ask the questions
 
    for i in range(0,len(questions)):
        query = questions[i]

        t1 = time.time()
        print(f"  getting question {i} related docs...")
        queryembed = ollama.embed(model=embedModel, input=query)['embeddings']
        relateddocs = '\n\n'.join(collection.query(query_embeddings=queryembed, n_results=10)['documents'][0])
        prompt = f"{base_prompt} {query} {rag_prompt} {relateddocs}"
        
        print(f"  asking question {i}...")
        answer = ollama.generate(model=llmodel, prompt=prompt, stream=False)

        stats[str(i)+"time"] = time.time()-t1
        stats[str(i)+"answer"] = answer['response']

    results.append(stats)

print(f"----QUESTIONS-----")
for i in range(0,len(questions)):
    print(f"Question {i}: {questions[i]}")

print(f"------PROMPT------")
print(f"{base_prompt}")

print(f"-----ANSWERS------")
for r in results:
    print(f"\nModel: {r['Model']}")
    for i in range(0,len(questions)):
        print(f"\n  A{i}: ----------\n{r[str(i)+'answer']}")

print(f"-----STATS------")
print(f"Chunk size: {chunck_size}")
print(f"Embed Time: {embed_time:.4f} secs")
for r in results:
    print(f"Model: {r['Model']}")
    for i in range(0,len(questions)):
        print(f"  Q{i}: {r[str(i)+'time']:.4f} secs")

            
    




