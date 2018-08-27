# _*_ encoding:utf-8 _*_
# 爬取猫眼排行榜
import requests
import re


def get_one_page(url):
    agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    header = {
        "User-Agent": agent
    }
    response = requests.get(url, headers= header)
    if response.status_code ==200:
        return response.text
    return None

def parse_one_page(html):

    pattern = re.compile('<dd.*?board-index.*?>?(\d+)</i>.*?<img.*?board-img.*?src="(.*?)">' ,re.S)

    items = re.findall(pattern, html)
    print(items)

url = "http://maoyan.com/board/4"

html = get_one_page(url)

parse_one_page(html)

