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
#
# Portions copyright 2018 Marc Paquette

from distutils.core import setup
import os
import glob

setupargs = {
    "name": "FlareLint",
    
    "version": "2.0",
    
    "packages": ["flarelint"],
    
    "url": "https://flarelint.github.io",
    
    "author": "Intelerad Medical Systems Incorporated",
    "author_email": 'documentation@intelerad.com',
    "maintainer": "Marc Paquette",
    "maintainer_email": 'flarelint@freelists.org',
    
    "description": "Catch style problems in MadCap Flare projects for faster production and higher-quality content.",
    
    "long_description": open("README.txt").read(),
    
    "license": "CDDL-1.0",
    
    "package_data": { 'flarelint': ['rules/*_rule.txt', 'LICENSE.txt'] },
    
    "classifiers": [
        'Development Status :: 4 - Beta',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing'
    ],
    
    "keywords": 'MadCap Flare lint',
}

if __name__ == '__main__':
    setup(**setupargs)
