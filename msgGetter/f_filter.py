import markdownify
import re, random, time

##----Filters
remove_strings = []
remove_patterns = []
remove_patterns.append(r'\u202f|\ufeff|\u200b|\u2003')
remove_patterns.append(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F82F\U0001F880-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U00002600-\U000026FF\U000024C2-\U0001F251\u200d\u23cf\u23e9\u23ea\u23e7\u23f0\u23f1\u23f2\u23f3\u23f9-\u23fa\u26a0\u2699\ufe0f]') #emojjis
remove_patterns.append(r'(\d{1,2}):(\d{2}):(\d{2})\s+(AM|PM)') #time with seconds
remove_patterns.append(r'(\d{1,2}):(\d{2})\s+(AM|PM)*,*') #time
remove_patterns.append(r'(\d+)\s+hours\s+ago') #hours ago
remove_patterns.append(r'((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b)\s*(\d{1,2}),*\s*(\d{4}),*') #dates
remove_patterns.append(r'(\d{1,2})\/(\d{1,2})\/(\d{2})')  #dates 3/12/25
remove_patterns.append(r'<.+?\@.+?>') #email address in brackets and the brackets
remove_patterns.append(r'\[(.*?)\]\((.*?)\)') #[stuff](stuff)  markdown weblink
remove_patterns.append(r'https?:\/\/\S+')  #http or https:// and all the non whitespace characters after
remove_patterns.append(r'###.?') # remove lines with ### (author)
remove_patterns.append(r'reply\s*all\s*Reply\s*to\s*author\s*Forward\s*Delete')
remove_patterns.append(r'reply\s*all\s*reply\s*to\s*author\s*forward')
remove_patterns.append(r'reply\s*to\s*author\s*forward\s*delete')
remove_patterns.append(r'You\s*do\s*not\s*have\s*permission\s*to\s*delete\s*messages\s*in\s*this\s*group')
remove_patterns.append(r'Copy\s*link\s*Report\s*message\s*Show')
remove_patterns.append(r'Reply\s*to\s*group')
remove_patterns.append(r'unsubscribe')
remove_patterns.append(r'original\s*message\s*to')
remove_patterns.append(r'Reply\s*all')
remove_patterns.append(r'cozy\_builders\@googlegroups\.com')
remove_patterns.append(r'You\s*received\s*this\s*message\s*because\s*you\s*are\s*subscribed\s*to\s*the\s*Google\s*Groups\s*"COZY\s*Builders\s*Mailing\s*List"\s*group.')
remove_patterns.append(r'You\s*received\s*this\s*message\s*because\s*you\s*are\s*subscribed\s*to')
remove_patterns.append(r'To\s*view\s*this\s*discussion\s*on\s*the\s*web\s*visit')
remove_patterns.append(r'canard\-aviators@yahoogroups.com')
remove_patterns.append(r"Cozy\s*(email)*\s*List")
remove_patterns.append(r'canard\-aviators@canardzone.groups.io')
remove_patterns.append(r'COZY\s*Builders\s*Mailing\s*List')
remove_patterns.append(r'Mailing\s*List\s*Aviators')
remove_patterns.append(r'To\s*view\s*this\s*discussion\s*visit')
remove_patterns.append(r'Canard\s*Aviators\s*Mailing\s*List')
remove_patterns.append(r'COZY\s*Mailing\s*List')
remove_patterns.append(r'COZY\s*Builders\s*Mailing\s*List')
remove_patterns.append(r'canard\-aviators*')
remove_patterns.append(r'Canard\s*Aa*viators*')
remove_patterns.append(r'Cozy\s*Groups*')
remove_patterns.append(r'Canard\s*Groups*')
remove_patterns.append(r'original\s*message')
remove_patterns.append(r'Copyright\s*©\s*(\d{4})') #copyright notice
remove_patterns.append(r'Sent\s*from\s*my\s*(iPhone|samsung|verizon)?')
remove_patterns.append(r'unread')
remove_patterns.append(r'\*\*\S+\s*\*\*') #**Subject  ** e.g.
remove_patterns.append(r'cozy(\s*|_*|\\_*)builders')
remove_patterns.append(r"\[.*profile\s*photo\]\(.*\)")
remove_patterns.append(r"\[Yahoo!\s*Groups\]\(.*\)")
remove_patterns.append(r"\[Privacy\]\(.*\)")
remove_patterns.append(r"\[Terms\s*of\s*Use\]\(.*\)")
remove_patterns.append(r"\[https://groups\.google\.com\/[a-z]\/msgid\/cozy.*\]\(.*\)")
remove_patterns.append(r"To\s*unsubscribe.*googlegroups.com")
remove_patterns.append(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{1,2},\s*\d{4},\s*\d{1,2}:\d{2}:\d{2}\s*(AM|PM)\s*\d{1,2}/\d{1,2}/\d{2}')
remove_patterns.append(r'\\<([a-zA-Z0-9._%+-\\ ]+@[a-zA-Z0-9.-\\ ]+)\\>') #email address in brackets
remove_patterns.append(r'[A-Za-z0-9=&_\-]{25,}') #repeating characters in urls
remove_patterns.append(r'([A-Za-z0-9=\-_])(%)([A-Za-z0-9=\-_])') #spaces in urls
remove_patterns.append(r'(http|https)') #http
remove_patterns.append(r'(googlegroups\.com|groups\.google\.com|googleusercontent\.com|google|gmail\.com|groups\.yahoo\.com|yahoogroups\.com|yahoo\.com|\.jpg)') #extra url stuff not
remove_patterns.append(r'(sbcglobal|aol|verizon|gmail|yahoo|hotmail|earthlink)\.(com|org|net')
remove_patterns.append(r'msgid')
remove_patterns.append(r'%[0-9A-Fa-foO]2') #url encoded characters
remove_patterns.append(r'\s+')

def normalize_quotes(text):
    """Replaces fancy/curly quotes with basic straight quotes in two re.sub lines."""
    
    # 1. Replace all double curly quotes with straight double quotes
    text = re.sub(r'[“”]', '"', text) 
    
    # 2. Replace all single curly quotes/apostrophes with straight single quotes
    text = re.sub(r'[‘’]', "'", text) 
    
    return text

def filter_markdown(markdown_text):
    #remove the first line
    lines = markdown_text.splitlines()
    lines = lines[1:]
    markdown_text = '\n'.join(lines)
    markdown_text = normalize_quotes(markdown_text)
    for remove_text in remove_strings:
        markdown_text = markdown_text.replace(remove_text, " ", flags=re.IGNORECASE) 
        #use a space to stop unintended word merge
    for remove_pattern in remove_patterns:
        markdown_text = re.sub(remove_pattern, ' ', markdown_text, flags=re.IGNORECASE)
    #replace backslashes with null
    markdown_text = markdown_text.replace('\\','')
    #remove back slashes, fwd slashes, colons, square and curly brackets with a space 
    # (might help break up URLs into useful things)
    #replace any repeating characters with space
    markdown_text = re.sub(r'(.)\1{5,}|[<>\(\)\\/:{}[\]\-_#@]', '  ', markdown_text)
    #make Lycoming engne numbers one word
    markdown_text = re.sub(r"[oO0]\s*(\d{3})", r"o\1", markdown_text)
 
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