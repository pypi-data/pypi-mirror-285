PROFNITY_LVL1=[
    "fuck","ass"
]
PROFNITY_LVL2=[
    "cunt"
]
PROFNITY_LVL3=[
    "nigga","niga"
]
PROFNITY_LVL4=[
    "nigger"
]

def bypass(text) -> str:
    i=0
    while i < 10:
        text = text.lower().replace(" ", "").replace(".", "").replace("_", "").replace("-", "").replace("#", "").replace("'", "") \
            .replace("+", "").replace("*", "").replace("~", "").replace(")", "").replace("`", "").replace("ß", "") \
            .replace("?", "").replace("=", "").replace("}", "").replace("{", "").replace("(", "").replace(")", "") \
            .replace("!", "").replace("@", "").replace("$", "").replace("%", "").replace("^", "").replace("&", "") \
            .replace("*", "").replace("(", "").replace(")", "").replace("_", "").replace("-", "").replace("+", "") \
            .replace("=", "").replace("[", "").replace("]", "").replace("{", "").replace("}", "").replace(";", "") \
            .replace(":", "").replace("<", "").replace(">", "").replace(",", "").replace(".", "").replace("/", "") \
            .replace("?", "").replace("|", "").replace("\\", "").replace("'", "").replace("‘", "").replace("’", "") \
            .replace("“", "").replace("”", "").replace("(", "").replace(")", "").replace("=", "").replace("–", "") \
            .replace("_", "").replace("—", "").replace(" ", "").replace("¡", "").replace("¿", "").replace("3", "e") \
            .replace("$", "s").replace("1", "i").replace("0", "o").replace("ee", "e").replace("ggg", "gg")
        i= i+1
    return(text)
def has_profanity(text:str,max_lvl:int) -> tuple[bool,list[str,int]]:
    """
    Check if the given text contains profanity words based on the specified maximum level.
    
    Args:
        text (str): The input text to check for profanity.
        max_lvl (int): The maximum level of profanity to check for. Levels range from 0 to 4,
                       where 0 indicates checking for all levels of profanity and 4 indicates
                       checking for nothing.
    
    Returns:
        tuple[bool, list[str, int]]: A tuple containing a boolean indicating if profanity was found
                                      in the text and a list of profanity words along with their levels.
                                      If no profanity is found, the second element of the tuple is None.
    """
    profanities=[]
    found=[]
    text = bypass(text.lower())
    if max_lvl == 0:
        for c in PROFNITY_LVL1:
            profanities.append({f"word":c,"lvl":1})
        for i in PROFNITY_LVL2:
            profanities.append({f"word":i,"lvl":2})
        for a in PROFNITY_LVL3:
            profanities.append({f"word":a,"lvl":3})
        for b in PROFNITY_LVL4:
            profanities.append({f"word":b,"lvl":4})
    elif max_lvl == 1:
        for i in PROFNITY_LVL2:
            profanities.append({f"word":i,"lvl":2})
        for a in PROFNITY_LVL3:
            profanities.append({f"word":a,"lvl":3})
        for b in PROFNITY_LVL4:
            profanities.append({f"word":b,"lvl":4})
    elif max_lvl == 2:
        for a in PROFNITY_LVL3:
            profanities.append({f"word":a,"lvl":3})
        for b in PROFNITY_LVL4:
            profanities.append({f"word":b,"lvl":4})
    elif max_lvl == 3:
        for b in PROFNITY_LVL4:
            profanities.append({f"word":b,"lvl":4})
    elif max_lvl == 4:
        pass
    

    for i in profanities:
        word = i["word"]
        lvl = i["lvl"]
        if word in text:
            found.append([word,lvl])
    else:
        pass
        
    if found:
        return(True,found)
    else:
        return(False,None)