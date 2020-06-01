#coding=utf-8

import file_utils
import os
import os.path
import smali_utils
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import ElementTree
import os
import os.path
import zipfile
import re
import subprocess
import platform
from xml.dom import minidom
import codecs
import shutil
import shlex, subprocess
import json
import ConfigParser
from PIL import Image
import channel_utils

import sys

androidNS = 'http://schemas.android.com/apk/res/android'

def execFormatCmd(cmd):
    cmd = cmd.replace('\\', '/')
    cmd = re.sub('/+', '/', cmd)
    cmdinfo = shlex.split(cmd)
    out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, outerr = out.communicate()
    if out.returncode == 0:
        return True, output
    else:
        return False, outerr


def jar2dex(srcDir, dstDir, channelConfig):
    cmd = 'dx --dex --output="%s" ' % (dstDir+"/classes.dex")
    for f in os.listdir(srcDir):
        if f.endswith(".jar"):
            cmd = cmd + " " + os.path.join(srcDir, f)
    libsPath = os.path.join(srcDir, "libs")
    if os.path.exists(libsPath):
        for f in os.listdir(libsPath):
            if f.endswith(".jar"):
                if f == 'bugly_crash_release.jar':
                    if channelConfig['game_info'].has_key('bugly_id') and len(channelConfig['game_info']['bugly_id']) > 0:
                        cmd = cmd + " " + os.path.join(srcDir, "libs", f)
                else:
                    cmd = cmd + " " + os.path.join(srcDir, "libs", f)
    ret, err = execFormatCmd(cmd)
    if ret:
        return True, cmd, ""
    return False, cmd, err


def dex2smali(dexFile, targetdir, bakSmaliJarPath):
    if not os.path.exists(bakSmaliJarPath):
        return
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)
    cmd = '%s -jar %s d -o %s %s' % (file_utils.getJavaCMD(), bakSmaliJarPath, targetdir, dexFile)
    ret, err = execFormatCmd(cmd)
    if ret:
        return True, cmd, ""
    return False, cmd, err


def splitDex(decompileDir):
    #方法数超过上限时，拆分smali，生成多个dex文件
    smaliPath = decompileDir + "/smali"
    multidexFilePath = os.path.join(smaliPath, "/android/support/multidex/MultiDex.smali")
    allFiles = []
    allFiles = file_utils.list_files(decompileDir, allFiles, [])
    maxFuncNum = 65500
    currFucNum = 0
    totalFucNum = 0
    currDexIndex = 1
    allRefs = []
    #保证NSdkApplication等类在第一个classex.dex文件中
    for f in allFiles:
        f = f.replace("\\", "/")
        if "/com/jiyou" in f or "/android/support/multidex" in f:
            currFucNum = currFucNum + smali_utils.get_smali_method_count(f, allRefs)
    totalFucNum = currFucNum
    for f in allFiles:
        f = f.replace("\\", "/")
        if not f.endswith(".smali"):
            continue
        if "/com/jiyou" in f or "/android/support/multidex" in f:
            continue
        thisFucNum = smali_utils.get_smali_method_count(f, allRefs)
        totalFucNum = totalFucNum + thisFucNum
        if currFucNum + thisFucNum >= maxFuncNum:
            currFucNum = thisFucNum
            currDexIndex = currDexIndex + 1
            newDexPath = os.path.join(decompileDir, "smali_classes"+str(currDexIndex))
            os.makedirs(newDexPath)
        else:
            currFucNum = currFucNum + thisFucNum
        if currDexIndex > 1:
            targetPath = f[0:len(decompileDir)] + "/smali_classes"+str(currDexIndex) + f[len(smaliPath):]
            file_utils.copy_file(f, targetPath)
            file_utils.del_file_folder(f)


def decompileApk(apkfile, targetdir, apktool):
    if os.path.exists(targetdir):
        file_utils.del_file_folder(targetdir)
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)
    cmd = '%s -jar %s d -f %s -o %s' % (file_utils.getJavaCMD(), apktool, apkfile, targetdir)
    ret, result = execFormatCmd(cmd)
    return ret, cmd, result

def removeDefaultSDKInfo(workDecompileDir, defaultSDKInfoConfigFile):
    #class:
    #   com.jiyou.*
    #   com.google.jygson.*
    #   jyokio.*
    #res:
    #   删除jy_开头的资源
    #   其他要删除的资源列表
    #assets:
    #   ['dkmpsdk_Channel.json', 'jysdk_Config.json', 'jysdk_Type.json', 'html/userArgeement.html']
    #manifest:
    #   删除com.jiyou.jysdklib.ui开头的activity
    resultmsg = ''

    defaultSDKInfoConfig = ConfigParser.ConfigParser()
    defaultSDKInfoConfig.read(defaultSDKInfoConfigFile)
    defaultClasses = eval(defaultSDKInfoConfig.get('class', 'classes')) #list
    defaultResCommon = eval(defaultSDKInfoConfig.get('res', 'common')) #list
    defaultResCommon = tuple(defaultResCommon)
    defaultResDrawable = eval(defaultSDKInfoConfig.get('res', 'drawable')) #list
    defaultResAnim = eval(defaultSDKInfoConfig.get('res', 'anim')) #list
    defaultResLayout = eval(defaultSDKInfoConfig.get('res', 'layout')) #list
    defaultAssetsFile = eval(defaultSDKInfoConfig.get('assets', 'configFile')) #list
    defaultAssetsDir = eval(defaultSDKInfoConfig.get('assets', 'configDir')) #list
    defaultManifestActivity = eval(defaultSDKInfoConfig.get('manifest', 'activity')) #list
    #删除class
    for defaultClass in defaultClasses:
        deleteDir = os.path.join(workDecompileDir, 'smali', defaultClass.replace('.', os.sep))
        file_utils.del_file_folder(deleteDir)
    #获取要处理的目录：drawable/anim/layout
    drawableDirList = []
    animDirList = []
    layoutDirList = []
    for filename in os.listdir(os.path.join(workDecompileDir, 'res')):
        filepath = os.path.join(os.path.join(workDecompileDir, 'res', filename))
        if os.path.isdir(filepath):
            if 'drawable' in filename:
                drawableDirList.append(filename)
            elif 'anim' in filename:
                animDirList.append(filename)
            elif 'layout' in filename:
                layoutDirList.append(filename)
    #删除res drawable
    for drawableItem in drawableDirList:
        drawablePath = os.path.join(workDecompileDir, 'res', drawableItem)
        for filename in os.listdir(drawablePath):
            if filename.startswith(defaultResCommon) or filename in defaultResDrawable:
                filePath = os.path.join(drawablePath, filename)
                os.remove(filePath)
    #删除res anim
    for animItem in animDirList:
        animPath = os.path.join(workDecompileDir, 'res', animItem)
        for filename in os.listdir(animPath):
            if filename.startswith(defaultResCommon) or filename in defaultResAnim:
                filePath = os.path.join(animPath, filename)
                os.remove(filePath)
    #删除res layout
    for layoutItem in layoutDirList:
        layoutPath = os.path.join(workDecompileDir, 'res', layoutItem)
        for filename in os.listdir(layoutPath):
            if filename.startswith(defaultResCommon) or filename in defaultResLayout:
                filePath = os.path.join(layoutPath, filename)
                os.remove(filePath)
    #处理res values colors.xml/
    colorPath = os.path.join(workDecompileDir, 'res', 'values', 'colors.xml')
    if os.path.isfile(colorPath):
        try:
            ctree = ET.parse(colorPath)
            croot = ctree.getroot()
        except Exception as err:
            resultmsg = u"%s|解析colors.xml失败" % resultmsg
            return False, resultmsg
        colorNodes = croot.findall('color')
        if colorNodes and len(colorNodes) > 0:
            for colorNode in colorNodes:
                if 'name' in colorNode.attrib:
                    colorNodeName = colorNode.attrib['name']
                    if colorNodeName.startswith(defaultResCommon):
                        croot.remove(colorNode)
            ctree.write(colorPath, "UTF-8")
            resultmsg = u"%s|成功删除colors.xml中默认渠道的资源信息" % resultmsg
    dimenPath = os.path.join(workDecompileDir, 'res', 'values', 'dimens.xml')
    if os.path.isfile(dimenPath):
        try:
            dtree = ET.parse(dimenPath)
            droot = dtree.getroot()
        except Exception as err:
            resultmsg = u"%s|解析dimens.xml失败" % resultmsg
            return False, resultmsg
        dimenNodes = droot.findall('dimen')
        if dimenNodes and len(dimenNodes) > 0:
            for dimenNode in dimenNodes:
                if 'name' in dimenNode.attrib:
                    dimenNodeName = dimenNode.attrib['name']
                    if dimenNodeName.startswith(defaultResCommon):
                        droot.remove(dimenNode)
            dtree.write(dimenPath, "UTF-8")
            resultmsg = u"%s|成功删除dimens.xml中默认渠道的资源信息" % resultmsg
    stringPath = os.path.join(workDecompileDir, 'res', 'values', 'strings.xml')
    if os.path.isfile(dimenPath):
        try:
            stree = ET.parse(stringPath)
            sroot = stree.getroot()
        except Exception as err:
            resultmsg = u"%s|解析strings.xml失败" % resultmsg
            return False, resultmsg
        stringNodes = sroot.findall('string')
        if stringNodes and len(stringNodes) > 0:
            for stringNode in stringNodes:
                if 'name' in stringNode.attrib:
                    stringNodeName = stringNode.attrib['name']
                    if stringNodeName.startswith(defaultResCommon):
                        sroot.remove(stringNode)
            stree.write(stringPath, "UTF-8")
            resultmsg = u"%s|成功删除strings.xml中默认渠道的资源信息" % resultmsg
    stylePath = os.path.join(workDecompileDir, 'res', 'values', 'styles.xml')
    if os.path.isfile(stylePath):
        try:
            stytree = ET.parse(stylePath)
            styroot = stytree.getroot()
        except Exception as err:
            resultmsg = u"%s|解析styles.xml失败" % resultmsg
            return False, resultmsg
        styleNodes = styroot.findall('style')
        if styleNodes and len(styleNodes) > 0:
            for styleNode in styleNodes:
                if 'name' in styleNode.attrib:
                    styleNodeName = styleNode.attrib['name']
                    if styleNodeName.startswith(defaultResCommon):
                        styroot.remove(styleNode)
            stytree.write(stylePath, "UTF-8")
            resultmsg = u"%s|成功删除styles.xml中默认渠道的资源信息" % resultmsg
    #删除assets 文件
    assetsPath = os.path.join(workDecompileDir, 'assets')
    for filename in os.listdir(assetsPath):
        filePath = os.path.join(assetsPath, filename)
        if os.path.isfile(filePath) and filename in defaultAssetsFile:
            os.remove(filePath)
        elif os.path.isdir(filePath) and filename in defaultAssetsDir:
            file_utils.del_file_folder(filePath)
    #删除public.xml 对应节点
    publicList = []
    for item in defaultResDrawable:
        publicList.append(os.path.splitext(item)[0])
    for item in defaultResAnim:
        publicList.append(os.path.splitext(item)[0])
    for item in defaultResLayout:
        publicList.append(os.path.splitext(item)[0])
    publicPath = os.path.join(workDecompileDir, 'res', 'values', 'public.xml')
    if os.path.isfile(publicPath):
        try:
            ptree = ET.parse(publicPath)
            proot = ptree.getroot()
        except Exception as err:
            resultmsg = u"%s|解析public.xml失败" % resultmsg
            return False, resultmsg
        pnodes = proot.findall("public")
        if pnodes is None or len(pnodes) == 0:
            resultmsg = u"%s|public.xml文件中没有public节点" % resultmsg
        else:
            for pnode in pnodes:
                if "name" in pnode.attrib:
                    nodeName = pnode.attrib["name"]
                    if nodeName in publicList or nodeName.startswith(defaultResCommon):
                        proot.remove(pnode)
            ptree.write(publicPath, "UTF-8")
            resultmsg = u"%s|成功删除public.xml中默认渠道的资源信息" % resultmsg
    #删除manifest 对应activity
    androidManifestFile = os.path.join(workDecompileDir, "AndroidManifest.xml")
    if os.path.isfile(androidManifestFile):
        key = "{" + androidNS + "}name"
        value = "{" + androidNS + "}value"
        try:
            tree = ET.parse(androidManifestFile)
            root = tree.getroot()
        except Exception as err:
            resultmsg = u"%s|删除AndroidManifest.xml中默认配置失败:%s" % (resultmsg, err)
            return False, resultmsg
        appnode = root.find("application")
        if appnode is None:
            resultmsg = u"%s|AndroidManifest.xml不存在application节点" % resultmsg
            return False, resultmsg
        else:
            activitylist = appnode.findall("activity")
            if activitylist is None or len(activitylist) == 0:
                resultmsg = u"%s|AndroidManifest.xml中没有activity标签" % resultmsg
                return False, resultmsg
            else:
                for activity in activitylist:
                    aName = activity.get(key)
                    if aName:
                        for defaultActivity in defaultManifestActivity:
                            if defaultActivity in aName:
                                appnode.remove(activity)
        tree.write(androidManifestFile, "UTF-8")
    return True, u"%s|删除默认SDK配置成功" % resultmsg

