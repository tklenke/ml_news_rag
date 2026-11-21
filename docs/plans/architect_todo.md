# Architect Todo - Image Database Project

**Last Updated:** 2025-11-06

---

# ACTIVE WORKSTREAM: Annual RAG/Website Refresh (started 2026-11-21)

**Status:** Plan written: `annual_refresh_plan.md`. Tom's decisions recorded there and in
`required_from_tom.md`. Phase 1 (model migration, deadline 2027-01-14) is ready for Programmer.

## Goal (from Tom)

Annual refresh of the RAG system + website; image database later. Focus areas:
1. **Retrieval mechanism** — "cludgy but works," probably leave as-is.
2. **RAG ingestion** — reconsider chunk size (currently 250 words, no overlap).
3. **Model + results** — OpenAI is sunsetting the model in use; must choose a replacement.
4. **Website** — refresh.
5. **Stretch:** add a link on the results page to a dynamic page showing all images
   from the messages that "made the RAG cut." (Ties back to image database.)

## Key Architecture Findings (from code investigation)

**The refresh spans TWO repositories:**

| Concern | Lives in | Current state |
|---|---|---|
| RAG ingestion (chunk + embed) | `ml/embedder/` (this repo) | `nomic-embed-text`; **chunk = 250 words, NO overlap** (`CHUNKSIZE=250` in `embedder.py`, split logic in `f_embed.py:chunksplitter`); doc prefix `search_document:` |
| Retrieval + LLM + results page | `../site_2024/fwww/` (SEPARATE git repo) | Flask job-queue; **two-stage LLM: draft=`gpt-4o-mini` → revise=`gpt-4.1`** (`fwww/src/llm_functions.py`) |
| Model experimentation | `ml/asker/`, `ml/modelTesting/` | throwaway harnesses (`ask_models.py`, `ask_chatgpt.py`, `askQuestions.py`) |
| Image database | `ml/imageGetter/` | Phase 6 done; revisit later |

**Live production RAG config** (`../site_2024/fwww/site.ini`):
- `EMBED = nomic-embed-text`, `PREFIX = search_query:` (asymmetric prefix is CORRECT — no bug)
- `LLM_DRAFT = gpt-4o-mini`, `LLM_REVISE = gpt-4.1` (both OpenAI → sunset exposure)
- `MAX_DISTANCE = .35`, `MIN_DOCUMENTS = 5`, `MAX_DOCUMENTS = 60`, `MAX_DRAFT_DOCUMENTS = 15`
- `USE_GPT = True`, `SHOW_REVISE = True`

**Observations shaping the plan:**
- Retrieval is fine. Only cludgy bit: `get_num_draft_docs()` in `llm_functions.py` (scans
  backward for last doc under threshold). Works; low priority.
- **Image-gallery stretch feature is very feasible.** Results page (`fwww/templates/cozyrag_results.html`)
  already renders each doc's `source` (= Google Groups message ID) via `originid_anchor`.
  The image DB (`imageGetter/`) is keyed by the SAME message IDs → direct join.
- **Chunk-size change = full corpus re-embed** (data/msgs, news, aeroelectric, cozybuilders).
  Only worth it if it measurably improves retrieval → wants an experiment, not a guess.
- Note: `ml/asker/` harnesses query the `all-minilm` collection, but production + embedder use
  `nomic-embed-text`. The asker/ scripts are stale test harnesses, NOT the production path.

**NOTE FROM PROGRAMMER (2026-11-21):** Tom decided the two DokuWiki sites
(`/dokucozy/`, `/dokuN657CZ/`) are removed in this refresh because they are not used.
This changes plan Phase 3: S7 (deny `data/`, `conf/`, `bin/`, `inc/`) becomes removal,
and the `php:7-fpm` end-of-life item in `opportunities_for_improvement.md` goes away with it.
Removal touches the nginx `location` blocks, the `php1`/`php2` services and the
`./data/dokucozy`, `./data/dokuN657CZ` volume mounts in `site_2024/docker-compose.yaml`.
Architect should decide where it is scheduled and whether the wiki data is archived
before removal. Production nginx details are recorded in `required_from_tom.md`.

## NOTES FROM PROGRAMMER SESSION 2026-11-21: decisions needed from Architect

