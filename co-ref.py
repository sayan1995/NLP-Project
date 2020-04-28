# Load your usual SpaCy model (one of SpaCy English models)
import spacy
from spacy import displacy
from collections import Counter

nlp = spacy.load('en_core_web_sm')

# Add neural coref to SpaCy's pipe
import neuralcoref


examples = [
    u'My sister has a dog and she loves him.',
    u'My sister has a dog and she loves him. He is cute.',
    u'My sister has a dog and she loves her.',
    u'My brother has a dog and he loves her.',
    u'Mary and Julie are sisters. They love chocolates.',
    u'John and Mary are neighbours. She admires him because he works hard.',
    u'ComiXology is a cloud-based digital comics platform with over 200 million comic downloads as of September 2013. It offers a selection of more than 40,000 comic books and graphic novels across Android, iOS, Fire OS and Windows 8 devices and over a web browser. Amazon bought the company in April 2014.',
    u'Shelfari users built virtual bookshelves of the titles which Shelfari users owned or had read and Shelfari users could rate review tag and discuss Shelfari users books. Users could also create groups that other members could join create discussions and talk about books or other topics. Recommendations could be sent to friends on the site for what books to read. Amazon bought the company in August 2008.',
]


def printMentions(doc):
    print ('\nAll the "mentions" in the given text:')
    for cluster in doc._.coref_clusters:
        print (cluster.mentions)

def printPronounReferences(doc):
    print ('\nPronouns and their references:')
    for token in doc:
        if  token._.in_coref:
            for cluster in token._.coref_clusters:
                print (token.text + " => " + cluster.main.text)

def processDoc(text):
    neuralcoref.add_to_pipe(nlp)
    doc = nlp(text)
    if doc._.has_coref:
        print ("Given text: " + text)
        printMentions(doc)
        #printPronounReferences(doc)
        print('Resolution')
        print(doc._.coref_resolved)

def countOrgs(text):
    doc = nlp(text)
    orgs = [(X.text, X.label_) for X in doc.ents]
    orgDict = {}
    for company in orgs:
        if company not in orgDict:
            orgDict[company] = 1
        else:
            orgDict[company] += 1

    return [k for k,v in orgDict.items() if v==max(orgDict.values())][0][0]

def preprocess(text):
    if 'the company' in text:
        return text.replace('the company', countOrgs(text))

if __name__ == "__main__":
    company = preprocess(examples[6])
    if company !=None:
        processDoc(company)
    else:
        processDoc(examples[6])



