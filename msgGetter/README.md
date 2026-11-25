<!-- ABOUTME: How to fetch the year's new Cozy Builders threads from Google Groups into data/ -->
<!-- ABOUTME: The yearly steps come first; background notes from 2024 and 2025 are at the end -->

# msgGetter: Message Thread Getter

## Yearly Update

Written 2026-11-24 for the next run, about a year later. Read it from the top; every step
says where it is run, what to type, what you should see and what to do if you do not.

### What this step is for

It fetches every Google Groups thread of the Cozy Builders list started or answered since the
last run, and saves each thread twice:

| File | What it is | Read later by |
|---|---|---|
| `data/msgids_<start>_<end>.txt` | the ids of the threads found, one per line | this step, to know what to fetch |
| `data/msgs_md/<letter>/<id>.md` | the thread as markdown, with picture links | `imageGetter` (the pictures) |
| `data/msgs/<letter>/<id>.txt` | the same text, filtered for embedding | `embedder` (the site's answers) |

`<letter>` is the first letter of the id in capitals, or `aDigits` when the id starts with a
digit, `-` or `_`. Everything is under `/home/tom/projects/ml/data` in WSL. Windows sees the
same folder as `\\wsl.localhost\Debian\home\tom\projects\ml\data`.

In 2026 (for scale): 237 thread ids, of which 227 were new threads and 10 were older threads
with new replies (see step 5).

### How it runs

The fetch drives your own Chrome through Selenium, signed in to Google Groups, so it runs on
**Windows**, with the **Windows Python**, from a **Command Prompt** (cmd). It runs in the WSL
folder, so the files land straight in WSL; cmd cannot `cd` into a `\\wsl.localhost\...` path,
but `pushd` can: it maps the folder to a drive letter (in 2026 `Z:`).

Steps 1 to 3, 6 and 7 are in cmd. Steps 4, 5 and 8 to 10 are in a WSL terminal. A WSL terminal
must be open the whole time, so that Windows can reach the WSL files.

### Before you start: what has to be installed (Windows)

**A. Python and its packages.** In cmd:

```
python --version
python -c "import selenium, bs4, markdownify; print('ok')"
```

- Expect `Python 3.13.7` (2026; a later 3.x is fine) and `ok`.
- If an import fails: `python -m pip install selenium beautifulsoup4 markdownify`, then the
  check again. (2026 versions: selenium 4.36.0, beautifulsoup4 4.14.2, markdownify 1.2.0.)

**B. Chrome and ChromeDriver, same version.** ChromeDriver is the program Selenium uses to
drive Chrome. Its major version (the first number) must equal Chrome's.

1. Chrome's version: open Chrome, go to `chrome://settings/help`. In 2026: `158.0.8127.37`.
   Let Chrome update first if it offers to.
2. ChromeDriver's version, in cmd:
   ```
   \\wsl.localhost\Debian\home\tom\projects\chromedriver-win64\chromedriver.exe --version
   ```
   Expect `ChromeDriver 158....` with the same first number as Chrome. If it differs, or the
   file is not found, go on with 3.
3. Download the matching one from https://googlechromelabs.github.io/chrome-for-testing/:
   the "Stable" row, `chromedriver`, `win64`. Unzip it so that the file ends up at
   `\\wsl.localhost\Debian\home\tom\projects\chromedriver-win64\chromedriver.exe`
   (the zip holds a folder `chromedriver-win64`; put that folder in
   `\\wsl.localhost\Debian\home\tom\projects\`, replacing the old one). Then check again (2).

The scripts find ChromeDriver at `..\..\chromedriver-win64\chromedriver.exe`, counted from the
`msgGetter` folder. That is why it lives in `/home/tom/projects/chromedriver-win64` and not in
your Windows Documents. `imageGetter` is told the same path.

### Step 1: start Chrome on the debug port (cmd)

Close **every** Chrome window first (also in the system tray); otherwise the new Chrome joins
the running one and the port does not open. Then open a cmd window:

```
pushd \\wsl.localhost\Debian\home\tom\projects\ml
chrome_with_debug.bat
```

- `chrome_with_debug.bat` is at the top of the repo because `imageGetter` uses it too.
- After `pushd` the prompt is a drive letter, like `Z:\home\tom\projects\ml>`.
- Chrome opens with its own profile, `C:\selenum\ChromeProfile` (Chrome does not open the
  debug port on your normal profile). The cmd window may stay busy while Chrome runs. Leave it.
- In that Chrome, open https://groups.google.com/g/cozy_builders and check you are signed in
  (your picture top right). If not, sign in. The profile remembers it for next time.

Run 2026-11-24 exactly like this.

### Step 2: check that the port is open (cmd, a second window)

```
curl http://127.0.0.1:9222/json/version
```

- Expect a few lines of JSON starting with `"Browser": "Chrome/158...`.
- If curl cannot connect, the port is not open: close all Chrome windows and do step 1 again.

Keep this second window for the next steps.

### Step 3: check the start date (cmd)

The search starts at `startDate` in `get_msg_ids.py`. It should be **one day before the end
date of the last run**: the overlap costs nothing (ids already fetched are skipped) and it is
not known whether Google's `after:` search includes its own date.

```
pushd \\wsl.localhost\Debian\home\tom\projects\ml\msgGetter
dir /o:d ..\data\msgids_*.txt
findstr /b startDate get_msg_ids.py
```

- The last file `dir` lists is the newest run. Its name ends with the end date: in 2026,
  `msgids_2025-10-01_2026-11-21.txt`, so the next start date is `2026-11-20`.
- `findstr` shows the date the script will use. In the repo it is `startDate = '2026-11-20'`.
- If they do not agree (the date should be the end date minus one day): `notepad
  get_msg_ids.py`, change the date on that line, save, and run `findstr` again.

`dir` and `findstr` here, and the ChromeDriver check of B.2, were run 2026-11-24.

### Step 4: get the thread ids (cmd)

```
python get_msg_ids.py
```

- It opens the Google Groups search in the debug Chrome and pages through the results. Each
  page prints a line like `Page 12 Wrote 30 DupePages 0 Pause 1.3`.
- It stops after 20 pages in a row that did not move on (the end of the results, or Google
  being slow), or after 600 pages.
- The last lines say `IDs found <n> on <p> pages written to msgids_<start>_<end>.txt`. In 2026
  `n` was 237. How long it took was not written down.

The file is written into `msgGetter`, but the next step reads it from `data`. Move it, by the
name the last line printed:

```
move msgids_2026-11-20_2027-11-25.txt ..\data\
```

(The name above is an example; use yours.) Step 5 counts its lines.

`get_msg_ids.py` was run in 2026 from the old Windows copy of the project, not from the WSL
folder; from the WSL folder it has not been run yet. `process_message.py` (step 6) has been.

### Step 5: set aside the older threads with new replies (WSL)

A thread that already has a `.txt` is skipped by the fetch, so replies of the last year to
an older thread would be missed. In 2026 10 such threads were in the list. Set their files
aside, so that they are fetched again. In a WSL terminal:

```
cd ~/projects/ml
NEW=$(ls -t data/msgids_*.txt | head -1); echo $NEW
wc -l < $NEW
venv/bin/python - $NEW <<'EOF' > data/refetch_ids.txt
import os, sys
for i in sorted({l.strip() for l in open(sys.argv[1]) if l.strip()}):
    d = i[0].upper() if i[0].isalpha() else 'aDigits'
    if os.path.exists(f'data/msgs/{d}/{i}.txt'):
        print(i)
EOF
wc -l < data/refetch_ids.txt
```

- `echo` must show the file you moved in step 4. If not, stop.
- The first number is the ids in it: the `n` of step 4 (2026: 237).
- The last line is the number of older threads in the list (2026: 10).

Then move their files aside:

```
B=data/refetch_backup; mkdir -p $B/msgs $B/msgs_md
while read i; do
  d=$(echo ${i:0:1} | tr a-z A-Z); [[ $d == [A-Z] ]] || d=aDigits
  mv -- data/msgs/$d/$i.txt $B/msgs/
  mv -- data/msgs_md/$d/$i.md $B/msgs_md/
done < data/refetch_ids.txt
ls $B/msgs $B/msgs_md | grep -c '\.'
```

- The count is twice the number of threads. Keep `data/refetch_ids.txt`: steps 7 and the
  embedding use it.

Rehearsed 2026-11-24 on a scratch copy. In 2026 itself the same was done by hand in Windows.

### Step 6: fetch the threads (cmd)

In the second cmd window (Chrome still running from step 1):

```
python process_message.py
```

**Keep the debug Chrome on screen, not minimized, until the run ends.** While it is
minimized, "Expand all" does nothing: the posts stay collapsed and the threads are not saved
(seen 2026-11-25). Whether a window that is only covered by others works was not tried.

- First lines: `reading ids from ...` for each id file, then `Ids:`, `Msgs already
  filtered:` and `Net to complete: <k>`. `k` is the new threads plus the ones set aside.
- Then `fetching id: <id>` for each, in random order, and every 5 a `Progress` line. Chrome
  shows each thread as it is read.
- A thread that still shows a collapsed post 15 s after the click is not saved:
  `Id <id> has <n> collapsed posts, not saved`. The run goes on.
- The end: `----STATS-----`, `Msgs Processed: <k>` and `Not saved, a post still collapsed:
  <n>` with their ids. If `n` is not 0, check Chrome is on screen and run step 6 again:
  a thread without a `.txt` is fetched again.
- About 7.5 s a thread (one thread, 2026-11-24): about half an hour for 237.
- It can be stopped (Ctrl+C) and run again: a thread with a `.txt` is skipped, so it goes on
  with what is left. An error in one thread stops the whole run (read from the code, not
  seen); run it again.

Close the debug Chrome when it is done.

### Step 7: keep the longer copy of each refetched thread (WSL)

If a thread came back shorter than the copy set aside (posts missing), the old copy is kept.

```
cd ~/projects/ml
B=data/refetch_backup
while read i; do
  d=$(echo ${i:0:1} | tr a-z A-Z); [[ $d == [A-Z] ]] || d=aDigits
  o=$(stat -c %s -- $B/msgs_md/$i.md); n=$(stat -c %s -- data/msgs_md/$d/$i.md)
  if [ $n -lt $o ]; then
    echo "$i shorter ($n < $o): the old copy is put back"
    mv -f -- $B/msgs_md/$i.md data/msgs_md/$d/; mv -f -- $B/msgs/$i.txt data/msgs/$d/
  else echo "$i kept ($n >= $o)"; fi
done < data/refetch_ids.txt
```

- One line per thread. In 2026, 8 of 10 had new posts and 2 came back the same.
- A thread put back has no new posts to embed; the embedding treats it like the others.
- `data/refetch_backup` can be deleted once the year's update is deployed.

Rehearsed 2026-11-24 on a scratch copy.

### Step 8: check the result (WSL)

**Every id has its two files:**

```
cd ~/projects/ml
NEW=$(ls -t data/msgids_*.txt | head -1)
while read i; do
  d=$(echo ${i:0:1} | tr a-z A-Z); [[ $d == [A-Z] ]] || d=aDigits
  [ -f "data/msgs/$d/$i.txt" ] && [ -f "data/msgs_md/$d/$i.md" ] || echo "missing: $i"
done < <(tr -d '\r' < $NEW)
echo checked
```

Expect only `checked`. A missing one: run step 6 again.

**No post saved collapsed.** The fetch saves no thread with a collapsed post (Google's
one-line preview, cut off), but files from before 2026-11-25 can have them. This lists the
threads of `data/msgs_md` that have one:

```
venv/bin/python msgGetter/f_collapsed.py
```

- Expect only `0 threads with a collapsed post`. Before the refetch of 2026-11 it was 33.
- A thread listed: set its two files aside and fetch it again the way of step 5, putting its
  id in `data/refetch_ids.txt`, with Chrome on screen.

**Look at two or three new threads** by eye, in `\\wsl.localhost\Debian\home\tom\projects\ml\data\msgs_md`.
A good one starts with `[Original Message ID:<id>](https://groups.google.com/g/cozy_builders/c/<id>)`,
then `# <subject>`, then for each post `### <name>` and a line beginning with `<address>`,
the date and the post's text.

**Your own posts.** Google shows extra buttons on posts of the signed-in user. Until 2026 the
filter did not know their text, and the `.txt` held "Reply to author You cannot reply
privately to your own message Forward Delete Copy link Report message You cannot report your
own message Show". The filter removes it now. If a `.txt` of one of your own posts holds
button text of another wording, the filter needs a new pattern (`f_filter.py`, with a test in
`tests/test_f_filter.py`): that is a code change.

### Step 9 (only if the filter changed): make the `.txt` again from the `.md` (WSL)

The `.txt` files can be made again from the `.md` without Chrome. For the threads listed in
a file of ids, one per line (here this year's id file):

```
cd ~/projects/ml/msgGetter
NEW=$(ls -t ../data/msgids_*.txt | head -1); echo $NEW
../venv/bin/python - $NEW <<'EOF'
import sys
from f_filter import filter_markdown
n = 0
for i in [l.strip() for l in open(sys.argv[1]) if l.strip()]:
    d = i[0].upper() if i[0].isalpha() else 'aDigits'
    md = open(f'../data/msgs_md/{d}/{i}.md', encoding='utf-8').read()
    with open(f'../data/msgs/{d}/{i}.txt', 'w', encoding='utf-8') as f:
        f.write(filter_markdown(md))
    n += 1
print(n, 'text files written')
EOF
```

Expect the number of ids. On 2026-11-24 the filter, run like this over the 237 threads of
2026, gave exactly the `.txt` files already there.

### Step 10: what comes next

Back to the top-level `README.md`: the pictures (`imageGetter`), the check of the server's
collection, then the embedding (`embedder`), which needs `data/refetch_ids.txt` from step 5.

### Not part of the yearly run

- `move_txt_files.py` moves every `.txt` out of `data/msgs` into `data/msgs_filtered`. Do not
  run it: the embedder reads `data/msgs`.

### Troubleshooting

Each case says whether it was seen.

- **`pushd` gives an error** (not seen): no WSL terminal is open, or WSL's name is not
  `Debian`. Open a WSL terminal; in cmd, `wsl -l` lists the names.
- **The port does not open** (not seen): a Chrome was still running. Close all of them, check
  in Task Manager that no `chrome.exe` is left, and do step 1 again. curl then says it failed
  to connect to port 9222.
- **ChromeDriver and Chrome versions differ** (not seen in 2026): Selenium stops at the start
  with a "session not created" error that names both versions. Do B.3.
- **ChromeDriver not found** (not seen): the error names the path it tried. Check that the
  file is at `\\wsl.localhost\Debian\home\tom\projects\chromedriver-win64\chromedriver.exe`
  and that you ran the script from the `pushd` folder.
- **Not signed in** (not seen): the threads come back without their posts, or as Google's
  sign-in page. Sign in in the debug Chrome, delete the bad files of this run (their ids are
  in this year's id file), and run step 6 again.
- **Google slows down or blocks the fetch** (not seen): pages stop loading or Chrome shows a
  check. Stop with Ctrl+C, wait an hour, run again; it goes on where it stopped.
- **Threads not saved, a post still collapsed** (seen 2026-11-25 with Chrome minimized):
  the debug Chrome was minimized. Bring it on screen and run step 6 again. See also step 8.

## Background notes (2024 and 2025)

This is the more recent interation than newsGetter.



Decided to push LLM stuff to embedding.  Reason being that message getter needs to be run under the Windows
environment along with Chrome due to use of Selenium.  This would require installing all of the
chromadb and ollama dependencies in the windows python instance, which I'd prefer not to do,
nor installing virtualenv in windows.  So left this as two (three) steps. Get the msg Ids and 
get and process msgs under windows.  And embedding and possible categorization on WSL/Linux.

Goal: 
 - pull msg
 - convert to markdown and save while reasonably cleaning up formatting.  
 - Filter out non relevant text agressively and embed
 - Test using models to categorize thread, pull product names, domains/companies

 gemma did most consistent job of returning JSON object. fast like llama as well. all models returned more or less similar sets of keywords.

 Messages with lists of parts
[Original Message ID:ABuaX8mcGcw](https://groups.google.com/g/cozy_builders/c/ABuaX8mcGcw)
 # exhaust parts