**NOTE FROM PROGRAMMER (2026-11-21):** Programmer started Phase 1, asked Tom the four
up-front questions, and stopped at task 1.0 because the `site_2024` test environment
cannot match production. Tom asked that everything be written down here so Architect
can make the call and update the plan. No code has been changed in `site_2024`. A branch
`wip/annual-refresh` exists there with no commits on it yet.

### A. Decision needed: dependency and runtime refresh (Tom's request)

**Tom's request (verbatim):** "I think we need to update the server to be python 3.13
and the latest version of chromadb don't you? that needs to be in the plan. or if there
is even a more uptodate version of both we should be refreshing all to the current most
stable versions. agree?"

**What blocked task 1.0:** local dev cannot reproduce production.

| | Production (`flask.dockerfile`, `requirements.txt`, `docker-compose.yaml`) | Local `site_2024/venv/` |
|---|---|---|
| Python | `python:3.11-slim` | 3.13.5 (`/usr/bin/python3.13`) |
| chromadb client | 1.1.1 (pinned) | 0.5.18 |
| Chroma server | `chromadb/chroma:1.1.1` | n/a |
| onnxruntime | 1.19.2 (pinned) | `pip install --dry-run -r requirements.txt` fails: no 1.19.2 build for Python 3.13 (earliest available is 1.20.0) |
| openai | 1.51.2 | 1.51.2 |

- Debian 13 (trixie) on Tom's WSL has only Python 3.13; there is no `python3.11` package.
- Docker is not enabled in this WSL distro ("activate the WSL integration in Docker Desktop").
- Importing `src.llm_functions` in the local venv works but prints an onnxruntime
  warning to stderr (`GPU device discovery failed ... /sys/class/drm/card0/device/vendor`),
  which would break pristine test output.
- Why it matters for 1.1b: the suspected prior-context defect depends on what
  `collection.get()` returns in the chromadb version production runs. A test against
  0.5.18 or a hand-built dict tests an assumption, not production.

Programmer's three options before Tom's request (now likely superseded): install `uv` and
build a Python 3.11 venv from `requirements.txt`; enable Docker and test in the flask
image; or add pytest to the 3.13 venv and accept the version gap.

**Latest versions on PyPI (checked 2026-11-21 with `pip index versions`):**

| Package | Pinned | Latest |
|---|---|---|
| chromadb | 1.1.1 | 1.5.9 |
| openai | 1.51.2 | 3.57.0 |
| flask | 3.0.3 | 3.1.3 |
| ollama | 0.3.3 | 0.6.3 |
| onnxruntime | 1.19.2 | 1.32.0 |
| gunicorn | 23.0.0 | 27.0.1 |
| markdown | 3.7 | 3.11.3 |

**Programmer's opinion, given to Tom (Tom wants Architect to decide):**

- Agree with refreshing, scoped and sequenced.
- The OpenAI SDK is two major versions behind and is likely forced by the gpt-6
  models anyway (plan 1.3 already suspects this). The call shape may change.
- Do the refresh before task 1.0 so tests and the harness are built once, on the stack
  production will run, and dev, tests and production match.
- Chroma is the risky part: client (`requirements.txt`) and server image
  (`chromadb/chroma:1.1.1`) must move together. Back up `./data/chroma` first; check
  release notes for storage migrations. A forced re-embed would cost hours and collide
  with the deadline. Upgrading before Phase 2 suits Phase 2, which builds new
  collections anyway.
- Python 3.13 rather than 3.14: 3.13 is what Debian trixie ships on Tom's machine, so
  dev and production match with no extra tooling; supported to 2029. 3.14 is defensible.
- Do not upgrade all ~100 frozen pins individually. `requirements.txt` is a `pip freeze`
  of mostly transitive packages. Proposed: list direct dependencies (Flask, gunicorn,
  chromadb, openai, ollama, Markdown, Flask-Markdown, python-dotenv), let pip resolve,
  then freeze. Test-only packages (pytest) kept out of the production image.
- Pin images: `nginx:latest` is unpinned (also in `opportunities_for_improvement.md`);
  check `ollama.dockerfile`. `php:7-fpm` goes with the DokuWiki removal (section B).
