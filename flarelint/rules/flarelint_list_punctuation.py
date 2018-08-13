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

from flarelint import rule
from flarelint import flarenode
import re

_ACCEPTED_PUNCT_EN = '!?.'
_RE_EN = r'[{0}]\s*$'.format(_ACCEPTED_PUNCT_EN)

_ACCEPTED_ENDING_FR = ' ;'
_ACCEPTED_ENDING_LAST_FR = '.'

_RE_FR = r'{0}\s*$'.format("".join("[{0}]".format(x) for x in _ACCEPTED_ENDING_FR))
_RE_LAST_FR = r'{0}\s*$'.format("".join("[{0}]".format(x) for x in _ACCEPTED_ENDING_LAST_FR))

rule.Error(
    extensions = rule.TOPICS_AND_SNIPPETS,

    match = lambda n: n.iselement('li') and n.parent('ul') and n.lang('en'),

    test = lambda n: not n.nextsibling('li')
    or (re.search(_RE_EN, n.valueof())
        and re.search(_RE_EN, n.nextsibling('li').valueof()))
    or (not re.search(_RE_EN, n.valueof())
        and not re.search(_RE_EN, n.nextsibling('li').valueof())),
    
    message = """Inconsistent punctuation in a bullet list (`ul`).  All items in a
    list must consistently use uncapitalized phrases (except, of
    course, product and proper names) with no ending punctuation, or
    full sentences with first words capitalized and ending
    punctuation.  Accepted ending punctuation is """ + rule.LDQUO
    + _ACCEPTED_PUNCT_EN + rule.RDQUO +
    """. To fix, adjust the capitalization and punctuation.  """
)

rule.Error(
    extensions = rule.TOPICS_AND_SNIPPETS,

    match = lambda n: n.iselement('li') and n.nextsibling('li') and n.parent('ul') and n.lang('fr'),

    test = lambda n: re.search(_RE_FR, n.valueof()),
    
    message = """Incorrect punctuation in a bullet list (`ul`).  Each item, except
    the last, in a bullet list must be an uncapitalized phrase
    (except, of course, product and proper names) and end with """ + rule.LDQUO
    + _ACCEPTED_ENDING_FR + rule.RDQUO +
    """. To fix, adjust the punctuation.  """
)

rule.Error(
    extensions = rule.TOPICS_AND_SNIPPETS,

    match = lambda n: n.iselement('li') and (not n.nextsibling('li')) and n.parent('ul') and n.lang('fr'),

    test = lambda n: re.search(_RE_LAST_FR, n.valueof()),
    
    message = """Incorrect punctuation in the last item (`li`) of a bullet list
    (`ul`).  The last item must be an uncapitalized phrase (except, of
    course, product and proper names) and end with """ + rule.LDQUO
    + _ACCEPTED_ENDING_LAST_FR + rule.RDQUO +
    """. To fix, adjust the punctuation.  """
)

