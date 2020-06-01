# apkpacktool
## 配置环境变量
CHANNEL_SDK_PATH_FILE=/Users/aaro/IdeaProjects/apkpacktool/sdk/version/channel<br>
export CHANNEL_SDK_PATH_FILE<br>
MEDIA_SDK_PATH_FILE=/Users/aaro/IdeaProjects/apkpacktool/sdk/version/media<br>
export MEDIA_SDK_PATH_FILE<br>
## 运行环境python2.7
Python 分包工具，目前已支持打官方SDK包，广点通、头条、快手



### 通用参数：


参数|	说明
---|---
partner_id|	渠道id
game_id	|游戏id
game_key| 游戏秘钥
pay_key| 支付秘钥
game_bundle_id|游戏包名
game_name|	安装显示的游戏名
channel_version|SDK版本
icon_name	|游戏包icon的名字
resource_path	|游戏替换资源的地址
icon_file	|icon文件存放位置
source_apk	|apk包的母包地址
game_resources| 替换资源路径
target_apk	|输出包的地址
buildtools| 默认传aapt特殊apk传aapt2
version_code|	版本号
target_sdk_version|	  22/26
channel_flag	|渠道标识
server_url| 


头条媒体包参数：
参数|	说明
---|---
partner_id|	渠道id
game_id	|游戏id
game_key| 游戏秘钥
pay_key| 支付秘钥
game_bundle_id|游戏包名
game_name|	安装显示的游戏名
channel_version|SDK版本
icon_name	|游戏包icon的名字
resource_path	|游戏替换资源的地址
icon_file	|icon文件存放位置
source_apk	|apk包的母包地址
game_resources| 替换资源路径
target_apk	|输出包的地址
buildtools| 默认传aapt特殊apk传aapt2
version_code|	版本号
target_sdk_version|	  22/26
channel_flag	|渠道标识
server_url| 
tt_id|头条appid
media_flag|媒体标识
media_version|媒体SDK版本


广点通媒体包参数：
参数|	说明
---|---
partner_id|	渠道id
game_id	|游戏id
game_key| 游戏秘钥
pay_key| 支付秘钥
game_bundle_id|游戏包名
game_name|	安装显示的游戏名
channel_version|SDK版本
icon_name	|游戏包icon的名字
resource_path	|游戏替换资源的地址
icon_file	|icon文件存放位置
source_apk	|apk包的母包地址
game_resources| 替换资源路径
target_apk	|输出包的地址
buildtools| 默认传aapt特殊apk传aapt2
version_code|	版本号
target_sdk_version|	  22/26
channel_flag	|渠道标识
server_url| 
gdt_id|广点通后台申请的ID
gdt_secret_key|广点通后台号申请的秘钥
media_flag|媒体标识
media_version|媒体SDK版本


快手媒体包参数：
参数|	说明
---|---
partner_id|	渠道id
game_id	|游戏id
game_key| 游戏秘钥
pay_key| 支付秘钥
game_bundle_id|游戏包名
game_name|	安装显示的游戏名
channel_version|SDK版本
icon_name	|游戏包icon的名字
resource_path	|游戏替换资源的地址
icon_file	|icon文件存放位置
source_apk	|apk包的母包地址
game_resources| 替换资源路径
target_apk	|输出包的地址
buildtools| 默认传aapt特殊apk传aapt2
version_code|	版本号
target_sdk_version|	  22/26
channel_flag	|渠道标识
server_url| 
ks_id|快手appid
ks_name|快手后台申请的应用名
media_flag|媒体标识
media_version|媒体SDK版本


广告包参数：
参数|	说明
---|---
source_apk|广告母包路径
target_apk|广告包输出路径
jy_ad|广告标识


### 应用宝（YSDK）
参数|	说明
---|---
yyb_qq_app_id| 手Qid
yyb_wx_app_id| 微信id

### VIVO
参数|	说明
---|---
vivo_app_id| 应用唯一标识（appid）
vivo_cp_id| 
vivo_app_key|



### OPPO
参数|	说明
---|---
oppo_app_id| 应用唯一标识（appid）
oppo_app_key| 应用秘钥
oppo_app_secret|


### 华为	
参数|	说明
---|---
huawei_app_id| 应用唯一标识（appid）
huawei_cp_id| 

### 小米	
参数|	说明
---|---
mi_appid| 应用唯一标识（appid）
mi_appkey| 应用秘钥

### UC九游	
参数|	说明
---|---
uc_gameid| 应用唯一标识（appid）

### 360	
参数|	说明
---|---
qihoo_app_id| 应用唯一标识（appid）
qihoo_app_key|应用秘钥
qihoo_app_Secret|


### 百度	
参数|	说明
---|---
baidu_appid| 应用唯一标识（appid）
baidu_appkey|应用秘钥

### 魅族	
参数|	说明
---|---
meizu_appid| 应用唯一标识（appid）
meizu_appkey|应用秘钥