- Deadline protection: Phase 1 must deploy by about 2026-12-31 for the plan's two weeks
  of margin. Plan needs a fallback, e.g. if the Chroma upgrade goes badly, ship the
  model switch on the old Chroma with only the OpenAI SDK upgraded.
- Proposed order: Python 3.13 + refreshed requirements and images, then Chroma upgrade
  with backup, then 1.0 (tests), then 1.1 onward. The local test env becomes a plain
  3.13 venv.

**Architect to decide:** scope, target versions, order, fallback, and the new tasks in
`programmer_todo.md`. Programmer will not start 1.0 until this is in the plan.

### B. Decision needed: DokuWiki removal (Tom, 2026-11-21)

Tom: "we are going to remove dokuwiki sites in this refresh as they are not being used."

- Replaces S7. `programmer_todo.md` marks S7 on hold pending this.
- Touches: the `/dokucozy/` and `/dokuN657CZ/` nginx `location` blocks; `php1` and
  `php2` services in `docker-compose.yaml`; `nginx` `depends_on: php1, php2`; volume
  mounts `./data/dokucozy` and `./data/dokuN657CZ`; README mentions "docuwiki (2x)".
- Removes the `php:7-fpm` end-of-life item from `opportunities_for_improvement.md`.
- Architect to decide: schedule (could ride with the dependency refresh, since both
  change `docker-compose.yaml`), and whether the wiki data is archived before removal.

### C. Decision needed: how production config changes are delivered

Facts from Tom's server output (verbatim outputs in section E):

- The server runs from a git checkout, `~/site_2024`, on `main`. `git status` says "up to
  date with 'origin/main'", but that ref is stale: the server's HEAD is `906ffd8`
  (2025-10-11). Determined by matching blob hashes in the `git diff` index lines to
  local history. The server has never pulled `63cca77`, `4dac70f`, `d940956`, `42db312`,
  `4e2f8d5`; Tom appears to edit on the server and copy files back to commit locally.
- **Production code matches the repo.** The server's edited `README.md` (`6aa2692`),
  `fwww/site_app.py` (`6cf73b1`) and `fwww/src/llm_functions.py` (`dc4f4ee`) are
  byte-identical to the repo's current `main`. So the site review findings S1 to S6,
  written from the repo code, apply to production.
- **Deployment config differs:**
  - `server/nginx_all_apps.conf`: production has the certbot, HTTP-to-HTTPS redirect
    and HTTPS server blocks uncommented; the repo has them commented out. `/cgimages/`:
    production uses `root /var/www/; index index.html index.htm; try_files $uri $uri/ =404;`;
    the repo uses `alias /home/admin/www/cgimages/;` and `try_files $uri $uri/ /cgimages/index.html;`.
  - `docker-compose.yaml`: production mounts `/home/admin/www/cgimages:/var/www/cgimages/:ro`
    (absolute); the repo (`42db312`) mounts `./home/admin/www/cgimages` (relative).
    Production looks correct; the repo copy looks stale.
- Untracked on the server: `exclude_from_tar.txt`, `fwww/static/test_08_fixture/`,
  `server/old.nginx_all_apps.conf`, `sudo_renew_cert.sh`. Not yet seen by Programmer.
- Unknown: whether the repo's commented-out HTTPS is deliberate for running locally
  (Tom has not said; Docker is not enabled on his WSL, so possibly no local runs).
- Programmer's suggestion (not agreed): commit the production nginx and compose config
  to the repo so it matches the server, then deliver changes by `git pull` on the server
  plus an nginx reload or container restart. First pull needs care: the server's five
  modified files would conflict, so they must be discarded (they match or are superseded
  by the repo once production config is committed).
- Needed for S2b (`limit_req`), the DokuWiki removal and the dependency refresh deploy.
- Housekeeping: Tom's `git diff` on the server was suspended (`[1]+ Stopped git diff`).
  Harmless; `fg` then `q`, or `kill %1`.

### D. Other things Programmer noticed

- `docker-compose.yaml` publishes `"8001:8001"` (flask) and `"8000:8000"` (chroma) on the
  host. The site review found both unreachable from outside, presumably because of the
  Lightsail firewall. If that firewall is ever opened, they are exposed; binding to
  `127.0.0.1` or dropping the mappings would remove the dependency. Architect's call.
