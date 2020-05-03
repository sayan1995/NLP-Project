# Load your usual SpaCy model (one of SpaCy English models)
import spacy
from docx import Document
from spacy import displacy
from spellchecker import SpellChecker
import os
import re
import neuralcoref


doc = ''

examples = [
    u"Abraham Thomas Lincoln (February 12, 1809 – April 15, 1865) was an American statesman, politician, and lawyer who served as the 16th president of the United States from 1861 until his assassination in April 1865. Lincoln led the nation through the American Civil War, its bloodiest war and its greatest moral, constitutional, and political crisis. He preserved the Union, abolished slavery, strengthened the federal government, and modernized the U.S. economy.",
    u"Born in Kentucky, Lincoln grew up on the frontier in a poor family. Self-educated, he became a lawyer, Whig Party leader, state legislator and Congressman. He left government to resume his law practice, but angered by the success of Democrats in opening the prairie lands to slavery, reentered politics in 1854. He became a leader in the new Republican Party and gained national attention in 1858 for debating and losing to national Democratic leader Stephen A. Douglas in a Senate campaign. He then ran for President in 1860, sweeping the North and winning. Southern pro-slavery elements took his win as proof that the North was rejecting the Constitutional rights of Southern states to practice slavery. They began the process of seceding from the union. To secure its independence, the new Confederate States of America fired on Fort Sumter, one of the few U.S. forts in the South. Lincoln called up volunteers and militia to suppress the rebellion and restore the Union.",
    u"Lincoln's farm is big. He loved it.",
    u"In a March 2014 interview, Apple designer Jonathan Ive used the iPhone as an example of Apple's ethos of creating high-quality, life-changing products. He explained that the phones are comparatively expensive due to the intensive effort that is used to make the phones:",
    u"Apple's success during this period was evident in its stock price. Between early 2003 and 2006, the price of Apple's stock increased more than tenfold, from around $6 per share (split-adjusted) to over $80. In January 2006, Apple's market cap surpassed that of Dell. Nine years prior, Dell's CEO Michael Dell had said that 'if he ran Apple he would shut it down and give the money back to the shareholders'. Although Apple's market share in computers had grown, it remained far behind its competitor Microsoft Windows, accounting for about 8% of desktops and laptops in the US.",
    u"In 1984, Apple launched the Macintosh, the first personal computer to be sold without a programming language. Apple debut was signified by 1984, a $1.5 million television advertisement directed by Ridley Scott that aired during the third quarter of Super Bowl XVIII on January 22, 1984. This is now hailed as a watershed event for Apple's success and was called a masterpiece by CNN and one of the greatest TV advertisements of all time by TV Guide.",
    u"Jobs was immediately convinced that all future computers would use a graphical user interface (GUI), and development of a GUI began for the Apple Lisa. In 1982, however, he was pushed from the Lisa team due to infighting. Jobs then took over Wozniak's and Raskin's low-cost-computer project, the Macintosh, and redefined it as a graphical system cheaper and faster than Lisa. In 1983, Lisa became the first personal computer sold to the public with a GUI, but was a commercial failure due to its high price and limited software titles, so in 1985 it would be repurposed as the high end Macintosh and discontinued in its second year.",
    u"The financial performance of the company is reported to shareholders on an annual basis and a matter of public record. The unit (except where noted) is billions of US dollars.",
    u"In May 2010, 3 months away from his 80th birthday, Buffett saids he would be succeeded at Berkshire Hathaway by a team consisting of a CEO and three or four investment managers; each of the latter would be responsible for a significant portion of Berkshire's investment portfolio. Five months later, Berkshire announced that Todd Combs, manager of the hedge fund Castle Point Capital, would join them as an investment manager. On September 12, 2011, Berkshire Hathaway announced that 50-year-old Ted Weschler, founder of Peninsula Capital Advisors, will join Berkshire in early 2012 as a second investment manager.",
    u"In 2017, Berkshire Hathaway indirectly acquired $400 million of the Toronto-based company's common shares as he gave a lifeline to the embattled mortgage lender Home Capital Group Inc.",
    u'The company is also involved in research into advanced algorithms and machine learning and their decision-making processes. To that end, the company recently released an analysis tool for how and why algorithms make decisions while scanning for biases in automated decision-making.',
    u'Shelfari was a social cataloging website for books. Shelfari users built virtual bookshelves of the titles which they owned or had read and they could rate, review, tag and discuss their books. Users could also create groups that other members could join, create discussions and talk about books, or other topics. Recommendations could be sent to friends on the site for what books to read. Amazon bought the company in August 2008. Shelfari continued to function as an independent book social network within the Amazon until January 2016, when Amazon announced that it would be merging Shelfari with Goodreads and closing down Shelfari.',
    u'Eero is a company that manufactures mesh-capable routers. The company was founded in 2015 and is based in San Francisco. Amazon announced it would buy Eero in 2019.',
    u'Jeff Bezos founded Amazon in July 1994. Jeff Bezos chose Seattle because of technical talent as Microsoft is located there. In May 1997, the organization went public. Seattle began selling music and videos in 1998, at which time Seattle began operations internationally by acquiring online sellers of books in United Kingdom and Germany. The following year, the organization also sold video games, consumer electronics, home-improvement items, software, games, and toys in addition to other items.',
    u'ComiXology is a cloud-based digital comics platform with over 200 million comic downloads as of September 2013. It offers a selection of more than 40,000 comic books and graphic novels across Android, iOS, Fire OS and Windows 8 devices and over a web browser. Amazon bought the company in April 2014.',
    u'Shelfari users built virtual bookshelves of the titles which Shelfari users owned or had read and Shelfari users could rate review tag and discuss Shelfari users books. Users could also create groups that other members could join create discussions and talk about books or other topics. Recommendations could be sent to friends on the site for what books to read. Amazon bought the company in August 2008.',
]

