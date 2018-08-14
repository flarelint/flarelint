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

"""XPath-inspired interface for querying Flare XML elements.

Note the difference between a Flare style and an HTML style. Flare
uses the term "style" to mean an item that appears in the Styles
window or Style Picker.  In HTML, "style" is the actual "style"
attribute for an element. In this module, we use the former; "style"
here means a combination of the element's tag and class attribute. For
more information, see the style() method.

For examples of using this interface and to test this module, see
class TestNode.

"""

import xml.etree.ElementTree as ET
import unittest
import os
import sys
import pdb

_FLARE_LANG_DEFAULT = "en-us"

_FLARE_NAMESPACE_URI = 'http://www.madcapsoftware.com/Schemas/MadCap.xsd'
_FLARE_PREFIX = 'MadCap'
_NAMESPACES = {
    _FLARE_PREFIX : _FLARE_NAMESPACE_URI,
    'xml': 'http://www.w3.org/XML/1998/namespace'}

class Node:
    """A Flare-friendly representation of a node in an XML file."""

    def __init__(self, element, parents, projectlang=_FLARE_LANG_DEFAULT):
        """Initialize an instance.

        The argument 'element' is an 'Element' object from
        xml.etree.ElementTree.

        Because the Element object does not refer to its parent, you
        must provide this information when instantiating a Node.
        The 'parents' argument is a dictionary of elements and their
        children, of which the 'element' argument is included. You can
        compute the 'parents' argument with this expression:

        parents = {c:p for p in root.iter() for c in p}

        """

        self._elem = element
        self._parents = parents
        self._projectlang = projectlang
        self._position = 0

    def iter(self):
        """Iterate over the Node and its children, recursively."""

        yield self
        children = list(self._elem)
        for e in children:
            yield from Node(e, self._parents).iter()

    def _isempty(self):
        return self == EMPTY

    def __bool__(self):
        return not self._isempty()

    def _expandname(self, name):
        prefix = name.split(':')[0] if ':' in name else None

        if prefix in _NAMESPACES:
            return name.replace(prefix + ':', '{' + _NAMESPACES[prefix] + '}')
        else:
            return name

    def _namematches(self, name):
        return name == '*' or self._elem.tag == self._expandname(name)

    def _getsiblings(self):
        if self._isempty():
            return []

        p = self._parents.get(self._elem, None)
        if p is None:
            return [self._elem]

        return list(p)

    def _matchsibling(self, siblings, name, predicate):
        pos = 0
        for c in siblings:
            n = Node(c, self._parents)
            if n._namematches(name):
                n._position = pos
                pos = pos + 1
                if predicate(n):
                    return n
        return EMPTY

    def _matchancestor(self, start, name, predicate):
        a = Node(start, self._parents)
        pos = 0
        while a._elem is not None:
            if a._namematches(name):
                a._position = pos
                pos = pos + 1
                if predicate(a):
                    return a
            a = Node(self._parents.get(a._elem, None), self._parents)
        return EMPTY

    def _matchdescendant(self, start, name, predicate, pos):
        for c in start:
            n = Node(c, self._parents)
            if n._namematches(name):
                n._position = pos
                pos = pos + 1
                if predicate(n):
                    return n, pos
            n, pos = n._matchdescendant(list(c), name, predicate, pos)
            if n:
                return n, pos

        return EMPTY, pos

    def trace(self, label='', encoding='utf-8'):
        """Print self to standard output with an optional prefix.  Returns
        self, so you can chain a call to this method to diagnose your
        expressions.
        """

        outStr = ET.tostring(self._elem, encoding='unicode') if not self._isempty() else 'empty'
        print('{0}{1}'.format(label, outStr).encode(encoding, errors='xmlcharrefreplace'))
        return self

    def debug(self):
        """Enter the Python Debugger."""

        pdb.set_trace()
        return self

    def lang(self, tag):
        """Returns True if the node or its nearest ancestor has an xml:lang
        attribute that matches tag, ingoring letter case.  If there is
        no attribute then use Flare's default, "en-us".

        See https://www.w3.org/International/articles/language-tags/
        for details.

        """

        langnode = self.ancestor_or_self('*', lambda n: n.attribute("xml:lang"))
        langattr = langnode.attribute("xml:lang") if langnode else self._projectlang

        return langattr.casefold().startswith(tag.casefold())

    def name(self):
        """Returns tag name of the node."""

        if not self._isempty():
            n = self._elem.tag.replace('{' + _FLARE_NAMESPACE_URI + '}', _FLARE_PREFIX + ':')
        else:
            n = ''

        return n

    def text(self):
        """Returns the text in an element, ignoring text in descendant elements."""

        if self._isempty():
            return ''

        t = self._elem.text if self._elem.text is not None else ''
        for e in self._elem:
            t = t + (e.tail if e.tail is not None else '')

        return t

    def valueof(self):
        """Returns the text in an element, including descendant elements."""

        if self._isempty():
            return ''

        return "".join(self._elem.itertext())

    def attribute(self, name):
        """Returns the value of an attribute or the empty string if the
        attribute does not exist or the node is empty."""

        return self._elem.get(self._expandname(name), '') if not self._isempty() else ''

    def position(self):
        """Returns the position of a matching element within its axis,
        undefined otherwise. The first element is at position 0.

        Note: For determining position, a matching element along an
        axis is one in which its tag is the same as the name argument
        specified in the axis function. The predicate has no effect on
        the position count.

        For example, given a Node x that refers to this XML tree

        <a>
          <b>bat</b>
          <b>bee</b>
          <b>bat</b>
        </a>

        then this Python expression

        x.child('b', lambda n: n.text() == 'bat' and n.position() == 1)

        would return an empty Node object because the 'b' child at
        position 1 contains "bee".
        """

        return self._position

    def indexof(self):
        """Returns the index of an element among all of its siblings. The
        first element is at index 0. An empty element has index -1 and
        the root element has index 0.

        Note the difference between indexof() and position().
        indexof() returns the cardinal place of a Node among all
        of its siblings while position() returns the relative, axial
        distance of elements with the same tag.

        For example, given a Node x that refers to this XML tree

        <x>
          <a>aardvark</a>
          <b>bee</b>
          <c>cat</c>
        </x>

        then this

        print(x.child('c').indexof(), x.child('c').position())

        gives this output

        2 0

        """

        if self._isempty():
            return -1
        sibs = self._getsiblings()
        if sibs:
            return sibs.index(self._elem)

        return 0

    def child(self, name, predicate=lambda n: True):
        """Returns the first matching element along the child axis or the
        empty element.
        """

        if self._isempty():
            return EMPTY
        return self._matchsibling(list(self._elem), name, predicate)

    def iselement(self, name, predicate=lambda n: True):
        """Returns the same element if it matches the name and
        predicate. Returns the empty element otherwise."""

        if not self._isempty() and self._namematches(name) and predicate(self):
            return self
        else:
            return EMPTY

    def parent(self, name, predicate=lambda n: True):
        """Returns the parent element if it matches, or the empty element."""

        if self._isempty() or self._parents.get(self._elem, None) is None:
            return EMPTY

        parent = Node(self._parents[self._elem], self._parents)

        if parent._namematches(name) and predicate(parent):
            return parent
        else:
            return EMPTY

    def ancestor_or_self(self, name, predicate=lambda n: True):
        """Returns the first matching element along the ancestor axis,
        including itself, or the empty element."""

        return self._matchancestor(self._elem, name, predicate)

    def ancestor(self, name, predicate=lambda n: True):
        """Returns the first matching element along the ancestor axis,
        or the empty element."""

        if self._isempty():
            return EMPTY
        return self._matchancestor(
            self._parents.get(self._elem, None), name, predicate)

    def descendant_or_self(self, name, predicate=lambda n: True):
        """Returns the first matching element along the descendant axis,
        including itself, or the empty element.

        Elements are scanned in document order/depth-first. """

        if self._isempty():
            return EMPTY
        n = self._matchdescendant([self._elem], name, predicate, 0)[0]
        return n

    def descendant(self, name, predicate=lambda n: True):
        """Returns the first matching element along the descendant axis,
        or the empty element.

        Elements are scanned in document order/depth-first. """

        if self._isempty():
            return EMPTY
        n = self._matchdescendant(list(self._elem), name, predicate, 0)[0]
        return n

    def precedingsibling(self, name, predicate=lambda n: True):
        """Returns the first matching element along the preceding sibling
        axis, or the empty element."""

        if self._isempty():
            return EMPTY
        sibs = self._getsiblings()
        last = sibs.index(self._elem)
        return self._matchsibling(reversed(sibs[0:last]), name, predicate)

    def previoussibling(self, name, predicate=lambda n: True):
        """Returns the sibling immediately before self if the sibling matches
        the name and the predicate is true. Otherwise, returns the
        empty element.  Also, returns the empty element if self has no
        preceding siblings.

        This method is equivalent to

        self.precedingsibling('*',
                              lambda n: n.iselement(name)
                              and n.position() == 0
                              and predicate(n))
        """

        return self.precedingsibling('*',
                                     lambda n: n.iselement(name)
                                     and n.position() == 0
                                     and predicate(n))


    def followingsibling(self, name, predicate=lambda n: True):
        """Returns the first matching element along the following sibling
        axis, or the empty element."""

        if self._isempty():
            return EMPTY
        siblings = self._getsiblings()
        first = siblings.index(self._elem) + 1
        return self._matchsibling(siblings[first:], name, predicate)

    def nextsibling(self, name, predicate=lambda n: True):
        """Returns the sibling immediately after self if the sibling matches
        the name and the predicate is true. Otherwise, returns the
        empty element.  Also, returns the empty element if self has no
        following siblings.

        This method is equivalent to

        self.followingsibling('*',
                              lambda n: n.iselement(name)
                              and n.position() == 0
                              and predicate(n))
        """

        return self.followingsibling('*',
                                     lambda n: n.iselement(name)
                                     and n.position() == 0
                                     and predicate(n))

    def style(self, name):
        """Returns self if the Flare style of the node matches the name
        argument, empty node otherwise. 

        The argument must be in the format displayed in the Styles
        window and Style Picker. That format is one of "tag.class",
        "tag", or ".class". If tag is missing, it is ignored when
        matching. If class is missing then it matches only the empty
        class attribute.

        For example, given a Flare node, n, for this element:

        <p class="Note">...</p>

        then n.style("p.Note") and n.style(".Note") each return True
        while n.style("p") returns False.

        """
        styletag, styleclass = (name + ".").split(".")[0:2]
        nodetag = self.name()
        nodeclass = self.attribute('class')

        tagmatch = not styletag or styletag == nodetag
        classmatch = styleclass == nodeclass

        if tagmatch and classmatch:
            return self
        else:
            return EMPTY

    def hascondition(self, cond):
        """Returns self if self has a condition, 'cond', empty node otherwise."""
        if self.ancestor_or_self("*",
                                 lambda n:
                                 cond in n.attribute("MadCap:conditions")):
            return self
        else:
            return EMPTY

    def toclevel(self):
        """Returns the depth of a TocEntry in a TOC. Level 0 is the top level."""

        level = 0
        n = self
        while not n.parent('CatapultToc'):
            n = n.parent('*')
            level = level + 1

        return level

    def snippet(self, src):
        """Returns self if the Flare node is a snippet that refers to src, the
        empty element otherwise."""

        if self.iselement("MadCap:snippetBlock", lambda n: n.attribute("src") == src):
            return self
        elif self.iselement("MadCap:snippetText", lambda n: n.attribute("src") == src):
            return self
        else:
            return EMPTY


    def path(self):
        """Returns the path of the file name from which the node was
        parsed. None if the node was not parsed from a file."""

