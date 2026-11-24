# YU1 trial: the message fetch from the WSL directory, in cmd

**Started 2026-11-24. Status: set up, waiting for Tom to run steps 1 to 3.**

Purpose: show that `msgGetter/process_message.py` runs with the Windows Python, from cmd, in
the WSL directory (reached by `pushd`), before the yearly instructions say so (YU1a in
`programmer_todo.md`).

## Set up (done by Programmer, 2026-11-24)

- ChromeDriver copied from `C:\Users\tom\Documents\projects\chromedriver-win64` to
  `/home/tom/projects/chromedriver-win64` (`\\wsl.localhost\Debian\home\tom\projects\chromedriver-win64`),
  where the scripts look for it when run from `msgGetter` in WSL (`..\..\chromedriver-win64`).
- One thread set aside so that the fetch has exactly one to get: `XxpI4Rhe3vY` ("JD Newman
  (Infinity Aerospace) memorial", 3 posts, Aug 2026). Moved from `data/msgs_md/X/XxpI4Rhe3vY.md`
  and `data/msgs/X/XxpI4Rhe3vY.txt` to `data/yu_trial_aside/`.

## If the trial is stopped or fails: put the thread back

In WSL, from `/home/tom/projects/ml`. Run only if the files are not back in place already:

    mv data/yu_trial_aside/XxpI4Rhe3vY.md data/msgs_md/X/
    mv data/yu_trial_aside/XxpI4Rhe3vY.txt data/msgs/X/
    rmdir data/yu_trial_aside

If the fetch did write new files, the `mv` asks before it overwrites; answer `y`, so that the
copies of 2026 are the ones kept.

## Steps for Tom (cmd on Windows)

**Step 1, Chrome.** Close every Chrome window. Open a cmd window:

    pushd \\wsl.localhost\Debian\home\tom\projects\ml\msgGetter
    chrome_with_debug.bat

- After `pushd` the prompt is a drive letter, for example `Z:\home\tom\projects\ml\msgGetter>`.
  An error instead: stop and note it.
- Chrome opens; the cmd window may stay busy while Chrome runs. Leave it.
- In that Chrome, open `https://groups.google.com/g/cozy_builders` and check you are signed in.

**Step 2, the port.** A second cmd window:

    curl http://127.0.0.1:9222/json/version

- Expect a few lines of JSON starting with `"Browser": "Chrome/...`. "Could not connect"
  means the debug port is not open.

**Step 3, the fetch.** In the second cmd window:

    pushd \\wsl.localhost\Debian\home\tom\projects\ml\msgGetter
    python process_message.py

- Expect `Ids: ...`, `Msgs already filtered: 10668`, `Net to complete: 1`, then
  `fetching id: XxpI4Rhe3vY` (the thread loads in Chrome), then `----STATS-----` with
  `Msgs Processed: 1.0`.
- An error that names a path for ChromeDriver shows where the script looked.

## After the trial (Programmer)

Compare the new `data/msgs_md/X/XxpI4Rhe3vY.md` and `data/msgs/X/XxpI4Rhe3vY.txt` with the
copies in `data/yu_trial_aside/`. Differences in the page text are expected only if the thread
changed. If anything differs, put the 2026 copies back (above). Then remove
`data/yu_trial_aside/`, record the result here and in YU1, and set the status above.

## Result

Not yet run.
