
def underscoreToCamel(underscoreStr : str) -> str:
    if not underscoreStr:
        return underscoreStr
    words = underscoreStr.split("_")
    while len(words[0]) == 0:
        words.pop(0)
    result = words[0]
    for i in range(1, len(words)):
        result += words[i].capitalize()
    return result   