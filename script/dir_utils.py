#coding=utf-8

import os

class WorkDirCls:
    channelsDir = ''
    currentChannelDir = ''
    workRootDir = ''
    workDecompileDir = ''
    workSDKDir = ''
    workTempDir = ''
    workDecompileSmaliDir = ''

    def __init__(self, rootDir, gameId, gamePkg, channelFlag, sdkVersion):
        self.channelsDir = os.path.join(rootDir, 'channel', sdkVersion)
        self.currentChannelDir = os.path.join(self.channelsDir, channelFlag)
        self.workRootDir = os.path.join(rootDir, 'workDir', gameId, channelFlag, gamePkg)
        self.workDecompileDir = os.path.join(self.workRootDir, 'decompile')
        self.workSDKDir = os.path.join(self.workRootDir, 'sdk')
        self.workTempDir = os.path.join(self.workRootDir,'temp')
        self.workDecompileSmaliDir = os.path.join(self.workDecompileDir, 'smali')
