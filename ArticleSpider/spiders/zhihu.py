# -*- coding: utf-8 -*-
import re
import scrapy
import json
import datetime
from scrapy.conf import settings

from urllib import parse
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuAnswerItem, ZhihuQuestionItem


# Scrapy中使用cookie免于验证登录和模拟登录


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    #allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/search?type=content&q=python']

    # question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"
    header = {
        'cookie' : 'd_c0="AKAignGUpA2PTtmB2rpdIGxSlOCFClmojFw=|1527163066";'
              ' _zap=28412dda-f7ac-4290-863f-b8c3d662bfbf; q_c1=2bc6ee9ec0294d69830ad3265df08a11|1533820485000|1527163066000;'
              ' _xsrf=s6gJ8Eo6mjxpC8uspcY2haBjeVToaxYq; __utma=155987696.219657935.1535289258.1535289258.1535289258.1;'
              ' __utmz=155987696.1535289258.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none);'
              ' tgw_l7_route=69f52e0ac392bb43ffb22fc18a173ee6;'
              ' capsion_ticket="2|1:0|10:1535335920|14:capsion_ticket|44:YTlhMDE1YzQ2M2E2NDQ3YWE3OTg3MzNiYWE3NDkyZTc=|a176e89154063591e828bcdcf75c68d65fcf58c544855bfe9d65a2317551c463";'
              ' z_c0="2|1:0|10:1535335921|4:z_c0|92:Mi4xOXdpOUNnQUFBQUFBb0NLQ2NaU2tEU1lBQUFCZ0FsVk44YXR3WEFBVml3Vzk5ZzFyT1dqN1NLU3pKOUk1YXFRYktR|9d4d1a437ae204eeabc62805a85123a64963cf572ff381ccabb53c66195b7560"',
        'Connection': 'keep - alive',  # 保持链接状态
        'HOST': 'www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',

    }

    def start_requests(self): # 携带cookie
        yield scrapy.Request(url=self.start_urls[0], dont_filter=True,headers=self.header)
        # return [scrapy.Request("https://www.zhihu.com")]

    def parse(self, response):
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls) # 过滤函数
        # print(all_urls)

        for url in all_urls:
            print(url)
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url) # 匹配出 zhihu.com/question/
            if match_obj:
                # 如果提取到question相关的页面下载后交由提取函数进行提取
                request_url = match_obj.group(1)
                # request_id = match_obj.group(2)
                # print(request_url, request_id)
                yield scrapy.Request(request_url, headers=self.header, callback=self.parse_question) # 下载器执行 (传函数名称)
            else:
                # 如果不是question页面进一步跟踪
                yield scrapy.Request(url, headers=self.header, callback=self.parse)



    def parse_question(self, response):
        # 处理question页面， 从页面中提取出具体的quetion item
        if "QuestionHeader-title" in response.text: #处理新版本
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)  # 匹配出 zhihu.com/question/
            if match_obj:
                request_id = int(match_obj.group(2))
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css("title", "h1.QuestionHeader-title::text")
            item_loader.add_css("content",".QuestionHeader-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", request_id)
            item_loader.add_css("answer_num", ".List-headerText span::text")
            item_loader.add_css("comments_num", ".QuestionHeader-Comment button::text")
            item_loader.add_css("watch_user_num", ".NumberBoard-itemValue::text")
            item_loader.add_css("topics",".QuestionHeader-topics .Popover div::text")# div::text 所有子节点

            question_item = item_loader.load_item()
        else: #处理旧版本
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)  # 匹配出 zhihu.com/question/
            if match_obj:
                request_id = int(match_obj.group(2))
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            # item_loader.add_css("title", ". h2 a::text")
            item_loader.add_xpath("title","//*[@class='zh-question-title']/h2/a/text()|//*[@class='zh-question-title']/h2/span/text()" )
            item_loader.add_css("content", "#zh-question-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", request_id)
            item_loader.add_css("answer_num", ".#zh-question-answer-num::text")
            item_loader.add_css("comments_num", "#zh-question-meta-wrap a[name='addcomment']::text'")
            # item_loader.add_css("watch_user_num", "#zh-question-side-header-wrap::text")
            item_loader.add_xpath("watch_user_num", "//*[@id='zh-question-side-header-wrap']/text()|//*[@class='zh-question-followers-sidebar']/div/a/strong/text()")

            item_loader.add_css("topics", ".zm-tag-editor-labels a::text")

            question_item = item_loader.load_item()

        yield scrapy.Request(self.start_answer_url.format(request_id, 20, 0), headers=self.header, callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        # 处理question的answer
        ans_json = json.loads(response.text)

        is_end = ans_json["paging"]["is_end"]
        totals_answer = ans_json["paging"]["totals"]
        next_url = ans_json["paging"]["next"]

        # 提取answer具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["parise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()
            yield answer_item

        if not is_end:
         yield scrapy.Request(next_url, headers=self.header, callback=self.parse_answer)