- The stale `__main__` block in `llm_functions.py` also calls `set_docs_params` with three
  arguments (no `MAX_DRAFT_DOCUMENTS`), in addition to passing a string to
  `process_question` (task 1.1e).
- `ml/` has no `requirements.txt`, though CLAUDE.md and the role files tell every session
  to read it. Doc fix or file to create.
- Tom's other answers are recorded in `required_from_tom.md`: spend cap is on;
  `.env_flask` only ever held `put-your-openai-key-here` (server copy and full git history
  checked), nothing to revoke; model access "we will need to test into that. probably
  not, but I can change as we determine", i.e. find out with the 1.2 smoke calls.

### E. Tom's outputs (verbatim, 2026-11-21)

**Production nginx config** (`cat nginx_all_apps.conf` on the server):

```
admin@ip-172-26-15-73:~/site_2024/server$ cat nginx_all_apps.conf
events {}

http {
    # HTTP server block to redirect all traffic to HTTPS, except Certbot
    server {
        listen 80;
        server_name localhost m24tom.com www.m24tom.com;
        server_tokens off;

    #     # Allow Certbot challenge requests to go through without redirection
         location /.well-known/acme-challenge/ {
             root /var/www/certbot;
         }

    #     # Redirect all other HTTP traffic to HTTPS
         location / {
             return 301 https://$host$request_uri;
         }
     }

    # # HTTPS server block
     server {
         listen 443 ssl;
         server_name localhost m24tom.com www.m24tom.com;

         ssl_certificate /var/www/ssl/fullchain.pem;
         ssl_certificate_key /var/www/ssl/privkey.pem;
          #note that symlinks will not work so need to make sure that
          #after ssl certificate upgrade the actual .pem files are copied into this directory

        # Proxy all traffic to the Flask app
        location / {
            proxy_pass http://flask:8001/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Dokucozy app configuration
        location /dokucozy/ {
            root /var/www/;
            index index.php index.html index.htm;

            location ~ \.php$ {
                try_files $uri =404;
                fastcgi_split_path_info ^(.+\.php)(/.+)$;
                fastcgi_pass php1:9000;
                fastcgi_index index.php;
                include fastcgi_params;
                fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
                fastcgi_param PATH_INFO $fastcgi_path_info;
            }
        }

        # DokuN675CZ configuration
        location /dokuN657CZ/ {
            root /var/www/;
            index index.php index.html index.htm;

            location ~ \.php$ {
                try_files $uri =404;
                fastcgi_split_path_info ^(.+\.php)(/.+)$;
                fastcgi_pass php2:9000;
                fastcgi_index index.php;
                include fastcgi_params;
                fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
                fastcgi_param PATH_INFO $fastcgi_path_info;
            }
        }

        #static content for cgimages
        location /cgimages/ {
            root /var/www/;
            index index.html index.htm;
            try_files $uri $uri/ =404;
        }

    }
}
admin@ip-172-26-15-73:~/site_2024/server$
```

**`.env_flask` on the server:**

```
admin@ip-172-26-15-73:~/site_2024$ cat .env_flask

OPENAI_KEY=put-your-openai-key-here
#Then Rename file as .env_openai_keyadmin@ip-172-26-15-73:~/site_2024$
```

**`git status` on the server:**

```
admin@ip-172-26-15-73:~/site_2024$ git status
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   README.md
        modified:   docker-compose.yaml
        modified:   fwww/site_app.py
        modified:   fwww/src/llm_functions.py
        modified:   server/nginx_all_apps.conf

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        exclude_from_tar.txt
        fwww/static/test_08_fixture/
        server/old.nginx_all_apps.conf
        sudo_renew_cert.sh

no changes added to commit (use "git add" and/or "git commit -a")
admin@ip-172-26-15-73:~/site_2024$
```

**`git diff` on the server:**

