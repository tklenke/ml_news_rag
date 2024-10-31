import ollama
import chromadb
import time
from chroma_functions import importdocs, getclient, getcollection

#--------- CONSTANTs -------------
sourceDocPath = "../data/test"
chunk_size = 75

questions = [
    "How much angle should I have for the control stick to allow for sufficient clearance between the stick and the fuselage side to get full aileron travel when your hand is on the stick?",
    "Give me some suggestions on cutting BID tapes",
    "How much vacuum should I pull when testing fuel tanks for leaks"
]
#news 9, news 4, news 10 

emodels = [
	"all-minilm",
	"bge-m3",
	"bge-large",
	"mxbai-embed-large",
	"snowflake-arctic-embed",
	"nomic-embed-text"
]

#-------METHODOLOGY-------
# Will embed newsletters and then ask three questions that are specifically addressed
# in the newsletters and see which embedding models provide the closest vector distance

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
        collection_name = emodel + "embedTest"
        collection = getcollection(chromaclient,collection_name) 
        importdocs(sourceDocPath, emodel, collection, chunk_size)
    stats['Embed time'] = time.time()-t0

    print(f" asking questions...")
    #ask the questions
 
    for i in range(0,len(questions)):
        query = questions[i]

        t1 = time.time()

        print(f"  getting question {i} related docs...")
        queryembed = ollama.embed(model=emodel, input=query)['embeddings']
        rQuery = collection.query(query_embeddings=queryembed, n_results=10)

        stats[str(i)+"distances"] = rQuery['distances'][0]
        stats[str(i)+"sources"] = rQuery['metadatas'][0]

        stats[str(i)+"time"] = time.time()-t1

    results.append(stats)


print(f"----QUESTIONS-----")
for i in range(0,len(questions)):
    print(f"Question {i}: {questions[i]}")


print(f"-----STATS------")
print(f"Chunk size: {chunk_size}")
for r in results:
    print(f"Model: {r['Model']}")
    print(f"  Embed: {r['Embed time']:.4f} secs")
    qTimeTotal = 0.
    for i in range(0,len(questions)):
        t = r[str(i)+'time']
        qTimeTotal += t
        print(f"  Q{i}: {t:.4f} secs")
        d10 = 0.
        d3 = 0.
        for j in range(0,10):
            d = r[str(i)+'distances'][j]
            d10 += d
            if j < 3:
                d3 += d
            print(f"      {d} {r[str(i)+'sources'][j]['source']}")
        print (f"Totals: embed: {r['Embed time']:.4f} query: {qTimeTotal:.4f} secs Distances: {(d10/10.):.4f} d10 {(d3/3.):.4f} d3")

            
    




