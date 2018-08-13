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

rule.Warning(
    extensions = rule.TOPICS_AND_SNIPPETS,

    match = lambda n: n.name() in ["h1", "h2", "h3", "h4", "h5", "h6"],

    test = lambda n: '*' not in n.valueof(),

    message = """A title contains an
        asterisk (""" + rule.LDQUO + """*""" + rule.RDQUO + """).  """ +
        """MadCap Flare version 8 (and possibly other versions) will not put a
        cross-reference to this topic in a relationships proxy for PDF
        targets.  To fix, remove or replace the asterisk with
        something else. Also, update TOC entries that refer to this
        topic. Finally, publicly shame MadCap for such a ridiculous,
        shameful, arbitrary, confounding, nonsensical, time-wasting
        bug.  """
)