```
admin@ip-172-26-15-73:~/site_2024$ git diff
diff --git a/README.md b/README.md
index 4c95c1c..6aa2692 100644
--- a/README.md
+++ b/README.md
@@ -13,6 +13,9 @@ Website 2024 revision.  Docker based.  Nginx, flask, docuwiki (2x) and supportin
   + replace fullchain.pem and privkey.pm symlinks with the actual files fullchain1.pem and privkey1.pm
   copied over from the current archive

+# Make new tar file
+tar -czf ../project.tar.gz -X exclude_from_tar.txt ~/project/site_2024
+

 ### Todo

diff --git a/docker-compose.yaml b/docker-compose.yaml
index fa9ce08..4dfb441 100644
--- a/docker-compose.yaml
+++ b/docker-compose.yaml
@@ -13,6 +13,7 @@ services:
       - ./data/dokuN657CZ:/var/www/dokuN657CZ
       - ./server/certbot/www/:/var/www/certbot/:ro
       - ./server/certbot/conf/live/m24tom.com/:/var/www/ssl/:ro
+      - /home/admin/www/cgimages:/var/www/cgimages/:ro
       #note that symlinks will not work so need to make sure that
       #after ssl certificate upgrade the actual .pem files are copied into this directory
     depends_on:
diff --git a/fwww/site_app.py b/fwww/site_app.py
index 326ecad..6cf73b1 100644
--- a/fwww/site_app.py
+++ b/fwww/site_app.py
@@ -30,7 +30,8 @@ FPThread = FileProcessorThread(cfg.get('PATHS','JOBS_DiR'), FPQueue, cfg.getbool
                                cfg.get('KEYS','OPENAI'), cfg.get('HOSTS','CHROMA'), cfg.get('HOSTS','OLLAMA'))
 FPThread.set_models(cfg.get('MODELS','EMBED'), cfg.get('MODELS','LLM_DRAFT'), cfg.get('MODELS','LLM_REVISE'))
 FPThread.set_prompts(cfg.get('PROMPTS','PREFIX'), cfg.get('PROMPTS','INITIAL'), cfg.get('PROMPTS','SECONDARY'))
-FPThread.set_docs_params(cfg.getfloat('RAG','MAX_DISTANCE'), cfg.getint('RAG','MIN_DOCUMENTS'), cfg.getint('RAG','MAX_DOCUMENTS'))
+FPThread.set_docs_params(cfg.getfloat('RAG','MAX_DISTANCE'), cfg.getint('RAG','MIN_DOCUMENTS'), \
+                         cfg.getint('RAG','MAX_DOCUMENTS'), cfg.getint('RAG','MAX_DRAFT_DOCUMENTS'),)

 FPQueue.put("startup...checking all jobs")
 Md = markdown.Markdown()
diff --git a/fwww/src/llm_functions.py b/fwww/src/llm_functions.py
index 56cd554..dc4f4ee 100644
--- a/fwww/src/llm_functions.py
+++ b/fwww/src/llm_functions.py
@@ -13,10 +13,10 @@ initial_prompt = ""
 secondary_prompt =""" Use the following pieces of context to answer the users question. -----"""
 secondary_prompt =""" Be concise, precise and accurate. If the answer is not within the context provided
 say so. Use the following pieces of context to answer the users question. ----- """
-secondary_prompt =""" Use the following pieces of context to answer the users question. ----- """
+secondary_prompt =""" Use the following pieces of context to answer the users question about a Cozy amatuer-build aircraft. ----- """

 revise_prompt="""You are the refinement model.
-Review the user's question, the draft response from GPT-4o-mini and the retrieved context.
+Review the user's question about a Cozy amatuer-build aircraft, the draft response from GPT-4o-mini and the retrieved context.
 Your task is to verify factual accuracy, add missing technical detail, and correct any mistakes.
 Cite or reference relevant context when useful.
 If the draft is already correct, restate it concisely.
@@ -31,12 +31,25 @@ and previous content as context.

 #------------FUNCTIONS---------------
 # find the index of the most irrelevant response within the defined thresholds
-def get_min_relevant_response(results,fMaxDistance,nMinDocs):
-    r = nMinDocs
-    for i in range(nMinDocs,len(results['distances'][0])):
-        if (results['distances'][0][i] < fMaxDistance):
-            r = i
-    return r
+def get_num_draft_docs(results, fMaxDistance, nMinDocs, nMaxDraftDocs):
+    distances = results['distances'][0]
+
+    # 2. Determine the upper bound for slicing.
+    n_limit = min(len(distances), nMaxDraftDocs)
+
+    try:
+        # Look for the last index where the condition is met.
+        for i in reversed(range(nMinDocs, n_limit)):
+            if distances[i] < fMaxDistance:
+                return i
+
+        # If no result satisfies the condition, return the starting point
+        return nMinDocs
+
+    except IndexError:
+        # Handle case where results['distances'][0] is empty or too short
+        # (though n_limit and nMinDocs should prevent this if the inputs are valid)
+        return nMinDocs

 def get_prior_doc_ids_from_data(data):
     r = data['result']
@@ -79,6 +92,9 @@ def get_doc_list_from_result(rQuery, nDocsFrom=None, nDocsTo=None):
             # zip() iterates over the three sliced lists in parallel
             for doc_id, distance, metadata in zip(sliced_ids, sliced_distances, sliced_metadatas)
         ]
+        #note this is likely to introduce a difference in the number of docs shown to the user
+        #and what the min and max documents are. As one source document may result in several
+        #chunks.  each chunk is a doc for purposes of counting max / min input to the model.
         r = dedupe_list_of_docs(r)
     else:
         ids = rQuery['ids']
@@ -132,10 +148,11 @@ class FileProcessorThread(threading.Thread):
         self.llm_revise_model = llm_revise
         return

-    def set_docs_params(self, max_distance=.45, min_documents=5, max_documents=20):
+    def set_docs_params(self, max_distance=.45, min_documents=5, max_documents=30, max_draft_documents=15):
         self.max_distance = max_distance
         self.min_documents = min_documents
         self.max_documents = max_documents
+        self.max_draft_documents = max_draft_documents
         return

     def set_prompts(self, prefix="", initial_prompt="", secondary_prompt=" Use the following pieces of context to answer the users question. ----- "):
@@ -158,7 +175,7 @@ class FileProcessorThread(threading.Thread):
         if data['type'] == "new":
             rQuery = self.get_query_results(data['query'])
             #prune related documents
-            nDocs = get_min_relevant_response(rQuery,self.max_distance,self.min_documents)
+            nDocs = get_num_draft_docs(rQuery,self.max_distance,self.min_documents,self.max_draft_documents)
             #construct the prompt
             relateddocs = '\n\n'.join(rQuery['documents'][0][:nDocs])
             prompt = f"{initial_prompt} {data['query']} {secondary_prompt} {relateddocs}"
@@ -183,12 +200,29 @@ class FileProcessorThread(threading.Thread):
     # Optional: specify what data to include (ids are always included)
     #include=["metadatas", "documents"] )
         if self.use_gpt:
+            #set default incase of error
+            r['model'] = modelName
+            r['prompt tokens'] = 0
+            r['completion tokens'] = 0
             #ask the model
-            completion = self.openaiclient.chat.completions.create(model=modelName,messages=[{"role": "user", "content": prompt}])
-            r['answer'] = completion.choices[0].message.content
-            r['model'] = completion.model
-            r['prompt tokens'] = completion.usage.prompt_tokens
-            r['completion tokens'] = completion.usage.completion_tokens
+            try:
+                completion = self.openaiclient.chat.completions.create(model=modelName,messages=[{"role": "user", "content": prompt}])
+                r['answer'] = completion.choices[0].message.content
+                r['model'] = completion.model
+                r['prompt tokens'] = completion.usage.prompt_tokens
+                r['completion tokens'] = completion.usage.completion_tokens
+            except openai.APIError as e:
+                #Handle API error here, e.g. retry or log
+                r['answer'] = f"OpenAI API returned an API Error: {e}"
+                pass
+            except openai.APIConnectionError as e:
+                #Handle connection error here
+                r['answer'] = f"Failed to connect to OpenAI API: {e}"
+                pass
+            except openai.RateLimitError as e:
+                #Handle rate limit error (we recommend using exponential backoff)
+                r['answer'] = f"OpenAI API request exceeded rate limit: {e}"
+                pass
         else:
             #Fake it
             r['answer'] = lorem_ipsum_string
diff --git a/server/nginx_all_apps.conf b/server/nginx_all_apps.conf
index 414172d..382fd3a 100644
--- a/server/nginx_all_apps.conf
+++ b/server/nginx_all_apps.conf
@@ -8,23 +8,23 @@ http {
         server_tokens off;

     #     # Allow Certbot challenge requests to go through without redirection
-    #     location /.well-known/acme-challenge/ {
-    #         root /var/www/certbot;
-    #     }
+         location /.well-known/acme-challenge/ {
+             root /var/www/certbot;
+         }

     #     # Redirect all other HTTP traffic to HTTPS
-    #     location / {
-    #         return 301 https://$host$request_uri;
-    #     }
-    # }
+         location / {
+             return 301 https://$host$request_uri;
+         }
+     }

     # # HTTPS server block
-    # server {
-    #     listen 443 ssl;
-    #     server_name localhost m24tom.com www.m24tom.com;
+     server {
+         listen 443 ssl;
+         server_name localhost m24tom.com www.m24tom.com;

-    #     ssl_certificate /var/www/ssl/fullchain.pem;
-    #     ssl_certificate_key /var/www/ssl/privkey.pem;
+         ssl_certificate /var/www/ssl/fullchain.pem;
+         ssl_certificate_key /var/www/ssl/privkey.pem;
           #note that symlinks will not work so need to make sure that
           #after ssl certificate upgrade the actual .pem files are copied into this directory

@@ -68,5 +68,13 @@ http {
                 fastcgi_param PATH_INFO $fastcgi_path_info;
             }
         }
+
+        #static content for cgimages
+        location /cgimages/ {
+            root /var/www/;
+            index index.html index.htm;
+            try_files $uri $uri/ =404;
+        }
+
     }
 }

[1]+  Stopped                 git diff
admin@ip-172-26-15-73:~/site_2024$
```