def handleSpecialResource(workDecompileDir):
    ET.register_namespace('android', androidNS)
    resultmsg = ''
    fillType = "{" + androidNS + "}fillType"
    keyboardNavigationCluster = "{" + androidNS + "}keyboardNavigationCluster"
    ic_launcher_foreground_file = os.path.join(workDecompileDir, 'res', 'drawable-v24', 'ic_launcher_foreground.xml')
    abc_screen_toolbar_file = os.path.join(workDecompileDir, 'res', 'layout-v26', 'abc_screen_toolbar.xml')
    if os.path.exists(ic_launcher_foreground_file):
        try:
            launcherTree = ET.parse(ic_launcher_foreground_file)
            launcherRoot = launcherTree.getroot()
        except Exception as err:
            resultmsg = u"%s|解析ic_launcher_foreground.xml失败" %resultmsg
            return False, resultmsg
        pathNodes = launcherRoot.findall("path")
        if pathNodes is not None and len(pathNodes) > 0:
            for pathNode in pathNodes:
                if pathNode.attrib.has_key(fillType):
                    del pathNode.attrib[fillType]
        launcherTree.write(ic_launcher_foreground_file, "UTF-8")
        resultmsg = '%s|删除ic_launcher_foreground.xml中的fillType成功'%resultmsg

    if os.path.exists(abc_screen_toolbar_file):
        try:
            toolbarTree = ET.parse(abc_screen_toolbar_file)
            toolbarRoot = toolbarTree.getroot()
        except Exception as err:
            resultmsg = u"%s|解析abc_screen_toolbar_file.xml失败" % resultmsg
            return False, resultmsg
        containerNode = toolbarRoot.find("android.support.v7.widget.ActionBarContainer")
        if containerNode is not None:
            if containerNode.attrib.has_key(keyboardNavigationCluster):
                del containerNode.attrib[keyboardNavigationCluster]
        toolbarTree.write(abc_screen_toolbar_file, "UTF-8")
        resultmsg = '%s|删除abc_screen_toolbar.xml中的keyboardNavigationCluster成功'%resultmsg
    return True, resultmsg

def recompileApk(workTempDir,sourceFolder, apkFile, apkToolPath):
    if os.path.exists(sourceFolder):
        cmd = '%s -jar %s b  -p %s  -f  %s -o %s' % (file_utils.getJavaCMD(), apkToolPath, workTempDir, sourceFolder, apkFile)
        ret, err = execFormatCmd(cmd)
    if ret:
        return True, cmd, ""
    return False, cmd, err

def isAarMode(workSDKDir):
    isAar = False
    for filename in os.listdir(workSDKDir):
        if filename.endswith('.aar'):
            isAar = True
            break
    return isAar

def unzipAarFiles(workSDKDir):
    for aarFile in os.listdir(workSDKDir):
        if aarFile.endswith('.aar'):
            aarPath = os.path.join(workSDKDir, aarFile)
            aarUnzipPath = os.path.join(workSDKDir, os.path.splitext(aarFile)[0])
            cmd = 'unzip %s -d %s'%(aarPath, aarUnzipPath)
            ret, err = execFormatCmd(cmd)
            if ret:
                os.remove(aarPath)
        #解压zip文件
        if aarFile.endswith('.zip'):
            zipPath = os.path.join(workSDKDir, aarFile)
            zipUnzipPath = os.path.join(workSDKDir, os.path.splitext(aarFile)[0])
            cmd = 'unzip %s -d %s'%(zipPath, zipUnzipPath)
            ret, err = execFormatCmd(cmd)
            if ret:
                os.remove(zipPath)

def mergeAarFiles(workSDKDir):
    for aarDir in os.listdir(workSDKDir):
        aarDirPath = os.path.join(workSDKDir, aarDir)
        if os.path.isdir(aarDirPath) and not aarDir.startswith('.'):
            for aarItem in os.listdir(aarDirPath):
                aarItemPath = os.path.join(aarDirPath, aarItem)
                if aarItem.startswith('.') or aarItem in ['R.txt', 'aapt']:
                    continue
                if aarItem == 'AndroidManifest.xml':
                    mergeManifestFile = os.path.join(workSDKDir, 'sdkmanifest.xml')
                    if not os.path.exists(mergeManifestFile):
                        file_utils.copy_file(aarItemPath, mergeManifestFile)
                    else:
                        mergeAarManifest(aarItemPath, mergeManifestFile)
                elif aarItem == 'classes.jar':
                    newJarName = '%s.jar'%os.path.splitext(aarDir)[0]
                    sdkJarPath = os.path.join(workSDKDir, 'libs', newJarName)
                    file_utils.copy_file(aarItemPath, sdkJarPath)
                elif aarItem in ['libs', 'aidl', 'jni']:
                    file_utils.copy_dir(aarItemPath, os.path.join(workSDKDir, 'libs'))
                elif aarItem == 'res':
                    copyResToApk(aarItemPath, os.path.join(workSDKDir, 'res'))
                elif aarItem == 'assets':
                    file_utils.copy_dir(aarItemPath, os.path.join(workSDKDir, 'assets'))
                elif os.path.isfile(aarItemPath):
                    file_utils.copy_file(aarItemPath, os.path.join(workSDKDir, aarItem))
                elif os.path.isdir(aarItemPath):
                    file_utils.copy_dir(aarItemPath, os.path.join(workSDKDir, aarItem))
            file_utils.del_file_folder(aarDirPath)

