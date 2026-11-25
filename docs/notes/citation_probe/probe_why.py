# ABOUTME: One-off probe: shows the two prompts of probe_question.py and asks gpt-6-luna why its
# ABOUTME: numbered answer left out hints that its plain answer gave. Not site code.
import json, os, re, sys
import openai
sys.path.insert(0, '/home/tom/projects/site_2024/evaluation')
from src import llm_functions as lf
from src.site_config import read_config
from answer_models import create_retriever
from probe_wording import INSTRUCTION

HERE = os.path.dirname(os.path.abspath(__file__))
rec = json.load(open(os.path.join(HERE, sys.argv[1])))
cfg = read_config('/home/tom/projects/site_2024/fwww')
client = openai.OpenAI(api_key=cfg.get('KEYS', 'OPENAI'))
ret = create_retriever(cfg, 'localhost', 'http://localhost:11434')
rq = ret.get_query_results(rec['question'])
n = len(rec['ids'])
assert rq['ids'][0][:n] == rec['ids'], 'retrieval changed'
docs = rq['documents'][0][:n]
data = {'type': 'new', 'query': rec['question']}

def numbered_prompt(d):
    old = lf.secondary_prompt
    lf.secondary_prompt = old.rstrip()[:-5] + INSTRUCTION + ' ----- '
    p = lf.build_prompt(data, [f"[{i}] {x}" for i, x in enumerate(d, 1)])
    lf.secondary_prompt = old
    return p

stub = ['(text of chunk)'] * 2
print('=== PLAIN PROMPT, chunk text left out ===\n' + lf.build_prompt(data, stub))
print('\n=== NUMBERED PROMPT, chunk text left out ===\n' + numbered_prompt(stub))
for w in ('spacer', 'vacuum', 'tap', 'thread'):
    print(w, [i for i, d in enumerate(docs, 1) if re.search(w, d, re.I)])
WHY = ("Below is another answer you gave to the same question with the same context. The only "
       "difference was that the prompt did not have the instruction about numbers in square brackets. "
       "That answer has hints that your numbered answer does not have: a spacer between the pads when "
       "a caliper is off the disc, vacuum bleeding drawing air past the bleeder threads, and tapping "
       "the caliper and high points. Why did your numbered answer leave these out? For each of the "
       "three hints, say whether it is in the context and, if so, in which numbered piece.\n\n"
       "The other answer:\n\n" + rec['plain'])
c = client.chat.completions.create(model='gpt-6-luna', messages=[
    {"role": "user", "content": numbered_prompt(docs)},
    {"role": "assistant", "content": rec['numbered']},
    {"role": "user", "content": WHY}])
print('\n=== FOLLOW-UP QUESTION ===\n' + WHY.split('\n\nThe other answer')[0])
print('\n=== MODEL REPLY ===\n' + (c.choices[0].message.content or ''))
open(os.path.join(HERE, 'probe_Q35_variation_why.md'), 'w', encoding='utf-8').write(
    '# Follow-up question\n\n' + WHY + '\n\n# Reply (gpt-6-luna)\n\n' + (c.choices[0].message.content or '') + '\n')
