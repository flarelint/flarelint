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

_HEADINGS_ACCEPTED = set(['h1', 'h2'])
_HEADINGS_ALL = set(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

rule.Error(
    extensions = rule.TOPICS_AND_SNIPPETS,

    # This match function is also the test, so the test function always fails.
    match = lambda n: n.name() in _HEADINGS_ALL.difference(_HEADINGS_ACCEPTED),

    test = lambda n: False,

    message = """Unsupported header. This level of header is not supported by our
    conventions or styles.  To fix, place a subtopic in a separate
    file."""
)

