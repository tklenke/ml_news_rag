# ABOUTME: Local review tool of image contents (D50): one picture per content, each marked keep or discard
# ABOUTME: Builds the suggested, new and decided lists and serves them on 127.0.0.1 with the standard library

import html
import json
import math
import mimetypes
import re
from collections import defaultdict
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Dict, List, Set
from urllib.parse import parse_qs, urlparse
from image_decisions import DECISIONS, load_decisions, save_decisions
from rename_images import thumbnail_name

SUGGEST_UNDER_BYTES = 1000
SUGGEST_SHORT_SIDE_PIXELS = 200
SUGGEST_IMAGENNN_BYTES = 20000
PAGE_SIZE = 100
LISTS = ("suggested", "new", "decided")
IMAGENNN_PATTERN = re.compile(r'^image\d+\.[A-Za-z]+$', re.IGNORECASE)


def thread_date(dctEntry: Dict) -> datetime:
    """Date of a thread from its metadata; a date that cannot be read sorts last."""
    try:
        return datetime.strptime(dctEntry["metadata"]["date"], '%b %d, %Y')
    except (KeyError, ValueError):
        return datetime.max


def is_suggested(dctItem: Dict, setSuggestions: Set[str]) -> bool:
    """Whether an undecided content belongs on the Suggested list."""
    if dctItem["hash"] in setSuggestions or dctItem["thread_count"] >= 2 \
            or dctItem["size_bytes"] < SUGGEST_UNDER_BYTES:
        return True
    if min(dctItem["width"], dctItem["height"]) < SUGGEST_SHORT_SIDE_PIXELS:
        return True
    return bool(IMAGENNN_PATTERN.match(dctItem["filename"])) and dctItem["size_bytes"] < SUGGEST_IMAGENNN_BYTES


def content_items(dctIndex: Dict, dctDecisions: Dict[str, str], setSuggestions: Set[str]) -> List[Dict]:
    """
    One item per measured content, shown under its earliest thread.

    Items are ordered by the date of that thread, the pictures of one thread together
    and those in more threads first.

    Returns:
        Items with hash, local_filename, filename, size_bytes, width, height, thread_count,
        thread_id, subject, date, decision (or None) and list (suggested, new or decided)
    """
    dctThreads = defaultdict(set)
    dctFirst = {}
    for strMessageId, dctEntry in dctIndex.items():
        for dctImage in dctEntry.get("images", []):
            strHash = dctImage.get("content_hash")
            if strHash is None:
                continue
            dctThreads[strHash].add(strMessageId)
            tplKey = (thread_date(dctEntry), strMessageId)
            if strHash not in dctFirst or tplKey < dctFirst[strHash][0]:
                dctFirst[strHash] = (tplKey, dctImage)

    lstItems = []
    for strHash, ((dtDate, strMessageId), dctImage) in dctFirst.items():
        dctItem = {
            "hash": strHash,
            "local_filename": dctImage["local_filename"],
            "filename": dctImage["filename"],
            "size_bytes": dctImage["size_bytes"],
            "width": dctImage["width"],
            "height": dctImage["height"],
            "thread_count": len(dctThreads[strHash]),
            "thread_id": strMessageId,
            "subject": dctIndex[strMessageId]["metadata"].get("subject", ""),
            "date": dctIndex[strMessageId]["metadata"].get("date", ""),
            "sort_date": dtDate,
            "decision": dctDecisions.get(strHash),
        }
        if dctItem["decision"] is not None:
            dctItem["list"] = "decided"
        elif is_suggested(dctItem, setSuggestions):
            dctItem["list"] = "suggested"
        else:
            dctItem["list"] = "new"
        lstItems.append(dctItem)

    lstItems.sort(key=lambda d: (d["sort_date"], d["thread_id"], -d["thread_count"], d["local_filename"]))
    return lstItems


class ReviewState:
    """The contents under review and Tom's decisions, saved to the decisions file at each change."""

    def __init__(self, dctIndex: Dict, setSuggestions: Set[str], strDecisionsPath: str):
        self.dctIndex = dctIndex
        self.setSuggestions = setSuggestions
        self.strDecisionsPath = strDecisionsPath
        self.dctDecisions = load_decisions(strDecisionsPath)
        self.dctFiles = {d["hash"]: d["local_filename"] for d in content_items(dctIndex, {}, setSuggestions)}

    def items(self) -> List[Dict]:
        return content_items(self.dctIndex, self.dctDecisions, self.setSuggestions)

    def check_known(self, strHash: str):
        if strHash not in self.dctFiles:
            raise KeyError(strHash)

    def decide(self, strHash: str, strDecision: str):
        """Mark a content remove or keep."""
        self.check_known(strHash)
        if strDecision not in DECISIONS:
            raise ValueError(f"Decision {strDecision} is not one of {DECISIONS}")
        self.dctDecisions[strHash] = strDecision
        save_decisions(self.strDecisionsPath, self.dctDecisions)

    def keep(self, lstHashes: List[str]) -> int:
        """Mark keep each of the contents not marked remove; returns how many were marked."""
        for strHash in lstHashes:
            self.check_known(strHash)
        lstKept = [strHash for strHash in lstHashes if self.dctDecisions.get(strHash) != "remove"]
        for strHash in lstKept:
            self.dctDecisions[strHash] = "keep"
        save_decisions(self.strDecisionsPath, self.dctDecisions)
        return len(lstKept)


