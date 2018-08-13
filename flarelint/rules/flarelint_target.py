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

import os
from flarelint import rule
from flarelint import flarenode

def targeterror(test, message, outputType = None):
    rule.Error(
        extensions = rule.TARGETS,
        match = lambda n: n.iselement('CatapultTarget')
        and (n.attribute('Type') == outputType or outputType is None),
        test = test,
        message = message
    )

targeterror(
    outputType = 'PDF',
    
    test = lambda n: n.attribute('PatchHeadingLevels') == 'true',

    message = """Use TOC Depth for Heading Levels is not enabled in the Advanced
    tab. We use this feature to make sure that topics in the PDF
    follow the hierarchy specified in the Flare TOC. To fix, enable
    Use TOC Depth for Heading Levels in the Advanced tab."""
)