#把aar中的manifest文件合并成sdkmanifest文件
def mergeAarManifest(aarManifest, sdkManifest):
    if not os.path.exists(aarManifest) or not os.path.exists(sdkManifest):
        return False
    ET.register_namespace('android', androidNS)
    try:
        sdkTree = ET.parse(sdkManifest)
        sdkRoot = sdkTree.getroot()
    except Exception as err:
        return False, u"解析sdk的AndroidManifest文件失败:%s" % err
    try:
        aarTree = ET.parse(aarManifest)
        aarRoot = aarTree.getroot()
    except Exception as err:
        return False, u"解析aar的manifest.xml文件失败:%s" % err
    f = open(sdkManifest)
    sdkContent = f.read()
    f.close()
    permissionConfigNode = aarRoot.findall('uses-permission')
    key = '{' + androidNS + '}name'
    # iconkey = '{' + androidNS + '}icon'
    if permissionConfigNode != None and len(permissionConfigNode) > 0:
        for child in permissionConfigNode:
            val = child.get(key)
            if val != None and len(val) > 0:
                attrIndex = sdkContent.find(val)
                if -1 == attrIndex:
                    sdkRoot.append(child)
    aarConfigNode = aarRoot.find('application')
    sdkNode = sdkRoot.find('application')
    if aarConfigNode != None:
        applicationName = aarConfigNode.get(key)
        # 渠道有自己的ApplicationName,母包没有时，添加到母包
        if applicationName != None and len(applicationName) > 0:
            sdkapplicationname = sdkNode.get(key)
            if sdkapplicationname != None and len(sdkapplicationname) > 0:
                pass
            else:
                sdkNode.attrib[key] = applicationName
        for child in list(aarConfigNode):
            # if sdkRoot.find('application'):
                #TODO 自己创建一个application
            sdkRoot.find('application').append(child)
    sdkTree.write(sdkManifest, 'UTF-8')
    return True, u'合并成功'


def handle_drawable_v4(decompileDir):
    drawable_xhdpiPath = os.path.join(decompileDir, "res", "drawable-xhdpi")
    drawable_xxhdpiPath = os.path.join(decompileDir, "res", "drawable-xxhdpi")
    drawable_xxxhdpiPath = os.path.join(decompileDir, "res", "drawable-xxxhdpi")
    #optional
    drawable_sizePath = os.path.join(decompileDir, "res", "drawable")
    drawable_ldpiPath = os.path.join(decompileDir, "res", "drawable-ldpi")
    drawable_mdpiPath = os.path.join(decompileDir, "res", "drawable-mdpi")
    drawable_hdpiPath = os.path.join(decompileDir, "res", "drawable-hdpi")
    mipmap_ldpiPath = os.path.join(decompileDir, "res", "mipmap-ldpi")
    mipmap_mdpiPath = os.path.join(decompileDir, "res", "mipmap-mdpi")
    mipmap_hdpiPath = os.path.join(decompileDir, "res", "mipmap-hdpi")
    mipmap_xhdpiPath = os.path.join(decompileDir, "res", "mipmap-xhdpi")
    mipmap_xxhdpiPath = os.path.join(decompileDir, "res", "mipmap-xxhdpi")
    mipmap_xxxhdpiPath = os.path.join(decompileDir, "res", "mipmap-xxxhdpi")

    if not os.path.exists(drawable_ldpiPath):
        os.makedirs(drawable_ldpiPath)
    if not os.path.exists(drawable_mdpiPath):
        os.makedirs(drawable_mdpiPath)
    if not os.path.exists(drawable_hdpiPath):
        os.makedirs(drawable_hdpiPath)
    if not os.path.exists(drawable_xhdpiPath):
        os.makedirs(drawable_xhdpiPath)
    if not os.path.exists(drawable_xxhdpiPath):
        os.makedirs(drawable_xxhdpiPath)
    if not os.path.exists(drawable_xxxhdpiPath):
        os.makedirs(drawable_xxxhdpiPath)

    #删除v4文件夹，防止冲突
    drawable_ldpi_v4Path = os.path.join(decompileDir, "res", "drawable-ldpi-v4")
    drawable_mdpi_v4Path = os.path.join(decompileDir, "res", "drawable-mdpi-v4")
    drawable_hdpi_v4Path = os.path.join(decompileDir, "res", "drawable-hdpi-v4")
    drawable_xhdpi_v4Path = os.path.join(decompileDir, "res", "drawable-xhdpi-v4")
    drawable_xxhdpi_v4Path = os.path.join(decompileDir, "res", "drawable-xxhdpi-v4")
    drawable_xxxhdpi_v4Path = os.path.join(decompileDir, "res", "drawable-xxxhdpi-v4")



    mipmap_hdpi_v4 = os.path.join(decompileDir, "res", "mipmap-hdpi-v4")
    mipmap_mdpi_v4 = os.path.join(decompileDir, "res", "mipmap-mdpi-v4")
    mipmap_xhdpi_v4 = os.path.join(decompileDir, "res", "mipmap-xhdpi-v4")
    mipmap_xxhdpi_v4 = os.path.join(decompileDir, "res", "mipmap-xxhdpi-v4")
    mipmap_xxxhdpi_v4 = os.path.join(decompileDir, "res", "mipmap-xxxhdpi-v4")




    if os.path.exists(drawable_ldpi_v4Path):
        file_utils.copy_dir(drawable_ldpi_v4Path, drawable_ldpiPath)
        file_utils.del_file_folder(drawable_ldpi_v4Path)
    if os.path.exists(drawable_mdpi_v4Path):
        file_utils.copy_dir(drawable_mdpi_v4Path, drawable_mdpiPath)
        file_utils.del_file_folder(drawable_mdpi_v4Path)
    if os.path.exists(drawable_hdpi_v4Path):
        file_utils.copy_dir(drawable_hdpi_v4Path, drawable_hdpiPath)
        file_utils.del_file_folder(drawable_hdpi_v4Path)
    if os.path.exists(drawable_xhdpi_v4Path):
        file_utils.copy_dir(drawable_xhdpi_v4Path, drawable_xhdpiPath)
        file_utils.del_file_folder(drawable_xhdpi_v4Path)
    if os.path.exists(drawable_xxhdpi_v4Path):
        file_utils.copy_dir(drawable_xxhdpi_v4Path, drawable_xxhdpiPath)
        file_utils.del_file_folder(drawable_xxhdpi_v4Path)
    if os.path.exists(drawable_xxxhdpi_v4Path):
        file_utils.copy_dir(drawable_xxxhdpi_v4Path, mipmap_xxxhdpiPath)
        file_utils.del_file_folder(drawable_xxxhdpi_v4Path)



    if os.path.exists(mipmap_hdpi_v4):
        file_utils.copy_dir(mipmap_hdpi_v4, mipmap_ldpiPath)
        file_utils.del_file_folder(mipmap_hdpi_v4)

    if os.path.exists(mipmap_mdpi_v4):
        file_utils.copy_dir(mipmap_mdpi_v4, mipmap_mdpiPath)
        file_utils.del_file_folder(mipmap_mdpi_v4)

    if os.path.exists(mipmap_xhdpi_v4):
        file_utils.copy_dir(mipmap_xhdpi_v4, mipmap_xhdpiPath)
        file_utils.del_file_folder(mipmap_xhdpi_v4)

    if os.path.exists(mipmap_xxhdpi_v4):
        file_utils.copy_dir(mipmap_xxhdpi_v4, mipmap_xxhdpiPath)
        file_utils.del_file_folder(mipmap_xxhdpi_v4)

    if os.path.exists(mipmap_xxxhdpi_v4):
        file_utils.copy_dir(mipmap_xxxhdpi_v4, mipmap_xxxhdpiPath)
        file_utils.del_file_folder(mipmap_xxxhdpi_v4)



