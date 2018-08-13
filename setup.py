from distutils.core import setup
import os
import glob

setupargs = {
    "name": "FlareLint",
    
    "version": "1.2",
    
    "packages": ["flarelint"],
    
    "url": "http://www.intelerad.com/flarelint",
    
    "author": "Intelerad Medical Systems Incorporated",
    "author_email": 'documentation@intelerad.com',
    
    "description": "Catch style problems in MadCap Flare projects for faster production and higher-quality content.",
    
    "long_description": open("README.txt").read(),
    
    "license": "CDDL-1.0",
    
    "package_data": { 'flarelint': ['rules/*.py', 'LICENSE.txt'] },
    
    "classifiers": [
        'Development Status :: 5 - Production/Stable',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing'
    ],
    
    "keywords": 'MadCap Flare lint',
}

if __name__ == '__main__':

    setup(**setupargs)
