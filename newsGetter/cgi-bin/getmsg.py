import os
import markdown

MSGS_DIR = "msgs"

if __name__ == '__main__':


    msg_id = os.environ['QUERY_STRING']
    #msg_id = 'rCc0g5bx-J0'
    msg_dir = msg_id[0].upper()
    debug_text = f"msg: {msg_id} dir {msg_dir}\n"
    debug_text += f"cwd: {os.getcwd()}\n"
    if msg_dir.isalpha() is not True:
        msg_dir = 'aDigits'

    msg_path = f"{MSGS_DIR}/{msg_dir}/{msg_id}.md"

    debug_text += f"{msg_path}\n"

    if os.path.exists(msg_path):
        with open(msg_path) as input_file:
            text = input_file.read()
            msg_txt = markdown.markdown(text)
            #msg_txt = text
    else:
        debug_text += f"file {msg_path} does not exist"
        msg_txt = f"<pre>{debug_text}</pre>"
    
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
""")
print(f"<div class='row'><div class='twelve columns'>{msg_txt}\n</div></div></div></body></html> ")
