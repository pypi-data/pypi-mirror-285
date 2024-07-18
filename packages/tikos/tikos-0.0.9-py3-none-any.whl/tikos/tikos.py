import json
from typing import Any, List, Tuple

import requests

from .config import VER, BASE_URL_API


def Description():
    print(f"Tikos Platform {VER}")


def Version():
    print(VER)


def CreateExtractionRequest(url: str = "", orgId: str = "", orgToken: str = "", userId: str = "0",
                            numOfFiles: str = "1"):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/client/extractionrequest',
                           json={'orgId': orgId, 'token': orgToken, 'userId': userId, 'numOfFiles': numOfFiles})
    return result.status_code, result.reason, result.text

# Add Text
def AddExtractionText(url: str = "", requestId: str = "", authToken: str = "", text: str = ""):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/client/storeprocesstext',
                           json={'requestId': requestId, 'authToken': authToken, 'chunk': text})
    return result.status_code, result.reason, result.text

# Add Files
def AddExtractionFile(url: str = "", requestId: str = "", authToken: str = "", fileObj: (str, str) = None):
    if url == "":
        url = BASE_URL_API

    payload = {'requestId': requestId, 'authToken': authToken}

    files = [
        ('json', ('payload.json', json.dumps(payload), 'application/json')),
        ('file', (fileObj[0], open(fileObj[1], 'rb')))
    ]

    result = requests.post(url + '/client/addprocessfile', files=files)
    return result.status_code, result.reason, result.text

def AddExtractionFiles(url: str = "", requestId: str = "", authToken: str = "", fileObjs: [(str, str)] = None):

    rtnResponses = []
    for fileObj in fileObjs:
        rtnVal = AddExtractionFile(url=url, requestId=requestId, authToken=authToken, fileObj=fileObj)
        rtnResponses.extend(rtnVal)

    return rtnResponses

def AddExtractionFileStream(url: str = "", requestId: str = "", authToken: str = "", fileObj: (str, Any) = None):
    if url == "":
        url = BASE_URL_API

    payload = {'requestId': requestId, 'authToken': authToken}

    files = [
        ('json', ('payload.json', json.dumps(payload), 'application/json')),
        ('file', (fileObj[0], fileObj[1]))
    ]

    result = requests.post(url + '/client/addprocessfile', files=files)
    return result.status_code, result.reason, result.text

def AddExtractionFileStreams(url: str = "", requestId: str = "", authToken: str = "", fileObjs: [(str, Any)] = None):

    rtnResponses = []
    for fileObj in fileObjs:
        rtnVal = AddExtractionFileStream(url=url, requestId=requestId, authToken=authToken, fileObj=fileObj)
        rtnResponses.extend(rtnVal)

    return rtnResponses

# EXTRACT
def ProcessExtract(url: str = "", requestId: str = "", authToken: str = ""):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/processextract',
                           json={'requestId': requestId, 'authToken': authToken})
    return result.status_code, result.reason, result.text


def GetExtract(url: str = "", requestId: str = "", authToken: str = ""):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/getextract',
                           json={'requestId': requestId, 'authToken': authToken})
    return result.status_code, result.reason, result.text

def GetExtractDocs(url: str = "", requestId: str = "", authToken: str = ""):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/getextractdocs',
                           json={'requestId': requestId, 'authToken': authToken})
    return result.status_code, result.reason, result.text

def GetGraphStructure(url: str = "", requestId: str = "", authToken: str = "", orgId: str = ""):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/getextractkg',
                      json={'requestId': requestId, 'authToken': authToken, 'orgId': orgId})
    return result.status_code, result.reason, result.text

def GenerateGraph(url: str = "", requestId: str = "", authToken: str = "", fileObj: str = ""):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/generategraph',
                      json={'requestId': requestId, 'authToken': authToken, 'payload': fileObj})
    return result.status_code, result.reason, result.text


def GetGraph(url: str = "", requestId: str = "", authToken: str = ""):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/extractgraph',
                           json={'requestId': requestId, 'authToken': authToken})
    return result.status_code, result.reason, result.text

def GetGraphRelationships(url: str = "", requestId: str = "", authToken: str = "", fromNode: str = "", toNode: str = ""):
    if url == "":
        url = BASE_URL_API

    payloadJson = '{"fromEntity": "' + fromNode + '", "toEntity": "' + toNode + '"}'

    result = requests.post(url + '/internals/extractgraph',
                           json={'requestId': requestId, 'authToken': authToken, 'payload': payloadJson})
    return result.status_code, result.reason, result.text

def GenerateSC(url: str = "", requestId: str = "", authToken: str = ""):
    pass


def GetGraphRetrieval(url: str = "", requestId: str = "", authToken: str = "", retrieveQuery: str = ""):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/retrievalexplainer',
                           json={'requestId': requestId, 'authToken': authToken, 'retrieveq': retrieveQuery})
    return result.status_code, result.reason, result.text

def GetGraphRetrievalWithDS(url: str = "", requestId: str = "", authToken: str = "", retrieveQuery: str = ""):
    if url == "":
        url = BASE_URL_API

    result = requests.post(url + '/internals/retrievalexplainerds',
                           json={'requestId': requestId, 'authToken': authToken, 'retrieveq': retrieveQuery})
    return result.status_code, result.reason, result.text

