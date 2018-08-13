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
    extensions = rule.TOPICS,

    # Match only the first title, ignore others. Multiple h1 elements
    # are handled by other rules.
    match = lambda n: n.iselement('h1') and not n.precedingsibling('h1'),
                 
    test = lambda n: n.indexof() == 0,
                 
    message = """Topic body must start with an `h1` element. To fix, move the `h1`
    element to the top of the body."""
)