def handlePackageIcon(gameIconFile, decompileDir, gameIconName):
    if not os.path.isfile(gameIconFile) or not os.path.exists(gameIconFile):
        return False, u"游戏图标不存在|%s" % gameIconFile
    resultmsg = ""
    try:
        gameIcon = Image.open(gameIconFile)
        if gameIcon.mode != "RGBA":
            gameIcon = gameIcon.convert("RGBA")
    except Exception as e:
        return False, e

    drawable_xhdpiSize = (96, 96)
    drawable_xxhdpiSize = (144, 144)
    drawable_xxxhdpiSize = (192, 192)
    #optional
    drawable_size = (512, 512)
    drawable_ldpiSize = (36, 36)
    drawable_mdpiSize = (48, 48)
    drawable_hdpiSize = (72, 72)
    mipmap_ldpiSize = (36, 36)
    mipmap_mdpiSize = (48, 48)
    mipmap_hdpiSize = (72, 72)
    mipmap_xhdpiSize = (96, 96)
    mipmap_xxhdpiSize = (144, 144)
    mipmap_xxxhdpiSize = (192, 192)

    drawable_xhdpiIcon = gameIcon.resize(drawable_xhdpiSize, Image.ANTIALIAS)
    drawable_xxhdpiIcon = gameIcon.resize(drawable_xxhdpiSize, Image.ANTIALIAS)
    drawable_xxxhdpiIcon = gameIcon.resize(drawable_xxxhdpiSize, Image.ANTIALIAS)

    drawable_xhdpiPath = os.path.join(decompileDir, "res", "drawable-xhdpi")
    drawable_xxhdpiPath = os.path.join(decompileDir, "res", "drawable-xxhdpi")
    drawable_xxxhdpiPath = os.path.join(decompileDir, "res", "drawable-xxxhdpi")
    #optional
    drawable_sizePath = os.path.join(decompileDir, "res", "drawable")
    drawable_ldpiPath = os.path.join(decompileDir, "res", "drawable-ldpi")
    drawable_mdpiPath = os.path.join(decompileDir, "res", "drawable-mdpi")
    drawable_hdpiPath = os.path.join(decompileDir, "res", "drawable-hdpi")
    mipmap_ldpiPath = os.path.join(decompileDir, "res", "mipmap-ldpi")
    mipmap_mdpiPath = os.path.join(decompileDir, "res", "mipmap-mdpi")
    mipmap_hdpiPath = os.path.join(decompileDir, "res", "mipmap-hdpi")
    mipmap_xhdpiPath = os.path.join(decompileDir, "res", "mipmap-xhdpi")
    mipmap_xxhdpiPath = os.path.join(decompileDir, "res", "mipmap-xxhdpi")
    mipmap_xxxhdpiPath = os.path.join(decompileDir, "res", "mipmap-xxxhdpi")

    if not os.path.exists(drawable_ldpiPath):
        os.makedirs(drawable_ldpiPath)
    if not os.path.exists(drawable_mdpiPath):
        os.makedirs(drawable_mdpiPath)
    if not os.path.exists(drawable_hdpiPath):
        os.makedirs(drawable_hdpiPath)
    if not os.path.exists(drawable_xhdpiPath):
        os.makedirs(drawable_xhdpiPath)
    if not os.path.exists(drawable_xxhdpiPath):
        os.makedirs(drawable_xxhdpiPath)
    if not os.path.exists(drawable_xxxhdpiPath):
        os.makedirs(drawable_xxxhdpiPath)

    #删除v4文件夹，防止冲突
    drawable_ldpi_v4Path = os.path.join(decompileDir, "res", "drawable-ldpi-v4")
    drawable_mdpi_v4Path = os.path.join(decompileDir, "res", "drawable-mdpi-v4")
    drawable_hdpi_v4Path = os.path.join(decompileDir, "res", "drawable-hdpi-v4")
    drawable_xhdpi_v4Path = os.path.join(decompileDir, "res", "drawable-xhdpi-v4")
    drawable_xxhdpi_v4Path = os.path.join(decompileDir, "res", "drawable-xxhdpi-v4")
    drawable_xxxhdpi_v4Path = os.path.join(decompileDir, "res", "drawable-xxxhdpi-v4")



    mipmap_hdpi_v4 = os.path.join(decompileDir, "res", "mipmap-hdpi-v4")
    mipmap_mdpi_v4 = os.path.join(decompileDir, "res", "mipmap-mdpi-v4")
    mipmap_xhdpi_v4 = os.path.join(decompileDir, "res", "mipmap-xhdpi-v4")
    mipmap_xxhdpi_v4 = os.path.join(decompileDir, "res", "mipmap-xxhdpi-v4")
    mipmap_xxxhdpi_v4 = os.path.join(decompileDir, "res", "mipmap-xxxhdpi-v4")




    if os.path.exists(drawable_ldpi_v4Path):
        file_utils.copy_dir(drawable_ldpi_v4Path, drawable_ldpiPath)
        file_utils.del_file_folder(drawable_ldpi_v4Path)
    if os.path.exists(drawable_mdpi_v4Path):
        file_utils.copy_dir(drawable_mdpi_v4Path, drawable_mdpiPath)
        file_utils.del_file_folder(drawable_mdpi_v4Path)
    if os.path.exists(drawable_hdpi_v4Path):
        file_utils.copy_dir(drawable_hdpi_v4Path, drawable_hdpiPath)
        file_utils.del_file_folder(drawable_hdpi_v4Path)
    if os.path.exists(drawable_xhdpi_v4Path):
        file_utils.copy_dir(drawable_xhdpi_v4Path, drawable_xhdpiPath)
        file_utils.del_file_folder(drawable_xhdpi_v4Path)
    if os.path.exists(drawable_xxhdpi_v4Path):
        file_utils.copy_dir(drawable_xxhdpi_v4Path, drawable_xxhdpiPath)
        file_utils.del_file_folder(drawable_xxhdpi_v4Path)
    if os.path.exists(drawable_xxxhdpi_v4Path):
        file_utils.copy_dir(drawable_xxxhdpi_v4Path, mipmap_xxxhdpiPath)
        file_utils.del_file_folder(drawable_xxxhdpi_v4Path)



    if os.path.exists(mipmap_hdpi_v4):
        file_utils.copy_dir(mipmap_hdpi_v4, mipmap_ldpiPath)
        file_utils.del_file_folder(mipmap_hdpi_v4)

    if os.path.exists(mipmap_mdpi_v4):
        file_utils.copy_dir(mipmap_mdpi_v4, mipmap_mdpiPath)
        file_utils.del_file_folder(mipmap_mdpi_v4)

    if os.path.exists(mipmap_xhdpi_v4):
        file_utils.copy_dir(mipmap_xhdpi_v4, mipmap_xhdpiPath)
        file_utils.del_file_folder(mipmap_xhdpi_v4)

    if os.path.exists(mipmap_xxhdpi_v4):
        file_utils.copy_dir(mipmap_xxhdpi_v4, mipmap_xxhdpiPath)
        file_utils.del_file_folder(mipmap_xxhdpi_v4)

    if os.path.exists(mipmap_xxxhdpi_v4):
        file_utils.copy_dir(mipmap_xxxhdpi_v4, mipmap_xxxhdpiPath)
        file_utils.del_file_folder(mipmap_xxxhdpi_v4)



        #optional
    if os.path.exists(drawable_sizePath) and os.path.exists(os.path.join(drawable_sizePath, gameIconName)):
        drawable_sizeIcon = gameIcon.resize(drawable_size, Image.ANTIALIAS)
        drawable_sizeIcon.save(os.path.join(drawable_sizePath, gameIconName), "PNG", quality=95)
    if os.path.exists(drawable_ldpiPath) and os.path.exists(os.path.join(drawable_ldpiPath, gameIconName)):
        drawable_ldpiIcon = gameIcon.resize(drawable_ldpiSize, Image.ANTIALIAS)
        drawable_ldpiIcon.save(os.path.join(drawable_ldpiPath, gameIconName), "PNG", quality=95)
    if os.path.exists(drawable_mdpiPath) and os.path.exists(os.path.join(drawable_mdpiPath, gameIconName)):
        drawable_mdpiIcon = gameIcon.resize(drawable_mdpiSize, Image.ANTIALIAS)
        drawable_mdpiIcon.save(os.path.join(drawable_mdpiPath, gameIconName), "PNG", quality=95)
    if os.path.exists(drawable_hdpiPath) and os.path.exists(os.path.join(drawable_hdpiPath, gameIconName)):
        drawable_hdpiIcon = gameIcon.resize(drawable_hdpiSize, Image.ANTIALIAS)
        drawable_hdpiIcon.save(os.path.join(drawable_hdpiPath, gameIconName), "PNG", quality=95)
    if os.path.exists(mipmap_ldpiPath) and os.path.exists(os.path.join(mipmap_ldpiPath, gameIconName)):
        mipmap_ldpiIcon = gameIcon.resize(mipmap_ldpiSize, Image.ANTIALIAS)
        mipmap_ldpiIcon.save(os.path.join(mipmap_ldpiPath, gameIconName), "PNG", quality=95)
    if os.path.exists(mipmap_mdpiPath) and os.path.exists(os.path.join(mipmap_mdpiPath, gameIconName)):
        mipmap_mdpiIcon = gameIcon.resize(mipmap_mdpiSize, Image.ANTIALIAS)
        mipmap_mdpiIcon.save(os.path.join(mipmap_mdpiPath, gameIconName), "PNG", quality=95)
    if os.path.exists(mipmap_hdpiPath) and os.path.exists(os.path.join(mipmap_hdpiPath, gameIconName)):
        mipmap_hdpiIcon = gameIcon.resize(mipmap_hdpiSize, Image.ANTIALIAS)
        mipmap_hdpiIcon.save(os.path.join(mipmap_hdpiPath, gameIconName), "PNG", quality=95)
    if os.path.exists(mipmap_xhdpiPath) and os.path.exists(os.path.join(mipmap_xhdpiPath, gameIconName)):
        mipmap_xhdpiIcon = gameIcon.resize(mipmap_xhdpiSize, Image.ANTIALIAS)
        mipmap_xhdpiIcon.save(os.path.join(mipmap_xhdpiPath, gameIconName), "PNG", quality=95)
    if os.path.exists(mipmap_xxhdpiPath) and os.path.exists(os.path.join(mipmap_xxhdpiPath, gameIconName)):
        mipmap_xxhdpiIcon = gameIcon.resize(mipmap_xxhdpiSize, Image.ANTIALIAS)
        mipmap_xxhdpiIcon.save(os.path.join(mipmap_xxhdpiPath, gameIconName), "PNG", quality=95)
    if os.path.exists(mipmap_xxxhdpiPath) and os.path.exists(os.path.join(mipmap_xxxhdpiPath, gameIconName)):
        mipmap_xxxhdpiIcon = gameIcon.resize(mipmap_xxxhdpiSize, Image.ANTIALIAS)
        mipmap_xxxhdpiIcon.save(os.path.join(mipmap_xxxhdpiPath, gameIconName), "PNG", quality=95)

    drawable_xhdpiIcon.save(os.path.join(drawable_xhdpiPath, gameIconName), "PNG", quality=95)
    drawable_xxhdpiIcon.save(os.path.join(drawable_xxhdpiPath, gameIconName), "PNG", quality=95)
    drawable_xxxhdpiIcon.save(os.path.join(drawable_xxxhdpiPath, gameIconName), "PNG", quality=95)

    return True, resultmsg


