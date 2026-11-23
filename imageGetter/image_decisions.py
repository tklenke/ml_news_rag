# ABOUTME: Decisions on image contents: one decision, remove or keep, per content hash (D50)
# ABOUTME: Reads and writes the decisions file and derives decisions from the 2025 removal lists

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set, Tuple

DECISIONS = ("remove", "keep")


def load_decisions(strPath: str) -> Dict[str, str]:
    """Read the decisions file; no file means no decisions yet."""
    if not Path(strPath).exists():
        return {}
    with open(strPath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_decisions(strPath: str, dctDecisions: Dict[str, str]):
    """Write the decisions file, sorted by content hash so that its changes read well in git."""
    for strHash, strDecision in dctDecisions.items():
        if strDecision not in DECISIONS:
            raise ValueError(f"Decision for {strHash} is {strDecision}, not one of {DECISIONS}")
    with open(strPath, 'w', encoding='utf-8') as f:
        json.dump(dict(sorted(dctDecisions.items())), f, indent=1)
        f.write('\n')


def decisions_from_removals(dctIndex: Dict, setRemovedNames: Set[str]) -> Tuple[Dict[str, str], Set[str]]:
    """
    Derive decisions from a list of removed local file names.

    Only measured entries count; a file is one copy however often the index lists it.
    A content of which every copy was removed becomes 'remove'. A content of which
    some copies were removed and others kept gets no decision and is returned as mixed.

    Returns:
        (decisions by content hash, content hashes removed in some copies only)
    """
    dctCopies = defaultdict(set)
    for dctEntry in dctIndex.values():
        for dctImage in dctEntry.get("images", []):
            if "content_hash" in dctImage:
                dctCopies[dctImage["content_hash"]].add(dctImage["local_filename"])

    dctDecisions = {}
    setMixed = set()
    for strHash, setNames in dctCopies.items():
        intRemoved = len(setNames & setRemovedNames)
        if intRemoved == len(setNames):
            dctDecisions[strHash] = "remove"
        elif intRemoved > 0:
            setMixed.add(strHash)
    return dctDecisions, setMixed
