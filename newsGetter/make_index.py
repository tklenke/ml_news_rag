import os.path
import requests
import pickle

from load import load_documents
from timing import timing
from index import Index

MSGS_DIR = "msgs"
MAX_MSGS = -1
index_file = 'bar.obj'


@timing
def index_documents(documents, index):
    for i, document in enumerate(documents):
        index.index_document(document)
        if i % 5000 == 0:
            print(f'Indexed {i} documents', end='\r')
    return index


if __name__ == '__main__':

    index = index_documents(load_documents(MSGS_DIR,MAX_MSGS), Index())
    print(f'Index contains {len(index.documents)} documents')

    docs = index.search('nose gear', search_type='AND', rank=True)
    print(f"found {len(docs)} ranked recs for nose AND gear")

    # Save the object to a file
    with open(index_file, 'wb') as file:
        pickle.dump(index, file)
    print(f"saved index to {index_file}")


