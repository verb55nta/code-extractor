import json
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# from datetime import


def getDocumentBodyFromURL(url):
    res = requests.get(url)
    return res.text


def getDocumentBodyFromFile(filepath):
    with open(filepath, "rb") as f:
        return f.read().decode('sjis')


def getMessages(html_str):
    obj = BeautifulSoup(html_str, 'html.parser')
    return obj.find_all('div', class_='message')


def getCodes(html_str=None, filepath=None, url=None, sortOps=True):

    if html_str is None:
        if filepath is not None:
            html_str = getDocumentBodyFromFile(filepath)
        elif url is not None:
            html_str = getDocumentBodyFromURL(url)
        else:
            ValueError('Please input filepath or url')

    obj = BeautifulSoup(html_str, 'html.parser')
    obj = obj.find_all('div', class_='message')

    codeDict = {}
    codeDictCache = {}
    dropList = ["RSI", "PSR", "NHK", "EV",
                "ETF", "REIT", "NISA", "SBI", "W", "VIX", "HTTP", "WWW", "WW", "IPO"]

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


def getThreadTime(html_str):
    obj = BeautifulSoup(html_str, 'html.parser')

    obj = obj.find_all('span', class_='date')

    start_time = obj[0].text
    end_time = obj[max(len(obj) - 3, 0)].text

    pattern = r'\d+'

    time_list = []
    for time_text in (start_time, end_time):
        res = re.findall(pattern, time_text)
        year = int(res[0])
        month = int(res[1])
        day = int(res[2])
        hour = int(res[3])
        minute = int(res[4])
        second = int(res[5])
        time_list.append(datetime(year, month, day, hour=hour,
                                  minute=minute, second=second))

    return tuple(time_list)


def digURL(url):
    html_str = getDocumentBodyFromURL(url)
    obj = BeautifulSoup(html_str, 'html.parser')
    title = obj.find('title').text
    obj = obj.find_all('div', class_='message')

    start_time, end_time = getThreadTime(html_str)

    codes = getCodes(html_str=html_str)

    number = int(re.sub(r"\D", "", title))
    dump_for_json = {}
    dump_for_json["url"] = url
    dump_for_json["number"] = number

    time_format = "%Y-%m-%dT%H:%M:%S"
    dump_for_json["start_time"] = start_time.strftime(time_format)
    dump_for_json["end_time"] = end_time.strftime(time_format)
    dump_for_json["codes"] = {}
    for c in codes:
        dump_for_json["codes"][c[1]] = c[0]
    file_template = "json/{}.json"
    with open(file_template.format(number), 'w') as f:
        json.dump(dump_for_json, f, indent=2, ensure_ascii=False)
        print("make {}".format(file_template.format(number)))

    prev = obj[0].find_all('a')
    return digURL(prev[-1].text)
