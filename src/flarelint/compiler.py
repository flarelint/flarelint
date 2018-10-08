# CDDL HEADER START
#
# Copyright 2016-2017 Intelerad Medical Systems Incorporated.  All
# rights reserved.
#
# The contents of this file are subject to the terms of the
# Common Development and Distribution License, Version 1.0 only
# (the "License").  You may not use this file except in compliance
# with the License.
#
# The full text of the License is in LICENSE.txt.  See the License
# for the specific language governing permissions and limitations
# under the License.
#
# When distributing Covered Software, include this CDDL HEADER in
# each file and include LICENSE.txt.  If applicable, add the
# following below this CDDL HEADER, with the fields enclosed by
# brackets "[]" replaced with your own identifying information:
# Portions Copyright [yyyy] [name of copyright owner]
#
# CDDL HEADER END
#
# Portions copyright 2018 Marc Paquette

import collections
import re
import sys
import textwrap
import os
import pdb

from flarelint import flarenode
from flarelint import resources

# Adapted from https://docs.python.org/3.5/library/re.html.

_Token = collections.namedtuple('Token', ['kind', 'value', 'line', 'column'])

_TOKEN_SPEC = [
    ('SECTION', r'^[A-Za-z]+:'),
    ('WILDCARD', r'[*]'),
    ('NAME', r'[.A-Za-z][-_.:A-Za-z0-9]*'),
    ('NUMBER', r'[0-9]+'),
    ('QUOTE', r"""["].*?["]"""),
    ('NEWLINE', r'\n'),
    ('WHITESPACE', r'[ \t]+'),
    ('OTHER', r'.'),
]

_TOK_REGEX = '|'.join('(?P<%s>%s)' % pair for pair in _TOKEN_SPEC)

# Inspired by Jack W. Crenshaw.

def _tokenreader(rulefile):
    with open(rulefile, 'r', encoding="utf-8-sig") as f:
        linenum = 0
        for line in f:
            linenum += 1
            for mo in re.finditer(_TOK_REGEX, line):
                kind = mo.lastgroup
                value = mo.group(kind)
                column = mo.start() + 1
                yield _Token(kind, value, linenum, column)

# Inspired by Jack W. Crenshaw.
class _Tokenizer:
    def __init__(self, rulefile):
        self._reader = _tokenreader(rulefile)
        self.filename = rulefile
        self.kind, self.value, self.line, self.column = (None, None, None, None)
        self.next()
        
    def next(self):
        try:
            self.kind, self.value, self.line, self.column = next(self._reader)
        except StopIteration:
            self.kind, self.value, self.line, self.column = ('EOF', resources.COMPILER_EOF, self.line, 1)

    def skipwhite(self):
        while self.kind == 'WHITESPACE' or self.kind == 'NEWLINE':
            self.next()

        
def _error(filename, line, msg):
    print(resources.ERROR_COMPILER.format(os.path.basename(filename), line, textwrap.indent(textwrap.fill(msg), '  ')))
    sys.exit(1)

def _expectsection(tok, section):
    if not (tok.kind == 'SECTION' and tok.value == section):
        _error(tok.filename,
               tok.line,
               resources.ERROR_EXPECT_SECTION.format(section, tok.value))
            
def _compiletag(tok, context):
    tok.skipwhite()
    if tok.kind == 'NAME' or tok.kind == 'WILDCARD':
        tag = tok.value
        tok.next()
        return tag
    else:
        _error(tok.filename, tok.line, resources.ERROR_EXPECT_TAG.format(context, tok.value))
            
def _compilename(tok, context):
    tok.skipwhite()
    if tok.kind == 'NAME':
        name = tok.value
        tok.next()
        return name
    else:
        _error(tok.filename, tok.line, resources.ERROR_EXPECT_NAME.format(context, tok.value))
            
def _compilenumber(tok, context):
    tok.skipwhite()
    if tok.kind == 'NUMBER':
        n = tok.value
        tok.next()
        return int(n)
    else:
        _error(tok.filename, tok.line, resources.ERROR_EXPECT_NUMBER.format(context, tok.value))
            
def _compilequote(tok, context):
    tok.skipwhite()
    if tok.kind == 'QUOTE':
        quote = tok.value[1:-1]
        parts = re.split(r"(\\\\|\\n)", quote)
        for i, j in enumerate(parts):
            parts[i] = {'\\\\': '\\', '\\n': '\n', '\\"': '"'}.get(j, parts[i])
        escaped = ''.join(parts)
        tok.next()
        return escaped
    else:
        _error(tok.filename, tok.line, resources.ERROR_EXPECT_QUOTE.format(context, tok.value))

