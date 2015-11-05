#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Test the basic functions of parsec.py.
'''

__author__ = 'He Tao, sighingnow@gmail.com'

from parsec import *

whitespace = regex(r'\s*', re.MULTILINE)

lexeme = lambda p: p << whitespace

lbrace = lexeme(string('{'))
rbrace = lexeme(string('}'))
lbrack = lexeme(string('['))
rbrack = lexeme(string(']'))
colon  = lexeme(string(':'))
comma  = lexeme(string(','))
true   = lexeme(string('true')).result(True)
false  = lexeme(string('false')).result(False)
null   = lexeme(string('null')).result(None)

def number():
    '''Parse number.'''
    return lexeme(
        regex(r'-?(0|[1-9][0-9]*)([.][0-9]+)?([eE][+-]?[0-9]+)?')
    ).parsecmap(float)

def charseq():
    '''Parse string. (normal string and escaped string)'''
    def string_part():
        '''Parse normal string.'''
        return regex(r'[^"\\]+')
    def string_esc():
        '''Parse escaped string.'''
        return string('\\') >> (
            string('\\')
            | string('/')
            | string('b').result('\b')
            | string('f').result('\f')
            | string('n').result('\n')
            | string('r').result('\r')
            | string('t').result('\t')
            | regex(r'u[0-9a-fA-F]{4}').parsecmap(lambda s: chr(int(s[1:], 16)))
        )
    return string_part() | string_esc()

@lexeme
@generate
def quoted():
    '''Parse quoted string.'''
    yield string('"')
    body = yield many(charseq())
    yield string('"')
    return ''.join(body)

@generate
def array():
    '''Parse array element in JSON text.'''
    yield lbrack
    first = yield value
    rest = yield many((comma >> value))
    yield rbrack
    return [first] + rest

@generate
def object_pair():
    '''Parse object pair in JSON.'''
    key = yield quoted
    yield colon
    val = yield value
    return (key, val)

@generate
def json_object():
    '''Parse json object.'''
    yield lbrace
    first = yield object_pair
    rest = yield many(comma >> object_pair)
    yield rbrace
    return dict([first] + rest)

value = quoted | number() | json_object | array | true | false | null

jsonc = whitespace >> json_object

