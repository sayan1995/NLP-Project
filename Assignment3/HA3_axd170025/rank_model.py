# -*- coding: utf-8 -*-
"""
@author ArpitaDutta
"""

import re
from collections import Counter
import os
import sys
import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet
import collections
from nltk.stem import WordNetLemmatizer
import time
import math as mt
import pandas as pd
import copy

def parseFileToReadRawText(filepath):
    file = open(filepath, "r", encoding="utf8")
    filecontent = file.read()
    #print(filecontent)
    #text_regex = '<TEXT>(.+?)</TEXT>'
    doc_regex = '<DOCNO>(.+?)</DOCNO>'
    docNumber = re.compile(doc_regex, re.DOTALL |  re.IGNORECASE).findall(filecontent)
    textContent = re.sub('\\<.*?>', '', filecontent)
    textContent = textContent.lower()
    file.close()
    return docNumber,textContent
    
# method to count the number of files present in a directory
def countFiles(dirname):
    return len([1 for x in list(os.scandir(dirname)) if x.is_file()])

# methid to get stopwords list from the file

def getstopwords(path):
    file = open(path, "r", encoding="utf8")
    filecontent = file.read()
    return filecontent.split()


# method to check if the token is part of stopwords list
def isPartOfStopWord(token, stopwords):
    if token in stopwords:
        return True
    return False


#method to get valid token from raw token list and removing the stopwords from the list

def getValidToken(token,stopwords):
    
    ## if token contains stop character then remove the stop character if abbreviation then compact them
    if bool(re.search(r'\.', token)):
        ## check if token is abbreviation
        if(len(token) > 1):
            token = token.replace('.','')
        else:
            return None
            

     ## if token contains possesive word them remove the possesion
    if bool(re.search(r'\'', token)):
         token = token[:token.index("\'")]
            
    if bool(re.search(r'\d', token)):
        token = None    
   ## this this point we have captured all the word we need to capture.
   ## Remove the words which are now not words
    if token is not None and bool(re.search(r'\W', token)):
        token = None
    ## if token is part of stopwords remove the token
    if isPartOfStopWord(token,stopwords):
        return None
    return token

def processTextToToken(tokenList,stopwords):
    ### 1) consider all the token to be lower case.
    ### 2) for each token check if it contain number then drop the token
    ### 3) check in the token contain hyphan then seperate the token in indivisual token
    ### 4) If token contain possesive remove 's from token
    ### 5) If token contains accronym, remove them
    ### 6) remove the stop character.
    validtokens = []
    for token in tokenList:  
        ## need to seperate this token because of having hyphen in token
        if bool(re.search(r'\-', token)):
            splitElement = token.split('-')
            for elem in splitElement:
                validToken = getValidToken(elem,stopwords)
                if validToken is not None:
                    validtokens.append(validToken)
        else:
            validToken = getValidToken(token,stopwords)
            if validToken is not None:
                validtokens.append(validToken)
            
    return validtokens

 # method to find the part of speech of a given word
def getPos( word ):
    w_synsets = wordnet.synsets(word)
    pos_counts = collections.Counter()
    pos_counts["n"] = len([ item for item in w_synsets if item.pos()=="n"])
    pos_counts["v"] = len([ item for item in w_synsets if item.pos()=="v"])
    pos_counts["a"] = len([ item for item in w_synsets if item.pos()=="a"])
    pos_counts["r"] = len([ item for item in w_synsets if item.pos()=="r"])
    
    most_common_pos_list = pos_counts.most_common(3)
    return most_common_pos_list[0][0] 


# methid to return the posting list from the query dictionary

def getPostingsList(dictionary,term): 
        return dictionary[term]["posting_list"]

# methid to create the dictionary from documents

def createDict(dictionary, termID, tokenList,docID,docLen):
    freq = Counter(tokenList)  
    maxtermFreq = max(freq.values())
    for word, termFreq in freq.items():
        if len(word) > 0:
            if word not in dictionary:
                termID += 1
                dictionary[word]={"tid": termID, "df": 1, "tf" : termFreq, 
                                "posting_list":{docID:{"maxtf":maxtermFreq,"doclen":docLen,"tf":termFreq}}}
            else:
    
                postingsList = getPostingsList(dictionary,word)
                if docID not in postingsList:
                    docFreq = dictionary[word]["df"] + 1
                    termFreqExisting = dictionary[word]["tf"]
                    maxtermFreq = maxtermFreq
                    dictionary[word]["df"] = docFreq
                    dictionary[word]["tf"] = termFreq+termFreqExisting
                    dictionary[word]["posting_list"].update({docID:{"maxtf":maxtermFreq,"doclen":docLen,"tf":termFreq}})
    
    return dictionary, termID