def _compileextensions(tok):
    tok.skipwhite()
    _expectsection(tok, 'extensions:')
    tok.next()
    tok.skipwhite()

    exts = []
    while tok.kind == 'NAME':
        exts.append(tok.value)
        tok.next()
        tok.skipwhite()
    return exts
        
def _compilewhens(tok):
    tok.skipwhite()
    _expectsection(tok, 'when:')
    return _compile_expression_section(tok, 'when:')
        
def _compiletests(tok):
    tok.skipwhite()
    _expectsection(tok, 'test:')
    return _compile_expression_section(tok, 'test:')

def _compilemessage(tok):
    tok.skipwhite()
    _expectsection(tok, 'message:')
    tok.next()
    tok.skipwhite()
    message = ""
    while tok.kind != 'SECTION' and tok.kind != 'EOF':
        message += tok.value
        tok.next()

    if tok.kind == 'SECTION':
        _error(tok.filename, tok.line, resources.ERROR_COMPILE_MESSAGE.format(tok.value))
                  
    return message.strip()

def _compileterm(tok):
    tok.skipwhite()
    if tok.value == 'not':
        notflag = True
        tok.next()
        tok.skipwhite()
    else:
        notflag = False

    p = _compilepredicate(tok)

    if notflag:
        return lambda n, p=p: not p(n)
    else:
        return p

def _empty(x):
    return x and x.valueof().strip() == ''

def _compile_predicate_pov(tok, povmethod, predicate):
    """Yes, this function is long and tedious. But it works."""
    p = None

    taxonomy = predicate.split('-')
    if len(taxonomy) > 1:
        subpred = "-".join(taxonomy[1:])
    else:
        subpred = ''

    if subpred == '':
        arg = _compiletag(tok, predicate)
        p = lambda n, m=povmethod, a=arg: m(n, a)
    elif subpred == 'style':
        arg = _compiletag(tok, predicate)
        p = lambda n, m=povmethod, a=arg: m(n, '*', flarenode.whenstyle(a))
    elif subpred == 'empty':
        arg = _compiletag(tok, predicate)
        p = lambda n, m=povmethod, a=arg: _empty(m(n, a))
    elif subpred == 'position':
        arg1 = _compiletag(tok, predicate)
        arg2 = _compilenumber(tok, predicate)
        p = lambda n, m=povmethod, a1=arg1, a2=arg2: m(n, a1).indexof() == a2
    elif subpred == 'first':
        arg1 = _compiletag(tok, predicate)
        p = lambda n, m=povmethod, a1=arg1: m(n, a1).indexof() == 0
    elif subpred == 'last':
        arg1 = _compiletag(tok, predicate)
        p = lambda n, m=povmethod, a1=arg1: m(n, a1).nextsibling('*') == flarenode.EMPTY
    elif subpred == 'padding':
        arg1 = _compiletag(tok, predicate)
        p = lambda n, m=povmethod, a1=arg1: m(n, a1).text().strip() != m(n, a1).text()
    elif subpred == 'contains':
        arg1 = _compiletag(tok, predicate)
        arg2 = _compilequote(tok, predicate)
        p = lambda n, m=povmethod, a1=arg1, a2=arg2: a2 in m(n, a1).valueof()
    elif subpred == 'text':
        arg1 = _compiletag(tok, predicate)
        arg2 = _compilequote(tok, predicate)
        p = lambda n, m=povmethod, a1=arg1, a2=arg2: a2 in m(n, a1).text()
    elif subpred == 'ends':
        arg1 = _compiletag(tok, predicate)
        arg2 = _compilequote(tok, predicate)
        p = lambda n, m=povmethod, a1=arg1, a2=arg2: m(n, a1).valueof().strip().endswith(a2.rstrip())
    elif subpred == 'begins':
        arg1 = _compiletag(tok, predicate)
        arg2 = _compilequote(tok, predicate)
        p = lambda n, m=povmethod, a1=arg1, a2=arg2: m(n, a1).valueof().strip().startswith(a2.lstrip())
    elif subpred == 'attribute':
        arg1 = _compiletag(tok, predicate)
        arg2 = _compilename(tok, predicate)
        p = lambda n, m=povmethod, a1=arg1, a2=arg2: m(n, a1).attribute(a2).strip()
    elif subpred == 'attribute-equals':
        arg1 = _compiletag(tok, predicate)
        arg2 = _compilename(tok, predicate)
        arg3 = _compilequote(tok, predicate)
        p = lambda n, m=povmethod, a1=arg1, a2=arg2, a3=arg3: m(n, a1).attribute(a2) == a3
    elif subpred == 'attribute-contains':
        arg1 = _compiletag(tok, predicate)
        arg2 = _compilename(tok, predicate)
        arg3 = _compilequote(tok, predicate)
        p = lambda n, m=povmethod, a1=arg1, a2=arg2, a3=arg3: a3 in m(n, a1).attribute(a2)
    elif subpred == 'attribute-ends':
        arg1 = _compiletag(tok, predicate)
        arg2 = _compilename(tok, predicate)
        arg3 = _compilequote(tok, predicate)
        p = lambda n, m=povmethod, a1=arg1, a2=arg2, a3=arg3: m(n, a1).attribute(a2).strip().endswith(a3.rstrip())
    elif subpred == 'variable':
        arg = _compilename(tok, predicate)
        p = lambda n, m=povmethod, a=arg: m(n, 'MadCap:variable', lambda n, a=arg: n.attribute('name') == a)
    else:
        _error(tok.filename, tok.line, resources.ERROR_COMPILE_PREDICATE.format(predicate))

    assert p
    return p

    
