#coding=utf-8
import os, json, sys, time

import file_utils, apk_utils, dir_utils, log_utils
global rootDir #打包工具根目录
global newBundleID #新包名
global gameId #gameid
global gamePkg #gamePkg

global currentChannelDir #当前打包的渠道插件目录
global commonConfigDir #通用配置目录
global toolsDir #工具目录
global defaultSDKInfoConfigFile #默认SDK信息配置

#工具路径
global apktoolPath #apktool路径
global androidJarPath #android.jar路径
global baksmaliJarPath #baksmali.jar路径
# global dxToolPath #dx.jar路径
# global aaptToolPath #aapt路径
#global zipalignToolPath #zipalign工具路径
# global jarSignerToolPath #jarSigner工具路径
# global jarToolPath #jar工具路径
global channelSdkPath
global mediaSdkPath

loginPluginsDic = {
    'android':'com.jiyou.jypluginlib.openapi.JYPluginLogic',
    'yyb':'com.jiyou.yybplubinlib.openapi.YYBPluginLogic',
    'huawei':'com.jiyou.huaweipluginlib.openapi.HuaweiPluginLogic',
    'oppo':'com.jiyou.oppopluginlib.openapi.OPPOPluginLogic',
    'vivo':'com.jiyou.vivopluginlib.openapi.VivoPluginLogic',
    'qihoo':'com.jiyou.qihoopluginlib.openapi.QihooPluginLogic',
    'mi':'com.jiyou.mipluginlib.openapi.MiPluginLogic',
    'uc':'com.jiyou.ucpluginlib.openapi.UcPluginLogic',
    'baidu':'com.jiyou.baidupluginlib.openapi.BaiduPluginLogic',
    'meizu':'com.jiyou.meizupluginlib.openapi.MeizuPluginLogic'
}

channelConfigKeys = ['huawei_app_id', 'huawei_cp_id', 'oppo_app_id', 'oppo_app_key', 'oppo_app_secret', 'vivo_app_id', 'vivo_app_key', 'vivo_cp_id', 'qihoo_app_id', 'qihoo_app_key', 'qihoo_app_Secret', 'mi_appid', 'mi_appkey', 'uc_gameid', 'baidu_appid', 'baidu_appkey', 'meizu_appid', 'meizu_appkey']

#模块目录
def createCommonPath():
    global commonConfigDir
    commonConfigDir = os.path.join(rootDir, 'config')
    global toolsDir

    toolsDir = os.path.join(rootDir, 'tool', file_utils.getSystemType())
    global defaultSDKInfoConfigFile
    defaultSDKInfoConfigFile = os.path.join(rootDir, 'script', 'defaultSDKInfo.conf')
    global apktoolPath
    apktoolPath = os.path.join(toolsDir, 'apktool_2.4.0.jar')
    global androidJarPath
    androidJarPath = os.path.join(toolsDir, 'android.jar')
    global baksmaliJarPath
    baksmaliJarPath = os.path.join(toolsDir, 'baksmali-2.2.7.jar')
    # global dxToolPath
    # dxToolPath = os.path.join(toolsDir, 'lib', 'dx.jar')
    global aaptToolPath
    aaptToolPath = os.path.join(toolsDir, 'aapt')
    global aapt2ToolPath
    aapt2ToolPath = os.path.join(toolsDir, 'aapt2')
    global zipalignToolPath
    zipalignToolPath = os.path.join(toolsDir, 'zipalign')
    # global jarSignerToolPath
    # jarSignerToolPath = os.path.join(toolsDir, 'jarsigner')
    # global jarToolPath
    # jarToolPath = os.path.join(toolsDir, 'jar')

    #管理渠道SDK版本的目录
    global channelSdkPath
    channelSdkPath = os.getenv("CHANNEL_SDK_PATH_FILE")
    #管理媒体SDK版本的目录
    global mediaSdkPath
    mediaSdkPath = os.getenv("MEDIA_SDK_PATH_FILE")





