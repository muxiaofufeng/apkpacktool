#coding=utf-8

import os, json
from xml.etree import ElementTree as ET


import file_utils,md5util



def handleChannelConf(channelConfig, workDecompileDir):
    cFlag = channelConfig['game_info']['channel_flag']
    if cFlag == 'huawei':
        huaweiConfPath = os.path.join(workDecompileDir, 'assets', 'huawei_config.json')
        if os.path.isfile(huaweiConfPath):
            with open(huaweiConfPath) as cConfig:
                channelConfigs = json.load(cConfig)
            channelConfigs['JY_GAMEID'] = channelConfig['game_info']['game_id']
            channelConfigs['JY_GAME_PKG'] = channelConfig['game_info']['game_pkg']
            channelConfigs['JY_PARTNERID'] = channelConfig['game_info']['partner_id']
            channelConfigs['JY_SDK_VER'] = channelConfig['game_info']['sdk_version']
            channelConfigs['HUAWEI_APPID'] = channelConfig['game_info']['huawei_app_id']
            channelConfigs['HUAWEI_CPID'] = channelConfig['game_info']['huawei_cp_id']
            with open(huaweiConfPath, 'w+') as sConfig:
                json.dump(channelConfigs, sConfig)
    elif cFlag == 'oppo':
        oppoConfPath = os.path.join(workDecompileDir, 'assets', 'oppo_config.json')
        if os.path.isfile(oppoConfPath):
            with open(oppoConfPath) as cConfig:
                channelConfigs = json.load(cConfig)
            channelConfigs['JY_GAMEID'] = channelConfig['game_info']['game_id']
            channelConfigs['JY_GAME_PKG'] = channelConfig['game_info']['game_pkg']
            channelConfigs['JY_PARTNERID'] = channelConfig['game_info']['partner_id']
            channelConfigs['JY_SDK_VER'] = channelConfig['game_info']['sdk_version']
            channelConfigs['OPPO_APPID'] = channelConfig['game_info']['oppo_app_id']
            channelConfigs['OPPO_APPKEY'] = channelConfig['game_info']['oppo_app_key']
            channelConfigs['OPPO_APPSECRET'] = channelConfig['game_info']['oppo_app_secret']
            with open(oppoConfPath, 'w+') as sConfig:
                json.dump(channelConfigs, sConfig)
    elif cFlag == 'vivo':
        vivoConfPath = os.path.join(workDecompileDir, 'assets', 'vivo_config.json')
        if os.path.isfile(vivoConfPath):
            with open(vivoConfPath) as cConfig:
                channelConfigs = json.load(cConfig)
            channelConfigs['JY_GAMEID'] = channelConfig['game_info']['game_id']
            channelConfigs['JY_GAME_PKG'] = channelConfig['game_info']['game_pkg']
            channelConfigs['JY_PARTNERID'] = channelConfig['game_info']['partner_id']
            channelConfigs['JY_SDK_VER'] = channelConfig['game_info']['sdk_version']
            channelConfigs['VIVO_APPID'] = channelConfig['game_info']['vivo_app_id']
            channelConfigs['VIVO_APPKEY'] = channelConfig['game_info']['vivo_app_key']
            channelConfigs['VIVO_CPID'] = channelConfig['game_info']['vivo_cp_id']
            with open(vivoConfPath, 'w+') as sConfig:
                json.dump(channelConfigs, sConfig)


    elif cFlag == 'mi':
        miConfPath = os.path.join(workDecompileDir, 'assets', 'mi_config.json')
        if os.path.isfile(miConfPath):
            with open(miConfPath) as cConfig:
                channelConfigs = json.load(cConfig)
            channelConfigs['JY_GAMEID'] = channelConfig['game_info']['game_id']
            channelConfigs['JY_GAME_PKG'] = channelConfig['game_info']['game_pkg']
            channelConfigs['JY_PARTNERID'] = channelConfig['game_info']['partner_id']
            channelConfigs['JY_SDK_VER'] = channelConfig['game_info']['sdk_version']

            channelConfigs['MI_APPID'] = channelConfig['game_info']['mi_appid']
            channelConfigs['MI_APPKEY'] = channelConfig['game_info']['mi_appkey']
            with open(miConfPath, 'w+') as sConfig:
                json.dump(channelConfigs, sConfig)




    elif cFlag == 'uc':
        ucConfPath = os.path.join(workDecompileDir, 'assets', 'uc_config.json')
        if os.path.isfile(ucConfPath):
            with open(ucConfPath) as cConfig:
                channelConfigs = json.load(cConfig)
            channelConfigs['JY_GAMEID'] = channelConfig['game_info']['game_id']
            channelConfigs['JY_GAME_PKG'] = channelConfig['game_info']['game_pkg']
            channelConfigs['JY_PARTNERID'] = channelConfig['game_info']['partner_id']
            channelConfigs['JY_SDK_VER'] = channelConfig['game_info']['sdk_version']

            channelConfigs['UC_GAMEID'] = channelConfig['game_info']['uc_gameid']
            with open(ucConfPath, 'w+') as sConfig:
                json.dump(channelConfigs, sConfig)


    elif cFlag == 'baidu':
        baiduConfPath = os.path.join(workDecompileDir, 'assets', 'baidu_config.json')
        if os.path.isfile(baiduConfPath):
            with open(baiduConfPath) as cConfig:
                channelConfigs = json.load(cConfig)
            channelConfigs['JY_GAMEID'] = channelConfig['game_info']['game_id']
            channelConfigs['JY_GAME_PKG'] = channelConfig['game_info']['game_pkg']
            channelConfigs['JY_PARTNERID'] = channelConfig['game_info']['partner_id']
            channelConfigs['JY_SDK_VER'] = channelConfig['game_info']['sdk_version']

            channelConfigs['BAIDU_APPID'] = channelConfig['game_info']['baidu_appid']
            channelConfigs['BAIDU_APPKEY'] = channelConfig['game_info']['baidu_appkey']
            with open(baiduConfPath, 'w+') as sConfig:
                json.dump(channelConfigs, sConfig)





    elif cFlag == 'meizu':
        meizuConfPath = os.path.join(workDecompileDir, 'assets', 'meizu_config.json')
        if os.path.isfile(meizuConfPath):
            with open(meizuConfPath) as cConfig:
                channelConfigs = json.load(cConfig)
            channelConfigs['JY_GAMEID'] = channelConfig['game_info']['game_id']
            channelConfigs['JY_GAME_PKG'] = channelConfig['game_info']['game_pkg']
            channelConfigs['JY_PARTNERID'] = channelConfig['game_info']['partner_id']
            channelConfigs['JY_SDK_VER'] = channelConfig['game_info']['sdk_version']

            channelConfigs['MEIZU_APPID'] = channelConfig['game_info']['meizu_appid']
            channelConfigs['MEIZU_APPKEY'] = channelConfig['game_info']['meizu_appkey']
            with open(meizuConfPath, 'w+') as sConfig:
                json.dump(channelConfigs, sConfig)


    elif cFlag == 'qihoo':
        qihooConfPath = os.path.join(workDecompileDir, 'assets', 'qihoo_config.json')
        if os.path.isfile(qihooConfPath):
            with open(qihooConfPath) as cConfig:
                channelConfigs = json.load(cConfig)
            channelConfigs['JY_GAMEID'] = channelConfig['game_info']['game_id']
            channelConfigs['JY_GAME_PKG'] = channelConfig['game_info']['game_pkg']
            channelConfigs['JY_PARTNERID'] = channelConfig['game_info']['partner_id']
            channelConfigs['JY_SDK_VER'] = channelConfig['game_info']['sdk_version']


            with open(qihooConfPath, 'w+') as sConfig:
                json.dump(channelConfigs, sConfig)


