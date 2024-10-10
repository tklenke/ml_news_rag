import ollama
import chromadb
import time
from chroma_functions import importdocs, getclient, getcollection

#--------- CONSTANTs -------------
embedModel = "all-minilm"
llmodel = "gemma2:2b"
llmodel = "ALIENTELLIGENCE/engineeringtechnicalmanuals:latest"
MAX_DISTANCE = .5
MIN_DOCUMENTS = 5
MAX_DOCUMENTS = int((8100 * .75)/ 75)
MAX_DOCUMENTS = 10

base_prompt ="""You are an aerospace engineer specializing in amatuer-built aircraft. Don't restate this. If you don't know the answer, 
    just say that you don't know, don't try to make up an answer. """
base_prompt = ""

rag_prompt =""" Use the following pieces of context to answer the users question. -----"""

questions = [
    "How much angle should I have for the control stick to allow for sufficient clearance?",
 #   "Give me a list of engines that I should consider.  Include two sentences of pros and cons for each.",
 #   "Give me a list of tips to consider when installing the engine.",
 #   "summarize issues related to control stick clearance fitting and interference",
]

#------------FUNCTIONS---------------
# find the index of the most irrelevant response within the defined thresholds
def get_min_relevant_response(results,fMaxDistance,nMinDocs):

    r = nMinDocs
    for i in range(nMinDocs-1,len(results['distances'][0])):
        if (results['distances'][0][i] < fMaxDistance):
            r = i
    return r
    

#-------------MAIN-------------------
print(f"Starting ModelTesting...")
chromaclient = getclient()
results=[]


#embed
t0 = time.time()
#get chromacollection
collection = getcollection(chromaclient,embedModel) 


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
    rQuery = collection.query(query_embeddings=queryembed, n_results=MAX_DOCUMENTS)
    nDocs = get_min_relevant_response(rQuery,MAX_DISTANCE,MIN_DOCUMENTS)
    relateddocs = '\n\n'.join(rQuery['documents'][0][:nDocs])
    prompt = f"{base_prompt} {query} {rag_prompt} {relateddocs}"
    
    print(f"  asking question {i}...")
    answer = ollama.generate(model=llmodel, prompt=prompt, stream=False)

    stats[str(i)+"time"] = time.time()-t1
    stats[str(i)+"answer"] = answer['response']
    stats[str(i)+"related"] = rQuery
    stats[str(i)+"numdocs"] = nDocs

print(f"\n------PROMPT------")
print(f"{base_prompt}")

print(f"\n----QUESTIONS-----")
for i in range(0,len(questions)):
    print(f"Question {i}: {questions[i]}")

print(f"\n------RELATED DOCS------")
for i in range(0,len(questions)):
    print(f"\nNum Relevant Docs in Query: {stats[str(i)+'numdocs']}")
    related = stats[str(i)+'related']
    for j in range(0,len(related['ids'])):
        print(f"--- Distance: {related['distances'][j]} ----")


print(f"\n-----ANSWERS------")
print(f"\n\nModel: {stats['Model']}")
for i in range(0,len(questions)):
    print(f"\n  A{i}: ----------\n{stats[str(i)+'answer']}")

print(f"\n-----STATS------")
print(f"Model: {stats['Model']}")
for i in range(0,len(questions)):
    print(f"  Q{i}: {stats[str(i)+'time']:.4f} secs")

            
    




