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
import shutil
import subprocess
import distutils.core
import setup
import sys
import glob
import zipfile

FLARE_CMD = "\"c:\\Program Files (x86)\\MadCap Software\\MadCap Flare V8\\Flare.app\\madbuild.exe\""
STAGE_DIR = "staging"
ARCHIVE_NAME = "{0}-{1}".format(setup.setupargs["name"].replace(' ', ''),
                                setup.setupargs["version"].replace('.', '-'))

def normalize_path(path):
    return path.replace('/', '\\')

def log(s):
    print(s)
    sys.stdout.flush()

def logcmd(s):
    log("  " + normalize_path(s))

def logtask(s):
    log("")
    log("-----------")
    log(s)

def pause():
    input("Press Enter to continue.")

def mkdir(path):
    """Make a directory, including intermediate directories if they don't
    exist. Or do nothing if the directory already exists."""
    logcmd("mkdir " + path)
    if not os.path.isdir(path):
        os.mkdir(path)

def rmdir(dirpath):
    """Remove a directory or do nothing if the directory does not exist."""
    logcmd("rmdir " + dirpath)
    if os.path.isdir(dirpath):
        shutil.rmtree(dirpath)

def delete(filepath):
    """Remove a file or do nothing if the file does not exist."""
    logcmd("del " + filepath)
    if os.path.exists(filepath):
        os.remove(filepath)

def copy(src, dst):
    for s in glob.glob(src):
        logcmd("copy " + s + " " + dst)
        shutil.copy2(s, dst)

def xcopy(src, dst):
    logcmd("xcopy " + src + " " + dst)
    shutil.copytree(src, dst)

def rename(src, dst):
    logcmd("rename " + src + " " + dst)
    os.rename(src, dst)
        
def cd(path):
    logcmd("cd " + path)
    os.chdir(path)
        
def zip(name):
    logcmd("zip " + name + ".zip")
    shutil.make_archive(base_name = name, format = "zip")
        
def shellcmd(cmd):
    logcmd(cmd)
    p = subprocess.Popen(args = cmd, shell = True)
    p.wait()
    
def clean():
    logtask("Cleaning")
    rmdir(STAGE_DIR)
    rmdir("doc/Output")
    rmdir("dist")
    rmdir("build")
    delete("MANIFEST")
    delete(ARCHIVE_NAME + '.zip')

def builddoc():
    logtask("Building doc")
    shellcmd(FLARE_CMD + " -project doc\\userguide.flprj -target HTML5.fltar")

def buildpkg():
    logtask("Building Python package installer")
    setup.setupargs["script_args"] = ["clean"]
    distutils.core.setup(**setup.setupargs)
    setup.setupargs["script_args"] = ["bdist_msi"]
    distutils.core.setup(**setup.setupargs)

def assemble():
    logtask("Assembling parts")
    mkdir(STAGE_DIR)
    for f in ["README.txt", "flarelint/LICENSE.txt", setup.setupargs["name"] + ".bat"]:
        copy(f, STAGE_DIR)
    copy("dist/*.msi", os.path.join(STAGE_DIR, setup.setupargs["name"] + ".msi"))

    xcopy(os.path.join("doc/Output", os.environ['USERNAME'], "HTML5"), os.path.join(STAGE_DIR, "doc"))

    mkdir(os.path.join(STAGE_DIR, "src"))
    xcopy(os.path.join("flarelint"), os.path.join(STAGE_DIR, "src/flarelint"))
    rmdir(os.path.join(STAGE_DIR, "src/flarelint/__pycache__"))
    rmdir(os.path.join(STAGE_DIR, "src/flarelint/rules/__pycache__"))
    for f in ["README.txt", setup.setupargs["name"] + ".bat", "setup.py", "build.py"]:
        copy(f, os.path.join(STAGE_DIR, "src"))

    mkdir(os.path.join(STAGE_DIR, "src/doc"))
    copy("doc/*.flprj", os.path.join(STAGE_DIR, "src/doc"))
    xcopy(os.path.join("doc/Content"), os.path.join(STAGE_DIR, "src/doc/Content"))
    xcopy(os.path.join("doc/Project"), os.path.join(STAGE_DIR, "src/doc/Project"))

def archive():
    logtask("Creating the ZIP")
    pwd = os.getcwd()
    cd(STAGE_DIR)
    zip(os.path.join(pwd, ARCHIVE_NAME))
    cd(pwd)
    
def main():
    clean()
    builddoc()
    buildpkg()
    assemble()
    archive()
    
if __name__ == '__main__':
    main()
