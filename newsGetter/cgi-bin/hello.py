import cgi
#import cgitb; cgitb.enable() # Optional; for debugging only

print ("Content-Type: text/html")
print ("")

print ("<pre>")
print ("hello....")
arguments = cgi.FieldStorage()
for i in arguments.keys():
    print (f"{i} {arguments[i].value}")

print ("</pre>")