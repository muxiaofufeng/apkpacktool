#coding=utf-8
import os, sys, json, file_utils, apk_utils


def unrar(apk, rarsource, direct):
    if os.path.exists(apk):
        cmd = 'unzip -C -j %s %s -d %s' % (apk, rarsource, direct)
        ret, err = apk_utils.execFormatCmd(cmd)
    if ret:
        return True, cmd, ""
    return False, cmd, err


def get_new_json(filepath,key,value):
    key_ = key.split(".")
    key_length = len(key_)
    with open(filepath, 'rb') as f:
        json_data = json.load(f)
        i = 0
        a = json_data
        while i < key_length :
            if i+1 == key_length :
                a[key_[i]] = value
                i = i + 1
            else :
                a = a[key_[i]]
                i = i + 1
    f.close()
    return json_data


def rewrite_json_file(filepath,json_data):
    with open(filepath, 'w') as f:
        json.dump(json_data,f)
    f.close()



def delete_config_file(source,deletePath):
    cmd=" zip  -d " + source + " " + deletePath
    ret, err = apk_utils.execFormatCmd(cmd)
    if ret:
        return True, cmd, ""
    return False, cmd, err


def add_config_file(temp_apk, json_path):

    if os.path.exists(temp_apk):
        apkparent=os.path.abspath(os.path.dirname(temp_apk))
        #cd 到临时目录下
        cmd_cd = "cd " + apkparent
        #新增文件
        cmd_rar = "zip -r " + temp_apk + "  assets"

        cmd = cmd_cd + " && pwd &&  "+ cmd_rar

        ret, err = apk_utils.execFormatCmd(cmd)

        if ret:
          return True, cmd, ""
        return False, cmd, err



def sign_ad_apk(targetApk, signInfo):
    cmdStr = ''
    keystorefile = signInfo['keystore']
    password = signInfo['password']
    alias = signInfo['aliaskey']
    aliaspwd = signInfo['aliaspwd']
    if keystorefile is None:
        return False, cmdStr, u"keystore文件不存在"
    if not os.path.exists(keystorefile):
        return False, cmdStr, u"keystore文件不存在"

    rmcmd = ' zip  -d %s META-INF/* ' % (targetApk)
    ret, err = apk_utils.execFormatCmd(rmcmd)

    signcmd = u'jarsigner -keystore "%s" -storepass "%s" -keypass "%s" "%s" "%s" -sigalg SHA1withRSA -digestalg SHA1' % (
        keystorefile, password, aliaspwd, targetApk, alias)
    ret, err = apk_utils.execFormatCmd(signcmd)
    if ret:
        return True, cmdStr, ""
    return False, cmdStr, u"签名失败|%s" % err


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print '{"status":0}'
    else:
        package_info = sys.argv[1]

    rootDir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    configDir = os.path.join(rootDir, 'config')

    #package_info='{"source_apk":"/Users/aaro-ou/Desktop/temp/source_apk/lhhc-JIYOU_ONLINE-v2.0.0-s2.0.0-JY0S0N00001-202005261823.apk","target_apk":"/Users/aaro-ou/Desktop/temp/target_apk","jy_ad":"2a832c77bd2c74c7bc9124c5dc7ee80b"}'
    try:
        package_dic = eval(package_info)
    except:
        print '{"status":0}'

    if package_dic.has_key('source_apk') and len(package_dic['source_apk']) > 0:
         source_apk_path=package_dic['source_apk']
    else:
        print '{"status":0}'

    if package_dic.has_key('target_apk') and len(package_dic['target_apk']) > 0:
        target_apk_path=package_dic['target_apk']
    else:
        print '{"status":0}'
    if package_dic.has_key('jy_ad') and len(package_dic['jy_ad']) > 0:
        jy_ad=package_dic['jy_ad']
    else:
        print '{"status":0}'

    if os.path.exists(target_apk_path+'/'+jy_ad):
        file_utils.del_file_folder(target_apk_path+'/'+jy_ad)

    #创建目标临时文件
    temp_apk=target_apk_path+'/'+jy_ad+'/'+jy_ad+'.apk'
    file_utils.copy_file(source_apk_path,temp_apk)

    #获取配置文件
    ret, cmd, result=unrar(source_apk_path,'assets/jy_public_config.json',target_apk_path+'/'+jy_ad)
    json_path=target_apk_path+'/'+jy_ad+'/jy_public_config.json'

    #修改配置参数
    m_json_data = get_new_json(json_path,'JY_AD',jy_ad)
    rewrite_json_file(json_path,m_json_data)

    #将配置文件当道新的assets目录下并删除原有配置文件
    new_assets =target_apk_path+'/'+jy_ad+'/assets'
    file_utils.copy_file(json_path,new_assets+'/'+'jy_public_config.json')
    file_utils.del_file_folder(json_path)

    #删除临时目录apk中的配置文件
    delete_config_file(temp_apk,'assets/jy_public_config.json')

    #将修改后的配置放到apk中去
    add_config_file(temp_apk,json_path)

    #重签
    signInfo = {"keystore": os.path.join(configDir, '7yol_default.keystore'), "password": "Aa314159", "aliaskey": "7yol_default", "aliaspwd": "Aa314159"}
    ret, cmd, result = sign_ad_apk(temp_apk, signInfo)
    if ret:
        file_utils.del_file_folder(new_assets)
        print '{"status":1, "apkPath":"%s"}'%(temp_apk)
    else:
        print '{"status":0}'