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

r"""Applies rules to a Flare project and generates an HTML report to
list the results.

This module loads rules from, well, the rules folder,
%APPDATA%\FlareLint.  If this directory does not exist, or it is
empty, then FlareLint copies the rules from its sub-module to
%APPDATA%\FlareLint.

Then this module reads each file in a project then iterates through
each element.  At each element, this module calls the match function
of each relevant rule.  If True, then the program applies the test
function to the element.  If the test fails (is False) then the
element is considered to have broken the rule. For each broken rule,
the module outputs the rule's message.

The rule's match function chooses which elements to apply the rule
to. The rule's test function determines if the matched element follows
the rule.

"""

import string
import os
import re
import xml.etree.ElementTree as ET
import datetime
import html
import pathlib
import pprint

from flarelint import rule
from flarelint import flarenode
from flarelint import resources

# Parts for assembling the report

def _firstfewwords(text):
    return (' '.join(text.split()[0:8]))[0:50]

def _describecontext(node):

    context = node.valueof().strip() \
              or node.attribute('alt').strip() \
              or node.attribute('title').strip() \
              or node.attribute('Title').strip() \
              or node.attribute('Comment').strip()

    if context:
        context = "&#8220;" + html.escape(_firstfewwords(context)) + "&#8230;&#8221;"
    else:
        context = node.attribute('href').strip() \
        or node.attribute('src').strip() \
        or node.attribute('Link').strip()

        if context:
            context = "<code>" + html.escape(context) + "</code>"

    return context

def _formatmessage(msg):
    formats = [
        (r'*', 'b'),
        (r'`', 'code'),
        (r'_', 'i')]

    msg = html.escape(msg)

    for char, tag in formats:
        formatRegex = "(?<!\\\\)[{0}]([^{0}]+)(?<!\\\\)[{0}]".format(char)
        formatRepl = "<{0}>\\1</{0}>".format(tag)
        escapeRegex = "\\\\\\{0}".format(char)
        msg = re.sub(formatRegex, formatRepl, msg)
        msg = re.sub(escapeRegex, char, msg)

    return msg

def _groupByFile(results):
    g = {}
    for r in results:
        if g.get(r.path, None) is None:
            g[r.path] = []
        g[r.path].append(r)

    return g

def _formatresult(result):

    nodeclasses = ".".join(result.node.attribute('class').split())
    flarestyle = '{0}{1}'.format(
        result.node.name(),
        '.' + nodeclasses if nodeclasses else '')
    
    return string.Template(resources.TEMPLATE_RESULT).substitute(
        source=html.escape(os.path.basename(result.source)),
        level=result.level,
        tag=flarestyle,
        context=_describecontext(result.node),
        message=_formatmessage(result.message))

def _format_file_results(file, fileresults, projectpath):
    fp = pathlib.Path(file)
    pp = pathlib.Path(projectpath)
    
    return string.Template(resources.TEMPLATE_FILE).substitute(
        fileuri=fp.as_uri(),
        path=fp.relative_to(pp.parent),
        results='\n'.join(_formatresult(r) for r in fileresults)
    )
def _format_all_results(results, projectpath):

    grouped = _groupByFile(results)
    
    return '\n'.join(
        _format_file_results(
            f, grouped[f], projectpath) for f in sorted(grouped, key=str.lower))

def _applyrules(rules, path, node, stats):
    allResults = []
    for r in rules:
        result = rule.apply(r, path, node)
        if result:
            stats[result.level] += 1
            allResults.append(result)

    return allResults

def _apply_rules_to_file(path, filename, projectlang, stats, verbose=False):

    extension = os.path.splitext(filename)[1]
    rules = rule.getrules(extension)
    if rules is None:
        return []
    
    fullPath = os.path.join(path, filename)
    if verbose:
        print(' ', fullPath)

    results = []

    try:
        flareNodes = flarenode.parse(fullPath, projectlang)
        for node in flareNodes.iter():
            results.extend(_applyrules(rules, fullPath, node, stats))
    except ET.ParseError:
        badXML = rule.Result(
            fullPath,
            resources.LEVEL_ERROR,
            flarenode.EMPTY,
            resources.ERROR_PARSE)
        results = [badXML]
        stats[badXML.level] += 1

    return results

def _scandirectory(directory, projectlang, stats, verbose=False):
    results = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            fileresults = _apply_rules_to_file(dirpath, f, projectlang, stats, verbose)
            results.extend(fileresults)

    return results

def build(projectpath, reportpath, verbose=False):
    """Given a path to a Flare project and a path to a report, read the
    Flare project and store the resulting report."""

    projectDir = os.path.dirname(projectpath)

    statistics = {resources.LEVEL_ERROR : 0,
                  resources.LEVEL_WARNING : 0}

    print(resources.PROGRESS_SCANNING)
    lang = flarenode.get_project_lang(projectpath)
    issues = []
    for subDir in ['Content', 'Project']:
        path = os.path.join(projectDir, subDir)
        issues.extend(_scandirectory(path, lang, statistics, verbose))
    if verbose:
        print('')

    print(resources.PROGRESS_FORMATTING)
    reportText = string.Template(resources.TEMPLATE_REPORT).substitute(
        errorLabel=resources.LEVEL_ERROR,
        warningLabel=resources.LEVEL_WARNING,
        project=projectpath,
        date=datetime.datetime.now().strftime(resources.DATE_FORMAT),
        user=os.environ['USERNAME'],
        errorCount=str(statistics[resources.LEVEL_ERROR]),
        warningCount=str(statistics[resources.LEVEL_WARNING]),
        results=_format_all_results(issues, projectpath) if issues else resources.REPORT_NO_ISSUES)

    print(resources.PROGRESS_TALLY.format(
        statistics[resources.LEVEL_ERROR],
        statistics[resources.LEVEL_WARNING]))

    try:
        report = ET.fromstring(reportText)
    except ET.ParseError:
        print(resources.ERROR_REPORT)
        sys.exit(1)

    with open(reportpath, 'bw') as f:
        f.write(b'<!DOCTYPE html>\n')
        ET.ElementTree(report).write(f, encoding="UTF-8", method="xml")
