#coding=utf-8

import logging
import time
import os

def getLogger(logfilename):
    logger = logging.getLogger("packageTool")
    logger.setLevel(logging.DEBUG)
    FORMAT = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    filehandler = logging.FileHandler(logfilename)
    filehandler.setLevel(logging.DEBUG)
    filehandler.setFormatter(FORMAT)
    logger.addHandler(filehandler)
    return logger

def deleteLogger(logfilename):
    logger = logging.getLogger("packageTool")
    filehandler = logging.FileHandler(logfilename)
    logger.removeHandler(filehandler)

