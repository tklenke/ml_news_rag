# ABOUTME: One-off probe: asks gpt-6-luna three rated questions with numbered chunks (plan 4.1a wording)
# ABOUTME: and writes the answers beside the cited chunks to probe.md for Tom to read. Not site code.
import json, os, re, sys, time
import chromadb, openai
from src import llm_functions as lf
from src.site_config import read_config

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = '/home/tom/projects/site_2024/fwww'
OUT = '/home/tom/projects/site_2024/evaluation/output'
ARCHIVE = '/home/tom/projects/ml/docs/archive'
MODEL = 'gpt-6-luna'
NAME = sys.argv[1]
QUESTIONS = sys.argv[2:]
INSTRUCTION = ("Each piece of context starts with its number in square brackets. After a statement "
               "that you take from the context, write the number of the piece it comes from in square "
               "brackets, like this: [3]. For more than one piece write [2][5]. Use only the numbers "
               "given. Do not write a list of sources at the end.")

cfg = read_config(SITE)
client = openai.OpenAI(api_key=cfg.get('KEYS', 'OPENAI'))
col = chromadb.HttpClient('localhost', 8000).get_collection('nomic-embed-text')
key = json.load(open(os.path.join(OUT, 'key.json')))
ratings = json.load(open(os.path.join(OUT, 'ratings.json')))

def source_link(meta, doc_id):
    src = (meta or {}).get('source', doc_id)
    if re.fullmatch(r'[A-Za-z0-9_-]{11}', src):
        return f"[{src}](https://groups.google.com/g/cozy_builders/c/{src})"
    return src

md = [f"# Citation probe: {MODEL}, numbered chunks\n",
      "Wording added to the prompt (plan 4.1a):\n", f"> {INSTRUCTION}\n"]
for q in QUESTIONS:
    saved = json.load(open(os.path.join(OUT, 'prompts', f'{q}.json')))
    docs = lf.get_docs_in_order(col, saved['ids'])
    data = {'type': 'new', 'query': saved['question']}
    same = lf.build_prompt(data, docs['documents']) == saved['prompt']
    numbered = [f"[{i}] {d}" for i, d in enumerate(docs['documents'], 1)]
    old = lf.secondary_prompt
    assert old.rstrip().endswith('-----')
    lf.secondary_prompt = old.rstrip()[:-5] + INSTRUCTION + ' ----- '
    prompt = lf.build_prompt(data, numbered)
    lf.secondary_prompt = old
    t = time.time()
    c = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
    secs = time.time() - t
    answer = c.choices[0].message.content or ''
    json.dump({'question_id': q, 'ids': docs['ids'], 'prompt': prompt, 'answer': answer,
               'model': c.model, 'usage': c.usage.model_dump()},
              open(os.path.join(HERE, f'{q}.json'), 'w'), indent=1)
    cited = sorted({int(n) for grp in re.findall(r'\[(\d+(?:\s*,\s*\d+)*)\]', answer)
                    for n in re.split(r'\s*,\s*', grp)})
    n = len(docs['ids'])
    bad = [x for x in cited if x < 1 or x > n]
    md += [f"\n---\n\n## {q}: {saved['question']}\n",
           f"- Chunks sent: {n}. Same chunks as the rated answer: {'yes' if same else 'NO'}.",
           f"- Numbers written name chunks: {[x for x in cited if x not in bad]}"
           + (f"; **numbers that name no chunk: {bad}**" if bad else "") ,
           f"- Tokens in {c.usage.prompt_tokens}, out {c.usage.completion_tokens}, {secs:.1f} s, model {c.model}\n",
           "### Answer with numbers\n", answer, "\n### The cited chunks\n"]
    for x in cited:
        if x in bad: continue
        md += [f"**[{x}]** {source_link(docs['metadatas'][x-1], docs['ids'][x-1])}\n",
               "> " + docs['documents'][x-1].replace('\n', '\n> ') + "\n"]
    md += ["### Chunks sent and not cited\n"]
    md += [", ".join(f"[{i}] {source_link(docs['metadatas'][i-1], docs['ids'][i-1])}"
                     for i in range(1, n+1) if i not in cited) or "none", ""]
    letter = next((k for k, v in key.get(q, {}).items() if v == MODEL), None)
    r = ratings.get(q, {}).get(letter, {})
    md += [f"### For comparison: the {MODEL} answer you rated on 2026-11-22 "
           f"({r.get('rating', 'rating not found')}"
           f"{', factual error' if r.get('factual_error') else ''}"
           f"{': ' + r['note'] if r.get('note') else ''})\n"]
    p = os.path.join(ARCHIVE, 'gpt6_luna_candidate_answers', f'{q}.md')
    md += [open(p, encoding='utf-8').read() if os.path.exists(p) else '(not found)']
    print(q, 'same chunks:', same, 'cited:', cited, 'bad:', bad, 'tokens', c.usage.prompt_tokens, c.usage.completion_tokens)
open(os.path.join(HERE, NAME), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
