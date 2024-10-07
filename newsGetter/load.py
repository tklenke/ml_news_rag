
import time
import os
from documents import Abstract

#Scans a directory and subdirectories for files with a '.md' extension and returns a list of their names without the extension.
#Args:      directory: The directory to scan.
#Returns:   A list of strings containing the names of the '.md' files without the extension.
def get_md_filenames(directory):
    md_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                md_files.append(file[:-3])  # Remove the '.md' extension

    return md_files

def load_documents(directory, max_files = -1):
    if max_files > 0:
        print(f"Loading maximum of {max_files} messages")
    else:
        print(f"loading all messages")
    start = time.time()
    doc_id = 0
    for root, dirs, files in os.walk(directory):
        if doc_id > max_files & max_files > 0:
            break
        for file in files:
            #if there is a max file to load limit, use it otherwise ignore
            if doc_id > max_files & max_files > 0:
                break
            if file.endswith(".md"):
                msg_id = (file[:-3])  # Remove the '.md' extension
                with open(os.path.join(root, file)) as f:
                    # Read the lines from the file
                    lines = f.readlines()

                    # Check if there are at least two lines for title
                    if len(lines) >= 2:
                        # Take the second line, remove the first character, and strip trailing whitespace
                        title = lines[1][3:].strip()
                    else:
                        title = ""

                    # Store lines from the 3rd line onward in the body (join them into a single string)
                    if len(lines) > 2:
                        body = ''.join(lines[2:]).strip()
                    else:
                        body = ""

                    yield Abstract(ID=doc_id, title=title, msg_id=msg_id, body=body)

                    doc_id += 1
                    if doc_id % 100 == 0:
                        print(f"{doc_id} {msg_id} {title}")
    end = time.time()
    print(f'Parsing msgs took {end - start} seconds')