PAGE_STYLE = """
body { font-family: sans-serif; margin: 1em; background: #fff; color: #222; }
nav a { margin-right: 1em; }
nav a.current { font-weight: bold; }
h2 { font-size: 1em; margin: 1.5em 0 0.5em; border-bottom: 1px solid #ccc; }
.pictures { display: flex; flex-wrap: wrap; gap: 8px; }
figure { margin: 0; width: 200px; font-size: 0.8em; word-break: break-all; }
figure img { width: 200px; height: 200px; object-fit: contain; background: #eee;
             border: 4px solid transparent; box-sizing: border-box; }
figure label { margin-right: 1em; font-size: 1.1em; cursor: pointer; }
figure.remove img { border-color: #c00; opacity: 0.35; }
figure.keep img { border-color: #080; }
button { margin: 0 0 2em; padding: 0.6em 1.2em; font-size: 1em; }
.instructions { background: #ffd; border: 1px solid #cc9; padding: 0.5em 1em; margin: 1em 0; }
"""

PAGE_SCRIPT = """
document.querySelectorAll('figure input[type=radio]').forEach(function (radio) {
  radio.addEventListener('change', function () {
    var fig = radio.closest('figure');
    fetch('/decide', {method: 'POST', headers: {'Content-Type': 'application/json'},
                      body: JSON.stringify({hash: fig.dataset.hash, decision: radio.value})})
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (d) { fig.className = d.decision; })
      .catch(function (e) { radio.checked = false; alert('Not saved: ' + e); });
  });
});
var btn = document.getElementById('keep');
if (btn) btn.addEventListener('click', function () {
  var hashes = Array.from(document.querySelectorAll('figure:not(.remove)')).map(function (f) { return f.dataset.hash; });
  fetch('/keep', {method: 'POST', headers: {'Content-Type': 'application/json'},
                  body: JSON.stringify({hashes: hashes})})
    .then(function (r) { if (!r.ok) throw new Error(r.status); location.reload(); })
    .catch(function (e) { alert('Not saved: ' + e); });
});
"""


def radio(strHash: str, strValue: str, strLabel: str, strDecision) -> str:
    """One choice of a picture's decision, checked when it is the decision taken."""
    strChecked = ' checked' if strDecision == strValue else ''
    return f'<label><input type="radio" name="{strHash}" value="{strValue}"{strChecked}> {strLabel}</label>'


def instructions(strList: str) -> str:
    """What to do on a page, shown at its top and bottom."""
    strText = ('Each keep or discard is saved the moment you click it; closing the page loses nothing. '
               'A choice can be changed at any time.')
    if strList != "decided":
        strText += (' The button below marks every picture of this page not set to discard as keep, '
                    'then shows the next pictures. Pictures you leave without a choice and without '
                    'pressing the button stay in this list.')
    return f'<p class="instructions">{strText}</p>'


