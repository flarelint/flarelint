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

_ACCEPTED_EMPTY_P_DESC = ['img', 'iframe', 'MadCap:snippetText', 'MadCap:variable']
_ACCEPTED_EMPTY_P_ANC = ['td']

rule.Error(
    extensions = rule.TOPICS_AND_SNIPPETS,
                 
    match = lambda n: n.iselement('p') and n.valueof().strip() == '',
                 
    test = lambda n: n.ancestor('*', lambda n: n.name() in _ACCEPTED_EMPTY_P_ANC)
    or n.descendant('*', lambda n: n.name() in _ACCEPTED_EMPTY_P_DESC),
                 
    message = """Empty paragraph. A `p` element must not be empty. To fix, delete
    it.

    *Note:* Empty paragraphs are permitted in
    """ + ", ".join("`{0}`".format(e) for e in _ACCEPTED_EMPTY_P_ANC) +
    """ elements."""
)

