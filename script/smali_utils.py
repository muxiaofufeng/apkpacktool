import os
import os.path
import re
import platform
import subprocess
import inspect
import sys
import codecs
import threading
import time


def get_smali_method_count(smaliFile, allMethods):
    if not os.path.exists(smaliFile):
        return 0
    f = open(smaliFile)
    lines = f.readlines()
    f.close()

    classLine = lines[0]
    classLine.strip()
    if not classLine.startswith(".class"):
        return 0
    className = parse_class(classLine)
    count = 0
    for line in lines:
        line = line.strip()
        method = None
        if line.startswith(".method"):
            method = parse_method_default(className, line)
        elif line.startswith("invoke-"):
            method = parse_method_invoke(line)
        if method is None:
            continue
        if method not in allMethods:
            count = count + 1
            allMethods.append(method)
        else:
            pass
           
    return count



def parse_class(line):

    if not line.startswith(".class"):
        return None
    blocks = line.split()
    return blocks[len(blocks)-1]



def parse_method_default(className, line):
    if not line.startswith(".method"):
        return None
    blocks = line.split()
    return className + "->" + blocks[len(blocks)-1]


def parse_method_invoke(line):
    if not line.startswith("invoke-"):
        pass
    blocks = line.split()
    return blocks[len(blocks)-1]