# method to create dictionary from Queries

def createQueryDictionary(dictionary, tokenList, QueryNo, docLen):
    count = collections.Counter(tokenList)

    maxtermFreq = max(count.values())
    #print(str(freq.items()))
    for word, termFreq in count.items():
        if len(word) > 0:
            if QueryNo not in dictionary.keys():
                dictionary[QueryNo]={word:{ "df": 1, "tf" : termFreq, 
                                 "maxtf":maxtermFreq,"doclen":docLen,"tf":termFreq}}
            else:
                dictionary[QueryNo].update({word:{"df": 1, "tf" : termFreq, 
                                 "maxtf":maxtermFreq,"doclen":docLen,"tf":termFreq}})
    
    return dictionary

def createIndex(filepath,pathStopWords):
    filesCount = countFiles(filepath) 
    wordDict = {}
    sortedDict = {}
    wordnet_lemmatizer = WordNetLemmatizer()
    termID = 0
    
    stopWordArr = getstopwords(pathStopWords)
    
    for number in range(filesCount):
        arrtoken = []
        fileNo = "0000" + str(number+1)
        docNo = fileNo[-4:]
        filePath = filepath + "/cranfield"+docNo 
        documentNo, textContent = parseFileToReadRawText(filePath)
        documentNo =(int)(documentNo[0].strip())
        tokens = textContent.split()
        tokens = processTextToToken(tokens,stopWordArr)
        for token in tokens:
            arrtoken.append(wordnet_lemmatizer.lemmatize(token,getPos(token)))
        #process the tokens to create dictionary
        wordDict, termID = createDict(wordDict, termID, arrtoken,documentNo,len(arrtoken))
    sortedDict = collections.OrderedDict(sorted(wordDict.items()))

    for stopWord in stopWordArr:
        if stopWord in sortedDict:
            del sortedDict[stopWord]
    #print(len(sortedDict))    
    return sortedDict

def createQueryIndices(pathqueries, pathStopWords):
    with open(pathqueries) as queriesFile:
        lines = queriesFile.readlines()
        
    queryArr = []
    queryDict = {}
    wordnet_lemmatizer = WordNetLemmatizer()
    stopWordArr = getstopwords(pathStopWords)
    
    queryNo = ""
    hyphenExcl = re.compile(r"[^a-zA-Z']") 
    for line in lines:
        ## if line is empty line then it is barrier between the two query
        if line in ['\n', '\r\n']:
            queryDict = createQueryDictionary(queryDict, queryArr, queryNo, len(queryArr))
            queryArr = []
            queryNo = ""
            continue
        ## check if line contain query number or not 
        if line.strip()[-1:]==":":
            queryNo = line.strip()[:-1]
            continue
        ## perform cleanup before tokenization
        line = line.replace('\n','')
        line = line.replace('-',' ') 
        line = line.replace('/',' ') 
        line = hyphenExcl.sub(" ",line)
        wordList = line.split()
        for word in wordList:
            if word.strip() not in stopWordArr:
                queryArr.append(wordnet_lemmatizer.lemmatize(word.strip(),getPos(word.strip())))
    
    ##### this loop will exclude the last query, for last query once we are out of for loop we have all data allocated
    queryDict = createQueryDictionary(queryDict, queryArr, queryNo, len(queryArr))
    
    return queryDict

## utilities for retrive text 
# method to check if the string is end start of a tag
def isEndTag(string):
    try:
        if string.index("</",0) == 0 and string.index(">",len(string)-1) == len(string)-1:
            return True
        else:
            return False
    except ValueError:
        return False

# method to fetch the text from tags in the document    
def getTextfromTag(filename, tag):
    docString = ""
    docBool = False
    text = ''
    with open(filename) as file:
        for line in file:
            if (line.strip() == "<"+tag+">" or docBool == True) and isEndTag(line.strip()) == False:                
                docBool = True
                line = line.replace("\n"," ")
                docString = docString + line
            if line.strip() == "</"+tag+">" and docBool == True:
                docBool = False
                text = docString[docString.index(">")+1:len(docString)]
                return text
            else:
                continue

def getExtDocId(docNo):
    return "cranfield"+str(docNo).rjust(4, '0')


### utility funtion to write to buffer and console accordingly 
def printBuffer(isConsole,string):
    f = open("Output.txt","a")
    if isConsole:
        print(string)
    f.write(string+"\n")
    f.close()