def render_page(lstItems: List[Dict], strList: str, intPage: int) -> str:
    """HTML of one page of one list."""
    dctCounts = {s: 0 for s in LISTS}
    for dctItem in lstItems:
        dctCounts[dctItem["list"]] += 1
    lstShown = [d for d in lstItems if d["list"] == strList]
    intPages = max(1, math.ceil(len(lstShown) / PAGE_SIZE))
    intPage = min(max(1, intPage), intPages)
    lstPage = lstShown[(intPage - 1) * PAGE_SIZE:intPage * PAGE_SIZE]

    lstHtml = ['<!doctype html><html><head><meta charset="utf-8"><title>Image review</title>',
               f'<style>{PAGE_STYLE}</style></head><body><nav>']
    for s in LISTS:
        strClass = ' class="current"' if s == strList else ''
        lstHtml.append(f'<a href="/?list={s}&page=1"{strClass}>{s.capitalize()} ({dctCounts[s]})</a>')
    lstHtml.append(f'</nav><p>Page {intPage} of {intPages}. ')
    if intPage > 1:
        lstHtml.append(f'<a href="/?list={strList}&page={intPage - 1}">Previous</a> ')
    if intPage < intPages:
        lstHtml.append(f'<a href="/?list={strList}&page={intPage + 1}">Next</a>')
    lstHtml.append('</p>')
    lstHtml.append(instructions(strList))

    strThread = None
    for dctItem in lstPage:
        if dctItem["thread_id"] != strThread:
            if strThread is not None:
                lstHtml.append('</div>')
            strThread = dctItem["thread_id"]
            lstHtml.append(f'<h2>{html.escape(dctItem["date"])}: {html.escape(dctItem["subject"])} '
                           f'({html.escape(strThread)})</h2><div class="pictures">')
        strHash = html.escape(dctItem["hash"])
        lstHtml.append(
            f'<figure data-hash="{strHash}" class="{dctItem["decision"] or ""}">'
            f'<img src="/thumb/{strHash}" loading="lazy" alt="">'
            f'<figcaption>{radio(strHash, "keep", "keep", dctItem["decision"])}'
            f'{radio(strHash, "remove", "discard", dctItem["decision"])}<br>'
            f'{dctItem["thread_count"]} thread{"s" if dctItem["thread_count"] > 1 else ""}, '
            f'{dctItem["width"]} x {dctItem["height"]}, {dctItem["size_bytes"]:,} bytes '
            f'<a href="/full/{strHash}" target="_blank">full</a><br>'
            f'{html.escape(dctItem["local_filename"])}</figcaption></figure>')
    if strThread is not None:
        lstHtml.append('</div>')

    lstHtml.append(instructions(strList))
    if strList != "decided" and lstPage:
        lstHtml.append('<button id="keep">Keep all the others on this page, then show the next pictures</button>')
    lstHtml.append(f'<script>{PAGE_SCRIPT}</script></body></html>')
    return ''.join(lstHtml)


def make_server(state: ReviewState, strFullDir: str, strThumbsDir: str, strHost: str, intPort: int) -> HTTPServer:
    """An HTTP server of the review tool; a port of 0 takes a free one."""
    pathFull = Path(strFullDir)
    pathThumbs = Path(strThumbsDir)

    class ReviewHandler(BaseHTTPRequestHandler):

        def log_message(self, format, *args):
            pass

        def send_body(self, bytesBody: bytes, strType: str, intStatus: int = 200):
            self.send_response(intStatus)
            self.send_header("Content-Type", strType)
            self.send_header("Content-Length", str(len(bytesBody)))
            self.end_headers()
            self.wfile.write(bytesBody)

        def send_json(self, obj):
            self.send_body(json.dumps(obj).encode("utf-8"), "application/json")

        def send_file(self, pathFile: Path):
            strType = mimetypes.guess_type(pathFile.name)[0] or "application/octet-stream"
            self.send_body(pathFile.read_bytes(), strType)

        def do_GET(self):
            urlParts = urlparse(self.path)
            lstSegments = urlParts.path.strip("/").split("/")
            if urlParts.path == "/":
                dctQuery = parse_qs(urlParts.query)
                strList = dctQuery.get("list", ["suggested"])[0]
                strPage = dctQuery.get("page", ["1"])[0]
                if strList not in LISTS or not strPage.isdigit():
                    self.send_error(404)
                    return
                self.send_body(render_page(state.items(), strList, int(strPage)).encode("utf-8"),
                               "text/html; charset=utf-8")
            elif urlParts.path == "/decisions":
                self.send_json(state.dctDecisions)
            elif len(lstSegments) == 2 and lstSegments[0] in ("thumb", "full") \
                    and lstSegments[1] in state.dctFiles:
                strName = state.dctFiles[lstSegments[1]]
                pathThumb = pathThumbs / thumbnail_name(strName)
                if lstSegments[0] == "thumb" and pathThumb.is_file():
                    self.send_file(pathThumb)
                elif (pathFull / strName).is_file():
                    self.send_file(pathFull / strName)
                else:
                    self.send_error(404)
            else:
                self.send_error(404)

        def do_POST(self):
            intLength = int(self.headers.get("Content-Length", 0))
            try:
                dctBody = json.loads(self.rfile.read(intLength))
                if self.path == "/decide":
                    state.decide(dctBody["hash"], dctBody["decision"])
                    self.send_json({"hash": dctBody["hash"], "decision": dctBody["decision"]})
                elif self.path == "/keep":
                    self.send_json({"kept": state.keep(dctBody["hashes"])})
                else:
                    self.send_error(404)
            except KeyError:
                self.send_error(404)
            except ValueError:
                self.send_error(400)

    return HTTPServer((strHost, intPort), ReviewHandler)
