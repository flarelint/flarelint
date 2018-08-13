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
    extensions = rule.TOPICS,

    match = flarenode.whenself('title'),

    test = lambda n: n.valueof().strip() == '',

    message = """The HTML `title` element contains text.
    Flare prefers using this text, when it exists, instead of the
    topic's `h1` title when generating online
    help.  We prefer the latter to make maintenance easier and avoid
    surprises.  For example, when these elements do not have identical
    content, the links in the See Also sections and search results of
    online help have different names than the topic title.  To fix,
    right-click the topic in Content Explorer, then in the Topic
    Properties tab, delete Topic Title."""
)

