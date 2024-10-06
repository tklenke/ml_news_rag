import ollama
import chromadb
import time
from chroma_functions import importdocs, getclient, getcollection

#--------- CONSTANTs -------------
mainModel = "llama3"
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

emodels = [
	"all-minilm",
	"bge-m3",
	"bge-large",
	"mxbai-embed-large",
	"snowflake-arctic-embed",
	"nomic-embed-text",
    None
]

#-------------MAIN-------------------
print(f"Starting EmbedTesting...")
chromaclient = getclient()
results=[]

for emodel in emodels:
    stats = {}
    stats['Model'] = emodel
    stats['totalanswertime'] = 0
    print(f"running embed model {emodel}...")

    #embed if appropriate
    t0 = time.time()
    if emodel is None:
        print(f" skipping embed for None")
    else:
        #get chromacollection
        collection = getcollection(chromaclient,emodel) 
        importdocs(sourceDocPath, emodel, collection, chunck_size)
    stats['Embed time'] = time.time()-t0

    print(f" asking questions...")
    #ask the questions
 
    for i in range(0,len(questions)):
        query = questions[i]

        t1 = time.time()
        if emodel is None:
            prompt = f"{base_prompt} {query}"
        else:
            print(f"  getting question {i} related docs...")
            queryembed = ollama.embed(model=emodel, input=query)['embeddings']
            relateddocs = '\n\n'.join(collection.query(query_embeddings=queryembed, n_results=10)['documents'][0])
            prompt = f"{base_prompt} {query} {rag_prompt} {relateddocs}"
        
        print(f"  asking question {i}...")
        answer = ollama.generate(model=mainModel, prompt=prompt, stream=False)

        stats[str(i)+"time"] = time.time()-t1
        stats['totalanswertime'] += time.time()-t1
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
for r in results:
    print(f"Model: {r['Model']}")
    print(f"  Embed: {r['Embed time']:.4f} secs")
    for i in range(0,len(questions)):
        print(f"  Q{i}: {r[str(i)+'time']:.4f} secs")

            
    




