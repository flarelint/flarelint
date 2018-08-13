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

rule.Error(
    extensions = rule.TOPICS_AND_SNIPPETS,
                 
    match = flarenode.whenself('h1'),
                 
    test = lambda n: (not '\n' in n.valueof()) or n.child('br'),
                 
    message = """Hidden line break. This line break could cause a broken page header
    in PDF.  To fix, open the topic in the text editor (raw XML) and
    make sure that the contents of the `h1` element are all on one
    line."""
)