def handlePackageResource(oldGameResourcePath, newGameResourcePath):
    if not os.path.exists(newGameResourcePath):
        return False, u"资源目录不存在，无需替换"
    if not os.path.exists(oldGameResourcePath):
        os.makedirs(oldGameResourcePath)
    for filename in os.listdir(newGameResourcePath):
        if not filename.startswith('.'):
            file_utils.copy_file(os.path.join(newGameResourcePath, filename), os.path.join(oldGameResourcePath, filename))
    return True, u"替换素材成功"

def signApk(targetApk, signInfo):
    cmdStr = ''
    keystorefile = signInfo['keystore']
    password = signInfo['password']
    alias = signInfo['aliaskey']
    aliaspwd = signInfo['aliaspwd']
    if keystorefile is None:
        return False, cmdStr, u"keystore文件不存在"
    if not os.path.exists(keystorefile):
        return False, cmdStr, u"keystore文件不存在"

    listcmd = 'aapt list %s' %targetApk
    cmdStr = '%s%s\n'%(cmdStr, listcmd)
    ret, output = execFormatCmd(listcmd)
    if ret:
        for filename in output.split('\n'):
            if filename.find('META_INF') == 0:
                rmcmd = 'aapt remove "%s" "%s"' % (targetApk, filename)
                cmdStr = '%s%s\n'%(cmdStr, rmcmd)
                ret, err = execFormatCmd(rmcmd)
                if not ret:
                    return False, cmdStr, err
    else:
        return False, cmdStr, output

    signcmd = u'jarsigner -keystore "%s" -storepass "%s" -keypass "%s" "%s" "%s" -sigalg SHA1withRSA -digestalg SHA1' % (
        keystorefile, password, aliaspwd, targetApk, alias)
    cmdStr = '%s%s\n'%(cmdStr, signcmd)
    ret, err = execFormatCmd(signcmd)
    if ret:
        return True, cmdStr, ""
    return False, cmdStr, u"签名失败|%s" % err

def alignApk(zipalignfile,apkfile, destApkFile):
    aligncmd = u'%s -f 4 "%s" "%s"' % (zipalignfile,apkfile, destApkFile)
    ret, err = execFormatCmd(aligncmd)
    if ret:
        return True, aligncmd,  ""
    return False, aligncmd, u"资源整合失败|%s" % err

def copyLibs(srcDir, dstDir):
    # logger = logging_utils.getLogger()
    if not os.path.exists(srcDir):
        return False, u"渠道插件包不存在libs目录"
    if not os.path.exists(dstDir):
        os.makedirs(dstDir)
    for f in os.listdir(srcDir):
        sourcefile = os.path.join(srcDir, f)
        targetfile = os.path.join(dstDir, f)
        if (sourcefile.endswith(".jar")):
            continue
        # if os.path.isdir(targetfile) or targetfile.split(os.sep)[-3] == 'lib':
        if os.path.isfile(sourcefile):
            shutil.copy(sourcefile, targetfile)
        if os.path.isdir(sourcefile):
            copyLibs(sourcefile, targetfile)
    return True, u"拷贝libs资源完成"

def deleteOtherLibDir(libDir, partnerId):
    targetLibList = []
    if partnerId == '1' or partnerId == '7'or partnerId == '6':
        targetArmeabi = 'armeabi-v7a'
    elif partnerId == '3'or partnerId == '9':
        targetArmeabi = 'armeabi'
    else:
        return False, u'请检查partnerId'
    targetLibPath = os.path.join(libDir, targetArmeabi)
    if os.path.exists(targetLibPath):
        for targetSo in os.listdir(targetLibPath):
            if targetSo.endswith('.so'):
                targetLibList.append(targetSo)

    for libname in os.listdir(libDir):
        libPath = os.path.join(libDir, libname)
        if libname != targetArmeabi and os.path.isdir(libPath):
            for otherSo in os.listdir(libPath):
                if otherSo not in targetLibList:
                    file_utils.copy_file(os.path.join(libPath, otherSo), os.path.join(targetLibPath, otherSo))
                    targetLibList.append(otherSo)
            file_utils.del_file_folder(libPath)
    return True, u"删除其他lib成功"


def mergeResXml(sourcefile, targetfile):
    if not os.path.exists(targetfile):
        return False
    aryXml = ['strings.xml', 'styles.xml', 'colors.xml', 'dimens.xml', 'ids.xml', 'attrs.xml', 'integers.xml',
              'arrays.xml', 'bools.xml', 'drawables.xml', 'values.xml']
    basename = os.path.basename(sourcefile)
    if basename in aryXml:
        f = open(targetfile, 'r')
        targetContent = f.read()
        f.close()
        try:
            sourceTree = ET.parse(sourcefile)
            sourceRoot = sourceTree.getroot()
            targetTree = ET.parse(targetfile)
            targetRoot = targetTree.getroot()
        except Exception as e:
            return False
        for node in list(sourceRoot):
            val = node.get('name')
            if val != None and len(val) > 0:
                valMatched = '"' + val + '"'
                attrIndex = targetContent.find(valMatched)
                if -1 == attrIndex:
                    targetRoot.append(node)
        targetTree.write(targetfile, 'UTF-8')
        return True
    return False


# copy渠道res和assets（特定xml文件进行合并）
def copyResToApk(copyFrom, copyTo):
    if not os.path.exists(copyFrom):
        return False, u"渠道资源目录不存在%s" % copyFrom
    if not os.path.exists(copyTo):
        os.makedirs(copyTo)
    if os.path.isfile(copyFrom) and not mergeResXml(copyFrom, copyTo):
        shutil.copy(copyFrom, copyTo)
        return True, ""
    for f in os.listdir(copyFrom):
        sourcefile = os.path.join(copyFrom, f)
        targetfile = os.path.join(copyTo, f)
        if os.path.isfile(sourcefile):
            if mergeResXml(sourcefile, targetfile):
                continue
            shutil.copy(sourcefile, targetfile)
        if os.path.isdir(sourcefile):
            copyResToApk(sourcefile, targetfile)
    return True, u"拷贝资源完成"

# copy 其他资源（如annotations.zip）
def copyOtherResToApk(copyFrom, copyTo):
    if not os.path.exists(copyFrom):
        return False, u"渠道资源目录不存在%s" % copyFrom
    if not os.path.exists(copyTo):
        os.makedirs(copyTo)
    for filename in os.listdir(copyFrom):
        if filename not in ['assets', 'libs', 'res', 'sdkmanifest.xml']:
            filepath = os.path.join(copyFrom, filename)
            if os.path.isfile(filepath):
                file_utils.copy_file(filepath, os.path.join(copyTo, filename))
            elif os.path.isdir(filepath):
                file_utils.copy_dir(filepath, os.path.join(copyTo, filename))
    return True, u'拷贝其他资源完成'

