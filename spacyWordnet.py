import spacy

from spacy_wordnet.wordnet_annotator import WordnetAnnotator

def getLemma(token):
    token._.wordnet.lemmas()
    return token

def getSynset(word):

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