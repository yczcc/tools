#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
import sys
import shutil
import re
import chardet
from platform import system

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

SOURCE_DIR_WINDOWS = "Z:/code/src"
SOURCE_DIR_LINUX = "/data/code/src"

SOURCE_DIR = ""
CONVERT_FILE_TYPES = [
  ".cpp",
  ".cc",
  ".cxx",
  ".c",
  ".h",
  ".hpp",
  ".hxx"
  ]


def detect_os():
    os = system().lower()
    if 'darwin' in os:
        return "MAC_OS_X"

    elif 'windows' in os:
        return "WINDOWS"

    elif 'linux' in os:
        with open('/proc/version', 'r') as f:
            vers = f.read()
            if 'microsoft' in vers.lower():
                return "WSL"  # Windows10的Linux子系统
        return "LINUX"

    elif 'bsd' in os:
        return "BSD"

    elif 'cygwin' in os:
        return "CYGWIN"

    else:
        return None

def check_need_convert(filename):
    for filetype in CONVERT_FILE_TYPES:
        if filename.lower().endswith(filetype):
            return True
    return False

os_type = detect_os()
if os_type == 'WINDOWS':
    SOURCE_DIR = SOURCE_DIR_WINDOWS
elif os_type == 'LINUX':
    SOURCE_DIR = SOURCE_DIR_LINUX
else:
    print "[error] unknown os type:" + sys.platform + " - " + system().lower()
    exit(0)

total_cnt = 0
success_cnt = 0
unkown_cnt = 0
def convert_encoding_to_utf_8(filename):
    global total_cnt,success_cnt,unkown_cnt
    # Backup the origin file.

    # convert file from the source encoding to target encoding
    content = codecs.open(filename, 'r').read()
    source_encoding = chardet.detect(content)['encoding']
    total_cnt+=1
    if source_encoding == None:
        print "??",filename
        unkown_cnt+=1
        return
    print "  ",source_encoding, filename
    # if source_encoding != 'utf-8' and source_encoding != 'UTF-8-SIG':
    if source_encoding != 'utf-8':
        content = content.decode(source_encoding, 'ignore') #.encode(source_encoding)
        codecs.open(filename, 'w', encoding='utf-8').write(content)
    success_cnt+=1

def convert_dir(root_dir):
    if os.path.exists(root_dir) == False:
        print "[error] dir:",root_dir,"do not exit"
        return
    print "work in",convertdir
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if check_need_convert(f):
                filename = os.path.join(root, f)
                try:
                    convert_encoding_to_utf_8(filename)
                except Exception, e:
                    print "WA",filename,e
    print "finish total:",total_cnt,"success:",success_cnt,"unkown_cnt",unkown_cnt

if __name__ == '__main__':
    # if len(sys.argv) == 1:
    #     raw_input("[error] need root dir")
    #     sys.exit(-1)
    # convertdir = sys.argv[1]
    convertdir = SOURCE_DIR
    convert_dir(convertdir)