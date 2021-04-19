from string import punctuation
import nltk
nltk.download('punkt')
from pickle import load
input = open('tagger.pkl', 'rb')
tagger = load(input)
input.close()

class TextTokenizing:
    @staticmethod
    def parse(text):
        sents = nltk.sent_tokenize(text)
        sents = [nltk.word_tokenize(sent) for sent in sents]
        return [[word for word in sent if word not in punctuation+"`"+"'"]for sent in sents]