# We use the empty node to allow chaining of calls to Node objects.
EMPTY = Node(None, None)

# Some utility functions.

def whenstyle(style):
    """Returns a function that checks for a specific Flare style. Useful
    for rule testing and matching."""

    return lambda n: n.style(style)

def whencondition(cond):
    """Returns a function that checks for a specific Flare condition.
    Useful for rule testing and matching.
    """
    return lambda n: n.hascondition(cond)

def whenself(tag):
    """Returns a function that checks for a specific tag.  Useful for rule
    testing and matching.
    """

    return lambda n: n.iselement(tag)

def parse(path, projectlang=_FLARE_LANG_DEFAULT):
    """Parse an XML-based Flare project file and return its root node,
    ready to iterate."""

    root = ET.parse(path).getroot()
    parents = {c:p for p in root.iter() for c in p}
    return Node(root, parents, projectlang)

def get_project_lang(path):
    """Get the language specified in a project file."""
    assert os.path.splitext(path)[1].lower() == '.flprj'

    project = parse(path)
    langattr = project.attribute("xml:lang")
    return langattr.casefold() if langattr else _FLARE_LANG_DEFAULT

class TestNode(unittest.TestCase):
    """Test the Node class."""

    root = ET.fromstring("<root xmlns:"
                         + _FLARE_PREFIX
                         + "='" + _FLARE_NAMESPACE_URI
                         + """'>
  <a xml:lang="fr-ca" MadCap:a = 'Alligator' b = 'Buffalo'>
    Ant
    <b>Bonobo</b>
    eater
    <b>Bee</b>
    <b>Bandicoot</b>
  </a>

  <d>Dog</d>

  <e e = 'Caterpillar'>
  </e>

  <a c = 'Crawfish'>
    <b>Banshee<c>Cat</c><c>Crocodile</c></b>
    <MadCap:b>Bobcat</MadCap:b>
  </a>

  <f>
    <MadCap:snippetBlock src="goodbye/yellow/brick/road"/>
  </f>

  <g class="Caption">
    <h>The loon is also called the Great Northern Diver.</h>
  </g>

  <i MadCap:conditions="Friendly.Giant">
    <j>Look up. Way up.</j>
  </i>
</root>
""")

    parents = {c:p for p in root.iter() for c in p}

    def normalize_words(text):
        return ' '.join(text.split())

    def test_name(self):
        n = Node(self.root, self.parents)
        self.assertEqual(n.name(), 'root')

        n = Node(self.root.find('.//MadCap:b', _NAMESPACES), self.parents)
        self.assertEqual(n.name(), 'MadCap:b')

    def test_text(self):
        n = Node(self.root.find('.//a/b/c'), self.parents)
        self.assertEqual(n.text(), 'Cat')
        n = Node(self.root.find('.//a'), self.parents)
        self.assertEqual(n.text().split(), ['Ant', 'eater'])
        self.assertEqual(n.valueof().split(),
                         ['Ant', 'Bonobo', 'eater', 'Bee', 'Bandicoot'])
        n = Node(self.root.find('.//a/b'), self.parents)
        self.assertEqual(n.parent('a').text().split(),
                         ['Ant',  'eater'])
        self.assertEqual(n.parent('a').valueof().split(),
                         ['Ant', 'Bonobo', 'eater', 'Bee', 'Bandicoot'])


    def test_attribute(self):
        n = Node(self.root.find('.//a'), self.parents)
        self.assertEqual(n.attribute('MadCap:a'), 'Alligator')
        self.assertEqual(n.attribute('b'), 'Buffalo')
        self.assertEqual(n.attribute('c'), '')

    def test_indexof(self):
        n = Node(self.root, self.parents)
        self.assertTrue(n.indexof() == 0)

        e = n.child('z') # Empty element.
        self.assertTrue(e.indexof() == -1)

        a1 = n.child('a')
        d2 = a1.followingsibling('d')
        a3 = a1.followingsibling('a')
        self.assertTrue(a1.indexof() == 0)
        self.assertTrue(d2.indexof() == 1)
        self.assertTrue(a3.indexof() == 3)

    def test_child(self):
        n = Node(self.root, self.parents)
        self.assertTrue(n.child('a'))
        self.assertFalse(n.child('b'))
        self.assertTrue(n.child('a', lambda n: n.attribute('b') == 'Buffalo'))
        self.assertFalse(n.child('a', lambda n: n.attribute('c') == 'Buffalo'))
        self.assertTrue(n.child('a', lambda n: n.child('b')))
        self.assertFalse(n.child('a', lambda n: n.child('c')))
        self.assertEqual(n.child('*').name(), 'a')
        self.assertTrue(n.child('a', lambda n: n.position() == 0))
        self.assertTrue(n.child('d', lambda n: n.position() == 0))
        self.assertTrue(n.child('a', lambda n: n.position() == 1))
        self.assertTrue(n.child('*', lambda n: n.position() == 0 and n.name() == 'a'))
        self.assertTrue(n.child('*', lambda n: n.position() == 1 and n.name() == 'd'))
        self.assertTrue(n.child('*', lambda n: n.position() == 3
                                and n.name() == 'a'))
        self.assertTrue(n.child('a', lambda n: n.position() == 0
                                and n.attribute('MadCap:a') == 'Alligator'))
        self.assertTrue(n.child('a', lambda n: n.position() == 1
                                and n.attribute('c') == 'Crawfish'))

    def test_iselement(self):
        n = Node(self.root.find('.//a'), self.parents)
        self.assertTrue(n.iselement('a'))
        self.assertFalse(n.iselement('b'))
        self.assertTrue(n.iselement('a', lambda n: n.attribute('MadCap:a') == 'Alligator'))

    def test_parent(self):
        n = Node(self.root.find('.//a'), self.parents)

        self.assertTrue(n.parent('root'))
        self.assertFalse(n.parent('z'))

    def test_ancestor_or_self(self):
        n = Node(self.root.find('.//c'), self.parents)
        self.assertTrue(n.ancestor_or_self('c'))
        self.assertTrue(n.ancestor_or_self('b'))
        self.assertTrue(n.ancestor_or_self('a'))
        self.assertTrue(n.ancestor_or_self('root'))

        self.assertTrue(n.ancestor_or_self('*', lambda n: n.position() == 0 and n.name() == 'c'))
        self.assertTrue(n.ancestor_or_self('*', lambda n: n.position() == 1 and n.name() == 'b'))
        self.assertTrue(n.ancestor_or_self('*', lambda n: n.position() == 2 and n.name() == 'a'))
        self.assertTrue(n.ancestor_or_self('*', lambda n: n.position() == 3 and n.name() == 'root'))

        self.assertTrue(n.ancestor_or_self('c', lambda n: n.position() == 0))
        self.assertTrue(n.ancestor_or_self('b', lambda n: n.position() == 0))
        self.assertFalse(n.ancestor_or_self('b', lambda n: n.position() == 1))
        self.assertTrue(n.ancestor_or_self('a', lambda n: n.position() == 0))
        self.assertFalse(n.ancestor_or_self('a', lambda n: n.position() == 2))
        self.assertTrue(n.ancestor_or_self('root', lambda n: n.position() == 0))
        self.assertFalse(n.ancestor_or_self('root', lambda n: n.position() == 3))
        self.assertFalse(n.ancestor_or_self('d'))

    def test_ancestor(self):
        n = Node(self.root.find('.//c'), self.parents)
        self.assertFalse(n.ancestor('c'))
        self.assertTrue(n.ancestor('b'))
        self.assertTrue(n.ancestor('a'))
        self.assertTrue(n.ancestor('root'))

        self.assertFalse(n.ancestor('*', lambda n: n.position() == 0 and n.name() == 'c'))
        self.assertTrue(n.ancestor('*', lambda n: n.position() == 0 and n.name() == 'b'))
        self.assertTrue(n.ancestor('*', lambda n: n.position() == 1 and n.name() == 'a'))
        self.assertTrue(n.ancestor('*', lambda n: n.position() == 2 and n.name() == 'root'))

        self.assertTrue(n.ancestor('b', lambda n: n.position() == 0))
        self.assertFalse(n.ancestor('b', lambda n: n.position() == 1))
        self.assertTrue(n.ancestor('a', lambda n: n.position() == 0))
        self.assertFalse(n.ancestor('a', lambda n: n.position() == 2))
        self.assertTrue(n.ancestor('root', lambda n: n.position() == 0))
        self.assertFalse(n.ancestor('root', lambda n: n.position() == 3))
        self.assertFalse(n.ancestor('d'))

    def test_descendant_or_self(self):
        n = Node(self.root, self.parents)
        self.assertTrue(n.descendant_or_self('root'))
        self.assertTrue(n.descendant_or_self('a'))
        self.assertTrue(n.descendant_or_self('a', lambda n: n.position() == 0))
        self.assertTrue(n.descendant_or_self('d', lambda n: n.position() == 0))
        self.assertTrue(n.descendant_or_self('a', lambda n: n.position() == 1))

        self.assertTrue(
            n.descendant_or_self('*', lambda n: n.position() == 0 and n.name() == 'root'))
        self.assertTrue(
            n.descendant_or_self('*', lambda n: n.position() == 1 and n.name() == 'a'))
        self.assertTrue(
            n.descendant_or_self('*', lambda n: n.position() == 2 and n.name() == 'b'))
        self.assertTrue(
            n.descendant_or_self('*', lambda n: n.position() == 3 and n.name() == 'b'))
        self.assertTrue(
            n.descendant_or_self('*', lambda n: n.position() == 5 and n.name() == 'd'))

    def test_descendant(self):
        n = Node(self.root, self.parents)
        self.assertFalse(n.descendant('root'))
        self.assertTrue(n.descendant('a'))
        self.assertTrue(n.descendant('a', lambda n: n.position() == 0))
        self.assertTrue(n.descendant('a', lambda n: n.position() == 1))

        self.assertTrue(n.descendant('*', lambda n: n.position() == 0 and n.name() == 'a'))
        self.assertTrue(n.descendant('*', lambda n: n.position() == 1 and n.name() == 'b'))
        self.assertTrue(n.descendant('*', lambda n: n.position() == 2 and n.name() == 'b'))
        self.assertTrue(n.descendant('*', lambda n: n.position() == 4 and n.name() == 'd'))

    def test_precedingsibling(self):
        n = Node(self.root.find('.//a'), self.parents)
        n = n.child('b', lambda n: n.position() == 2)
        self.assertTrue(n.precedingsibling('b'))
        self.assertTrue(
            n.precedingsibling('b', lambda n: n.position() == 0 and n.text() == 'Bee'))
        self.assertTrue(
            n.precedingsibling('b', lambda n: n.position() == 1 and n.text() == 'Bonobo'))
        self.assertFalse(n.precedingsibling('a'))

        n = Node(self.root.find('.//d'), self.parents)
        self.assertTrue(n.precedingsibling('a'))
        self.assertFalse(n.precedingsibling('root'))

    def test_previousandnextsibling(self):
        n = Node(self.root.find('.//e'), self.parents)
        self.assertTrue(n.previoussibling('d'))
        self.assertTrue(n.nextsibling('a', lambda n: n.attribute('c') == 'Crawfish'))

    def test_followingsibling(self):
        n = Node(self.root.find('.//a'), self.parents)
        self.assertTrue(n.followingsibling('d'))
        self.assertTrue(n.followingsibling('a'))
        self.assertFalse(n.followingsibling('b'))

        self.assertTrue(n.followingsibling('*', lambda n: n.iselement('d') and n.position() == 0))
        self.assertTrue(n.followingsibling('*', lambda n: n.iselement('a') and n.position() == 2))

    def test_chaining(self):
        n = Node(self.root, self.parents)
        self.assertTrue(n.iselement('root').child('a'))
        self.assertFalse(n.iselement('z').child('a'))
        self.assertFalse(n.iselement('z').iselement('a'))
        self.assertFalse(n.iselement('z').ancestor_or_self('a'))
        self.assertFalse(n.iselement('z').ancestor('a'))
        self.assertFalse(n.iselement('z').descendant_or_self('a'))
        self.assertFalse(n.iselement('z').descendant('a'))
        self.assertFalse(n.iselement('z').followingsibling('a'))
        self.assertFalse(n.iselement('z').precedingsibling('a'))
        self.assertFalse(n.iselement('z').parent('*'))
        self.assertFalse(n.iselement('z').name())
        self.assertFalse(n.iselement('z').text())
        self.assertFalse(n.iselement('z').attribute('a'))
        self.assertFalse(n.iselement('z').position())
        self.assertTrue(n.iselement('z').indexof() == -1)

    def test_lang(self):
        n = Node(self.root, self.parents)
        self.assertTrue(n.lang('en-us'))
        self.assertTrue(n.lang('en'))
        self.assertTrue(n.lang('EN'))
        self.assertTrue(n.child('a').lang('fr'))
        self.assertFalse(n.child('a').lang('en-us'))
        self.assertTrue(n.child('a').child('b').lang('fr-ca'))
        self.assertFalse(n.child('a').child('b').lang('fr-ca-DURP'))
        self.assertFalse(n.child('a').child('b').lang('en'))

    def test_snippet(self):
        n = Node(self.root.find('.//f'), self.parents)
        self.assertTrue(n.child('MadCap:snippetBlock').snippet("goodbye/yellow/brick/road"))
        self.assertTrue(n.child('MadCap:snippetBlock').snippet("goodbye/yellow/brick/road").parent("f"))
        self.assertFalse(n.child('MadCap:snippetBlock').snippet("goodbye/yellow/brick/road").parent("a"))
        self.assertFalse(n.child('MadCap:snippetBlock').snippet("hello/red/wood/path"))
        self.assertFalse(n.snippet("hello/red/wood/path"))
        
    def test_style(self):
        n = Node(self.root.find('.//g'), self.parents)
        self.assertTrue(n.style('g.Caption'))
        self.assertTrue(n.style('.Caption'))
        self.assertTrue(n.style('g.Caption').child('h'))
        self.assertFalse(n.style('g.Caption').child('zzz'))
        self.assertFalse(n.style('g'))

    def test_hascondition(self):
        n = Node(self.root.find('.//i'), self.parents)
        self.assertTrue(n.hascondition('Friendly.Giant'))
        self.assertTrue(n.hascondition('Friendly.Giant').child('j'))
        self.assertTrue(n.child('j').hascondition('Friendly.Giant'))
        self.assertFalse(n.hascondition('Mister.Dressup'))
        
if __name__ == '__main__':
    unittest.main()
