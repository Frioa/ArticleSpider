# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.http import Request
from urllib import parse

from ArticleSpider.items import JobBolePythonAricleItem
from ArticleSpider.utils.common import get_md5

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['python.jobbole.com']
    start_urls = ['http://python.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1.获取文章列表页中的url交给解析函数解析
        2.获取下一页URL交给scarpy进行下载， 下载完成后交给parse
        :param response:
        :return:
        """
        # 解析列表页中所有URL
        # URL_list = response.xpath('//*a[contains(@class,"archive-title")]').extarct()
        URL_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for node in URL_nodes:
            image_url = node.css("img::attr(src)").extract_first("")
            node_url = node.css("::attr(href)").extract_first("")
            yield scrapy.Request(url=parse.urljoin(response.url, node_url), meta={"front_image_url": image_url}, callback=self.parse_detail, dont_filter=True)
            # yield Request(url=list, callback=self.parse_detail)

        # 提取下一页交给scrapy下载
        newxt_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if newxt_url:
            yield Request(url=parse.urljoin(response.url, newxt_url), callback=self.parse, dont_filter=False)

    def parse_detail(self, response):
        article_item = JobBolePythonAricleItem()


        # 提取文章的具体字段
        front_image_meta = response.meta.get("front_image_url", "")
        title = response.css('.entry-header h1::text').extract_first("")
        create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract_first("").strip().replace(" ·","")
        prais_nums = int(response.xpath('//span[contains(@class,"href-style vote-post-up")]/h10/text()').extract_first(""))
        fav_nums = response.xpath('//span[contains(@class," bookmark-btn ")]/text()').extract_first("")
        match_re = re.match(r".*?(\d+).*",fav_nums)
        if match_re:
            fav_nums = int(match_re.group(1))
        else:
            fav_nums = 0
        comment_nums = response.xpath('//a[contains(@href,"article-comment")]/span/text()').extract_first("")
        comment_nums = comment_nums
        match_re = re.match(r".*?(\d+).*",comment_nums)
        if match_re:
            comment_nums = int(match_re.group(1))
        else:
            comment_nums = 0
        content = response.css('div.entry').extract()[0]

        tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        tags = ",".join(tag_list)

        article_item["url_object_id"] = get_md5(response.url)
        article_item["title"] = title
        try:
            create_date = datetime.datetime.struct_time(create_date, "%y/%m/%d").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()
        article_item["url"] = response.url
        article_item["create_date"] = create_date
        article_item["front_image_url"] = [front_image_meta]
        article_item["praise_nums"] = prais_nums
        article_item["comment_nums"] = comment_nums
        article_item["fav_nums"] = fav_nums
        article_item["tags"] = tags
        article_item["content"] = content

        yield article_item