## Questions answered by Tom (2026-11-21)

1. **User-requested feature:** reference links to source documents inside the answer text
   (as Gemini does). Nice-to-have; evaluate after the other work.
2. **OpenAI sunset:** all GPT-4 versions. Both production models shut down 2027-01-14.
3. **LLM strategy:** stay with OpenAI; keep cheap first answer plus better "dig deeper" model.
4. **Chunk size:** test it; Architect guides test design and evaluation criteria.

## Completed

- [x] Get answers to the 4 open questions.
- [x] Decide plan-doc location: master plan in `ml/docs/plans/annual_refresh_plan.md`,
      cross-repo tasks noted per phase.
- [x] Write the refresh plan, `required_from_tom.md`, and the Phase 1 / Phase 2 breakdown
      in `programmer_todo.md`.

## NEXT STEPS (resume point)

- [x] Propose a shortlist from https://m24tom.com/cozyrag/jobs for Tom to pick from:
      52 candidates in `refresh_question_candidates.csv` (25 factual, 27 broad; `long_doc`
      marks likely newsletter / Canard Pusher / AeroElectric answers). Built from the 835
      logged jobs: 691 first-answer jobs, 624 after dropping short entries and exact repeats.
- [x] Tom approved all 52. Candidates file renamed to `refresh_questions.csv` with a `use`
      column: three balanced batches of 10, 10 chunk-only, 12 reserve.
