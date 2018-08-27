# _*_ encoding:utf-8 _*_

import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib

import re

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")  # cookie存储文件，
try:
    session.cookies.load(ignore_discard=True)  # 从文件中读取cookie
except:
    print("cookie 未能加载")


agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
header = {
    "HOST": "www.zhihu.com",
    "Referer": "https://www.zhihu.com/signup?next=%2F",
    "User-Agent": agent,
}


def get_xsrf():
    response = session.post("https://www.zhihu.com/signup?next=%2F",headers=header)
    # print(response.cookies['_xsrf'])
    return response.cookies['_xsrf']


def zhihu_login(account, password):
    # 知乎登陆
    if re.match("^1\d{10}",account):
        print("手机号码登陆")
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            "_xsrf": get_xsrf(),
            "phone_num": account,
            "password": password,
        }

get_xsrf()
