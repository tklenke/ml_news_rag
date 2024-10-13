import chromadb, ollama
import time, os, random
from chroma_functions import getclient, getcollection, embed_file

#--------- CONSTANTs -------------
embedModel = "all-minilm"
sourceDocPaths = ["./data/news","./data/aeroelectric","./data/msgs",]
chunk_size = 75
initialize_embed = False
completed_embed_file = "embedstatus.txt"
max_file_count = 10000 


#------------FUNCTIONS---------------

#Reads ids from a file into a list, removing trailing carriage returns and linefeeds.
#Args:    filename: The name of the file to read.
#Returns:   A list of strings, each containing a line from the file 
#           with trailing carriage returns and linefeeds removed.
def get_embed_ids(filename):
    with open(filename, 'r') as f:
        lines = [line.rstrip() for line in f]
    f.close()
    return lines

#Scans a directory and subdirectories for files
#Args:      directory: The directory to scan.
#Returns:   A list of strings containing the paths of all the files
def get_filenames(directory):
    md_files = []

    if not os.path.exists(directory):
        print(f" Err: Directory {directory} does not exist.")
    else:
        for root, dirs, files in os.walk(directory):
            for name in files:
                md_files.append(os.path.join(root, name))

    return md_files


#given a full path, return the filename without extension
def get_id(path):
    filename = path.split("/")[-1]

    # Split the filename based on the last dot (.)
    parts = filename.rsplit(".", 1)

    # Check if there's only one part (no extension)
    if len(parts) == 1:
        return filename
    # Otherwise, return the part before the dot
    else:
        return parts[0]

#-------------MAIN-------------------
print(f"Starting Embedding...")

#get list of all embedable files
embed_files = []
for directory in sourceDocPaths:
    embed_files.extend(get_filenames(directory))
print(f"Total embeddable files: {len(embed_files)}")

#get list of ids that have already been embedded
if initialize_embed:
    ids_embedded = []
    if os.path.exists(completed_embed_file):
        os.remove(completed_embed_file)
        print(f" Initializing Embed: {completed_embed_file} deleted")
else:
    ids_embedded = get_embed_ids(completed_embed_file)
print(f"Files embedded: {len(ids_embedded)}")

#remove the ids that have been saved from the files
files = []
for f in embed_files:
    if get_id(f) not in ids_embedded:
        files.append(f)  #put full path of file into list to be done

print(f"Net to complete: {len(files)}")

#get chromacollection
chromaclient = getclient()
collection = getcollection(chromaclient, embedModel, initialize_embed)

# loop on the following
#   select a random message id and check that it has not been saved
#       if has been saved, remove from list and select another 
#           (NR - cleaned list above)
#       if the list is empty we are done (see while conditional)
#   get the message text and save it
#       remove from the list and select another
#   print out some stats
nTotalSavedThisSession = 0
fTotalEmbedTime = 0.
fpCompleted = open(completed_embed_file,"a")
#index = 0

while (len(files) > 0) & (nTotalSavedThisSession < max_file_count):
    t0 = time.time()
    random_index = random.randint(0, len(files) - 1)
    random_file = files.pop(random_index)
    #random_file = files.pop(index)
    #index += 1

    print(f"embedding file: {random_file}{'':>50}", end="\r")
    embed_file(random_file, embedModel, collection, chunk_size)
    fpCompleted = open(completed_embed_file,"a")
    fpCompleted.write(get_id(random_file) + '\n')
    fpCompleted.close()


    # stats
    fTotalEmbedTime += time.time() - t0
    nTotalSavedThisSession += 1
    if nTotalSavedThisSession % 10 == 0:
       print(f"Progress This session: {nTotalSavedThisSession} files. {collection.count()} Total Collection Items. Files To Go: {len(files)}")

print(f"\n")
print(f"-----STATS------")
print(f" Remaining to Embed: {len(files)}")
print(f" Total Embedded: {nTotalSavedThisSession}")
print(f" Size of Collection: {collection.count()}")
print(f" Total Embed Time: {fTotalEmbedTime:.4f} secs")
print(f" Average Embed Time: {(fTotalEmbedTime/nTotalSavedThisSession):.4f} secs")

            
    