people = []

import spacy
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span


class EntityMatcher(object):
    name = 'entity_matcher'

    def __init__(self, nlp, terms, label):
        patterns = [nlp(term) for term in terms]
        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add(label, None, *patterns)

    def __call__(self, doc):
        matches = self.matcher(doc)
        spans = []
        for label, start, end in matches:
            span = Span(doc, start, end, label=label)
            spans.append(span)
        doc.ents = spans
        return doc

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
def getPerson(text):
    global people
    doc = nlp(text)
    orgs = [(X.text, X.label_) for X in doc.ents]
    for person in orgs:
        if person[1] == 'PERSON':
            people.append(person[0])
    print(people)
    for person in people:
        if person in text:
            continue

        subWord = person.split(' ')
        for word in subWord:
            if word in text:
                print('------',word)
                regexWord = r'\bword\b'.replace('word',word)
                #text = re.sub(regexWord,person,text)
                text = text.replace(word,person)

                print(text)
                break
    return text
def personsAndOrgs(text):
    doc = nlp(text)
    orgs = [(X.text, X.label_) for X in doc.ents]
    orgDict = {}
    print(orgs)
    for company in orgs:
        if company[1] == 'PERSON':
            if company not in orgDict:
                orgDict[company[0]] = [company[1]]
            else:
                if company[1] not in orgDict[company[0]]:
                    orgDict[company[0]].append(company[1])
    print(orgDict)
    return orgDict

def processDoc(text):
    nlp.get_pipe('neuralcoref').set_conv_dict(conv_dict = {"Lincoln":['PESRON','HUMAN','man','president']})


    doc = nlp(text)


    if doc._.has_coref:
        print ("Given text: " + text)
        #printMentions(doc)
        #printPronounReferences(doc)
        print('Resolution')
        #print(doc)
        return doc._.coref_resolved
    else:
        return text

def change_char(original_text, from_position, to_position, change_with):
        return "{}{}{}".format(original_text[:from_position],
                               change_with,
                               original_text[to_position + 1:])
