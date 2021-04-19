import os
import re
from flask import Flask, request, json
from grammarChecker import GrammarChecker
from parser import TextTokenizing
import _nlp_

app = Flask(__name__)

@app.route('/')
def home():
    file = ''
    with open('./static/html/home.html', 'r') as file:
        html = file.read()
    return html

@app.route('/check', methods=['POST', 'GET'])
def check():
    text = request.form.get('text')
    print(text)
    taggedTokens = TextTokenizing.parse(text)
    print(taggedTokens)
    # execute the testing process
    p = [ 0 < _nlp_.test([taggedToken], GrammarChecker.grammar, GrammarChecker.fdist, GrammarChecker.n_gram_nbr) for taggedToken in taggedTokens]
    #r = GrammarChecker.checkGrammar(taggedTokens)
    result = False not in p
    sents = list()
    for i in range(len(p)):
        if not p[i]:
            sents.append(' '.join(taggedTokens[i]))
    
    data = {'result': result, 'errors': sents}
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/train', methods=['POST', 'GET'])
def train():
    text = request.form.get('text')
    print(text)
    taggedTokens = TextTokenizing.parse(text)
    print(taggedTokens)
    # execute the training process
    grammar, fdist, n_gram_nbr = _nlp_.train(taggedTokens)
    GrammarChecker.grammar = grammar
    GrammarChecker.fdist = fdist
    GrammarChecker.n_gram_nbr = n_gram_nbr
    
    result = GrammarChecker.checkGrammar(taggedTokens)
    print(result)
    data = {'result': result}
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response

if __name__ == '__main__':
    app.run()