"""
Data Processor and File Splitter.

This script processes a list of input lines (simulating lines read from a larger log or data file).
It performs two main actions:

1. Filtering: It skips any lines matching predefined 'REMOVE_PATTERNS'.
2. File Rotation: It checks for a 'BREAK_PATTERN' (e.g., 'ISSUE-A'). When a line matches this
   pattern and the extracted issue ID is new, the script closes the current output file
   and opens a new one, ensuring data for different issues are separated.

The script uses a try...finally block for robust file handling, guaranteeing that
the last output file is always closed.
"""

import re
remove_patterns = []
remove_patterns.append( r'\s*(CP|VVN)\d{1,2}, Page' ) #page breaks
remove_patterns.append( r'^\s*\-{3,}' ) #line of ----
break_pattern = r'\s*(VARIVIGGEN\s+NEWS\s+NO\.?|THE\s+CANARD\s+PUSHER\s+NO\.?)'

CP_CORPUS_FILE = '/mnt/c/users/tom/downloads/CPs_1_to_82_Sections.txt'
OUTDIR = '../data/cozybuilders/'

lines = []
with open(CP_CORPUS_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        if len(line) > 2:
           lines.append(line.strip())
f.close()

curIssue = ""
nIssue = 0
f = None
for line in lines:
    bSkip = False
    for pattern in remove_patterns:
        if re.match(pattern, line):
            bSkip = True
            break
    if bSkip:
        print(f"skip {line}")
        continue
    if re.match(break_pattern, line.upper()):
        issue = line.split(',')[0]
        if issue != curIssue:
            curIssue = issue
            nIssue += 1
            outpath = OUTDIR + "cp__no" + str(nIssue)
            print(f"writing {curIssue} to {outpath}")
            if f is not None:
                f.close()
            f = open(outpath,"w", encoding='utf-8')
    if f is not None:
        f.write(line + "\n")