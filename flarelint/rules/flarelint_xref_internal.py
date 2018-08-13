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

    match = flarenode.whenself('MadCap:xref'),

    test = lambda n: '#' not in n.attribute('href') ,

    message = """Cross-reference to a location in the same topic or to a specific
    element inside another topic. Our write style allows
    cross-references to link only to an entire topic file. To fix,
    restructure or link the cross-references to another topic (in the
    same project)."""
)


