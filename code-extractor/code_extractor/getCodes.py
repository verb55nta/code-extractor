import re

import requests
from bs4 import BeautifulSoup


def getDocumentBodyFromURL(url):
    res = requests.get(url)
    return res.text


def getDocumentBodyFromFile(filepath):
    with open(filepath, "rb") as f:
        return f.read().decode('sjis')


def getMessages(html_str):
    obj = BeautifulSoup(html_str, 'html.parser')
    return obj.find_all('div', class_='message')


def getCodes(filepath=None, url=None, sortOps=False):
    if filepath is not None:
        html_str = getDocumentBodyFromFile(filepath)
    elif url is not None:
        html_str = getDocumentBodyFromURL(url)
    else:
        ValueError('Please input filepath or url')

    codeDict = {}
    codeDictCache = {}
    dropList = ["RSI", "PSR", "NHK", "EV", "ETF", "REIT", "NISA"]

    obj = BeautifulSoup(html_str, 'html.parser')
    obj = obj.find_all('div', class_='message')

    for i, ob in enumerate(obj):
        rawText = ob.text
        code = ""
        codeDictCache = {}
        for i in range(len(rawText)):
            c = rawText[i]
            if (c >= 'A' and c <= 'Z') or (c >= 'a' and c <= 'z') or c == '.' or c == ':' or c == '/':
                code += c
            else:
                if len(code) > 0 and len(code) <= 4 and code.isalpha():
                    code = code.upper()
                    if code not in codeDict:
                        codeDict[code] = 1
                    elif code not in codeDictCache:
                        codeDict[code] += 1
                codeDictCache[code] = 1
                code = ""

    for d in dropList:
        if d in codeDict:
            codeDict.pop(d)

    res = []
    for k, v in codeDict.items():
        res.append((v, k))

    if sortOps:
        return sorted(res)[::-1]

    return res
