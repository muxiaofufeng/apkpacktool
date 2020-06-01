# -*- coding: utf-8 -*-

import os
import os.path
import re
import platform
import inspect
import sys
import codecs
import threading
import time

curDir = os.path.join(os.path.dirname(os.getcwd()), )


def execWinCommand(cmd):
    os.system(cmd)


def execWinCommandInput(tip):
    r = os.popen("set /p s=" + tip)
    txt = r.read()
    r.close()
    return txt


def del_file_folder(src):
    if os.path.exists(src):
        if os.path.isfile(src):
            try:
                src = src.replace('\\', '/')
                os.remove(src)
            except:
                pass

        elif os.path.isdir(src):
            for item in os.listdir(src):
                itemsrc = os.path.join(src, item)
                del_file_folder(itemsrc)

            try:
                os.rmdir(src)
            except:
                pass


def copy_files(src, dest):
    if not os.path.exists(src):
        return

    if os.path.isfile(src):
        copy_file(src, dest)
        return

    for f in os.listdir(src):
        sourcefile = os.path.join(src, f)
        targetfile = os.path.join(dest, f)
        if os.path.isfile(sourcefile):
            copy_file(sourcefile, targetfile)
        else:
            copy_files(sourcefile, targetfile)


def copy_file(src, dest):
    sourcefile = getFullPath(src)
    destfile = getFullPath(dest)
    if not os.path.exists(sourcefile):
        return
    if not os.path.exists(destfile) or os.path.getsize(destfile) != os.path.getsize(sourcefile):
        destdir = os.path.dirname(destfile)
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        destfilestream = open(destfile, 'wb')
        sourcefilestream = open(sourcefile, 'rb')
        destfilestream.write(sourcefilestream.read())
        destfilestream.close()
        sourcefilestream.close()

def getCurrDir():
    global curDir
    retPath = curDir
    retPath = retPath.decode('gbk')
    return retPath


def getFullPath(filename):
    if os.path.isabs(filename):
        return filename
    currdir = getCurrDir()
    filename = os.path.join(os.path.dirname(currdir), 'tool', filename)
    filename = filename.replace('\\', '/')
    filename = re.sub('/+', '/', filename)
    return filename

def getJavaCMD():
    return "java"

def getJavacCMD():
    return "javac"

#def getToolPath(filename):
#    return "bin/" + filename

def getSystemType():
    s=platform.system()
    if platform.system() == 'Windows':
        return "win"
    if platform.system() =='Darwin':
        return "mac"
    if platform.system() =='linux':
        return "linux"

#def getFullToolPath(filename):
#    return getFullPath(getToolPath(filename))


def getFullOutputPath(channel):
    path = getFullPath('packages/' + channel)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def execFormatCmd(cmd):
    s = os.popen(cmd)
    ret = s.read()
    return ret

def replaceStringAtFile(filePath, toBeReplaceString, replaceWithString):
    if not os.path.exists(filePath):
        return
    with open(filePath, 'r') as re:
        lines = re.readlines()

    with open(filePath, 'w') as wi:
        for s in lines:
            wi.write(s.replace(toBeReplaceString, replaceWithString))
        else:
            wi.write


# copy文件夹
def copy_dir(src, dest):
    if not os.path.exists(src):
        return
    for f in os.listdir(src):
        sourcefile = os.path.join(src, f)
        targetfile = os.path.join(dest, f)
        if os.path.isfile(sourcefile):
            copy_file(sourcefile, targetfile)
        else:
            copy_dir(sourcefile, targetfile)

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def list_files(src, resFiles, igoreFiles):
    if os.path.exists(src):
        if os.path.isfile(src) and src not in igoreFiles:
            resFiles.append(src)
        elif os.path.isdir(src):
            for f in os.listdir(src):
                if src not in igoreFiles:
                    list_files(os.path.join(src, f), resFiles, igoreFiles)
    return resFiles