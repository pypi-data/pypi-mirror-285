"""
    配置了 SimNow 常用的四个环境
    可以使用监控平台 http://openctp.cn 查看前置服务是否正常
"""

# 也可以按需配置其他的支持 ctp官方ctpapi库的柜台
# 注意需要同时修改相应的 user/password/broker_id/authcode/appid 等信息

# SimNow 提供的四个环境
fronts = {
    "7x24": {
        "td": "tcp://180.168.146.187:10130",
        "md": "tcp://180.168.146.187:10131",
    },
    "电信1": {
        "td": "tcp://180.168.146.187:10201",
        "md": "tcp://180.168.146.187:10211",
    },
    "电信2": {
        "td": "tcp://180.168.146.187:10202",
        "md": "tcp://180.168.146.187:10212",
    },
    "移动": {
        "td": "tcp://218.202.237.33:10203",
        "md": "tcp://218.202.237.33:10213",
    },
    "hy-test": {
        "td": "tcp://101.230.79.235:33205",
        "md": "tcp://101.230.79.235:33213",
    },
    "hy-prd": {
        "td": "tcp://180.169.112.52:42205",
        "md": "tcp://180.169.112.52:42213",
    },
    "tts": {
        "td": "tcp://121.37.80.177:20002",
        "md": "tcp://121.37.80.177:20004",
    },
    "zt": {
        "td": "tcp://122.112.139.0:6102",
        "md": "tcp://119.3.103.38:6002",
    },
}

# 投资者ID / 密码

# user = "4645"
# password = "557557"
# user = "209025"
# password = "sWJedore20@#0807"

# 以下为连接 SimNow 环境的固定值
# broker_id = "9999"
# authcode = "0000000000000000"
# appid = "simnow_client_test"

# hy穿透
# user = "333306558"
# password = "hGJedore20200807"
# broker_id = "3070"
# authcode = "BM2BQIJ79NGKQA7K"
# appid = "client_jctp_1.0.0"

# 中泰测试
user = "253191003633"
password = "CzK2LG8D"
broker_id = "1080"
authcode = "1"
appid = "b8aa7173bba3470e390d787219b2112e"
