#### Message Thread Getter

This is the more recent interation than newsGetter.



Decided to push LLM stuff to embedding.  Reason being that message getter needs to be run under the Windows
environment along with Chrome due to use of Selenium.  This would require installing all of the
chromadb and ollama dependencies in the windows python instance, which I'd prefer not to do,
nor installing virtualenv in windows.  So left this as two (three) steps. Get the msg Ids and 
get and process msgs under windows.  And embedding and possible categorization on WSL/Linux.

Goal: 
 - pull msg
 - convert to markdown and save while reasonably cleaning up formatting.  
 - Filter out non relevant text agressively and embed
 - Test using models to categorize thread, pull product names, domains/companies

 gemma did most consistent job of returning JSON object. fast like llama as well. all models returned more or less similar sets of keywords.

 Messages with lists of parts
[Original Message ID:ABuaX8mcGcw](https://groups.google.com/g/cozy_builders/c/ABuaX8mcGcw)
 # exhaust parts