#配置填充
def updateConfFile(channelConfig, workDecompileDir):


 #jysdk SDK star===============

    #assets/jyg_config.json
    generalConfigPath = os.path.join(workDecompileDir, 'assets', 'jyg_config.json')
    with open(generalConfigPath) as rgConfig:
        generalConfig = json.load(rgConfig)
    generalConfig['JY_SDK_TYPE'] = channelConfig['plugins']['login_plugin']
    #ad
    if (channelConfig['ad_sdk'].has_key('tt_id') and len(channelConfig['ad_sdk']['tt_id']) > 0) or (channelConfig['ad_sdk'].has_key('gdt_id') and channelConfig['ad_sdk'].has_key('gdt_secret_key') and len(channelConfig['ad_sdk']['gdt_id']) > 0 and len(channelConfig['ad_sdk']['gdt_secret_key']) > 0) or (channelConfig['ad_sdk'].has_key('ks_id') and len(channelConfig['ad_sdk']['ks_id']) > 0 and channelConfig['ad_sdk'].has_key('ks_name') and len(channelConfig['ad_sdk']['ks_name']) > 0):
        generalConfig['JY_STA_GLOBAL_STATISTIC'] = channelConfig['plugins']['ad_plugin']
    else:
        generalConfig['JY_STA_GLOBAL_STATISTIC'] = ''

    with open(generalConfigPath, 'w+') as wgConfig:
        json.dump(generalConfig, wgConfig)


    #assets/jy_public_config.json
    sdkConfigPath = os.path.join(workDecompileDir, 'assets', 'jy_public_config.json')
    if os.path.isfile(sdkConfigPath):
        with open(sdkConfigPath) as sgConfig:
            sdkConfig = json.load(sgConfig)
        sdkConfig['JY_GAMEID'] = channelConfig['game_info']['game_id']
        sdkConfig['JY_PARTNERID'] = channelConfig['game_info']['partner_id']
        sdkConfig['JY_GAME_KEY'] = channelConfig['game_info']['game_key']
        sdkConfig['JY_PAY_KEY'] = channelConfig['game_info']['pay_key']
        sdkConfig['JY_SDK_VERSION'] = channelConfig['game_info']['channel_version']
        sdkConfig['JY_SERVER_URL'] = channelConfig['game_info']['server_url']

        with open(sdkConfigPath, 'w+') as sgConfig:
            json.dump(sdkConfig, sgConfig)

 #jysdk SDK end===============



    #assets/ysdkconf.ini
    if channelConfig['game_info']['partner_id'] == '3': #yyb
        ysdkConfPath = os.path.join(workDecompileDir, 'assets', 'ysdkconf.ini')
        ysdkConfData = ''
        with open(ysdkConfPath) as ysdkConf:
            for line in ysdkConf.readlines():
                if line.startswith('QQ_APP_ID='):
                    newLine = 'QQ_APP_ID=' + channelConfig['game_info']['yyb_qq_app_id'] + '\n'
                    ysdkConfData = ysdkConfData + newLine.encode('utf8')
                elif line.startswith('WX_APP_ID='):
                    newLine = 'WX_APP_ID=' + channelConfig['game_info']['yyb_wx_app_id'] + '\n'
                    ysdkConfData = ysdkConfData + newLine.encode('utf8')
                elif line.startswith('OFFER_ID='):
                    newLine = 'OFFER_ID=' + channelConfig['game_info']['yyb_qq_app_id'] + '\n'
                    ysdkConfData = ysdkConfData + newLine.encode('utf8')
                else:
                    ysdkConfData = ysdkConfData + line
        with open(ysdkConfPath, 'w+') as newYsdkConf:
            newYsdkConf.write(ysdkConfData)
    
    #修改头条conf
    toutiaoConfPath = os.path.join(workDecompileDir, 'assets', 'toutiao_config.json')
    if channelConfig['ad_sdk'].has_key('tt_id') and os.path.isfile(toutiaoConfPath):
        with open(toutiaoConfPath) as ttConfig:
            ttConfigs = json.load(ttConfig)
        ttConfigs['JY_TouTiaoID'] = channelConfig['ad_sdk']['tt_id']
        with open(toutiaoConfPath, 'w+') as sConfig:
            json.dump(ttConfigs, sConfig)

    #修改广点通conf
    gdtConfPath = os.path.join(workDecompileDir, 'assets', 'gdt_config.json')
    if channelConfig['ad_sdk'].has_key('gdt_id') and channelConfig['ad_sdk'].has_key('gdt_secret_key') and os.path.isfile(gdtConfPath):
        with open(gdtConfPath) as gdtConfig:
            gdtConfigs = json.load(gdtConfig)
        gdtConfigs['JY_GDT_USERACTIONSETID'] = channelConfig['ad_sdk']['gdt_id']
        gdtConfigs['JY_GDT_APPSECRETKEY'] = channelConfig['ad_sdk']['gdt_secret_key']
        if channelConfig['ad_sdk'].has_key('gdt_reporting_probability')and len(channelConfig['ad_sdk']['gdt_reporting_probability']) > 0:
            gdtConfigs['JY_GDT_REPORTING_PROBABILITY'] = channelConfig['ad_sdk']['gdt_reporting_probability']
        else:
            gdtConfigs['JY_GDT_REPORTING_PROBABILITY'] = ''


        if channelConfig['ad_sdk'].has_key('jy_gdt_pay_once')and len(channelConfig['ad_sdk']['jy_gdt_pay_once']) > 0 and channelConfig['ad_sdk']['gdt_reporting_probability']==1:
            gdtConfigs['JY_GDT_PAY_ONCE'] = channelConfig['ad_sdk']['jy_gdt_pay_once']
        else:
            gdtConfigs['JY_GDT_PAY_ONCE'] = '0'
        with open(gdtConfPath, 'w+') as sConfig:
            json.dump(gdtConfigs, sConfig)
    
    #修改快手conf
    kuaishouConfPath = os.path.join(workDecompileDir, 'assets', 'kuaishou_config.json')
    if channelConfig['ad_sdk'].has_key('ks_id') and channelConfig['ad_sdk'].has_key('ks_name') and os.path.isfile(kuaishouConfPath):
        with open(kuaishouConfPath) as kuaishouConfig:
            kuaishouConfigs = json.load(kuaishouConfig)
        kuaishouConfigs['JY_KuaiShouID'] = channelConfig['ad_sdk']['ks_id']
        kuaishouConfigs['JY_KuaiShouName'] = channelConfig['ad_sdk']['ks_name']
        with open(kuaishouConfPath, 'w+') as sConfig:
            json.dump(kuaishouConfigs, sConfig)


    
    #修改渠道配置(huawei/oppo/vivo...)
    channel_utils.handleChannelConf(channelConfig, workDecompileDir)

#修改apktool.yml versionCode
def updateApktoolYmlFile(channelConfig, workDecompileDir):
    hasVersionCode = False
    hasTargetSdkVersion = False
    if channelConfig['game_info'].has_key('version_code') and len(channelConfig['game_info']['version_code']) > 0:
        hasVersionCode = True
    if channelConfig['game_info'].has_key('target_sdk_version') and len(channelConfig['game_info']['target_sdk_version']) > 0:
        hasTargetSdkVersion = True
    if hasVersionCode or hasTargetSdkVersion:
        apktoolYmlFile = os.path.join(workDecompileDir, 'apktool.yml')
        if os.path.isfile(apktoolYmlFile):
            ymlContent = ''
            with open(apktoolYmlFile, 'r') as ryml:
                for line in ryml.readlines():
                    if hasVersionCode and 'versionCode' in line:
                        newLine = "%s: '%s'\n"%(line.split(':')[0], channelConfig['game_info']['version_code'])
                        ymlContent = '%s%s'%(ymlContent, newLine)
                    elif hasTargetSdkVersion and 'targetSdkVersion' in line:
                        newLine = "%s: '%s'\n"%(line.split(':')[0], channelConfig['game_info']['target_sdk_version'])
                        ymlContent = '%s%s'%(ymlContent, newLine)
                    else:
                        ymlContent = '%s%s'%(ymlContent, line)
            with open(apktoolYmlFile, 'w') as wyml:
                wyml.write(ymlContent)

