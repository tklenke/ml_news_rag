# ABOUTME: Settings of the production collection and of the files embedded in it
# ABOUTME: Shared by the embedder and the repair of the collection

SOURCEDOCPATHS = ["../data/msgs","../data/news","../data/aeroelectric","../data/cozybuilders"]
#SOURCEDOCPATHS = ["../data/test",]
COMPLETEDEMBEDFILE = "embedstatus.txt"

CHUNKSIZE = 250 #initial 75
EMBEDMODEL = "nomic-embed-text"
EMBED_PREFIX = "search_document:"  #search_query:
