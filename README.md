# ml_news_rag
Python based RAG implementation for expert system based on newgroup corpus




### Procedure to Update Tool/website

The yearly update, in this order. Each part has its own "Yearly Update" section with every
command, what to expect and what to do when it goes wrong; start there, not here. Written
2026-11-24 after the update of 2026.

 1. **Fetch the year's messages** (Windows cmd and WSL): `msgGetter/README.md`, steps 1 to 9.
    Needs Chrome, ChromeDriver and a sign-in to Google Groups. Ends with new `.md` files in
    `data/msgs_md` and `.txt` files in `data/msgs`, and `data/refetch_ids.txt`.
 1. **Other sites** (`webGetter`): not run in 2026 (every file in `data/aeroelectric`,
    `data/news` and `data/cozybuilders` is from 2025-10-08), and there are no step-by-step instructions for it. Skip unless there is
    a reason; if there is, it needs instructions written first.
 1. **The pictures** (Windows cmd and WSL): `imageGetter/README.md`, steps 1 to 8. Needs the
    `.md` files of step 1. Includes your review of the new pictures.
 1. **The embedding** (WSL): `embedder/README.md`, steps 1 to 5. Needs the `.txt` files of
    step 1. Can be done before or after the pictures.
 1. **The deploy**, after both are checked locally. Each part changes the site on its own, so
    they can be done on different days:
    - the collection: `embedder/README.md`, steps 6 to 8 (stops the site for a minute);
    - the pictures: `imageGetter/README.md`, step 9;
    - a change of the site's code, if there is one: `README.md` of `site_2024`, "Deploy a
      change of the code". If it is on the same day as the collection, replace the
      collection while the containers are stopped for the code.
 1. **Clean up** after a few days of the site running well: `embedder/README.md` step 9,
    `imageGetter/README.md` step 9e, and the image tag of a code deploy (`site_2024`).

Server work is done over ssh as `admin`, in `~/site_2024`; files go up with `scp`. Run the
server blocks one at a time and read the output before the next.

### TODO NOTES

 - convert existing dokucozy to docker image
    - copy dokucozy data
    - install docker
    - install docuwiki docker
    - install dokucozy data
- add front end to server to send to separate dockers
    - dokucozy
    - DokuN657cz
    - TkBlog
    - CozyRAG
     - msg search
        - index
        - chromaDB
     - CozyChat