- [x] Note for Programmer to get the production nginx config from Tom at the start.
- [ ] Review Programmer's finding on the suspected revise-context defect (plan 1.1).
- [ ] Review Programmer's smoke-call report on the GPT-6 candidates (plan 1.3).
- [x] Scope the website refresh with Tom: reference links and images only (plan Phase 4).
- [x] Review `site_2024` code and live server for serious errors and security concerns;
      findings S1 to S9 in plan Phase 3.
- [x] Add 10 / 20 / 30 checkpoints to the model evaluation (plan 1.5).
- [x] Propose the chunk experiment question set: same 30 plus about 10 new (plan 2.3).
- [x] Get Tom's choice of which S findings to fix; tasks added to `programmer_todo.md`,
      S1 and S2 designs added to the plan.
- [x] Get Tom's confirmation of the chunk experiment question set (mixed).
- [x] Create `docs/notes/opportunities_for_improvement.md` with the job-processing item (S8).
- [ ] Approve the nginx rate Programmer proposes for S2b.
- [ ] Design reference links (plan 4.1) and image gallery (4.2) after Phase 1.

## Findings from the production job log (2026-11-21)

- About 850 logged questions; about 45 carry a rating and roughly 20 of those are `n/a`.
  Rating scale changed over time (awesome/useful/meh, later perfect/ok/not_good).