#转换字典
def getChannelConfig(package_info):
    try:
        package_dic = eval(package_info)
    except:
        print '{"status":0}'
    orginal_package_dic = {}
    orginal_package_dic['plugins'] = {}
    orginal_package_dic['ad_sdk'] = {}
    orginal_package_dic['game_info'] = {}

    msglist = []

    #登录插件
    if package_dic.has_key('channel_flag') and len(package_dic['channel_flag']) > 0:
        if loginPluginsDic.has_key(package_dic['channel_flag']) and len(loginPluginsDic[package_dic['channel_flag']])>0:
            orginal_package_dic['plugins']['login_plugin'] = loginPluginsDic[package_dic['channel_flag']]
        else:
            msglist.append("ERROR：channel flag is illegal")
            print '{"status":0}'
    else:
        msglist.append("ERROR：no channel flag")
        print '{"status":0}'

    # 媒体插件标识
    if package_dic.has_key('media_flag') and len(package_dic['media_flag']) > 0:
        orginal_package_dic['ad_sdk']['channel_flag'] = package_dic['channel_flag']

    #广告插件
    ad_plugin = ''
    #gdt
    if package_dic.has_key('gdt_id') and len(package_dic['gdt_id']) > 0 and package_dic.has_key('gdt_secret_key') and len(package_dic['gdt_secret_key']) > 0:
        if ad_plugin == '':
            orginal_package_dic['plugins']['ad_plugin'] = 'com.jiyou.gdtpluginlib.openapi.GdtPluginStatistic'
        else:
            orginal_package_dic['plugins']['ad_plugin'] = '|com.jiyou.gdtpluginlib.openapi.GdtPluginStatistic'
    #tt
    if package_dic.has_key('tt_id') and len(package_dic['tt_id']) > 0:
        if ad_plugin == '':
            orginal_package_dic['plugins']['ad_plugin'] = 'com.jiyou.toutiaopluginlib.openapi.ToutiaoStatistic'
        else:
            orginal_package_dic['plugins']['ad_plugin'] = '|com.jiyou.toutiaopluginlib.openapi.ToutiaoStatistic'
    #ks
    if package_dic.has_key('ks_id') and len(package_dic['ks_id']) > 0 and package_dic.has_key('ks_name') and len(package_dic['ks_name']) > 0:
        if ad_plugin == '':
            orginal_package_dic['plugins']['ad_plugin'] = 'com.jiyou.kuaishoupluginlib.openapi.KuaishouStatistic'
        else:
            orginal_package_dic['plugins']['ad_plugin'] = '|com.jiyou.kuaishoupluginlib.openapi.KuaishouStatistic'
    #广告参数
    if package_dic.has_key('gdt_id') and len(package_dic['gdt_id']) > 0:
        orginal_package_dic['ad_sdk']['gdt_id'] = package_dic['gdt_id']
    if package_dic.has_key('gdt_secret_key') and len(package_dic['gdt_secret_key']) > 0:
        orginal_package_dic['ad_sdk']['gdt_secret_key'] = package_dic['gdt_secret_key']
    if package_dic.has_key('gdt_reporting_probability') and len(package_dic['gdt_reporting_probability']) > 0:
        orginal_package_dic['ad_sdk']['gdt_reporting_probability'] = package_dic['gdt_reporting_probability']
    if package_dic.has_key('tt_id') and len(package_dic['tt_id']) > 0:
        orginal_package_dic['ad_sdk']['tt_id'] = package_dic['tt_id']
    if package_dic.has_key('ks_id') and len(package_dic['ks_id']) > 0:
        orginal_package_dic['ad_sdk']['ks_id'] = package_dic['ks_id']
    if package_dic.has_key('ks_name') and len(package_dic['ks_name']) > 0:
        orginal_package_dic['ad_sdk']['ks_name'] = package_dic['ks_name']
    #游戏包参数
    #partner_id
    if package_dic.has_key('partner_id') and len(package_dic['partner_id']) > 0:
        orginal_package_dic['game_info']['partner_id'] = package_dic['partner_id']
    else:
        msglist.append("ERROR：no partner_id")
        print '{"status":0}'
    #game_id
    if package_dic.has_key('game_id') and len(package_dic['game_id']) > 0:
        orginal_package_dic['game_info']['game_id'] = package_dic['game_id']
    else:
        msglist.append("ERROR：no game_id")
        print '{"status":0}'

    #game_key
    if package_dic.has_key('game_key') and len(package_dic['game_key']) > 0:
        orginal_package_dic['game_info']['game_key'] = package_dic['game_key']
    else:
        msglist.append("ERROR：no game_id")
        print '{"status":0}'

    #pay_key
    if package_dic.has_key('pay_key') and len(package_dic['pay_key']) > 0:
        orginal_package_dic['game_info']['pay_key'] = package_dic['pay_key']
    else:
        msglist.append("ERROR：no game_id")
        print '{"status":0}'

    #channel_flag
    orginal_package_dic['game_info']['channel_flag'] = package_dic['channel_flag']


    #game_name
    if package_dic.has_key('game_name') and len(package_dic['game_name']) > 0:
        orginal_package_dic['game_info']['game_name'] = package_dic['game_name'].encode('utf-8')
    else:
        msglist.append("WARN：no game_name")
    #game_bundle_id
    if package_dic.has_key('game_bundle_id') and len(package_dic['game_bundle_id']) > 0:
        orginal_package_dic['game_info']['game_bundle_id'] = package_dic['game_bundle_id']
    else:
        msglist.append("WARN：no game_bundle_id")

    #server_url
    if package_dic.has_key('server_url') and len(package_dic['server_url']) > 0:
        orginal_package_dic['game_info']['server_url'] = package_dic['server_url']
    else:
        msglist.append("ERROR：no server_url")
        print '{"status":0}'

    #icon_name
    if package_dic.has_key('icon_name') and len(package_dic['icon_name']) > 0:
        orginal_package_dic['game_info']['icon_name'] = package_dic['icon_name']
    else:
        msglist.append("WARN：no icon_name")
    #icon_file
    if package_dic.has_key('icon_file') and len(package_dic['icon_file']) > 0:
        orginal_package_dic['game_info']['icon_file'] = package_dic['icon_file']
    else:
        msglist.append("WARN：no icon_file")
    #source_apk
    if package_dic.has_key('source_apk') and len(package_dic['source_apk']) > 0:
        orginal_package_dic['game_info']['source_apk'] = package_dic['source_apk']
    else:
        msglist.append("ERROR：no source_apk")
        print '{"status":0}'
    #resource_path
    if package_dic.has_key('resource_path') and len(package_dic['resource_path']) > 0:
        orginal_package_dic['game_info']['resource_path'] = package_dic['resource_path']
    else:
        msglist.append("WARN：no resource_path")
    #game_resources
    if package_dic.has_key('game_resources') and len(package_dic['game_resources']) > 0:
        orginal_package_dic['game_info']['game_resources'] = package_dic['game_resources']
    else:
        msglist.append("WARN：no game_resources")
    #orientation
    #if package_dic.has_key('orientation') and len(package_dic['orientation']) > 0:
    #    orginal_package_dic['game_info']['orientation'] = package_dic['orientation']
    #else:
    #    msglist.append("ERROR：no orientation")
    #    print '{"status":0}'
    #yyb_qq_app_id
    if package_dic.has_key('yyb_qq_app_id') and len(package_dic['yyb_qq_app_id']) > 0:
        orginal_package_dic['game_info']['yyb_qq_app_id'] = package_dic['yyb_qq_app_id']
    else:
        msglist.append("WARN：no yyb_qq_app_id")
    #yyb_wx_app_id
    if package_dic.has_key('yyb_wx_app_id') and len(package_dic['yyb_wx_app_id']) > 0:
        orginal_package_dic['game_info']['yyb_wx_app_id'] = package_dic['yyb_wx_app_id']
    else:
        msglist.append("WARN：no yyb_wx_app_id")
    #target_sdk_version
    if package_dic.has_key('target_sdk_version') and len(package_dic['target_sdk_version']) > 0:
        orginal_package_dic['game_info']['target_sdk_version'] = package_dic['target_sdk_version']
    else:
        msglist.append("WARN：no target_sdk_version")
    #target_apk
    if package_dic.has_key('target_apk') and len(package_dic['target_apk']) > 0:
        orginal_package_dic['game_info']['target_apk'] = package_dic['target_apk']
    else:
        msglist.append("ERROR：no target_apk")
        print '{"status":0}'
    #bugly_id
    if package_dic.has_key('bugly_id') and len(package_dic['bugly_id']) > 0:
        orginal_package_dic['game_info']['bugly_id'] = package_dic['bugly_id']
    else:
        msglist.append("WARN：no bugly_id")
    #version_code
    if package_dic.has_key('version_code') and len(package_dic['version_code']) > 0:
        orginal_package_dic['game_info']['version_code'] = package_dic['version_code']
    else:
        msglist.append("WARN：no version_code")
    #channel_version
    if package_dic.has_key('channel_version') and len(package_dic['channel_version']) > 0:
        orginal_package_dic['game_info']['channel_version'] = package_dic['channel_version']
    else:
        msglist.append("ERROR：no channel_version")
        print '{"status":0}'

    #media_version 媒体SDK版本
    if package_dic.has_key('media_version') and len(package_dic['media_version']) > 0:
        orginal_package_dic['game_info']['media_version'] = package_dic['media_version']

    #is_dudai
    if package_dic.has_key('is_dudai') and len(package_dic['is_dudai']) > 0:
        orginal_package_dic['game_info']['is_dudai'] = package_dic['is_dudai']
    else:
        msglist.append("WARN：no is_dudai")
    #buildtools
    if package_dic.has_key('buildtools') and len(package_dic['buildtools']) > 0:
        orginal_package_dic['game_info']['buildtools'] = package_dic['buildtools']
    else:
        orginal_package_dic['game_info']['buildtools'] = ''
    #其他渠道字段(huawei/oppo/vivo...)
    for channelKey in channelConfigKeys:
        if package_dic.has_key(channelKey) and len(package_dic[channelKey]) > 0:
            orginal_package_dic['game_info'][channelKey] = package_dic[channelKey]

    targetLogFilename = orginal_package_dic['game_info']['game_bundle_id'] + '_' + time.strftime('%y-%m-%d_%H_%M_%S', time.localtime()) + '.log'
    logfilepath = os.path.join(orginal_package_dic['game_info']['target_apk'], orginal_package_dic['game_info']['game_id'], orginal_package_dic['game_info']['channel_flag'], orginal_package_dic['game_info']['game_bundle_id'], targetLogFilename)
    if not os.path.exists(os.path.dirname(logfilepath)):
        os.makedirs(os.path.dirname(logfilepath))
    logger = log_utils.getLogger(logfilepath)
    logger.info(package_info)
    for msg in msglist:
        if "ERROR" in msg:
            logger.error(msg)
        elif "WARN" in msg:
            logger.warn(msg)
        else:
            logger.info(msg)
    return orginal_package_dic, logger, logfilepath

