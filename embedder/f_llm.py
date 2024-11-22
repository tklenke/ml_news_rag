import ollama
import os, time, json, re

#--------- CONSTANTs -------------


#------------FUNCTIONS---------------


# ---- LLM PROCESSING 
class LLMProcessing():
    def __init__(self, ollamahost, initial_prompt='', secondary_prompt=''):
        self.ollamaclient = ollama.Client(ollamahost)
        self.initial_prompt = initial_prompt
        self.secondary_prompt = secondary_prompt

    def ask_question(self, question, model='llama3.2:3b'):
        r = {}
        t0 = time.time()

        prompt = f"{self.initial_prompt} {question} {self.secondary_prompt}"

        #ask the model
        answer = self.ollamaclient.generate(model=model, prompt=prompt, stream=False)
  
        r["model"] = model
        r['question'] = question
        r["answer"] = answer['response']
        r['time'] = time.time()-t0

        return r

#-------------MAIN-------------------
if __name__ == "__main__":
    from f_misc import get_filenames
    #set up test constants
    LLMODELS = [
        "phi3.5:3.8b",
        "gemma2:2b",
        "ALIENTELLIGENCE/engineeringtechnicalmanuals:latest",
        "llama3.2:3b"
    ]
    INITIAL_PROMPT = """ Following is a thread from a users group for builders of aircraft. 
        Analyze the text for aviation keywords and products.
        Suggest a six word or less title that summarizes the thread.
        Provide result as JSON object with three arrays: keywords, products, title. 
        Thread follows: """
    SECONDARY_PROMPT =""" """
    MSG_DIR = r"../data/msgs"
    OLLAMAHOST = "http://localhost:11434"

    print(f"LLM test...")
    #set up instance
    oLLM = LLMProcessing(OLLAMAHOST, INITIAL_PROMPT, SECONDARY_PROMPT) 
    
    #get a list of documents
    msgfiles = get_filenames(MSG_DIR)

    for file in msgfiles:
        print(f"file: {file} ----------------")
        #get the text
        with open(file, 'r') as f:
            txt = f.read()

        #ask the question of the models

        for model in LLMODELS:
            r = oLLM.ask_question(txt, model)
            txt = re.sub(r"[\s\\]"," ",r['answer'])
            rA = re.findall(r"\{(.*)\}", txt)
            if len(rA) > 0:
                rJson = "{" + rA[0] + "}"
            else:
                rJson = f"JSON MISSING {r['answer']}"

            #write the results
            print(f"ANSWER from {r['model']} in {r['time']:.1f} secs\n{rJson}\n")



