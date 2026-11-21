# site_2024 production server state, 2026-11-21

Outputs Tom ran on the production server (`~/site_2024`), verbatim. The nginx config
here is what the repo copy must match (refresh plan, step 2).

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

