import spacy
from nltk import pos_tag
from nltk.tokenize import word_tokenize,sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
#from spacy import displacy 

f2 = open('ouput1.txt', 'w')

def dependency(sentences):
    print('----Dependency parsing----')
    nlp = spacy.load("en_core_web_sm")
    #TODO
    #Add
    sentenceDict = {}
    for sentence in sentences:
        doc = nlp(sentence)
        tokenDict = {}
        for token in doc:
            tokenDict[token] = [token.text, token.dep_, token.head.text, token.head.pos_,
                  [child for child in token.children]]
        sentenceDict[sentence] = tokenDict
        #displacy.serve(doc, style="dep") 
    write('Dependency parsing', sentenceDict)

    return sentenceDict

def write(type,text):
    f2.write('--------------'+type+'------\n')
    f2.write(str(text))
    f2.write('\n-----------------------------------------------------\n')

def tokenize(text):
    print('----Tokenize the sentences into words----')
    tokens =  word_tokenize(text)
    write('Tokenize the sentences into words',tokens)
    return tokens

def sentences(text):
    print('----Spliting the document into sentences----')
    sentenceList = sent_tokenize(text)
    write('Spliting the document into sentences',sentenceList)
    return sentenceList

def lemmatize(tokens):
    print('----Lemmatize the words to extract lemmas as features----')
    lemmatizer = WordNetLemmatizer()
    lemmaDict = {}
    for token in tokens:
        lemma = lemmatizer.lemmatize(token)
        lemmaDict[token] = lemma

    write('Lemmatize the words to extract lemmas as features', lemmaDict)

def posTagging(tokens):
    print('----Part-of-speech (POS) tag the words to extract POS tag features----')
    posTag = pos_tag(tokens)

    write('Part-of-speech (POS) tag the words to extract POS tag features', posTag)
    return posTag

def wordnet(tokens):
    wordDict = {}
    tokens = ['buy']
    for token in tokens:
        hypernymns = []
        hyponyms = []
        meronyms =[]
        holonyms = []
        synsets = wn.synsets(token)
        for synset in synsets:
            for h in synset.hypernyms():
                for l in h.lemmas():
                    hypernymns.append(l.name())
            for h in synset.hyponyms():
                for l in h.lemmas():
                    hyponyms.append(l.name())
            for h in synset.part_meronyms():
                for l in h.lemmas():
                    meronyms.append(l.name())
            for h in synset.member_holonyms():
                for l in h.lemmas():
                    holonyms.append(l.name())
        wordDict[token] = {
            'hypernymns': hypernymns,
            'hyponyms':hyponyms,
            'meronyms':meronyms,
            'holonyms':holonyms
        }
    write('Using WordNet, extract hypernymns, hyponyms, meronyms, AND holonyms',wordDict)
    return wordDict


if __name__ == "__main__":
    print('--------Start---------')
    #nlp = spacy.load('en_core_web_sm')
    f1 = open('input.txt','r')
    text = f1.read()
    sentences = sentences(text)
    tokens = tokenize(text)
    lemma = lemmatize(tokens)
    pos = posTagging(tokens)
    wordNet = wordnet(tokens)
    dependency(sentences)
    print('--------Done----------')