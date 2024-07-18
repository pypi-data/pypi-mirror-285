from tikos.tikos import AddExtractionFile, AddExtractionFiles, AddExtractionFileStream, AddExtractionFileStreams, ProcessExtract, GetExtract, GetExtractDocs, GenerateGraph, GetGraphRetrievalWithDS
from typing import List
import datetime
import json
import requests

# def AddFile():
#     requestId = 'b8d1c770-2b71-4273-a768-9cebc5b87ff2'
#     authToken = '8d9f9bd7-c92f-4ce4-8f87-77180836f770'
#     # files = [('README.1.md',open('README.1.md', 'rb'))]
#     files = ('6 Legal agreement.pdf','6 Legal agreement.pdf')
#
#     rtnval = AddExtractionFile(requestId=requestId, authToken=authToken, fileObj=files)
#     print(rtnval)

# def AddFiles():
#     requestId = 'b8d1c770-2b71-4273-a768-9cebc5b87ff2'
#     authToken = '8d9f9bd7-c92f-4ce4-8f87-77180836f770'
#     # files = [('README.md','../README.md'), ('LICENSE','../LICENSE')]
#     files = [('README.md', open('../README.md', 'rb')), ('LICENSE', open('../LICENSE', 'rb'))]
#
#     rtnval = AddExtractionFileStreams(requestId=requestId, authToken=authToken, fileObjs=files)
#     print(rtnval)

# def checkfile(files: List[object]=None):
#
#     for fileObj in files:
#         name = fileObj[0]
#         fileLocation = fileObj[1]
#         print(name, fileLocation)

def processExtract():
    requestId = 'b8d1c770-2b71-4273-a768-9cebc5b87ff2'
    authToken = '8d9f9bd7-c92f-4ce4-8f87-77180836f770'

    rtnval = ProcessExtract(requestId=requestId, authToken=authToken)
    print(rtnval)
#
# def getExtract():
#     requestId = 'b8d1c770-2b71-4273-a768-9cebc5b87ff2'
#     authToken = '8d9f9bd7-c92f-4ce4-8f87-77180836f770'
#
#     s, r, t = GetExtract(requestId=requestId, authToken=authToken)
#     # print(rtnval)
#     return t

def getExtractDocs():
    requestId = 'b8d1c770-2b71-4273-a768-9cebc5b87ff2'
    authToken = '8d9f9bd7-c92f-4ce4-8f87-77180836f770'

    s, r, t = GetExtractDocs(requestId=requestId, authToken=authToken)
    # print(rtnval)
    return t

def loadGraph():
    requestId = 'b89d01f6-d388-4614-945d-79f279719be4'
    authToken = '2dfab946-883d-4121-ae44-40c57ec08c40'
    with open('payloadElement.json') as f:
        fileJ = str(f.read())

    print(fileJ)

    s, r, t = GenerateGraph(requestId=requestId, authToken=authToken, fileObj=fileJ)
    print(s, r, t)
    return t
    # return ""

def loadGraphDS():
    requestId = '111fce15-2e13-48cd-b81d-9e2bdfd2f4a9'
    authToken = 'a4f3186a-1a7c-4c56-8aca-8f6fa1add75c'
    retrieveQuery = "what is croydon council?"

    s, r, t = GetGraphRetrievalWithDS(requestId=requestId, authToken=authToken, retrieveQuery=retrieveQuery)
    print(s, r, t)
    return t
    # return ""

if __name__ == '__main__':
    start = datetime.datetime.now()
    # ViewVersion()
    # Description()
    # AddRequest()
    # AddText()
    # AddFile()
    # AddFiles()
    # processExtract()
    # txtDocs = getExtract()
    # txtDocs = getExtractDocs()
    # #
    #
    # if len(txtDocs) > 0:
    #     jsonfy = json.loads(txtDocs)
    #     for doc in jsonfy:
    #         print(doc)

    # GRAPH Extract
    # t = loadGraph()
    # print(t)

    t = loadGraphDS()
    print(t)

    end = datetime.datetime.now()
    print(end - start)
    print(f"start:{start}, end:{end}")