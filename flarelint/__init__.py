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

r"""Welcome to FlareLint!

You can use FlareLint to make production of your MadCap Flare output
faster and less tedious.  Use FlareLint to produce more consistent,
higher-quality content for your end users.

FlareLint scans your MadCap Flare project for conformance to your
rules then generates a report. This report lists files in your project
that break the rules.  For example, FlareLint reports when a topic
does not start with an h1 element.

For more information, see doc\index.html

"""

import webbrowser
import os
import glob
import sys

from flarelint import report
from flarelint import resources
from flarelint import rule

def _rename_previous_report(path):
    newpath = path
    base, ext = os.path.splitext(path)
    count = 0
    while os.path.isfile(newpath):
        count = count + 1
        newpath = base + "-%i" % count + ext

    if count > 0:
        os.rename(path, newpath)

def _defaultproject():
    projectfiles = glob.glob(os.path.join(os.getcwd(), '*.flprj'))

    if projectfiles and os.path.isfile(projectfiles[0]):
        return projectfiles[0]
    else:
        return None

def main(args):
    """Main entry point for FlareLint."""

    print(resources.WELCOME)

    verbose = False
    projectpath = None
    
    for a in args:
        if a == '-v':
            verbose = True
        elif a == '--help':
            print(resources.HELP)
            sys.exit(0)
        elif a.startswith('-') or projectpath:
            print(resources.BAD_ARG)
            sys.exit(1)
        else:
            projectpath = a

    if not projectpath:
        projectpath = _defaultproject()
        
    if projectpath is None:
        print(resources.MISSING_PROJECT)
        sys.exit(1)

    projectdir, projectfile = os.path.split(projectpath)
    reportpath = os.path.join(projectdir, resources.REPORT_FILE)

    print(resources.PROGRESS_PROJECT.format(projectdir, projectfile))
    rule.load(verbose)
    _rename_previous_report(reportpath)
    report.build(projectpath, reportpath, verbose)
    webbrowser.open(reportpath)

    print(resources.PROGRESS_REPORT.format(resources.REPORT_FILE))
    print(resources.PROGRESS_DONE)
