import json

def loadFile(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def makeFile(path):
    data = {"metaData": {}, "data": {}}
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    return data

def updateFile(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=4)