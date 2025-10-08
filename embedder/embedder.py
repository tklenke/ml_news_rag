import chromadb, ollama
import time, os, random
from f_embed import Embedder
from f_misc import get_filepaths_list, get_ids_list_from_file, get_id_from_path

#--------- CONSTANTs -------------
SOURCEDOCPATHS = ["../data/msgs","../data/news","../data/aeroelectric","../data/cozybuilders"]
#SOURCEDOCPATHS = ["../data/test",]
COMPLETEDEMBEDFILE = "embedstatus.txt"
NMAXFILE = 20_000 
NMAXFILE = 20


CHUNKSIZE = 75 #initial 75
INITEMBED = False
EMBEDMODEL = "nomic-embed-text"
EMBED_PREFIX = "search_document:"  #search_query:
#use default localhose for chroma and ollam
#use default ports for chroma and ollama

#------------FUNCTIONS---------------


    

#-----------------------------------
#--   MAIN
#-----------------------------------
print(f"Starting Embedding...")

#get embedder object
embdr = Embedder()
embdr.set_collection(EMBEDMODEL,initialize=INITEMBED)
embdr.set_chunk_size(CHUNKSIZE)
embdr.set_model(EMBEDMODEL)
embdr.set_prefix(EMBED_PREFIX)
print(f"Embed:{EMBEDMODEL} has {embdr.get_collection_count()} objects")

#get list of all embedable files
embed_files = []
for directory in SOURCEDOCPATHS:
    embed_files.extend(get_filepaths_list(directory))
print(f"Total embeddable files: {len(embed_files)}")

#get list of ids that have already been embedded
ids_embedded = []
if os.path.exists(COMPLETEDEMBEDFILE):
    if INITEMBED:
            os.remove(COMPLETEDEMBEDFILE)
            print(f"Initializing Embed: {COMPLETEDEMBEDFILE} deleted")
    else:
        if os.path.exists(COMPLETEDEMBEDFILE):
            print(f"reading list of previously embedded files...")
            ids_embedded = get_ids_list_from_file(COMPLETEDEMBEDFILE)
print(f"Files embedded: {len(ids_embedded)}")

#remove the ids that have been saved from the files
files = []
for f in embed_files:
    if get_id_from_path(f) not in ids_embedded:
        files.append(f)  #put full path of file into list to be done

print(f"Net to complete: {len(files)}")



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
fpCompleted = open(COMPLETEDEMBEDFILE,"a")
#index = 0

while (len(files) > 0) & (nTotalSavedThisSession < NMAXFILE):
    t0 = time.time()
    random_index = random.randint(0, len(files) - 1)
    random_file = files.pop(random_index)
    #random_file = files.pop(index)
    #index += 1

    print(f"embedding file: {random_file}{'':>50}", end="\r")
    embdr.embed_file(random_file)
    fpCompleted = open(COMPLETEDEMBEDFILE,"a")
    fpCompleted.write(get_id_from_path(random_file) + '\n')
    fpCompleted.close()


    # stats
    fTotalEmbedTime += time.time() - t0
    nTotalSavedThisSession += 1
    if nTotalSavedThisSession % 10 == 0:
       print(f"Files This Session: {nTotalSavedThisSession} Files To Go: {len(files)} \
Avg Embed Time: {(fTotalEmbedTime/nTotalSavedThisSession):.4f} secs {embdr.get_collection_count()} \
Collection Items.")

print(f"\n")
print(f"-----STATS------")
print(f" Remaining to Embed: {len(files)}")
print(f" Total Embedded: {nTotalSavedThisSession}")
print(f" Size of Collection: {embdr.get_collection_count()}")
print(f" Total Embed Time: {fTotalEmbedTime:.4f} secs")
print(f" Average Embed Time: {(fTotalEmbedTime/nTotalSavedThisSession):.4f} secs")

            
    




