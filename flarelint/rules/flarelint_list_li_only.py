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

    # This match function is also the test. We do this to make sure
    # that the message generated from the failure of the test refers
    # to the offending non-li element.

    match = lambda n: n.iselement('*',
                             lambda n: (n.parent('ol') or n.parent('ul')) and n.name() != 'li'),

    test = lambda n: False,
    
    message = """A non-list element in a list. Only `li` elements are supported in
    lists.  To fix, convert this element to a list item or wrap it in
    a list item."""
)

