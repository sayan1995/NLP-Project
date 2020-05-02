import spacy

from spacy_wordnet.wordnet_annotator import WordnetAnnotator
from nltk.corpus import wordnet as wn

def getLemma(token):
    token._.wordnet.lemmas()
    return token

def getSynset(word):
    synList = []
    synsets = wn.synsets(word)
    for synset in synsets:
        for h in synset.hypernyms():
            for l in h.lemmas():
                synList.append(l.name())
        for h in synset.hyponyms():
            for l in h.lemmas():
                synList.append(l.name())
        for h in synset.part_meronyms():
            for l in h.lemmas():
                synList.append(l.name())
        for h in synset.member_holonyms():
            for l in h.lemmas():
                synList.append(l.name())

    return synList

def spacySynset(word):
    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')
    token = nlp(word)[0]

    #Load all synsets
    token._.wordnet.synsets()
    #load all lemmas
    token._.wordnet.lemmas()
    token._.wordnet.wordnet_domains()

    economy_domains = ['economy','linguistics']

    #Condition sysnsets of a domain
    synsets = token._.wordnet.wordnet_synsets_for_domain(economy_domains)
    lemmas_for_synset = []
    if synsets:
            for s in synsets:
                lemmas_for_synset.extend(s.lemma_names())


    return (lemmas_for_synset)

print(getSynset("buy"))