- Typical first answer: about 4,500 tokens in, 300 out, 5 s on `gpt-4o-mini`.
  Follow-up sampled: about 21,000 tokens in on `gpt-4.1`.
- Answers do not cite sources in their text.
- `site_2024` has no automated tests.

## Housekeeping

- [x] Work moved to branch `wip/annual-refresh`.
- [x] `docs/acronyms.md` and `docs/style-guide.md` named the wrong project (`ea_tools`); corrected
      to `ml_news_rag`. Unused KiCAD acronym (SD) removed, RAG added.
- [x] Untracked debugging snippet `docs/input/compare.html` deleted per Tom.
- [x] `docs/notes/opportunities_for_improvement.md` created with its first item.
- Note: no root `requirements.txt`; dependencies are per-module.

---

## Current Status

**Phase:** Phase 6 (Keyword Scoring) design complete, ready for Programmer implementation

**Documentation:**
- Design: `image_database_design.md` (updated with Phase 6 scoring design)
- Programmer instructions: `programmer_todo.md` (rewritten with 7 detailed implementation tasks)

---

## Completed Tasks

### Phase 6 Design - Keyword Scoring
- [x] Design image-level keyword scoring approach
- [x] Define JSON schema for scored keywords: `[["keyword", score], ...]`
- [x] Document KeywordScorer algorithm (proximity + subject bonus + frequency + length)
- [x] Update image_database_design.md with Phase 6 details
- [x] Write comprehensive programmer_todo.md with TDD instructions
- [x] Plan archival strategy for unused LLM tagger code

---

## Pending Tasks

### Phase 6 Oversight
- [ ] Monitor Programmer implementation progress
- [ ] Review any design questions that arise during implementation
- [ ] Validate scoring algorithm parameters if issues arise
- [ ] Review completed implementation before deployment

### User Testing and Evaluation (Post Phase 6)
- [ ] Review Phase 6 after Tom tests scored static site
  - [ ] Assess if scoring improves image relevance ordering
  - [ ] Determine appropriate score threshold value (currently 0)
  - [ ] Decide if scores should be displayed to users or hidden
  - [ ] Evaluate if 557 keywords provide adequate coverage
- [ ] If issues arise, revise scoring parameters or keyword strategy

---

## Open Questions

1. Is vocabulary size (557 keywords) sufficient for coverage?
2. What score threshold should we use for display filtering? (default: 0, but may want 10-20)
3. Should we display scores to users or keep them invisible for ranking only?
4. Will image-level scoring be accurate enough, or do we need multimodal embeddings?
5. Should we track query analytics to improve keyword list and scoring weights?

---

## Current Risks

1. **Scoring algorithm parameters may need tuning**
   - Mitigation: Designed with configurable threshold, can adjust weights if needed
   - Designed for fast iteration (no LLM dependency)

2. **Image-level scoring may not match user expectations**
   - Mitigation: User testing will validate approach
   - Can fall back to multimodal embeddings if text-based scoring insufficient

---

## Design Decisions Made (Phase 6)

1. **Image-level scoring only** (no message-level keywords)
   - Rationale: Each image in multi-image message needs independent scores

2. **Proximity-based scoring** (exponential decay from image URL)
   - Rationale: Keywords near image are more relevant than distant ones

3. **Integer scores** (rounded from float calculations)
   - Rationale: Reduces JSON file size ~25%, precision loss negligible for ranking

4. **Score threshold parameter** (WAPGNI - probably gonna need it!)
   - Rationale: Allows future noise filtering without code changes

5. **Archive LLM tagger** (not delete)
   - Rationale: Not being used, search-based scoring sufficient and faster

---

## Escalation Protocol

**When Programmer should escalate to Architect:**
- Design ambiguities or conflicts in implementation
- Scoring algorithm parameters causing issues
- Performance problems with scoring
- Test failures suggesting design problems
- Major technical blockers

Use "Strange things are afoot at the Circle K" for immediate attention.

---

**Last Updated:** 2025-11-06 by Claude (Architect)