def autoCorrect(text):
    global doc
    #remove duplicate words back to back
    text = re.sub(r'\b(.+)(\s+\1\b)+', r'\1', text)
    correct = []
    dictionary = []
    doc = nlp(text)
    spell = SpellChecker(case_sensitive=True)
    for token in doc:
        #print(token.pos_, token.text)
        if token.pos_ != 'PROPN' or token.pos_ != 'DET' or token.pos_ != 'NUM':
            dictionary.append(token.text)
            corrects = (str(spell.correction(token.text)))
            index = text.index(token.text)
            endIndex =  text.index(token.text) + len(corrects)
            correct.append((corrects,index , endIndex-1, text))


    for token in correct:
        text = change_char(token[3],token[1],token[2],token[0])
    print(text)
    #textblob.en.spelling.update(correct)
    #parser = TextBlob(text)
    #spell = SpellChecker()

    return text


def countOrgs(text):
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
    print('---')
    if len(orgDict) == 0:
        return ''
    return [k for k,v in orgDict.items() if v==max(orgDict.values())][0][0]

def removeBadIdentifiers(text):
    #.replace(',','').replace('"','')
    return text.replace('()','').replace(', Inc. ,','')

def removeDates(text):
    if re.search(r'^[I|i]n\s?\w+?\s?\d{0,4}', text):
        text = re.sub(r'^[I|i]n\s?\w+?\s?\d{0,4}', '', text).lstrip()

    if re.search(r'^[I|i]n\s\w+\s\d{0,4}', text):
        print('s')
        text = re.sub(r'^[I|i]n\s\w+\s\d{0,4}', '', text).lstrip()
    return text
def preprocess(text):
    text = removeBadIdentifiers(text)
    text = removeDates(text)
    #text = getPerson(text)
    countOrgs(text)
    if "it's" in text or "It's" in text:
        text = text.replace("it's", "its").replace("It's","Its")
    if 'the company' in text or 'The company' in text:
        if countOrgs(text) !='':
            text =  text.replace('the company', countOrgs(text))
    if 'the organization' in text or 'The organization' in text:
        if countOrgs(text)!='':
            text =  text.replace('the organization', countOrgs(text))

    return text

def co_ref(text):
    nlp = spacy.load('en_core_web_sm')
    neuralcoref.add_to_pipe(nlp)
    #nlp = spacy.load('en_core_web_sm')
    neuralcoref.add_to_pipe(nlp)
    finalText = preprocess(text)
    finalText = processDoc(finalText)
    finalText = autoCorrect(finalText)
    return finalText

if __name__ == "__main__":

    nlp = spacy.load('en_core_web_sm')
    neuralcoref.add_to_pipe(nlp)

    '''print(os.listdir())
    os.chdir('/Users/sayan/Documents/course/spring 2020/NLP/project/NLP-Project/WikipediaArticles')
    files = os.listdir()
    i =0
    '''

    '''
    files = ["AbrahamLincoln.txt"]
    for file in files:
        document = Document()
        f = open("/Users/sayan/Documents/course/spring 2020/NLP/project/NLP-Project/WikipediaArticles/" + str(file), "r")
        para = f.readlines()
        for sentence in para:
            company = preprocess(sentence)
            finalText = processDoc(company)
            document.add_paragraph(finalText)
        document.save('/Users/sayan/Documents/course/spring 2020/NLP/project/NLP-Project/output' +str(file.replace('.txt','')) +'.docx')
    '''
    #co_ref(examples[0])

    #nlp = en_coref_md.load()
    '''patterns = [
        {"label": "PERSON", "pattern": [{"lower": "Lincoln"}, {"lower": "lincoln"}]}
    ]
    ruler = EntityMatcher(nlp,['Lincoln'],'PERSON')
    nlp.add_pipe(ruler)
    print(nlp.pipe_names)


    doc = nlp("Lincoln is a good boy.")
    print(doc.ents)
    print([(ent.text, ent.label_) for ent in doc.ents])

    company = preprocess(examples[0])

    finalText = processDoc(company)
    finalText = autoCorrect(finalText)
    print(finalText)

    company = preprocess(examples[1])

    finalText = processDoc(company)
    finalText = autoCorrect(finalText)
    print(finalText)'''
