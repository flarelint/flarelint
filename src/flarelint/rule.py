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

import os
import glob
import shutil
import importlib.util
import pprint

from flarelint import resources
from flarelint import compiler

_RULES_DIR = os.path.join(os.environ["APPDATA"], "FlareLint");
_RULE_FILE_PATTERN = "*rule.txt"

class Result():
    """Contains an message from a broken rule and related information."""

    def __init__(self, path, source, level, node, message):
        self.path = path
        self.source = source
        self.level = level
        self.node = node
        self.message = message

_rulebook = {}

def _addrule(rule):
    for e in rule['extensions']:
        if e not in _rulebook:
            _rulebook[e] = []
        _rulebook[e].append(rule)

def getrules(extension):
    """Returns the rule objects for a specific file name extension. Call
    load() first."""
    
    return _rulebook.get(extension.split('.')[-1], None)

def _check(user, default, verbose=False):
    """If there are no rules in the user's personal rule folder, copy the
    default rules."""

    if not (os.path.isdir(user) and glob.glob(os.path.join(user, _RULE_FILE_PATTERN))):
        if verbose:
            print(resources.PROGRESS_RULES_DEFAULT)
        os.makedirs(user, exist_ok=True)
        for src in glob.glob(os.path.join(default, _RULE_FILE_PATTERN)):
            shutil.copy(src, user)

    assert os.path.isdir(user)

def load(verbose=False):
    """Load rules from the user's personal folder."""

    userpath = _RULES_DIR
    defaultpath = os.path.join(os.path.split(__file__)[0], "rules")
    
    _check(userpath, defaultpath, verbose)
    print(resources.PROGRESS_RULES_LOAD.format(userpath))

    for f in glob.glob(os.path.join(userpath, _RULE_FILE_PATTERN)):
        if verbose:
            print(' ', os.path.basename(f))
        rule = compiler.compile(f)
        _addrule(rule)

    if verbose:
        print('')
        
    assert _rulebook

def _applyterms(terms, node):
    for t in terms:
        if not t(node):
            return False

    return True
    
def _applyconditions(conditions, node):
    """Applies a bunch of conditions, stopping at the first one that
    returns True. If all conditions return False, then return False."""

    for c in conditions:
        if _applyterms(c, node):
            return True

    return False

def apply(rule, path, node):
    if _applyconditions(rule['when'], node) and not _applyconditions(rule['test'], node):
        return Result(path, rule['source'], rule['rule'], node, rule['message'])
    
    return None
