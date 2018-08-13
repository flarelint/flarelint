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

_ACCEPTED_ANCESTORS_VAR = ['MadCap:xref', 'code', 'pre']

CASE_SENSITIVE = True

def variablerule(text, variable, caseSensitive = False):
    """Generates an error rule that checks to see if an element contains
    a piece of text that should really be a Flare variable."""

    if caseSensitive:
        normalizedText = ' '.join(text.split())
        normalizedTest = lambda n: normalizedText not in ' '.join(n.text().split())
    else:
        normalizedText = ' '.join(text.split()).casefold()
        normalizedTest = lambda n: normalizedText not in ' '.join(n.text().split()).casefold()

    rule.Error(
        extensions = rule.TOPICS_AND_SNIPPETS,
        
        match = lambda n: not n.ancestor_or_self('*', lambda n: n.name() in _ACCEPTED_ANCESTORS_VAR),
        
        test = normalizedTest,
        
        message = """The text """
        + rule.LDQUO + """`"""
        + text + """`""" + rule.RDQUO 
        + """ instead of its variable.  We ensure consistency and simplify
        maintenance by using a variable for this text instead. To fix,
        replace this text with variable `""" + variable + """`."""
)

# Add your variable rules here:
#
# variablerule('text-that-should-be-a-variable', 'variable-file.variable-name', [optional: CASE_SENSITIVE])

variablerule('FlareLint', 'Var.FlareLint', CASE_SENSITIVE)
variablerule('Flare Lint', 'Var.FlareLint', CASE_SENSITIVE)

