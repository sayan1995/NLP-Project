# Load your usual SpaCy model (one of SpaCy English models)
import spacy
from docx import Document
from spacy import displacy
import os
import re
import neuralcoref
nlp = spacy.load('en_core_web_sm')
neuralcoref.add_to_pipe(nlp)

from textblob import TextBlob
import textblob
doc = ''

examples = [
    u"Shelfari was a social cataloging website for books. Shelfari users built virtual bookshelves of the titles which Shelfari users owned or had read and Shelfari users could rate, review, tag and discuss Shelfari users books. Users could also create groups that other members could join, create discussions and talk about books, or other topics. Recommendations could be sent to friends on the site for what books to read. Amazon bought Shelfari in August 2008. Shelfari continued to function as an independent book social network within Amazon Amazon until January 2016, when Amazon announced that Amazon would be merging Shelfari with Goodreads and closing down Shelfari.",
    u"Deepika has a dogs. She loves him. The movie star has always been fond of animals",
    u"In May 2010, 3 months away from his 80th birthday, Buffett saids he would be succeeded at Berkshire Hathaway by a team consisting of a CEO and three or four investment managers; each of the latter would be responsible for a significant portion of Berkshire's investment portfolio. Five months later, Berkshire announced that Todd Combs, manager of the hedge fund Castle Point Capital, would join them as an investment manager. On September 12, 2011, Berkshire Hathaway announced that 50-year-old Ted Weschler, founder of Peninsula Capital Advisors, will join Berkshire in early 2012 as a second investment manager.",
    u"In 2017, Berkshire Hathaway indirectly acquired $400 million of the Toronto-based company's common shares as he gave a lifeline to the embattled mortgage lender Home Capital Group Inc.",
    u'The company is also involved in research into advanced algorithms and machine learning and their decision-making processes. To that end, the company recently released an analysis tool for how and why algorithms make decisions while scanning for biases in automated decision-making.',
    u'Shelfari was a social cataloging website for books. Shelfari users built virtual bookshelves of the titles which they owned or had read and they could rate, review, tag and discuss their books. Users could also create groups that other members could join, create discussions and talk about books, or other topics. Recommendations could be sent to friends on the site for what books to read. Amazon bought the company in August 2008. Shelfari continued to function as an independent book social network within the Amazon until January 2016, when Amazon announced that it would be merging Shelfari with Goodreads and closing down Shelfari.',
    u'Eero is a company that manufactures mesh-capable routers. The company was founded in 2015 and is based in San Francisco. Amazon announced it would buy Eero in 2019.',
    u'Jeff Bezos founded Amazon in July 1994. Jeff Bezos chose Seattle because of technical talent as Microsoft is located there. In May 1997, the organization went public. Seattle began selling music and videos in 1998, at which time Seattle began operations internationally by acquiring online sellers of books in United Kingdom and Germany. The following year, the organization also sold video games, consumer electronics, home-improvement items, software, games, and toys in addition to other items.',
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
    #nlp.get_pipe('neuralcoref').set_conv_dict(conv_dict = {'Berkshire Hathaway':['woman','actress']})
    doc = nlp(text)
    if doc._.has_coref:
        print ("Given text: " + text)
        printMentions(doc)
        #printPronounReferences(doc)
        print('Resolution')
        print(doc._.coref_resolved)
        return doc._.coref_resolved
    else:
        return text

def change_char(original_text, from_position, to_position, change_with):
        return "{}{}{}".format(original_text[:from_position],
                               change_with,
                               original_text[to_position + 1:])
def autoCorrect(text):

    from spellchecker import SpellChecker
    spell = SpellChecker()
    #print(spell.unknown(text))
    correct = {}
    for token in doc:
        if token.pos_ == 'PROPN':
            correct[token.text] = 1
            '''
            index = text.index(token.text)
            endIndex =  text.index(token.text) + len(token.text)
            correct.append((str(parser.correct()),index , endIndex-1, token.text))'''

    textblob.en.spelling.update(correct)
    parser = TextBlob(text)


    return parser.correct()


def countOrgs(text):
    global doc
    doc = nlp(text)
    orgs = [(X.text, X.label_) for X in doc.ents]
    orgDict = {}
    print(orgs)
    for company in orgs:
        if company[1] == 'ORG':
            if company not in orgDict:
                orgDict[company] = 1
            else:
                orgDict[company] += 1
    print(orgDict)
    if len(orgDict) == 0:
        return ''
    return [k for k,v in orgDict.items() if v==max(orgDict.values())][0][0]

def removeBadIdentifiers(text):
    return text.replace('()','').replace(', Inc. ,','').replace(',','').replace("'",'')
def removeDates(text):
    if re.search(r'^[I|i]n\s?\w+?\s?\d{0,4}', text):
        text = re.sub(r'^[I|i]n\s\d{0,4}', '', text).lstrip()

    if re.search(r'^[I|i]n\s\w+\s\d{0,4}', text):
        print('s')
        text = re.sub(r'^[I|i]n\s\w+\s\d{0,4}', '', text).lstrip()
    return text
def preprocess(text):
    text = removeBadIdentifiers(text)
    text = removeDates(text)
    countOrgs(text)
    if "it's" in text or "It's" in text:
        text = text.replace("it's", "its").replace("It's","Its")
    if 'the company' in text or 'The company' in text:
        text =  text.replace('the company', countOrgs(text))
    if 'the organization' in text or 'The organization' in text:
        print(countOrgs(text))
        text =  text.replace('the organization', countOrgs(text))

    return text


if __name__ == "__main__":
    '''print(os.listdir())
    os.chdir('/Users/sayan/Documents/course/spring 2020/NLP/project/NLP-Project/WikipediaArticles')
    files = os.listdir()
    i =0
    for file in files:
        if i < 18:
            i+=1
            continue
        document = Document()
        f = open("/Users/sayan/Documents/course/spring 2020/NLP/project/NLP-Project/WikipediaArticles/" + str(file), "r")
        para = f.readlines()
        for sentence in para:
            company = preprocess(sentence)
            finalText = processDoc(company)
            document.add_paragraph(finalText)
        document.save('/Users/sayan/Documents/course/spring 2020/NLP/project/NLP-Project/output' +str(file.replace('.txt','')) +'.docx')
    '''
    company = preprocess(examples[2])

    finalText = processDoc(company)
    finalText = autoCorrect(finalText)


def co_ref(text):
    finalText = preprocess(text)
    finalText = processDoc(finalText)
    finalText = autoCorrect(finalText)
    return finalText