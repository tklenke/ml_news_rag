# ABOUTME: One-off probe: retrieves chunks for a new question as the site does and asks gpt-6-luna
# ABOUTME: twice, with and without numbered chunks; writes both answers to a markdown file. Not site code.
import json, os, re, sys, time
import openai
sys.path.insert(0, '/home/tom/projects/site_2024/evaluation')
from src import llm_functions as lf
from src.site_config import read_config
from answer_models import create_retriever
from probe_wording import INSTRUCTION

HERE = os.path.dirname(os.path.abspath(__file__))
NAME, QUESTION = sys.argv[1], sys.argv[2]
MODEL = 'gpt-6-luna'
cfg = read_config('/home/tom/projects/site_2024/fwww')
client = openai.OpenAI(api_key=cfg.get('KEYS', 'OPENAI'))
ret = create_retriever(cfg, 'localhost', 'http://localhost:11434')
rq = ret.get_query_results(QUESTION)
n = lf.get_num_draft_docs(rq, ret.max_distance, ret.min_documents, ret.max_draft_documents)
ids, docs, metas = rq['ids'][0][:n], rq['documents'][0][:n], rq['metadatas'][0][:n]
data = {'type': 'new', 'query': QUESTION}

def ask(prompt):
    t = time.time()
    c = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
    u = c.usage
    return c.choices[0].message.content or '', (f"tokens in {u.prompt_tokens}, out {u.completion_tokens} "
            f"(reasoning {u.completion_tokens_details.reasoning_tokens}), {time.time()-t:.1f} s")

def link(i):
    src = (metas[i] or {}).get('source', ids[i])
    return f"[{src}](https://groups.google.com/g/cozy_builders/c/{src})" if re.fullmatch(r'[A-Za-z0-9_-]{11}', src) else src

plain, plain_stats = ask(lf.build_prompt(data, docs))
old = lf.secondary_prompt
lf.secondary_prompt = old.rstrip()[:-5] + INSTRUCTION + ' ----- '
numbered, num_stats = ask(lf.build_prompt(data, [f"[{i}] {d}" for i, d in enumerate(docs, 1)]))
lf.secondary_prompt = old
cited = sorted({int(x) for g in re.findall(r'\[(\d+(?:\s*,\s*\d+)*)\]', numbered) for x in re.split(r'\s*,\s*', g)})
bad = [x for x in cited if x < 1 or x > n]
json.dump({'question': QUESTION, 'ids': ids, 'plain': plain, 'numbered': numbered},
          open(os.path.join(HERE, NAME.replace('.md', '.json')), 'w'), indent=1)
md = [f"# {QUESTION}\n", f"{MODEL}, {n} chunks retrieved as the site does, the same chunks for both answers.\n",
      f"## Without citations (as the site answers today)\n\n- {plain_stats}\n", plain,
      f"\n## With citations\n\n- {num_stats}\n- Chunks cited: {cited}" + (f"; **name no chunk: {bad}**" if bad else "") + "\n",
      numbered, "\n## The cited chunks\n"]
for x in cited:
    if x not in bad:
        md += [f"**[{x}]** {link(x-1)}\n", "> " + docs[x-1].replace('\n', '\n> ') + "\n"]
md += ["## Chunks sent and not cited\n", ", ".join(f"[{i}] {link(i-1)}" for i in range(1, n+1) if i not in cited) or "none"]
open(os.path.join(HERE, NAME), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
print('chunks', n, 'cited', cited, 'bad', bad); print('plain:', plain_stats); print('numbered:', num_stats); print(ids)