def doPack(package_info):
    channelConfig, logger, logfilepath = getChannelConfig(package_info)
    workDirCls = dir_utils.WorkDirCls(rootDir, channelConfig['game_info']['game_id'], channelConfig['game_info']['game_bundle_id'], channelConfig['game_info']['channel_flag'], channelConfig['game_info']['channel_version'])
    logger.info(channelConfig)
    workDir = workDirCls.workRootDir
    if not os.path.exists(workDir):
        os.makedirs(workDir)
    # 反编译apk
    logger.info('clean workdir')
    file_utils.del_file_folder(workDir)
    logger.info("copy sourceapk to workdir")
    apkSource = os.path.join(workDir, 'temp.apk')
    file_utils.copy_file(channelConfig['game_info']['source_apk'], apkSource)
    logger.info("decompile apk")
    ret, cmd, result = apk_utils.decompileApk(apkSource, workDirCls.workDecompileDir, apktoolPath)  ###反编译
    logger.info(cmd)
    logger.info(str(ret) + "======" + result)
    #删除原SDK相关内容
    logger.info("delete default sdk info")
    ret, result = apk_utils.removeDefaultSDKInfo(workDirCls.workDecompileDir, defaultSDKInfoConfigFile)
    logger.info(str(ret) + "======" + result)
    # 对资源进行特殊处理(删除layout-v26/abc_screen_toolbar.xml中的android:keyboardNavigationCluster、删除drawable-v24/ic_launcher_foreground.xml中的android:fillType)
    logger.info("handle special resource")
    ret, result = apk_utils.handleSpecialResource(workDirCls.workDecompileDir)
    logger.info(str(ret) + "======" + result)
    #拷贝sdk插件到工作目录
    logger.info("copy sdk plugin to workdir")

    #拷贝渠道SDK到工作目录
    channelSdk=os.path.join(channelSdkPath, channelConfig['game_info']['channel_flag'], channelConfig['game_info']['channel_version'])
    file_utils.copy_files(channelSdk, workDirCls.workSDKDir)

    #拷贝媒体SDK到工作目录
    if channelConfig['ad_sdk'].has_key('media_flag') and channelConfig['ad_sdk']['media_flag'] > 0:
        madiaSdk=os.path.join(mediaSdkPath, channelConfig['ad_sdk']['media_flag'], channelConfig['game_info']['media_version'])
        file_utils.copy_files(madiaSdk, workDirCls.workSDKDir)

    #copy头条aar
    #logger.info("if has toutiao, copy toutiao plugin to workdir")
    #if channelConfig['ad_sdk'].has_key('tt_id') and len(channelConfig['ad_sdk']['tt_id']) > 0:
    #    toutiaoPluginDir = os.path.join(workDirCls.channelsDir, 'toutiao')
    #    file_utils.copy_files(toutiaoPluginDir, workDirCls.workSDKDir)
    #copy广点通aar
    #logger.info("if has gdt, copy gdt plugin to workdir")
    #if channelConfig['ad_sdk'].has_key('gdt_id') and channelConfig['ad_sdk'].has_key('gdt_secret_key') and len(channelConfig['ad_sdk']['gdt_id']) > 0 and len(channelConfig['ad_sdk']['gdt_secret_key']) > 0:
    #    gdtPluginDir = os.path.join(workDirCls.channelsDir, 'gdt')
    #    file_utils.copy_files(gdtPluginDir, workDirCls.workSDKDir)
    #copy快手aar
    #logger.info("if has kuaishou, copy kuaishou plugin to workdir")
    #if channelConfig['ad_sdk'].has_key('ks_id') and len(channelConfig['ad_sdk']['ks_id']) > 0 and channelConfig['ad_sdk'].has_key('ks_name') and len(channelConfig['ad_sdk']['ks_name']) > 0:
    #    kuaishouPluginDir = os.path.join(workDirCls.channelsDir, 'kuaishou')
    #    file_utils.copy_files(kuaishouPluginDir, workDirCls.workSDKDir)
    #copy独代aar
    #logger.info("if has dudai, copy dudai plugin to workdir")
    #if channelConfig['game_info'].has_key('is_dudai') and channelConfig['game_info']['is_dudai'] == 'true':
    #    dudaiPluginDir = os.path.join(workDirCls.channelsDir, 'dudai')
    #    file_utils.copy_files(dudaiPluginDir, workDirCls.workSDKDir)

    #aar模式需进行解压和资源合并
    logger.info("in workdir, unzip aar and zip, then merge")
    if apk_utils.isAarMode(workDirCls.workSDKDir):
        apk_utils.unzipAarFiles(workDirCls.workSDKDir)
        apk_utils.mergeAarFiles(workDirCls.workSDKDir)
    # copy libs(.jar除外)
    logger.info("copy sdk libs(except jar) to decompile dir")
    ret, result = apk_utils.copyLibs(os.path.join(workDirCls.workSDKDir, 'libs'), os.path.join(workDirCls.workDecompileDir, 'lib'))
    logger.info(str(ret) + "======" + result)
    # 处理lib文件夹，仅保留一个，防止不一致导致部分机型崩溃
    logger.info("handle lib dir(cpu type)")
    ret, result = apk_utils.deleteOtherLibDir(os.path.join(workDirCls.workDecompileDir, 'lib'), channelConfig['game_info']['partner_id'])
    logger.info(str(ret) + "======" + result)
    #copy 渠道res
    logger.info("copy sdk res to decompile res dir")
    ret, result = apk_utils.copyResToApk(os.path.join(workDirCls.workSDKDir, 'res'), os.path.join(workDirCls.workDecompileDir, 'res'))
    logger.info(str(ret) + "======" + result)
    #copy 渠道assets
    logger.info("copy sdk assets to decompile assets dir")
    ret, result = apk_utils.copyResToApk(os.path.join(workDirCls.workSDKDir, 'assets'), os.path.join(workDirCls.workDecompileDir, 'assets'))
    logger.info(str(ret) + "======" + result)
    #copy 其他资源
    logger.info("copy sdk other res to decompile dir")
    ret, result = apk_utils.copyOtherResToApk(workDirCls.workSDKDir, workDirCls.workDecompileDir)
    logger.info(str(ret) + "======" + result)
    #配置写入 独代配置暂时写死，没有更新
    logger.info("update conf file()")
    apk_utils.updateConfFile(channelConfig, workDirCls.workDecompileDir)
    #修改apktool.yml 版本号 targetSdkVersion
    logger.info("update apktool.yml, include targetSdkVersion, version_code etc.")
    apk_utils.updateApktoolYmlFile(channelConfig, workDirCls.workDecompileDir)
    #修改包名，合并manifest 2019-08-01新增：应用宝渠道，在主activity里面添加url scheme 格式：scheme://host/path（path为分包名）
    logger.info("merge manifest")
    ret, result, oldPackageName = apk_utils.mergeManifest(os.path.join(workDirCls.workDecompileDir, 'AndroidManifest.xml'), os.path.join(workDirCls.workSDKDir, 'sdkmanifest.xml'), channelConfig)
    logger.info(str(ret) + "======" + result)
    #替换AndroidManifest里面的占位符
    logger.info("replace placeholder in manifest")
    apk_utils.replaceSpecialString(os.path.join(workDirCls.workDecompileDir, 'AndroidManifest.xml'), channelConfig, oldPackageName)
    #修改应用名称
    logger.info("update app display name")
    ret, result = apk_utils.updateAppDisplayName(workDirCls.workDecompileDir, channelConfig['game_info']['game_name'])
    logger.info(str(ret) + "======" + result)

    apk_utils.handle_drawable_v4(workDirCls.workDecompileDir)
    #修改icon
    if channelConfig['game_info'].has_key('icon_file') and channelConfig['game_info'].has_key('icon_name'):
        logger.info("handle app icon")
        ret, result = apk_utils.handlePackageIcon(channelConfig['game_info']['icon_file'], workDirCls.workDecompileDir, channelConfig['game_info']['icon_name'])
        logger.info(str(ret) + "======" + result)

    #替换游戏素材（闪屏、loading、登录背景图）
    logger.info("replace app resource")
    if channelConfig['game_info'].has_key('game_resources') and len(channelConfig['game_info']['game_resources']) > 0 and channelConfig['game_info'].has_key('resource_path') and len(channelConfig['game_info']['resource_path']) > 0:
        oldGameResourcePath = os.path.join(workDirCls.workDecompileDir, channelConfig['game_info']['resource_path'].replace('/', os.sep))
        for newGameResourcePath in channelConfig['game_info']['game_resources']:
            file_utils.copy_file(newGameResourcePath, os.path.join(oldGameResourcePath, os.path.basename(newGameResourcePath)))
    #重新生成R文件，编译，然后生成jar包搭配渠道的libs目录下
    logger.info("generate R file")
    ret, cmd, result = apk_utils.generateNewRFile(oldPackageName, channelConfig['game_info']['game_bundle_id'], workDirCls.workDecompileDir, toolsDir, channelConfig)
    logger.info(cmd)
    logger.info(str(ret) + "======" + result)
    #jar to dex
    logger.info("convert jar to dex")
    if not os.path.exists(os.path.join(workDirCls.currentChannelDir, "classes.dex")):
        ret, cmd, result = apk_utils.jar2dex(workDirCls.workSDKDir, workDirCls.workSDKDir, channelConfig)
        logger.info(cmd)
        logger.info(str(ret) + "======" + result)
    #dex to smali
    logger.info("convert dex to smali")
    sdkDexFile = os.path.join(workDirCls.workSDKDir, "classes.dex")
    ret, cmd, result = apk_utils.dex2smali(sdkDexFile, workDirCls.workDecompileSmaliDir, baksmaliJarPath)
    logger.info(cmd)
    logger.info(str(ret) + "======" + result)
    #应用宝/小米 多Dex处理
    if channelConfig['game_info']['partner_id'] == '3' or channelConfig['game_info']['partner_id'] == '9':
        logger.info("handle multi dex")
        apk_utils.splitDex(workDirCls.workDecompileDir)

    # 处理需要特殊处理的smali文件
    apk_utils.handleSmali(channelConfig, workDirCls.workDecompileDir)

    #重新编译
    logger.info("compile new apk")
    targetApkFile = os.path.join(workDirCls.workTempDir, "output.apk")
    ret, cmd, result = apk_utils.recompileApk(workDirCls.workTempDir, workDirCls.workDecompileDir, targetApkFile, apktoolPath)
    logger.info(cmd)
    logger.info(str(ret) + "======" + result)
    #签名
    logger.info("sign apk")
    signInfo = {"keystore": os.path.join(commonConfigDir, '7yol_default.keystore'), "password": "Aa314159", "aliaskey": "7yol_default", "aliaspwd": "Aa314159"}
    ret, cmd, result = apk_utils.signApk(targetApkFile, signInfo)
    logger.info(cmd)
    logger.info(str(ret) + "======" + result)
    #对齐
    logger.info("align apk")
    targetZApk = os.path.join(workDirCls.workTempDir, "outputZ.apk")
    ret, cmd, result = apk_utils.alignApk(zipalignToolPath,targetApkFile, targetZApk)
    logger.info(cmd)
    logger.info(str(ret) + "======" + result)
    #copy到target目录
    logger.info("copy apk to target dir")
    targetApkFileName = os.path.splitext(os.path.basename(logfilepath))[0]
    targetApkFilePath = os.path.join(channelConfig['game_info']['target_apk'], channelConfig['game_info']['game_id'], channelConfig['game_info']['channel_flag'], channelConfig['game_info']['game_bundle_id'], targetApkFileName + '.apk')
    file_utils.copy_file(targetZApk, targetApkFilePath)
    if os.path.exists(targetApkFilePath):
        logger.info("pack success!!!===target apk is: %s"%targetApkFilePath)
        print '{"status":1, "apkPath":"%s", "logPath": "%s"}'%(targetApkFilePath, logfilepath)
    else:
        logger.info("pack fail")
        print '{"status":0, "logPath": "%s"}'%(logfilepath)



if __name__ == '__main__':
    #if len(sys.argv) != 2:
    #    print '{"status":0}'
    #else:
    #    package_info = sys.argv[1]
    package_info='{"partner_id":"1","game_id":"100000","game_key":"26f6ffa953668ad5884f81bd2be2d129","pay_key":"a91ca4cb988c9c53c38e7205b3291346","game_bundle_id":"com.brcq.zjcg.qihoo","game_name":"\u5192\u9669\u4f20\u5947\u002d\u9ad8\u7206\u6563\u4eba","channel_version":"1.1.0","icon_name":"icon.png","resource_path":"assets","icon_file":"/Users/aaro-ou/Desktop/temp/icon/icon.png","source_apk":"/Users/aaro/Desktop/temp/source_apk/app-release.apk","game_resources":"","target_apk":"/Users/aaro/Desktop/temp/target_apk","buildtools":"aapt2","version_code":"","target_sdk_version":"26","channel_flag":"android","server_url":"https://ndk.7yol.cn/"}'
    rootDir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    createCommonPath()
    doPack(package_info)
















