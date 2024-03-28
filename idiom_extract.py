import json
import spacy
from difflib import SequenceMatcher
import sys

dataset_path='idiom_repository_all.json'
with open(dataset_path,"r",encoding="UTF-8") as file:
    data=json.load(file)


nlp = spacy.load("en_core_web_sm")


def tag_idioms(phrase,pos, dataset):
    doc1=nlp(phrase)
    maxscore=0.84 if len(phrase.split())==2 else 0.67; #more accuracy for 2 word phrases
    idiom=None
    for idiom_data in dataset:
        i = idiom_data["idiom"]
        score=SequenceMatcher(None, i.lower(), phrase.lower()).ratio()
        if maxscore<score:
            maxscore=score
            idiom=i
    return idiom

def reduce_dataset(dataset,pos):
    newdataset=[]
    for idiom in dataset:
        if idiom['entry']:
           for entry_pos in idiom['entry']:
               if pos in entry_pos['pos']:
                   newdataset.append(idiom)
    return newdataset

verb_dataset= reduce_dataset(data,'verb')
noun_dataset= reduce_dataset(data,'noun')


def verb_chunks(doc):
    chunks=set()
    for token in doc:
        if token.pos_ in ['AUX','VERB']:
            subtree=[node for node in token.subtree]
            arcwords=[]
            for child in subtree[subtree.index(token):]:
                arcwords.append(child.text)
                if child.dep_ in (['dobj','attr','aux','prt'] if  token.dep_ =='ROOT' else ['dobj','attr','prt']):
                    break
            if token.dep_ =='ROOT' or token.dep_=='advcl':
                chunks.add(' '.join([right.text for right in subtree[subtree.index(token):]]))
            chunks.add(' '.join(arcwords))
    return list() if chunks==set() else list(chunks)

def fetch_phrases(sentence):
    doc=nlp(sentence)
    phrases={'noun':set(),'verb':[]}
    #noun phrase
    for chunk in doc.noun_chunks:
        phrases['noun'].add(chunk.text)
    phrases['noun'] = list(phrases['noun'])
    #verb phrase
    phrases['verb']=verb_chunks(doc)
    return phrases


def process_text(text):
    doc = nlp(text)
    idioms=[]
    for sentence in doc.sents:
        phrases=fetch_phrases(sentence.text)
        print(f'My phrases : \n {phrases}')
        for pos in phrases:
            posdataset={}
            if pos=='noun':
                posdataset=noun_dataset
            elif pos=='verb':
                posdataset=verb_dataset
            for p in phrases[pos]:
                i=tag_idioms(p,pos,posdataset)
                if i:
                    idioms.append(i)
    return idioms


with open(sys.argv[1],'r',encoding='UTF-8') as file:
	text=file.read()



print(process_text(text))



