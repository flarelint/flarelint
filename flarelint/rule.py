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

r"""A rule may generate one of two levels of message: an error or warning.

An error describes a problem that will give incorrect output or cause
production failure.

A warning describes something suspicious that needs further
investigation from the user. Or it describes a situation that is not a
show-stopper but addressing it could result in better content.

To create a rule, import this module and instantiate class Error or
class Warning.

A rule comprises a list of file name extensions, a match function,
a test function, and a message.

The file name extensions and the match function specify to which type
of file and element in that file the rule is applicable.

The match and test functions are called with an object of class
Node, defined in flarenode.py.

The test function returns True when the matching element meets your
requirements.

The rule's message describes why the test function returned False.  A
message should, at a minimum, answer the question: why did the matched
element break this rule?  The message should also include a solution
and other guidance.

The message can use simple markdown-like syntax. For bold, wrap text
in asterisks (*). For monospace code, wrap text in back-ticks (`). You
can escape these formatting characters with a backslash (\).

For example, to ensure that a topic body starts with an h1 element,
you might write this rule:

  from flarelint import rule
  from flarelint import flarenode

  rule.Error(
      extensions=['.htm'],
      match=lambda n: n.Name() = 'body',
      test=lambda n: n.child('h1'),
      message="Missing h1 in topic body.")

Tip: To help users, try to write match functions that match the
error-producing element as closely as possible.  Along with the
message output, the tool outputs some contextual information about the
element that caused the test to return False.  Contextual information
is taken from element that caused the match function to return True.

For example, say a rule requires all unordered lists (ul) to contain
only list items. The ideal match function would return True for the
element that is not an li element. A simpler match function would
simply return True for ul elements.  But the context derived from the
entire ul element would not be as helpful to the user.

Tip: Sometimes it's more convenient or shorter for the match function
to also serve as the test function. In that case, just specify a test
function that returns False.

For example, if your style guide does not allow the bold, underline,
and italic elements, then you would write a rule that matches the b,
u, and i elements.  Since this rule already matches the offending
element, there's no need for a further test. The match and test
functions end up looking like this:

  rule.Error(
      extensions=['.htm'],
      match=lambda n: n.Name() in ['b', 'u', 'i'],
      test=lambda n: False,
      message="Hard-coded styles are not permitted.")

"""

import os
import glob
import shutil
import importlib.util
import pprint

from flarelint import resources
from flarelint import compiler

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

def _rulesdir():
    return os.path.join(os.environ["APPDATA"], "FlareLint")

LDQUO = '&#8220;'
RDQUO = '&#8221;'
HELLIP = '&#8230;'
NBSP = '&#160;'

TOPICS = ['.htm', '.html']
TOPICS_AND_SNIPPETS = TOPICS + ['.flsnp']
TOCS = ['.fltoc']
TARGETS = ['.fltar']
CAPTURE_GRAPHICS = ['.props']
IMPORTS = ['.flimpfl']

_RULE_FILE_PATTERN = "*rule.txt"

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

    userpath = os.path.join(os.environ["APPDATA"], "FlareLint")
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