def _compilepredicate(tok):
    """Converts a predicate to a Python lambda function. 

    Yes, I know that this function's structure is long and tedious. But
    it works and it's easy to add new predicates.

    """

    p = None

    tok.skipwhite()
    predicate = tok.value
    tok.next()
    pov = predicate.split('-')[0]
    
    if pov == 'after':
        p = _compile_predicate_pov(tok, flarenode.Node.followingsibling, predicate)
    elif pov == 'ancestor':
        p = _compile_predicate_pov(tok, flarenode.Node.ancestor, predicate)
    elif pov == 'before':
        p = _compile_predicate_pov(tok, flarenode.Node.precedingsibling, predicate)
    elif pov == 'child':
        p = _compile_predicate_pov(tok, flarenode.Node.child, predicate)
    elif pov == 'descendant':
        p = _compile_predicate_pov(tok, flarenode.Node.descendant, predicate)
    elif pov == 'next':
        p = _compile_predicate_pov(tok, flarenode.Node.nextsibling, predicate)
    elif pov == 'parent':
        p = _compile_predicate_pov(tok, flarenode.Node.parent, predicate)
    elif pov == 'previous':
        p = _compile_predicate_pov(tok, flarenode.Node.previoussibling, predicate)
    elif pov == 'self':
        p = _compile_predicate_pov(tok, flarenode.Node.iselement, predicate)
    elif predicate == 'condition':
        arg = _compilename(tok, predicate)
        p = lambda n, a=arg: n.hascondition(a)
    elif predicate == 'fail':
        p = lambda n: False
    elif predicate == 'language':
        arg = _compilename(tok, predicate)
        p = lambda n, a=arg: n.lang(a)
    elif predicate == 'snippet':
        arg = _compilequote(tok, predicate)
        p = lambda n, a=arg: n.snippet(a)
    else:
        _error(tok.filename, tok.line, resources.ERROR_COMPILE_PREDICATE.format(predicate))

    assert p

    return p

def _compileexpression(tok):
    p = [_compileterm(tok)]
    tok.skipwhite()
    while tok.value == 'and':
        tok.next()
        p.append(_compileterm(tok))
        tok.skipwhite()

    return p

def _compile_expression_section(tok, sectname):
    tok.skipwhite()
    sections = []
    while tok.kind == 'SECTION' and tok.value == sectname:
        tok.next()
        tok.skipwhite()
        while tok.kind == 'NAME':
            sections.append(_compileexpression(tok))

    return sections

def _compilecomment(tok):
    tok.skipwhite()
    if tok.kind == 'SECTION' and tok.value == 'comment:':
        tok.next()
        while tok.kind != 'SECTION' and tok.kind != 'EOF':
            tok.next()

def _compiletype(tok):
    tok.skipwhite()
    _expectsection(tok, 'rule:')
    tok.next()
    ruletype = _compilename(tok, 'rule:')

    if ruletype not in [resources.LEVEL_ERROR, resources.LEVEL_WARNING]:
        _error(tok.filename, tok.line, resources.ERROR_COMPILE_TYPE.format(
            resources.LEVEL_ERROR,
            resources.LEVEL_WARNING,
            ruletype))
    
    return ruletype
    
def compile(rulefile):
    tok = _Tokenizer(rulefile)
    rule = {}
    rule['source'] = rulefile
    _compilecomment(tok)
    rule['rule'] = _compiletype(tok)
    rule['extensions'] =_compileextensions(tok)
    rule['when'] = _compilewhens(tok)
    rule['test'] = _compiletests(tok)
    rule['message'] = _compilemessage(tok)

    return rule
