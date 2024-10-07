import cgi
import os.path
import pickle
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from load import load_documents
from timing import timing
from index import Index

MSGS_DIR = "msgs"
INDEX_FILE = "bar.obj"
#retun ranked results always
RANKED = True


@timing
def index_documents(documents, index):
    for i, document in enumerate(documents):
        index.index_document(document)
        if i % 5000 == 0:
            print(f'Indexed {i} documents', end='\r')
    return index


if __name__ == '__main__':

    with open(INDEX_FILE, 'rb') as file:
        index = pickle.load(file)
    debug_text = (f'Index contains {len(index.documents)} documents\n')

    arguments = cgi.FieldStorage()
    for i in arguments.keys():
        debug_text += f"{i} {arguments[i].value}\n"


    results = index.search(arguments['keywords'].value, 
                           search_type=arguments['search_type'].value,
                           rank=RANKED)
    debug_text += f"Found {len(results)} documents\n"
    doc_list = "<ul>\n"
    for r in results:
        title = r[0].title.replace('\\','')
        doc_list += (f"<li><a href=\"/cgi-bin/getmsg.py?{r[0].msg_id}\">{title}</a></li>\n")

    doc_list += (f"</ul>")
    
    print("""Content-Type: text/html\n

<html lang=\"en\">
<head>
  <!-- Basic Page Needs
  –––––––––––––––––––––––––––––––––––––––––––––––––– -->
  <meta charset=\"utf-8\">
  <title>Cozy Builders Message Search</title>
  <meta name=\"Search Page for Cozy Builders Archive\" content=\"\">
  <meta name=\"tklenke\" content=\"\">
  <!-- Mobile Specific Metas
  –––––––––––––––––––––––––––––––––––––––––––––––––– -->
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <!-- FONT
  –––––––––––––––––––––––––––––––––––––––––––––––––– -->
  <link href=\"//fonts.googleapis.com/css?family=Raleway:400,300,600\" rel=\"stylesheet\" type=\"text/css\">
  <!-- CSS
  –––––––––––––––––––––––––––––––––––––––––––––––––– -->
  <link rel=\"stylesheet\" href=\"../css/normalize.css\">
  <link rel=\"stylesheet\" href=\"../css/skeleton.css\">
</head>
<body>
  <div class=\"container\">
  <div class=\"row\">
    <div class="six columns">""")
print(f"<pre>\n{debug_text}\n</pre>\n</div></div>\n")
print("""
 """)
print(f"<div class='row'><div class='twelve columns'>{doc_list}\n</div></div></div></body></html> ")
