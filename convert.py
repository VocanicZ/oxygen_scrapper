import re
import safe_open

def split(text, upper=False):
    if upper:
        text = text.upper()
    else:
        text = text.lower()
    return re.split(r'[ _]', text)

# Helper function to convert to camelCase
def c(text):
    words = split(text)
    return words[0] + ''.join(word.capitalize() for word in words[1:])
    
# Helper function to convert to pascalCase
def p(text):
    words = split(text)
    return ''.join(word.capitalize() for word in words)
    
# Helper function to convert to snake_case
def s(text):
    words = split(text)
    return '_'.join(words)
    
# Helper function to convert to kebab-case
def k(text):
    words = split(text)
    return '-'.join(words)
    
# Helper function to convert to flat_case (all lowercase with no separators)
def f(text):
    return ''.join(split(text))
    
# Helper function to convert to upper flat case (all uppercase with no separators)
def uf(text):
    return ''.join(split(text))
    
# Helper function to convert to Pascal Snake Case
def ps(text):
    words = split(text)
    pascal_case = ''.join(word.capitalize() for word in words)
    return pascal_case.lower().replace(' ', '_')
    
# Helper function to convert to Camel Snake Case
def cs(text):
    words = split(text)
    camel_case = words[0] + ''.join(word.capitalize() for word in words[1:])
    return camel_case.lower().replace(' ', '_')
    
# Helper function to convert to screaming_snake_case
def ss(text):
    return text.upper().replace(' ', '_')
    
# Helper function to convert to train-case
def t(text):
    words = split(text)
    return ' '.join(words).replace(' ', '-')
    
# Helper function to convert to cobol-case
def co(text):
    words = split(text, upper=True)
    return '-'.join(words)

def ca(text):
    words = split(text, upper=True)
    return ' '.join(word.capitalize() for word in words)

#-----------------------------------update case - function mapping--------------------------------------------
convert = {"c":c, "p":p, "s":s, "k":k, "f":f, "uf":uf, "ps":ps, "cs":cs, "ss":ss, "t":t, "co":co, "ca":ca}
#-------------------------------------------------------------------------------------------------------------

database = safe_open.r("database.json")["database"]
default = {}
for contents in database:
    if contents["name"] == "elements":
        default = contents["default"]
        database=None
        break

def get(js, key, text=None, convert=convert, default=default):
    #print(f"js={js}, key={key}, text={text}")
    if text == None:
        if "file_name" in js:
            text=js["file_name"]
        else:
            text = js["name"]
    elif text in js:
        text = js[text]
    if key in js:
        key = js[key]
        if key in convert:
            #print(f"   1|_ js={js}, key={key}, text={text}")
            return convert[key](text)
        #print(f"   2|_ js={js}, key={key}, text={text}")
        return key
    #print(f"   3|_ js={js}, key={key}, text={text}")
    if key in convert:
        return convert[key](text)
    return convert[default[key]](text)