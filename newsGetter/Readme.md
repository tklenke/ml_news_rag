# Notes:
--------------------------------------------------
## indexer
--------------------------------------------------
used bart.degoe.de code and modified
tool chain is:  
1 - run make_index.py
2 - run use_index.py

initially pickle of index (bar.obj) was over 12megs for 100 msgs
rev 1 680602 bytes  (set body = None)
rev 2 508790 bytes  (remove md urls)
rev 3 453052 bytes  (remove tags and 100 top english words)
rev 4 428370 bytes  (200 top english words)
100 records = .43 mb
1000 = 3.50 mb  3.06 mb rev 5 with stemming
5000 = 15.95 mb
10000 = 31.54 mb 28.05 rev 5 with stemming



--------------------------------------------------
## Indexing Technologies
--------------------------------------------------
Whoosh  (python search indexer)
Gensim
ElasticSearch
PyTerrier
https://www.datacamp.com/tutorial/discovering-hidden-topics-python
https://medium.com/codex/document-indexing-using-tf-idf-189afd04a9fc
https://bart.degoe.de/building-a-full-text-search-engine-150-lines-of-code/


---------------------------------------------------
## Initial Connection via Selenium with Google login
----------------------------------------------------
chrome.bat    
      This batch file opens a chrome browser with a debugging port.  It stores the session data in c:\selenium\ChromeProfile.
      It's great because it will also store persistent google login info into this session.  Then Selenium can connect to it

SeleniumToExistingChromeExample.py  
    Uses selenium to connect to the existing Chrome instance

Usage -- run the chrome.bat file.  Login to Google with two factor authentication etc.  Check the trust this computer button.  Now run the SeleniumToExistingChromeExample.py script and it will be able to see the google groups!  