# 合并渠道manifest文件到母包的AndroidManifest.xml
def mergeManifest(sourceManifest, sdkManifest, channelConfig):
    specialPackageName = channelConfig['game_info']['game_bundle_id']
    if not os.path.exists(sourceManifest):
        return False, u"母包AndroidManifest.xml文件不存在|%s" % sourceManifest
    if not os.path.exists(sdkManifest):
        return False, u"渠道manifest.xml文件不存在|%s" % sdkManifest
    mainActivityName = getMainActivityName(sourceManifest)
    returnmsg = ""
    # 合并
    ET.register_namespace('android', androidNS)
    try:
        sourceTree = ET.parse(sourceManifest)
        sourceRoot = sourceTree.getroot()
    except Exception as err:
        return False, u"解析AndroidManifest文件失败:%s" % err
    # 修改包名
    oldPackageName = sourceRoot.attrib['package']
    sourceRoot.attrib['package'] = specialPackageName
    try:
        sdkTree = ET.parse(sdkManifest)
        sdkRoot = sdkTree.getroot()
    except Exception as err:
        return False, u"解析渠道manifest.xml文件失败:%s" % err
    compileSdkVersion = '{' + androidNS + '}compileSdkVersion'
    compileSdkVersionCodename = '{' + androidNS + '}compileSdkVersionCodename'
    if sourceRoot.attrib.has_key(compileSdkVersionCodename):
        del sourceRoot.attrib[compileSdkVersionCodename]
    if sourceRoot.attrib.has_key(compileSdkVersion):
        del sourceRoot.attrib[compileSdkVersion]
    # sdkRoot.remove('compileSdkVersionCodename')
    f = open(sourceManifest)
    sourceContent = f.read()
    f.close()
    permissionConfigNode = sdkRoot.findall('uses-permission')
    key = '{' + androidNS + '}name'
    if permissionConfigNode != None and len(permissionConfigNode) > 0:
        for child in permissionConfigNode:
            val = child.get(key)
            if val != None and len(val) > 0:
                attrIndex = sourceContent.find(val)
                if -1 == attrIndex:
                    sourceRoot.append(child)
    appConfigNode = sdkRoot.find('application')
    appNode = sourceRoot.find('application')
    
    if appConfigNode != None:
        applicationName = appConfigNode.get(key)
        # 渠道有自己的ApplicationName,母包没有时，添加到母包
        if applicationName != None and len(applicationName) > 0:
            sourceapplicationname = appNode.get(key)
            if sourceapplicationname != None and len(sourceapplicationname) > 0:
                pass
            else:
                appNode.attrib[key] = applicationName
        for child in list(appConfigNode):
            sourceRoot.find('application').append(child)
    #处理provider
    authorities = '{' + androidNS + '}authorities'
    providerlist = appNode.findall("provider")
    if providerlist and len(providerlist) > 0:
        for provider in providerlist:
            #只替换FileProvider，防止误伤
            if provider.attrib[key].endswith(r'.FileProvider'):
                cFlag = channelConfig['game_info']['channel_flag']
                if(cFlag!='mi'):
                    provider.attrib[authorities] = channelConfig['game_info']['game_bundle_id'] + '.fileProvider'


    #渠道特殊处理
    #游戏主界面的launchMode不能设置为singleTask,否则会导致点击home键再返回游戏时拉不起登录界面
    #而且主界面activity的configChanges属性要有screenSize
    if 1:
        launchMode = '{' + androidNS + '}launchMode'
        configChanges = '{' + androidNS + '}configChanges'
        activitylist = appNode.findall("activity")
        if activitylist is not None and len(activitylist) > 0:
            isMainActivity = False
            for activity in activitylist:
                intentlist = activity.findall("intent-filter")
                if intentlist is not None and len(intentlist) > 0:
                    for intentNode in intentlist:
                        isFindAction = False
                        isFindCategory = False
                        actionlist = intentNode.findall('action')
                        if actionlist is not None and len(actionlist) > 0:
                            for actionNode in actionlist:
                                if actionNode.attrib[key] == "android.intent.action.MAIN":
                                    isFindAction = True
                                    break
                        categorylist = intentNode.findall('category')
                        if categorylist is not None and len(categorylist) > 0:
                            for categoryNode in categorylist:
                                if categoryNode.attrib[key] == "android.intent.category.LAUNCHER":
                                    isFindCategory = True
                                    break
                        if isFindAction and isFindCategory:
                            isMainActivity = True
                            break
                    if isMainActivity:
                        if activity.attrib.has_key(launchMode):
                            #del activity.attrib[launchMode] #删掉
                            activity.attrib[launchMode] = "singleTop" #设置为singleTop
                        if activity.attrib.has_key(configChanges):
                            if "screenSize" not in activity.attrib[configChanges]:
                                activity.attrib[configChanges] = "%s|screenSize" % activity.attrib[configChanges]
                        else:
                            activity.attrib[configChanges] = "screenSize"
                        #2019-08-01添加：应用宝渠道，在主activity里面添加url scheme 格式：scheme://host/path（path为分包名）
                        if channelConfig['game_info']['partner_id'] == '3':
                            aScheme = '{' + androidNS + '}scheme'
                            aHost = '{' + androidNS + '}host'
                            aPath = '{' + androidNS + '}path'
                            urlSchemeIntentNode = SubElement(activity, 'intent-filter')
                            #data node
                            urlSchemeDataNode = SubElement(urlSchemeIntentNode, 'data')
                            urlSchemeDataNode.attrib[aScheme] = 'jyapp'
                            urlSchemeDataNode.attrib[aHost] = 'game'
                            urlSchemeDataNode.attrib[aPath] = '/' + channelConfig['game_info']['game_bundle_id']
                            #category node1
                            urlSchemeCategoryNode1 = SubElement(urlSchemeIntentNode, 'category')
                            urlSchemeCategoryNode1.attrib[key] = 'android.intent.category.DEFAULT'
                            #category node2
                            urlSchemeCategoryNode2 = SubElement(urlSchemeIntentNode, 'category')
                            urlSchemeCategoryNode2.attrib[key] = 'android.intent.category.BROWSABLE'
                            #action node
                            urlSchemeActionNode = SubElement(urlSchemeIntentNode, 'action')
                            urlSchemeActionNode.attrib[key] = 'android.intent.action.VIEW'
                        #20191118修改：修改主activity中的android:label，改为与application中的一样，值为：@string/app_name
                        applabel = '{' + androidNS + '}label'
                        if activity.attrib.has_key(applabel):
                            activity.attrib[applabel] = "@string/app_name"
                        #主activity渠道特殊处理
                        channel_utils.handleMainActivityInManifest(activity, channelConfig)
                        break
    sourceTree.write(sourceManifest, 'UTF-8')
    # 替换掉AndroidManifest.xml文件中${JYNSDK_MAINACTIVITY}标签
    if mainActivityName and mainActivityName != '':
        file_utils.replaceStringAtFile(sourceManifest, "${JYNSDK_MAINACTIVITY}", mainActivityName.encode('utf8'))
        # os.system("sed -i 's/${JYNSDK_MAINACTIVITY}/%s/g' %s" % (mainActivityName, sourceManifest))
    return True, u"合并manifest成功|%s" % returnmsg, oldPackageName


def replaceSpecialString(androidmanifestfile, channelConfig, oldPackageName):
    if channelConfig['game_info'].has_key('yyb_qq_app_id'):
        file_utils.replaceStringAtFile(androidmanifestfile, "${QQ_APPID}", (channelConfig['game_info']['yyb_qq_app_id']).encode('utf8'))
    if channelConfig['game_info'].has_key('yyb_wx_app_id'):
        file_utils.replaceStringAtFile(androidmanifestfile, "${WX_APPID}", (channelConfig['game_info']['yyb_wx_app_id']).encode('utf8'))
    if channelConfig['game_info'].has_key('game_bundle_id'):
        packagename = channelConfig['game_info']['game_bundle_id']
        file_utils.replaceStringAtFile(androidmanifestfile, "${PACKAGENAME}", packagename.encode('utf8'))
        file_utils.replaceStringAtFile(androidmanifestfile, oldPackageName, packagename.encode('utf8'))
    #替换渠道manifest占位符(huawei/oppo/vivo...)
    channel_utils.handleChannelManifest(androidmanifestfile, channelConfig)

def updateAppDisplayName(workDecompileDir, gameName):
    stringFilePath = os.path.join(workDecompileDir, 'res', 'values', 'strings.xml')
    resultmsg = ''
    if os.path.isfile(stringFilePath):
        try:
            ptree = ET.parse(stringFilePath)
            proot = ptree.getroot()
        except Exception as err:
            resultmsg = u"%s|解析strings.xml失败" % resultmsg
            return False, resultmsg
        pnodes = proot.findall("string")
        if pnodes is None or len(pnodes) == 0:
            resultmsg = u"%s|strings.xml文件中没有public节点" % resultmsg
        else:
            for pnode in pnodes:
                if "name" in pnode.attrib and pnode.attrib["name"] == 'app_name':
                    pnode.text = gameName
            ptree.write(stringFilePath, "UTF-8")
    return True, resultmsg


