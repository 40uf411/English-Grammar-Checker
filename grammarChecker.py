import _nlp_

class GrammarChecker:
    grammar = _nlp_.load_input('./grammar')
    fdist = _nlp_.load_input('./fdist')
    n_gram_nbr = _nlp_.load_input('./n_gram_nbr')
    
    grammarFile = '' # location of the grammar file
    grammar = dict() # grammar a dict() or a list()

    @staticmethod
    def extractGrammar(filename):
        GrammarChecker.grammarFile = filename
        # the instraction
        GrammarChecker.grammar = None
        return GrammarChecker.grammar

    @staticmethod
    def checkGrammar(taggedTokens):
        isValid = [True, True, True, True]
        # do the treatment
        return isValid