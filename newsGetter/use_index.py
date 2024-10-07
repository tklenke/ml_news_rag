import os.path
import pickle

from load import load_documents
from timing import timing
from index import Index

MSGS_DIR = "msgs"
MAX_MSGS = 100


@timing
def index_documents(documents, index):
    for i, document in enumerate(documents):
        index.index_document(document)
        if i % 5000 == 0:
            print(f'Indexed {i} documents', end='\r')
    return index


if __name__ == '__main__':

    with open('bar.obj', 'rb') as file:
        index = pickle.load(file)
    print(f'Index contains {len(index.documents)} documents')

    results = index.search('nose gear', search_type='AND', rank=False)
    for r in results:
        #print(f"{doc[0].msg_id} {doc[0].title}")
        print (f"{r[1]} {r[0].msg_id} {r[0].title} ")

    print('index next --- ')
    #index.print_index()
 
