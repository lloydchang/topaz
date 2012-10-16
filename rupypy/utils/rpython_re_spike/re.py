# re module

import os
from pypy.rlib.parsing.ebnfparse import parse_ebnf, make_parse_function
from pypy.rlib.parsing.lexer import Lexer
from pypy.rlib.parsing.parsing import PackratParser, Rule

with open(os.path.join(os.path.dirname(__file__), "oniguruma_ebnf.txt")) as f:
    ebnf = f.read()

from pprint import pprint
regexs, rules, ToAST = parse_ebnf(ebnf)
names, regexs = zip(*regexs)
lexer = Lexer(list(regexs), list(names), ignore=[])

# regex needs to be passed as a raw string
# TODO: find a way to convert input to a raw string
def compile(regex, flag=0):
    regex = save_number_references(regex)
    print repr(regex)
    
    t = lexer.tokenize(regex, False)
    pprint(t)

    parser = PackratParser(rules, rules[0].nonterminal)
    t = parser.parse(t)

    t = ToAST().transform(t)
    t.view()
    
    
def save_number_references(regex):
    saved_refs = []
    for i in range(len(regex)):
        if regex[i] == "\\":
            cand = i + 1
            if cand < len(regex) and regex[cand].isdigit():
                while cand < len(regex) and regex[cand].isdigit():
                    cand += 1
                saved_refs.append(regex[i:cand])
                regex = regex.replace(regex[i:cand], "%s", 1)
    regex = regex.decode("unicode_escape")
    print saved_refs
    # because conversion from list to tuple wont work...
    for ref in saved_refs:
        regex = regex.replace("%s", ref, 1)
    return regex
    
print compile(r"/\2/")


# parse_fn = make_parse_function(regexs, rules)

# reg = "/^\A\wabcd[[a-z]&&[abcdefg]]*?/"
# print ToAST().transform(parse_fn(reg))
# print ToAST().transform(parse_fn("/W[aeiou]rd?/"))
# print ToAST().transform(parse_fn("/(?<hallo>aber)/"))

# try:
#     reg = "/Wrd/"
#     print ToAST().transform(parse_fn(reg))
# except Exception as e:
#     print e.errorinformation.failure_reasons
#     print "Error occured at: %i" % e.errorinformation.pos
#     print "This means at character: %s" % reg[e.errorinformation.pos] 