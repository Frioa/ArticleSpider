# 利用requests 模拟登陆
import requests
import http.cookiejar as cookielib
import re
import time
import hmac
from hashlib import sha1
import json
import base64
from PIL import Image

# 利用session保持链接
session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")  # cookie存储文件，
# 提取保存的cookie
try:
    session.cookies.load(ignore_discard=True)  # 从文件中读取cookie
except:
    print("cookie 未能加载")

# 伪造header
agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
header = {
    "HOST": "www.zhihu.com",
    "Referer": "https://www.zhihu.com",
    "User-Agent": agent,
    'Connection': 'keep-alive'
}


def is_login():
    # 通过个人中心页面返回状态码来判断是否登录
    # 通过allow_redirects 设置为不获取重定向后的页面
    response = session.get("https://www.zhihu.com/inbox", headers=header, allow_redirects=False)
    if response.status_code != 200:
        zhihu_login("17631094456", "199641yueqi")
    else:
        print("你已经登陆了")


def get_xsrf_dc0():
    # 获取xsrf code和d_c0
    # 在请求登录页面的时候页面会将xsrf code 和d_c0加入到cookie中返回给客户端
    response = session.get("https://www.zhihu.com/signup", headers=header)
    return response.cookies["_xsrf"], response.cookies["d_c0"]


def get_signature(time_str):
    # 生成signature,利用hmac加密
    # 根据分析之后的js，可发现里面有一段是进行hmac加密的
    # 分析执行加密的js 代码，可得出加密的字段，利用python 进行hmac几码
    h = hmac.new(key='d1b964811afb40118a12068ff74a12f4'.encode('utf-8'), digestmod=sha1)
    grant_type = 'password'
    client_id = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
    source = 'com.zhihu.web'
    now = time_str
    h.update((grant_type + client_id + source + now).encode('utf-8'))
    return h.hexdigest()


def get_identifying_code(headers):
    # 判断页面是否需要填写验证码
    # 如果需要填写则弹出验证码，进行手动填写

    # 请求验证码的url 后的参数lang=en，意思是取得英文验证码
    # 原因是知乎的验证码分为中文和英文两种
    # 中文验证码是通过选择倒置的汉字验证的，破解起来相对来说比较困难，
    # 英文的验证码则是输入验证码内容即可，破解起来相对简单，因此使用英文验证码
    response = session.get('https://www.zhihu.com/api/v3/oauth/captcha?lang=en', headers=headers)
    # 盘但是否存在验证码
    r = re.findall('"show_captcha":(\w+)', response.text)
    if r[0] == 'false':
        return ''
    else:
        response = session.put('https://www.zhihu.com/api/v3/oauth/captcha?lang=en', headers=header)
        show_captcha = json.loads(response.text)['img_base64']
        with open('captcha.jpg', 'wb') as f:
            f.write(base64.b64decode(show_captcha))
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
        captcha = input('输入验证码:')
        session.post('https://www.zhihu.com/api/v3/oauth/captcha?lang=en', headers=header,
                     data={"input_text": captcha})
        return captcha


def zhihu_login(account, password):
    '''知乎登陆'''
    post_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
    XXsrftoken, XUDID = get_xsrf_dc0()
    header.update({
        "authorization": "oauth c3cef7c66a1843f8b3a9e6a1e3160e20",  # 固定值
        "X-Xsrftoken": XXsrftoken,
    })
    time_str = str(int((time.time() * 1000)))
    # 直接写在引号内的值为固定值，
    # 只要知乎不改版反爬虫措施，这些值都不湖边
    post_data = {
        "client_id": "c3cef7c66a1843f8b3a9e6a1e3160e20",
        "grant_type": "password",
        "timestamp": time_str,
        "source": "com.zhihu.web",
        "password": password,
        "username": account,
        "captcha": "",
        "lang": "en",
        "ref_source": "homepage",
        "utm_source": "",
        "signature": get_signature(time_str),
        'captcha': get_identifying_code(header)
    }

    response = session.post(post_url, data=post_data, headers=header, cookies=session.cookies)
    if response.status_code == 201:
        # 保存cookie，下次直接读取保存的cookie，不用再次登录
        session.cookies.save()
    else:
        print("登录失败")


head = {
    'cookie': 'd_c0="AKAignGUpA2PTtmB2rpdIGxSlOCFClmojFw=|1527163066";'
              ' _zap=28412dda-f7ac-4290-863f-b8c3d662bfbf; q_c1=2bc6ee9ec0294d69830ad3265df08a11|1533820485000|1527163066000;'
              ' _xsrf=s6gJ8Eo6mjxpC8uspcY2haBjeVToaxYq; __utma=155987696.219657935.1535289258.1535289258.1535289258.1;'
              ' __utmz=155987696.1535289258.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none);'
              ' tgw_l7_route=69f52e0ac392bb43ffb22fc18a173ee6;'
              ' capsion_ticket="2|1:0|10:1535335920|14:capsion_ticket|44:YTlhMDE1YzQ2M2E2NDQ3YWE3OTg3MzNiYWE3NDkyZTc=|a176e89154063591e828bcdcf75c68d65fcf58c544855bfe9d65a2317551c463";'
              ' z_c0="2|1:0|10:1535335921|4:z_c0|92:Mi4xOXdpOUNnQUFBQUFBb0NLQ2NaU2tEU1lBQUFCZ0FsVk44YXR3WEFBVml3Vzk5ZzFyT1dqN1NLU3pKOUk1YXFRYktR|9d4d1a437ae204eeabc62805a85123a64963cf572ff381ccabb53c66195b7560"',
    'HOST': 'www.zhihu.com',
    'User-Agent': agent,
}
r = requests.get('https://www.zhihu.com/api/v4/questions/20702054/answers?include=data[*].is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata[*].mark_infos[*].url%3Bdata[*].author.follower_count%2Cbadge[%3F(type%3Dbest_answerer)].topics&limit=15&offset=20', headers=head)
print(r.text)

# is_login()
