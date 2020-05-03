from nltk.corpus import wordnet as wn

syn = wn.synsets('staff')
print(syn)
print ("Synset name :  ", syn.name())

print ("\nSynset abstract term :  ", syn.hypernyms())

print ("\nSynset specific term :  ",
       syn.hypernyms()[0].hyponyms())

print ("\nSynset root hypernerm :  ", syn.root_hypernyms())

print("\nSynset root holonym", syn.member_holonyms())

print("\nSynset root meronym", syn.part_meronyms())