# generate w1 and w2 weight functions for the queries

def generateWeightFunctionForQuery(queryDict):
    t3 = time.time()
    printBuffer(True,"Generating vectors for queries ...")
    w1queryDict = {}
    w2queryDict = {}
    for queryNo in queryDict.keys():
        
        for word in queryDict[queryNo].keys():
            tf = queryDict[queryNo][word]["tf"]
            maxtf = queryDict[queryNo][word]["maxtf"]
            w1query = (0.4 + 0.6 * mt.log(tf + 0.5)/
                                   mt.log(maxtf+1.0))  
            
            w2query = (0.4 + 0.6 * (tf / (tf + 0.5 + 1.5)))
            
            if queryNo not in w1queryDict.keys():
                w1queryDict[queryNo] = {word:w1query}
            else:
                w1queryDict[queryNo].update({word:w1query})
            
            if queryNo not in w2queryDict.keys():
                w2queryDict[queryNo] = {word:w2query}
            else:
                w2queryDict[queryNo].update({word:w2query})
    
    printBuffer(True,"Generated vectors for queries "+"("+str(round(time.time() - t3, 2))+" secs)")
    return w1queryDict,w2queryDict



 # method to generate weight function for Documents
def getWeightForDocument(termDict, filesCount):
    t4 = time.time()
    w1docDict = {}
    w2docDict = {}
    totalDocLen = 0
    printBuffer(True,"Generating vectors for documents ...")
    
    for docIdx in documentDict.keys():
        totalDocLen += documentDict[docIdx]["doclen"]
        
    avgDocLen = round(totalDocLen/len(documentDict.keys()),2)


    for word in termDict.keys():
        #print("in dict")
        for docId in termDict[word]["posting_list"]:
            tf = termDict[word]["posting_list"][docId]["tf"]
            maxtf = termDict[word]["posting_list"][docId]["maxtf"]
            df = termDict[word]["df"]
            docLen = termDict[word]["posting_list"][docId]["doclen"]
            #print(str(tf) + " | " + str(maxtf) + " | " + str(df))
            w1doc = ((0.4 + 0.6 * mt.log(tf + 0.5)/
                           mt.log(maxtf+1.0)) 
                          * (mt.log(filesCount/df)/mt.log(filesCount)))
            #printOut(False,"in Doc "+str(docId) + " -- " + str(w1doc))
            w2doc = (0.4 + 0.6 * (tf / (tf + 0.5 + 1.5 *
                    (docLen / avgDocLen))) * mt.log(filesCount/df)/
                            mt.log(filesCount))
                
            if docId not in w1docDict.keys():
                w1docDict[docId] = {word:w1doc}
            else:
                w1docDict[docId].update({word:w1doc})
                
            if docId not in w2docDict.keys():
                w2docDict[docId] = {word:w2doc}
            else:
                w2docDict[docId].update({word:w2doc})    
    
    printBuffer(True,"Generated vectors for documents "+"("+str(round(time.time() - t4, 2))+" secs)")
    return w1docDict,w2docDict

# method to generate score to rank documents

def GenerateScoreMatrix(queryDictionary,w1docDict, w2queryDict):
    scorew1 = {}
    scorew2 = {}
    t5 = time.time()
    printBuffer(True,"Generating score matrix for ranking ...")
    for queryNo in queryDictionary.keys():
        
        sumOfWts = 0        
        for word in queryDictionary[queryNo].keys():
            
            if word in termDict.keys():
                for docId in termDict[word]["posting_list"].keys():

                    sumOfWts = 0
                    for term in w1docDict[docId].keys():
                        sumOfWts += w1docDict[docId][term]**2

                    try:
                        wtQueryTerm = w1queryDict[queryNo][word]
                        wtDocTerm = w1docDict[docId][word]
                    except:
                        wtQueryTerm = 0
                        wtDocTerm = 0
                    
                    if queryNo not in scorew1.keys():
                        scorew1[queryNo] = {docId:wtQueryTerm*wtDocTerm}
                    else:    
                        if docId not in scorew1[queryNo].keys():
                            scorew1[queryNo].update({docId:wtQueryTerm*wtDocTerm})
                        else:
                            prevScore = scorew1[queryNo][docId]
                            currScore = prevScore + wtQueryTerm*wtDocTerm
                            scorew1[queryNo].update({docId:currScore})
   
        for word in w2queryDict[queryNo].keys():
            sumOfWts += w2queryDict[queryNo][word]**2
        for word in queryDictionary[queryNo].keys():
            
            if word in termDict.keys():
                for docId in termDict[word]["posting_list"].keys():

                    sumOfWts = 0
                    for term in w2docDict[docId].keys():
                        sumOfWts += w2docDict[docId][term]**2

                    try:
                        wtQueryTerm = w2queryDict[queryNo][word]
                        wtDocTerm = w2docDict[docId][word]
                    except:
                        wtQueryTerm = 0
                        wtDocTerm = 0
                    
                    if queryNo not in scorew2.keys():
                        scorew2[queryNo] = {docId:wtQueryTerm*wtDocTerm}
                    else:    
                        if docId not in scorew2[queryNo].keys():
                            scorew2[queryNo].update({docId:wtQueryTerm*wtDocTerm})
                        else:
                            prevScore = scorew2[queryNo][docId]
                            currScore = prevScore + wtQueryTerm*wtDocTerm
                            scorew2[queryNo].update({docId:currScore})
                            
    printBuffer(True,"\nGenerated vectors in "+"("+str(round(time.time() - t5, 2))+" secs)")  
    return  scorew1,scorew2
    
       
