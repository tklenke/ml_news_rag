import markdownify
import re, random, time

##----Filters
remove_strings = []
remove_patterns = []
remove_patterns.append(r'Reply\sto\sauthor\sForward\sDelete\sYou\sdo\snot\shave\spermission\sto\sdelete\smessages\sin\sthis\sgroup\sCopy\slink\sReport\smessage\sShow')
remove_patterns.append(r'Reply\sall\sReply\sto\sauthor\sForward')
remove_patterns.append(r'You\sreceived\sthis\smessage\sbecause\syou\sare\ssubscribed\sto\sthe\sGoogle\sGroups\s"COZY\sBuilders\sMailing\sList"\sgroup.')
remove_patterns.append(r'To\sview\sthis\sdiscussion\son\sthe\sweb\svisit')
remove_patterns.append(r'original\smessageto\sCanard\sAviators,\sCozy\sBuilders')
remove_patterns.append(r'original\smessageto\sCozy\sBuilders')
remove_patterns.append(r'original\smessageto\scanard\-aviators@yahoogroups.com,\scozy\_builders@googlegroups.com\s')
remove_patterns.append(r'original\smessageto\scozy\_builders@googlegroups.com')
remove_patterns.append(r"original\smessageto\sCozy\sList")
remove_patterns.append(r'original\smessageto\scozy\_builders,\scanard\-aviators@canardzone.groups.io')
remove_patterns.append(r'original\smessageto\sCOZY\sBuilders\sMailing\sList')
remove_patterns.append(r'Mailing\sList\sAviators')
remove_patterns.append(r'Canard\sAviators\sMailing\sList')
remove_patterns.append(r'original\smessageto\sCOZY\sMailing\sList')
remove_patterns.append(r'COZY\sBuilders\sMailing\sList')
remove_patterns.append(r'cozy\_builders@googlegroups.com')
remove_patterns.append(r'canard\-aviators')
remove_patterns.append(r'original\smessage\sto')
remove_patterns.append(r'Sent\sfrom\smy\siPhone')
remove_patterns.append(r'unread,')
remove_patterns.append(r"\[.*profile photo\]\(.*\)")
remove_patterns.append(r"\[Yahoo! Groups\]\(.*\)")
remove_patterns.append(r"\[Privacy\]\(.*\)")
remove_patterns.append(r"\[Terms of Use\]\(.*\)")
remove_patterns.append(r"\[https://groups\.google\.com\/[a-z]\/msgid\/cozy.*\]\(.*\)")
remove_patterns.append(r"To unsubscribe.*googlegroups.com")
remove_patterns.append(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{1,2},\s\d{4},\s\d{1,2}:\d{2}:\d{2}\s(AM|PM)\s\d{1,2}/\d{1,2}/\d{2}')
#remove_patterns.append(r'\d{1,2}/\d{1,2}/\d{2}') #date
#remove_patterns.append(r'\d{1,2}, \d{4}, \d{1,2}:\d{2}:\d{2}') #date
#remove_patterns.append(r'\s(AM|PM)\s') #date piece
remove_patterns.append(r'\\<([a-zA-Z0-9._%+-\\ ]+@[a-zA-Z0-9.-\\ ]+)\\>') #email address in brackets
remove_patterns.append(r'[A-Za-z0-9=&_\-]{25,}') #repeating characters in urls
remove_patterns.append(r'([A-Za-z0-9=\-_])(%)([A-Za-z0-9=\-_])') #spaces in urls
remove_patterns.append(r'(http|https)') #http
remove_patterns.append(r'(googlegroups\.com|groups\.google\.com|googleusercontent\.com|google|gmail\.com|groups\.yahoo\.com|yahoogroups\.com|yahoo\.com|\.jpg)') #extra url stuff not


def filter_markdown(markdown_text):
    #remove the first line
    lines = markdown_text.splitlines()
    lines = lines[1:]
    markdown_text = '\n'.join(lines)
    for remove_text in remove_strings:
        markdown_text = markdown_text.replace(remove_text, " ") 
        #use a space to stop unintended word merge
    for remove_pattern in remove_patterns:
        markdown_text = re.sub(remove_pattern, ' ', markdown_text)
    #replace backslashes with null
    markdown_text = markdown_text.replace('\\','')
    #remove back slashes, fwd slashes, colons, square and curly brackets with a space 
    # (might help break up URLs into useful things)
    #replace any repeating characters with space
    markdown_text = re.sub(r'(.)\1{5,}|[<>\(\)\\/:{}[\]\-_#@]', ' ', markdown_text)
    #make Lycoming engne numbers one word
    markdown_text = re.sub(r"[oO0]\s?(\d{3})", r"o\1", markdown_text)
 
    return markdown_text

# Function to convert HTML to Markdown
def html_to_markdown(html):
    # Add space after html close
    html = html.replace(">", "> ")
    # Use markdownify to convert HTML to Markdown
    md = markdownify.markdownify(html, heading_style="ATX", convert=['b', 'i', 'strong', 'em', 'img', 'a', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    return md

#function to take elements array and save as html file
def elements_to_html(elements):
    rtnhtml = "<html>\n"

    for element in elements:
        # Extract the inner HTML
        inner_html = element.get_attribute('innerHTML')
        #add to return text
        rtnhtml += " " + inner_html + "\n"

    rtnhtml += "\n</html>"
    return rtnhtml

#function to extract text in list of elements and return markdown blob of text
def elements_to_markdown(elements):
    rtntxt = ""
    for element in elements:
        # Convert the HTML to Markdown
        markdown_text = html_to_markdown(element.get_attribute('innerHTML'))
        #clean up non unicode characters and remove extraneous strings
        markdown_text = re.sub(r'[\x85|\xA0|\uE83A|\uE15F|\uE5D4|\uE5D3|\uE15E|\uE154|\uE984|\uE674]', ' ', markdown_text)

        #add to return text
        rtntxt += " " + markdown_text + " "
    #remove extra spaces
    rtntxt = re.sub(r'\ +', ' ', rtntxt)
    return rtntxt