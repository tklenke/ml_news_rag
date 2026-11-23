# ABOUTME: Embeds the files of the corpus that are not yet in the collection
# ABOUTME: Keeps a list of embedded files, so that it can be stopped and continued
import argparse
import time, os, random, sys, traceback
from embedder_settings import SOURCEDOCPATHS, COMPLETEDEMBEDFILE, EXPERIMENTDIR, CHUNKSIZE, \
    EMBEDMODEL, EMBED_PREFIX
from f_embed import Embedder
from f_misc import get_filepaths_list, get_ids_list_from_file, get_id_from_path

#--------- CONSTANTs -------------
NMAXFILE = 20_000 
NMAXFAILURES = 20


INITEMBED = False
#use default localhose for chroma and ollam
#use default ports for chroma and ollama

#------------FUNCTIONS---------------

#Reads the parameters of a run. Without any, the run is the one of the production collection.
#Args:      args: The command line as a list of strings, without the name of the script.
#Returns:   The parameters as attributes.
def parse_args(args):
    parser = argparse.ArgumentParser(description="Embeds the files not yet in the collection")
    parser.add_argument("--collection", default=EMBEDMODEL)
    parser.add_argument("--chunk-size", type=int, default=CHUNKSIZE)
    parser.add_argument("--overlap", type=int, default=0)
    parser.add_argument("--chroma-port", default="8000")
    parser.add_argument("--ollama-port", default="11434")
    parser.add_argument("--sources", nargs="+", default=SOURCEDOCPATHS)
    parsed = parser.parse_args(args)
    if parsed.collection == EMBEDMODEL and (parsed.chunk_size, parsed.overlap) != (CHUNKSIZE, 0):
        parser.error("another chunk size or overlap needs a --collection of its own")
    return parsed

#Gives the file that lists the ids already embedded in a collection.
#Args:      collection: The name of the collection.
#Returns:   The path of the file.
def get_progress_file(collection):
    if collection == EMBEDMODEL:
        return COMPLETEDEMBEDFILE
    return f"{EXPERIMENTDIR}/embedstatus_{collection}.txt"

#Removes the files that have been embedded.
#Args:      paths: The paths of all files.
#           progressfile: The file that lists the ids already embedded.
#Returns:   The paths of the files still to be embedded, in the same order.
def get_files_to_embed(paths, progressfile):
    ids_embedded = set()
    if os.path.exists(progressfile):
        print(f"reading list of previously embedded files...")
        ids_embedded = set(get_ids_list_from_file(progressfile))
    print(f"Files embedded: {len(ids_embedded)}")
    return [f for f in paths if get_id_from_path(f) not in ids_embedded]

#Embeds files in the order given and lists each in the progress file when it is stored.
#A file that fails is left out of the progress file. Many failures in a row end the run,
#since the cause is then not the file.
#Args:      embdr: An Embedder set to the collection, model, prefix and chunks.
#           files: The paths of the files.
#           progressfile: The file that lists the ids already embedded.
#Returns:   True when no file failed.
def embed_files(embdr, files, progressfile):
    nTotalSavedThisSession = 0
    nChunks = 0
    nFailed = 0
    nFailedInARow = 0
    fTotalEmbedTime = 0.

    # loop on the following
    #   get the message text and save it
    #   print out some stats
    for file in files[:NMAXFILE]:
        t0 = time.time()

        print(f"embedding file: {file}{'':>50}", end="\r")
        try:
            nChunks += embdr.embed_file(file)
        except Exception:
            print(f"\nFAILED {file}\n{traceback.format_exc()}")
            nFailed += 1
            nFailedInARow += 1
            if nFailedInARow >= NMAXFAILURES:
                print(f"{nFailedInARow} failures in a row, ending the run")
                break
            continue
        nFailedInARow = 0
        fpCompleted = open(progressfile,"a")
        fpCompleted.write(get_id_from_path(file) + '\n')
        fpCompleted.close()


        # stats
        fTotalEmbedTime += time.time() - t0
        nTotalSavedThisSession += 1
        if nTotalSavedThisSession % 10 == 0:
           print(f"Files This Session: {nTotalSavedThisSession} Files To Go: {len(files) - nTotalSavedThisSession} \
Avg Embed Time: {(fTotalEmbedTime/nTotalSavedThisSession):.4f} secs Chunks: {nChunks} \
{(fTotalEmbedTime/max(nChunks, 1)):.4f} secs/chunk {embdr.get_collection_count()} Collection Items.")

    print(f"\n")
    print(f"-----STATS------")
    print(f" Remaining to Embed: {len(files) - nTotalSavedThisSession}")
    print(f" Total Embedded: {nTotalSavedThisSession}")
    print(f" Failed: {nFailed}")
    print(f" Chunks: {nChunks}")
    print(f" Size of Collection: {embdr.get_collection_count()}")
    print(f" Total Embed Time: {fTotalEmbedTime:.4f} secs")
    print(f" Average Embed Time: {(fTotalEmbedTime/max(nTotalSavedThisSession, 1)):.4f} secs")
    print(f" Time per Chunk: {(fTotalEmbedTime/max(nChunks, 1)):.4f} secs")
    return nFailed == 0

#Embeds the files of the sources that are not yet in the collection, in random order.
#Args:      args: The parameters, from parse_args.
#Returns:   The result of embed_files.
def run(args):
    print(f"Starting Embedding...")

    #get embedder object
    embdr = Embedder(chromaport=args.chroma_port, ollamaport=args.ollama_port)
    embdr.set_collection(args.collection,initialize=INITEMBED)
    embdr.set_chunk_size(args.chunk_size)
    embdr.set_overlap(args.overlap)
    embdr.set_model(EMBEDMODEL)
    embdr.set_prefix(EMBED_PREFIX)
    print(f"Embed:{args.collection} has {embdr.get_collection_count()} objects")

    #get list of all embedable files
    embed_paths = []
    for directory in args.sources:
        embed_paths.extend(get_filepaths_list(directory))
    print(f"Total embeddable files: {len(embed_paths)}")

    progressfile = get_progress_file(args.collection)
    os.makedirs(os.path.dirname(progressfile) or ".", exist_ok=True)
    if INITEMBED and os.path.exists(progressfile):
        os.remove(progressfile)
        print(f"Initializing Embed: {progressfile} deleted")

    files = get_files_to_embed(embed_paths, progressfile)
    print(f"Net to complete: {len(files)}")

    random.shuffle(files)
    return embed_files(embdr, files, progressfile)


#-----------------------------------
#--   MAIN
#-----------------------------------
if __name__ == "__main__":
    sys.exit(0 if run(parse_args(sys.argv[1:])) else 1)
