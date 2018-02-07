import json
from requests import get
import os.path
import sys

nGramSize = 7
letterPairJSON = {}

def insertInDictionary(gender, letterPair):
    global letterPairJSON
    if letterPair in letterPairJSON[gender]:
        letterPairJSON[gender][letterPair] = int(letterPairJSON[gender][letterPair]) + 1
    else :
        letterPairJSON[gender][letterPair] = 1

def downloadSpellchecker():
    url = "https://dictionary.spellchecker.lu/output/lb_LU_morph.dic"
    fileName = "lb_LU_morph.dic"
    with open(fileName, "wb") as file:
        response = get(url)
        file.write(response.content)

def generateJSON():
    global letterPairJSON, nGramSize
    masculineLetterPairs = {}
    feminineLetterPairs = {}
    neutralLetterPairs = {}
    letterPairJSON["masculine"] = masculineLetterPairs
    letterPairJSON["feminine"] = feminineLetterPairs
    letterPairJSON["neutral"] = neutralLetterPairs
    with open("lb_LU_morph.dic") as f:
        for line in f:
            nGramSizeFlexible = nGramSize
            gender = getGenderOfWord(line.rstrip())
            if gender:
                word = list(line.rstrip().split(" ")[0].split("/")[0].lower())
                if len(word) < nGramSize:
                    nGramSizeFlexible = len(word)
                for i in range(1,nGramSizeFlexible+1):
                    letterPair = "".join(word[-i:])
                    insertInDictionary(gender, letterPair)
    with open("letterPairJSON.json", 'w') as outputfile:
        json.dump(letterPairJSON, outputfile, ensure_ascii=False)

def getGenderOfWord(word):
    try:
        tsSplit = word.split("ts:")[1]
        result = None
        if tsSplit:
            if "masculine_" in tsSplit:
                result = "masculine"
            elif "feminine_" in tsSplit:
                result = "feminine"
            elif "neutral_" in tsSplit:
                result = "neutral"
        return result
    except IndexError:
        return None

def getNumberInJSON(gender, letterPair):
    global letterPairJSON
    if letterPair in letterPairJSON[gender]:
        return letterPairJSON[gender][letterPair]
    else:
        return 0

def tellGender(word):
    global letterPairJSON, nGramSize
    original = word
    word = word.lower()
    if "/" in word:
        word = word.split("/")[0]
    masculine = {}
    feminine = {}
    neutral = {}
    result = {}
    masculine["number"] = 0
    masculine["percentage"] = 0
    feminine["number"] = 0
    feminine["percentage"] = 0
    neutral["number"] = 0
    neutral["percentage"] = 0
    result["masculine"]=masculine
    result["feminine"]=feminine
    result["neutral"]=neutral
    result["total"]=0
    result["highest"]=[]
    result["word"]=original
    nGramSizeFlexible = nGramSize
    if len(word) < nGramSize:
        nGramSizeFlexible = len(word)
    for i in range(nGramSizeFlexible,1,-1):
        letterPair = "".join(word[-i:])
        result["masculine"]["number"] += getNumberInJSON("masculine", letterPair)
        result["feminine"]["number"] += getNumberInJSON("feminine", letterPair)
        result["neutral"]["number"] += getNumberInJSON("neutral",letterPair)
        if result["masculine"]["number"] != 0 or result["feminine"]["number"] != 0 or result["neutral"]["number"] != 0:
            break

    result["total"] = result["masculine"]["number"] + result["feminine"]["number"] + result["neutral"]["number"]
    for key in ["masculine","feminine","neutral"]:
        if result[key]["number"] == 0 or result["total"] == 0:
            result[key]["percentage"] = 0
        else:
            result[key]["percentage"] = result[key]["number"] / result["total"]
    highest = max(result["masculine"]["number"], result["feminine"]["number"], result["neutral"]["number"])
    for key in ["masculine","feminine","neutral"]:
        if highest == result[key]["number"]:
            result["highest"].append(key)
    return result

def __init__():
    global letterPairJSON
    if not os.path.isfile("lb_LU_morph.dic"):
        downloadSpellchecker()
    if not os.path.isfile("letterPairJSON.json"):
        generateJSON()
    if not letterPairJSON:
        with open("letterPairJSON.json", 'r') as inputfile:
            letterPairJSON=json.load(inputfile)

__init__()

if __name__ == "__main__":
    if sys.argv[1]):
        print(tellGender(sys.argv[1]))
