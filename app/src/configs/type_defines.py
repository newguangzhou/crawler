# -*- coding: utf-8 -*-

##############################################
# 认证相关定义
##############################################
"""
用户认证类型
"""
USER_AUTH = 1
"""
正常用户认证
"""
NORMAL_AUTH = 1
"""
老用户认证
"""
OLD_AUTH = 2
"""
老用户新认证
"""
OLD_NORMAL_AUTH = 3
"""
用户认证状态正常
"""
ST_AUTH_NORMAL = 1
"""
用户认证状态被永久冻结
"""
ST_AUTH_FREEZE_FOREVER = 2
"""
用户认证状态被暂时冻结
"""
ST_AUTH_FREEZE_TEMP = 3
"""
验证码类型
"""
VERIFY_CODE_TYPES = (
    1,  #登陆验证码
    2,  #密码找回验证码
    3,  #共享宠物验证码
)

##############################################
# 全局ID分配相关定义
##############################################
USER_GID = 2

AUDIT_GID = 6

PET_GID = 7

###############################################
# 文件种类定义
###############################################
USER_LOGO_FILE = 1

PUBLIC_FILE = 50
################################################
# 设备类型
################################################
DEVICE_ANDROID = 1
DEVICE_IOS = 2





HTTP_HD_OS = "X-OS"
#android系统版本号,默认23
HTTP_HD_OS_INT="x_os_int"
HTTP_HD_APPVERSION = "X-App-Version"
# HTTP_HD_DEVICE_MODEL = "X-OS-Name"
HTTP_HD_DEVICE_MODEL = "device_model"
HTTP_HD_ANDROID_START_STRING = "Android"
PLATFORM_ANDROID = 1
PLATFORM_IOS = 2

# msg_type
MSG_TYPE_APP_PUSH = 0  #  APP推送
MSG_TYPE_WEIXIN_PUSH = 1  #  微信推送
MSG_TYPE_SMS      = 2  #  SMS推送

# 消息模板定义
MSG_TMPL_IN_HOME = 1    # 到家
MSG_TMPL_OUT_HOME = 2   # 离家
MSG_TMPL_ON_LINE  = 3   # 设备在线
MSG_TMPL_OFF_LINE = 4   # 设备离线
MSG_TMPL_IN_PROTECTED = 5 # 在保护状态
MSG_TMPL_OUT_PROTECTED = 6 # 脱离保护状态
MSG_TMPL_COMMON_BATTERY = 7 # 正常电量通知
MSG_TMPL_LOW_BATTERY = 8 # 低电量告警
MSG_TMPL_SUPER_LOW_BATTERY = 9 # 超低电量告警
MSG_TMPL_LOCATION_CHANGE = 10  # 新位置信息推送
MSG_TMPL_SHARE_PET = 11  # 增加子账号验证码
MSG_TMPL_SET_MASTER = 12 # 转移主账号
MSG_TMPL_DEL_SLAVE = 13 #  删除子账号
MSG_TMPL_ADD_SLAVE = 14 # 增加子账号
MSG_TMPL_WARN_BEFORE_DEADLINE = 20  # 到期前30天提示用户续费
MSG_TMPL_WARN_DEADLINE = 21  # 到期提醒
MSG_TMPL_WARN_STOP_SERVICE = 22 # 停机提醒
MSG_TMPL_WARN_UNREGIST   = 23 # 销户提醒


FINDSTATUS_FINDING = 1   #正在找狗
FINDSTATUS_FOUND   = 2   #找到狗了

PETSTATUS_NORMAL   = 0   #正常状态
PETSTATUS_SPORT    = 1   #遛狗
PETSTATUS_FINDING  = 2   #搜狗

#离线原因
OFFLINE_REASON_ELECTRIC = 1  #电量为零
OFFLINE_REASON_STATION  = 2  #移动网络信号差
OFFLINE_REASON_OTHER    = 3  #其他原因
GPS_ON   = 1
GPS_OFF  = 0

PET_TYPE_CAT = 2
PET_TYPE_DOG = 1
PET_TYPE_OTHER = -1

# SIM卡状态
SIM_STATUS_UNACTIVE = -1 # 未激活
SIM_STATUS_NORMAL   = 0 # 正常
SIM_STATUS_30_DAYS_TO_DEADLINE = 1 # 差30天到期
SIM_STATUS_DEADLINE = 2 # 欠费
SIM_STATUS_STOP_SERVICE = 3 # 停机
SIM_STATUS_UNREGIST = 4  # 销户

