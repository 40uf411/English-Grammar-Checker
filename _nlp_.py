# -*- coding: utf-8 -*-
import nltk
#nltk.download('brown')
from nltk.corpus import brown

from pickle import load, dump
def save_output(output_path, output):
  output_file = open(output_path+'.pkl', 'wb')
  dump(output, output_file, -1)
  output_file.close()

def load_input(input_path):
  input_file = open(input_path+'.pkl', 'rb')
  input = load(input_file)
  input_file.close()
  return input

tagger = load_input('./tagger')

class TextParser:
  @staticmethod
  def parse(tokens):
    #tokens = text.split()
    return tagger.tag(tokens)

#util for list substraction..
import collections

class OrderedSet(collections.Set):
    def __init__(self, iterable=()):
        self.d = collections.OrderedDict.fromkeys(iterable)

    def __len__(self):
        return len(self.d)

    def __contains__(self, element):
        return element in self.d

    def __iter__(self):
        return iter(self.d)

#Source : https://stackoverflow.com/questions/10005367/retaining-order-while-using-pythons-set-difference

from string import punctuation

def get_tag_(sents):
  return [TextParser.parse(sent) for sent in sents]

def remove_punctuation_tokens(sents):
  return [[word for word in sent if word[0] not in punctuation+"``"+"''"]for sent in sents]

def remove_punctuation_pos(sents):
  for sent in sents:
    for index, word in enumerate(sent):
      for p in list(str(punctuation+"``"+"''")):
        if p in word[1]:
          tag = word[1]
          tag = tag.replace(p, ' ')
          updated_tuple = (word[0], tag)
          sent[index] = updated_tuple
  return sents

def clean(sents):
  new_sents = []
  for sent in sents:
    cleaned_tags = []
    for index, word in enumerate(sent):
      if(word[1] != " "):
        cleaned_tags += [elt for elt in word[1].split(" ") if elt != ""]
        
    new_sents.append(cleaned_tags)
  return new_sents
     
def get_data(sents):
  sents = remove_punctuation_tokens(sents)
  sents = get_tag_(sents)
  sents = remove_punctuation_pos(sents)
  sents = clean(sents)
  

  return sents

from nltk.util import everygrams as n_grams
#extracts n_grams from a list of sentences..
def extract_n_gram(tagged_sents, min_len=2):
  return [list(n_grams(tagged_sent, min_len)) for tagged_sent in tagged_sents]

from nltk.probability import FreqDist
#returns the frequency distribution of a list of sentences n_grams.. 
def pos_frequency_distribution(sents_n_grams):
  fdist = FreqDist()
  for n_gram_list in sents_n_grams:
    for n_gram_tuple in n_gram_list:
      fdist[n_gram_tuple] += 1
  return fdist

from nltk import Nonterminal as Nt, Production as Prod
def create_rule(fdist, prod_nbr=0):
  fdist_list = fdist.most_common(len(fdist))
  i = 0
  boolean = False
  prod = Prod(Nt(''), [])
  while(i < len(fdist)):
    max_fdist = fdist_list[i][0]
    rhs = list(max_fdist)
    if(len(rhs) == 1 and isinstance(rhs[0], Nt)):
      i += 1
    else:
      boolean = True
      break
  if(boolean):
    prod_nbr += 1
    nt = Nt('nt'+str(prod_nbr))
    prod = Prod(nt, list(max_fdist))
  return prod, prod_nbr, boolean


def get_source_rules(sents, rules):
  source = []
  rules_s = []
  rules_p = []
  new_rules = []
  for sent in sents:
    for elt in sent:
      source.append(elt)

  for prod in rules:
    if(prod.lhs() in source):
      rules_s.append(Prod(Nt('S'), list(prod.rhs())))
    else:
      rules_p.append(prod)
  
  new_rules = rules_s + rules_p
  return new_rules

def substitute(sents, prod):
  modified_sents = []
  to_be_removed = list(prod.rhs())
  nt = []
  nt.append(prod.lhs())
  tbr_len = len(to_be_removed)
  for sent in sents:
    if(len(sent) < tbr_len):
      modified_sents.append(sent)
    else:
      index = 0
      end = index + tbr_len
      while(end <= len(sent)):
        if(sent[index : end] == to_be_removed):
          sent[index : end] = nt
        index += 1
        end += 1
      modified_sents.append(sent)
  return modified_sents

def grammar_induction(sents):
  sents_temp = sents
  rulesList = []
  sourceList = []
  i = 0
  boolean = True
  first_iteration = True
  fdist_ = {}
  
  while True:
    sents_n_grams = extract_n_gram(sents_temp)
    fdist = pos_frequency_distribution(sents_n_grams)
    if first_iteration:
      fdist_ = fdist
      n_gram_nbr = len(sents_n_grams)
      first_iteration = False

    prod, i, boolean = create_rule(fdist, i)
    if(not boolean):
      break
    rulesList.append(prod)
    sents_temp = substitute(sents_temp, prod)

  return get_source_rules(sents_temp, rulesList), fdist_, n_gram_nbr

def str_(productions):
  return [str(prod) for prod in productions]

def Rf(l, p):
  return p / l

def weight(fdist, n_grams, n_gram_nbr):
  w = 1
  for n_gram in n_grams:
    if n_gram in fdist.keys():
      w *= fdist[n_gram]/n_gram_nbr
  return w

def p(n_grams, parser):
  for n_gram in reversed(n_grams):
    result = parser.parse(n_gram)
    if(result):
      for tree in result:
        print(tree)
      return len(n_gram)
  return 0
  
def precision(tokens, fdist, n_gram_nbr, parser):
  n = 0
  d = 0
  nbr_tokens = len(tokens)
  n_grams = extract_n_gram(tokens)
  for index, token in enumerate(tokens):
    n_grams_ = n_grams[index]
    w = weight(fdist, n_grams_, n_gram_nbr)
    n += (Rf(len(token), p(n_grams_, parser)) * w)
    d += w
  if(d == 0):
    return 0
  else:
    return n/d

def train(sents):
  tagged_sents = get_data(sents)
  productions, fdist, n_gram_nbr = grammar_induction(tagged_sents)
  rules = str_(productions)
  grammar = nltk.CFG.fromstring(rules)
  return grammar, fdist, n_gram_nbr

from nltk.parse.shiftreduce import ShiftReduceParser as srp
def test(tokens, grammar, fdist, n_gram_nbr):
  tagged_tokens = get_data(tokens)
  srp_parser = srp(grammar)
  p = precision(tagged_tokens, fdist, n_gram_nbr, srp_parser)
  print("Precision: ", p)
  return p

if __name__ == '__main__':
  #get training set
  sents = brown.sents(categories='adventure')[:30]

  #launch training..
  grammar, fdist, n_gram_nbr = train(sents)

  #save output
  save_output('./grammar', grammar)
  save_output('./fdist', fdist)
  save_output('./n_gram_nbr', n_gram_nbr)

  print(grammar)

  #get testing set
  tokens = brown.sents(categories='adventure')[:3]

  #load input
  grammar = load_input('./grammar')
  fdist = load_input('./fdist')
  n_gram_nbr = load_input('./n_gram_nbr')

  #launch testing..
  r = test(tokens, grammar, fdist, n_gram_nbr)
  print()