#${PACKAGENAME}已经在上层替换
def handleChannelManifest(androidmanifestfile, channelConfig):
    cFlag = channelConfig['game_info']['channel_flag']
    if cFlag == 'huawei':
        if channelConfig['game_info'].has_key('huawei_app_id'):
            file_utils.replaceStringAtFile(androidmanifestfile, "${HUAWEI_APPID}", (channelConfig['game_info']['huawei_app_id']).encode('utf8'))
        if channelConfig['game_info'].has_key('huawei_cp_id'):
            file_utils.replaceStringAtFile(androidmanifestfile, "${HUAWEI_CPID}", (channelConfig['game_info']['huawei_cp_id']).encode('utf8'))
    elif cFlag == 'oppo':
        if channelConfig['game_info'].has_key('oppo_app_key'):
            file_utils.replaceStringAtFile(androidmanifestfile, "${OPPO_APPKEY}", (channelConfig['game_info']['oppo_app_key']).encode('utf8'))
    elif cFlag == 'vivo':
        pass


    elif cFlag=='qihoo':  #360
        if channelConfig['game_info'].has_key('qihoo_app_id'):
            file_utils.replaceStringAtFile(androidmanifestfile, "${QIHOO_APPID}", (channelConfig['game_info']['qihoo_app_id']).encode('utf8'))

        if channelConfig['game_info'].has_key('qihoo_app_key'):
            file_utils.replaceStringAtFile(androidmanifestfile, "${QIHOO_APPKEY}", (channelConfig['game_info']['qihoo_app_key']).encode('utf8'))

        if channelConfig['game_info'].has_key('qihoo_app_key') and channelConfig['game_info'].has_key('qihoo_app_Secret'):
            qihoo_app_key = channelConfig['game_info']['qihoo_app_key']
            qihoo_appSecret = channelConfig['game_info']['qihoo_app_Secret']
            qihoo_priatekey = md5util.md5(qihoo_appSecret + "#" + qihoo_app_key)
            file_utils.replaceStringAtFile(androidmanifestfile, "${QIHOO_PRIATEKEY}", qihoo_priatekey.encode('utf8'))




#manifest文件，主activity渠道特殊处理
def handleMainActivityInManifest(mainActivity, channelConfig):
    cFlag = channelConfig['game_info']['channel_flag']
    if cFlag == 'huawei':
        pass
    elif cFlag == 'oppo':
        androidNS = 'http://schemas.android.com/apk/res/android'
        screenOrientation = '{' + androidNS + '}screenOrientation'
        if channelConfig['game_info']['orientation'] == '1':
            mainActivity.attrib[screenOrientation] = 'portrait'
        else:
            mainActivity.attrib[screenOrientation] = 'landscape'
    elif cFlag == 'vivo':
        pass