# 重新生成R文件，编译，然后copy到反编译的smali目录
def generateNewRFile(oldPackageName, newPackageName, decompileDir, toolDir, channelConfig):
    cmdStr = ''
    partner_id = channelConfig['game_info']['partner_id']
    buildtools = channelConfig['game_info']['buildtools']
    game_id = channelConfig['game_info']['game_id']
    checkValueResources(decompileDir)
    workPath = os.path.dirname(decompileDir)
    tempPath = os.path.join(workPath, "temp")
    if os.path.exists(tempPath):
        file_utils.del_file_folder(tempPath)
    if not os.path.exists(tempPath):
        os.makedirs(tempPath)
    resPath = os.path.join(decompileDir, "res")
    targetResPath = os.path.join(tempPath, "res")
    file_utils.copy_dir(resPath, targetResPath)
    genPath = os.path.join(tempPath, "gen")
    if not os.path.exists(genPath):
        os.makedirs(genPath)

    aaptPath = os.path.join(toolDir, "aapt")
    aapt2Path = os.path.join(toolDir, "aapt2")

    androidPath = os.path.join(toolDir, "android.jar")
    manifestPath = os.path.join(decompileDir, "AndroidManifest.xml")
    if buildtools=="aapt2":
        #分成complie和link两步
        # aapt2 compile --dir src/main/res -o resources.zip -v
        cmd ='"%s" compile --dir "%s"  -o "%s" -v' % (aapt2Path, targetResPath, tempPath+os.sep+"resources.zip")
        cmdStr = '%s%s\n'%(cmdStr, cmd)
        ret, err = execFormatCmd(cmd)
        if not ret:
            return False, cmdStr, u"aapt2生成资源二进制文件失败|%s" % err

        #aapt2生成R文件
        #aapt2 link -o output.apk --manifest src/main/AndroidManifest.xml -I D:/Android/sdk/platforms/android-27/android.jar resources.zip --java ./ -v
        cmd ='"%s" link -o "%s" --manifest "%s"  -I  "%s"  "%s" --java  "%s" -v' % (aapt2Path, tempPath+os.sep+"resources.apk", manifestPath, androidPath, tempPath+os.sep+"resources.zip",genPath)
        cmdStr = '%s%s\n'%(cmdStr, cmd)
        ret, err = execFormatCmd(cmd)
        if not ret:
            return False, cmdStr, u"aapt2生成文件失败|%s" % err

    else:
        cmd = '"%s" p -f -m -J "%s" -S "%s" -I "%s" -M "%s"' % (aaptPath,genPath, targetResPath, androidPath, manifestPath)
        cmdStr = '%s%s\n'%(cmdStr, cmd)
        ret, err = execFormatCmd(cmd)
        if not ret:
            return False, cmdStr, u"生成R.java文件失败|%s" % err
    # 编译R文件
    rPath = newPackageName.replace('.', os.sep)
    rFile = os.path.join(genPath, rPath, "R.java")
    cmd = '%s -source 1.8 -target 1.8 -encoding UTF-8 "%s"' % (file_utils.getJavacCMD(), rFile)
    cmdStr = '%s%s\n'%(cmdStr, cmd)
    ret, err = execFormatCmd(cmd)
    if not ret:
        return False, cmdStr, u"编译R文件失败|%s" % err
    # 删除R.java
    os.remove(rFile)
    # 腾讯需处理WXEntryActivity.java文件
    if partner_id == '3':
        sourceWXFile = os.path.join(decompileDir, 'assets', 'WXEntryActivity.java')
        targetWXFile = os.path.join(genPath, rPath, 'wxapi', 'WXEntryActivity.java')
        if os.path.isfile(sourceWXFile):
            file_utils.copy_file(sourceWXFile, targetWXFile)
            os.remove(sourceWXFile)
            #TODO
            # file_utils.replaceStringAtFile(targetWXFile, "${YHNSDK_PACKAGE_NAME}", newPackageName)
            file_utils.replaceStringAtFile(targetWXFile, 'com.tencent.tmgp.qyzzj', newPackageName.encode('utf8'))
            # os.system("sed -i 's/${YHNSDK_PACKAGE_NAME}/%s/g' %s" % (newPackageName, targetWXFile))
            libsDir = os.path.join(os.path.dirname(decompileDir), 'sdk', 'libs')
            # libsDir = os.path.join(pkg_utils.PLUGIN_UNZIP_PATH, 'libs')
            libname = []
            for filename in os.listdir(libsDir):
                if partner_id == '3':  # 腾讯
                    if 'SDK_Android_' in filename and '.jar' in filename:
                        libname.append(filename)
            cmd = '%s -source 1.8 -target 1.8 -encoding utf-8 -classpath ' % (os.path.join(file_utils.getJavacCMD()))
            splitdot = ':'
            for libitem in libname:
                cmd = '%s%s%s' % (cmd, os.path.join(libsDir, libitem), splitdot)
            cmd = '%s%s "%s"' % (cmd, os.path.join(toolDir, 'android.jar'), targetWXFile)
            ret, err = execFormatCmd(cmd)
            cmdStr = '%s%s\n'%(cmdStr, cmd)
            if not ret:
                return False, cmdStr, u"渠道partner_id:%s编译WXEntryActivity.java失败|%s" % (partner_id, err)
            os.remove(targetWXFile)

    # targetRjar = os.path.join(workPath, "sdk", "libs")
    # file_utils.mkdir(targetRjar)
    targetRjar = os.path.join(workPath, "sdk", "libs", "newR.jar")
    cmd = "jar cf %s -C %s ." % (targetRjar, genPath)
    cmdStr = '%s%s'%(cmdStr, cmd)
    ret, err = execFormatCmd(cmd)
    if not ret:
        return False, cmdStr, u"生成newR.jar失败|%s" % err
    return True, cmdStr, u"生成R文件成功"


# 检查res/values/是否有重复资源
def checkValueResources(decompileDir):
    valXmls = ['strings.xml', 'styles.xml', 'colors.xml', 'dimens.xml', 'ids.xml', 'attrs.xml', 'integers.xml',
               'arrays.xml', 'bools.xml', 'drawables.xml', 'public.xml']
    resDir = os.path.join(decompileDir, 'res', 'values')
    existsStrs = {}
    stringsXml = os.path.join(resDir, 'strings.xml')
    if os.path.exists(stringsXml):
        stringTree = ET.parse(stringsXml)
        root = stringTree.getroot()
        for node in list(root):
            name = node.attrib.get('name')
            existsStrs[name] = node.text

    existsColors = {}
    colorsXml = os.path.join(resDir, 'colors.xml')
    if os.path.exists(colorsXml):
        colorTree = ET.parse(colorsXml)
        root = colorTree.getroot()
        for node in list(root):
            name = node.attrib.get('name')
            val = node.text.lower()
            existsColors[name] = val

    valueFiles = {}
    for filename in os.listdir(resDir):
        if filename in valXmls or filename.split('.')[1] != 'xml':
            continue
        srcFile = os.path.join(resDir, filename)
        try:
            tree = ET.parse(srcFile)
            root = tree.getroot()
        except Exception as err:
            continue
        if root.tag != 'resources':
            continue
        dictRes = None
        for node in list(root):
            if node.tag == 'string':
                dictRes = existsStrs
            elif node.tag == 'color':
                dictRes = existsColors
            else:
                continue
            name = node.attrib.get('name')
            if name is None:
                continue
            val = node.text
            resVal = dictRes.get(name)
            if resVal is not None:
                root.remove(node)
        tree.write(srcFile)


# 获得母包AndroidManifest.xml中主activity的名称
def getMainActivityName(sourceManifest):
    key = '{' + androidNS + '}name'
    value = '{' + androidNS + '}value'
    ET.register_namespace('android', androidNS)
    try:
        sourceTree = ET.parse(sourceManifest)
        sourceRoot = sourceTree.getroot()
    except Exception as err:
        return ''
    appNode = sourceRoot.find('application')
    activitylist = appNode.findall("activity")
    if activitylist is None:
        return ''
    isSplash = False
    activityName = ''
    for activity in activitylist:
        intentlist = activity.findall("intent-filter")
        if intentlist is None:
            break
        for intentNode in intentlist:
            isFindAction = False
            isFindCategory = False
            actionlist = intentNode.findall('action')
            if actionlist is None:
                break
            for actionNode in actionlist:
                if actionNode.attrib[key] == "android.intent.action.MAIN":
                    isFindAction = True
                    break
            categorylist = intentNode.findall('category')
            if categorylist is None:
                break
            for categoryNode in categorylist:
                if categoryNode.attrib[key] == "android.intent.category.LAUNCHER":
                    isFindCategory = True
                    break
            if isFindAction and isFindCategory:
                isSplash = True
                break
        if isSplash:
            activityName = activity.attrib[key]
            return activityName
    return ''



def handleSmali(channelConfig, decompileDir):


    cFlag = channelConfig['game_info']['channel_flag']

    # 重新为小米SDK指定新的R文件位置
    if cFlag == 'mi':
        smaliPath = decompileDir + "/smali/com/jiyou/mipluginlib/openapi/MiPluginLogic.smali"
        newRpath = channelConfig['game_info']['game_bundle_id']
        result = eval(repr(newRpath).replace('.', '/'))
        newRpath = "L" + result + "/R"
        find_str = "Lcom/jiyou/mipluginlib/R"
        file_utils.replaceStringAtFile(smaliPath, find_str, newRpath)


