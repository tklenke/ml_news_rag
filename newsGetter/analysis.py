import re
import string
#import Stemmer  pystemmer is faster but is wrapper for c lib, so needs compiler 
import snowballstemmer



# top 25 most common words in English and "wikipedia":
# https://en.wikipedia.org/wiki/Most_common_words_in_English
'''
STOPWORDS = set(['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
                 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you',
                 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'wikipedia',
                 'cozy'])
'''
STOPWORDS = set([
   "about", "after", "again", "air", "all", "along", "also", "an", "and", "another",
    "any", "are", "around", "as", "at", "away", "back", "be", "because", "been",
    "before", "below", "between", "both", "but", "by", "came", "can", "come", "could",
    "day", "did", "different", "do", "does", "dont", "down", "each", "end", "even",
    "every", "few", "find", "first", "for", "found", "from", "get", "give", "go",
    "good", "great", "had", "has", "have", "he", "help", "her", "here", "him",
    "his", "home", "house", "how", "i", "if", "in", "into", "is", "it",
    "its", "just", "keep", "kind", "know", "large", "last", "left", "let", "like",
    "little", "live", "long", "look", "made", "make", "man", "many", "may", "me",
    "mean", "men", "might", "more", "most", "much", "must", "my", "name", "near",
    "need", "never", "new", "next", "no", "not", "now", "number", "of", "off",
    "old", "on", "one", "only", "or", "other", "our", "out", "over", "own",
    "part", "people", "place", "put", "read", "right", "said", "same", "saw", "say",
    "see", "she", "should", "show", "small", "so", "some", "something", "sound", "still",
    "such", "take", "tell", "than", "that", "the", "them", "then", "there", "these",
    "they", "thing", "think", "this", "those", "thought", "three", "through", "time", "to",
    "together", "too", "two", "under", "up", "us", "use", "very", "want", "water",
    "way", "we", "well", "went", "were", "what", "when", "where", "which", "while",
    "who", "why", "will", "with", "without", "word", "work", "world", "would", "write",
    "year", "you", "your",
    "ill",'im','pm','re',
    "cozy"])
PUNCTUATION = re.compile('[%s]' % re.escape(string.punctuation))
MISC_TAGS = set(['http', 'mailto', 'textalign', 'fontfamily', 'googlegroup',
                 'yahoogroup','unsubscribe','messageto'])
##STEMMER = Stemmer.Stemmer('english')
STEMMER = snowballstemmer.stemmer('english');

def remove_md_urls(text):
    return re.sub(r'\[.*?\]\(.*?\)', '', text)

def tokenize(text):
    return text.split()

def lowercase_filter(tokens):
    return [token.lower() for token in tokens]

def punctuation_filter(tokens):
    return [PUNCTUATION.sub('', token) for token in tokens]

def tags_filter(tokens):
    for tag in MISC_TAGS:
        tokens = tag_filter(tokens,tag)
    return tokens

def tag_filter(tokens,tag):      
    return [token for token in tokens if tag not in token]

def stopword_filter(tokens):
    return [token for token in tokens if token not in STOPWORDS]

def stem_filter(tokens):
    #return(tokens)
    return STEMMER.stemWords(tokens)

def analyze(text):
    text = remove_md_urls(text)
    tokens = tokenize(text)
    tokens = lowercase_filter(tokens)
    tokens = punctuation_filter(tokens)
    tokens = tags_filter(tokens)
    tokens = stopword_filter(tokens)
    tokens = stem_filter(tokens)

    return [token for token in tokens if token]