if __name__ == '__main__':
    docFilePath = str(sys.argv[1])  
    pathStopWords = str(sys.argv[2]) 
    pathQueries = str(sys.argv[3])  
    filesCount = countFiles(docFilePath)  

    # for the given query generate the query dictionary 
    queryDictionary = createQueryIndices(pathQueries,pathStopWords)
    #print(len(queryDictionary))

    

    
    t1 = time.time()
    f = open("Output.txt","w")
    printBuffer(True,"\n ########################Program Run Statistics #############################\n")
    printBuffer(True,"Creating document inverted index (lemma dictionary) ...")
    termDict = createIndex(docFilePath,pathStopWords)
    
    documentDict ={}
    printBuffer(True,"Creating document dictionary ...")
    for word in termDict.keys():
        for docId in termDict[word]["posting_list"].keys():
            if docId not in documentDict:
                documentDict[docId] = {"maxtf":termDict[word]["posting_list"][docId]["maxtf"],
                                        "doclen":termDict[word]["posting_list"][docId]["doclen"]}
    
    printBuffer(True,"Created document inverted index in "+"("+str(round(time.time() - t1, 2))+" secs)")
    
    totalDocumentLen = 0
    noOfDocs = 0
    
    for docId in documentDict.keys():
        totalDocumentLen += documentDict[docId]["doclen"]
        
    avgDocLen = round(totalDocumentLen/len(documentDict.keys()),2)

    w1queryDict, w2queryDict = generateWeightFunctionForQuery(queryDictionary)
    w1docDict,w2docDict = getWeightForDocument(termDict, filesCount)
    
    t10 = time.time()
    scorew1Dict, scorew2Dict = GenerateScoreMatrix(queryDictionary,w1docDict, w2queryDict)
    
    # Calculating W1
    tempArr1 = []
    for queryNo in scorew1Dict.keys():
        for docId in scorew1Dict[queryNo].keys():
            tempArr1.append((queryNo,docId,scorew1Dict[queryNo][docId]))
    
    rankMatrixW1Df = pd.DataFrame(data=tempArr1, columns=['Q_NO','DOC','SCORE'])   

    sortedMatrixW1 = rankMatrixW1Df.sort_values(by=['Q_NO','SCORE'], ascending=False)    
    sortedMatrixW1 = sortedMatrixW1.reset_index(drop=True)
    sortedMatrixW1.assign(RANK=0)
    sortedMatrixW1.assign(EXT_DOC_ID="")
    sortedMatrixW1.assign(HEADLINE="")
    
    prevQ = ""
    currQ = ""
    rank = 0
    for idx, row in sortedMatrixW1.iterrows():
        currQ = row['Q_NO']
        if currQ != prevQ:
            rank = 1
        sortedMatrixW1.at[idx,'RANK'] = rank
        sortedMatrixW1.at[idx,'EXT_DOC_ID'] = getExtDocId(row['DOC'])
        sortedMatrixW1.at[idx,'HEADLINE'] = getTextfromTag(docFilePath
                                         + "/" +getExtDocId(row['DOC']),'TITLE')
        prevQ = row['Q_NO']
        rank += 1
            

    # Calculating W2
    tempArr2 = []
    for queryNo in scorew2Dict.keys():
        for docId in scorew2Dict[queryNo].keys():
            tempArr2.append((queryNo,docId,scorew2Dict[queryNo][docId]))
    
    rankMatrixW2Df = pd.DataFrame(data=tempArr2, columns=['Q_NO','DOC','SCORE'])   

    sortedMatrixW2 = rankMatrixW2Df.sort_values(by=['Q_NO','SCORE'], ascending=False)    
    sortedMatrixW2 = sortedMatrixW2.reset_index(drop=True)
    sortedMatrixW2.assign(RANK=0)
    sortedMatrixW2.assign(EXT_DOC_ID="")
    sortedMatrixW2.assign(HEADLINE="")
    
    prevQ = ""
    currQ = ""
    rank = 0
    for idx, row in sortedMatrixW2.iterrows():
        currQ = row['Q_NO']
        if currQ != prevQ:
            rank = 1
        sortedMatrixW2.at[idx,'RANK'] = rank
        sortedMatrixW2.at[idx,'EXT_DOC_ID'] = getExtDocId(row['DOC'])
        sortedMatrixW2.at[idx,'HEADLINE'] = getTextfromTag(docFilePath
                                        + "/"  +getExtDocId(row['DOC']),'TITLE')
        prevQ = row['Q_NO']
        rank += 1
    
    printBuffer(True,"Generated score matrix "+"in ("+str(round(time.time() - t10, 2))+" secs)")

    pd.set_option('display.max_colwidth', -1)
    for queryNo in w1queryDict.keys():
        printBuffer(True, "\n Query Number:" + queryNo + "\n")
        printBuffer(True, " Vector representation for the query (W1)")
        printBuffer(True, "------------------------------------------\n")
        vectorStr = ""
        for word in w1queryDict[queryNo].keys():
            vectorStr += word + " : " + str(w1queryDict[queryNo][word]) + " | "
            #printOut(True, word + " : " + str(w1queryDict[queryNo][word])+" | ")
        printBuffer(True,vectorStr)
        printBuffer(True,"\n")
        printBuffer(True," Rank || Score || External Document Identifier || Headline (W1)")
        printBuffer(True,"--------------------------------------------------------------\n")
        tempDf = copy.deepcopy(sortedMatrixW1[(sortedMatrixW1.RANK > 0) & (sortedMatrixW1.RANK < 6) & (sortedMatrixW1.Q_NO == queryNo)])
        printBuffer(True,tempDf[['RANK','SCORE','EXT_DOC_ID','HEADLINE']].to_string())
        
        printBuffer(True, " \nVector representation of top 5 ranked documents (W1)")
        printBuffer(True, "-------------------------------------------------------------\n")
        
        for doc in tempDf['DOC']:
            vectorStr = ""
            printBuffer(True, "Document : " + getExtDocId(doc) + "\n")
            for word in w1docDict[doc].keys():
                vectorStr += word + " : " + str(w1docDict[doc][word]) + " | "
            printBuffer(True,vectorStr)
            printBuffer(True,"\n")
        
        printBuffer(True, " \nVector representation of the query (W2)")
        printBuffer(True, "-----------------------------------------\n")
        
        vectorStr = ""
        for word in w2queryDict[queryNo].keys():
            vectorStr += word + " : " + str(w2queryDict[queryNo][word]) + " | "
            #printOut(True, word + " : " + str(w1queryDict[queryNo][word])+" | ")
        printBuffer(True,vectorStr)
        printBuffer(True,"\n")
        printBuffer(True," Rank || Score || External Document Identifier || Headline (W2)")
        printBuffer(True,"--------------------------------------------------------------\n")
        tempDf2 = copy.deepcopy(sortedMatrixW2[(sortedMatrixW2.RANK > 0) & (sortedMatrixW2.RANK < 6) & (sortedMatrixW2.Q_NO == queryNo)])
        printBuffer(True,tempDf2[['RANK','SCORE','EXT_DOC_ID','HEADLINE']].to_string())
        
        printBuffer(False, " \nVector representation for the top 5 ranked documents (W2)")
        printBuffer(False, "-------------------------------------------------------------\n")
        
        for doc in tempDf2['DOC']:
            vectorStr = ""
            printBuffer(False, "Document : " + getExtDocId(doc) + "\n")
            for word in w2docDict[doc].keys():
                vectorStr += word + " : " + str(w2docDict[doc][word]) + " | "
            printBuffer(False,vectorStr)
            printBuffer(False,"\n")

    printBuffer(True,"\n------------------------------------------------------\n")
    printBuffer(True,"Total time taken: " + str(round(time.time() - t1, 2))+" secs")

    
    