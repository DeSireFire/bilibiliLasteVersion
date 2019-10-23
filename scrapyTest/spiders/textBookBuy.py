# -*- coding: utf-8 -*-
import scrapy,json

# 全国大中专教材网络采选系统 爬虫测试
class TextbookbuySpider(scrapy.Spider):
    name = 'textBookBuy'
    allowed_domains = ['www.textbooking.com.cn']
    start_urls = ['http://www.textbooking.com.cn/foreground/subjectSearch']

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {'Referer': 'http://www.textbooking.com.cn/foreground/subjectSearch'}
    }

    def start_requests(self):
        url = 'http://www.textbooking.com.cn/foreground/subjectSearch/page'
        # for page in range(1,18580):
        for page in range(1,500):
            yield scrapy.FormRequest(
                url=url,
                formdata={"page": str(page)},
                callback=self.parse_pages,
                meta={"page": str(page)}
            )

    def parse_pages(self, response):
        page_date = json.loads(response.text)
        print('正在获取第 %s 页'%response.meta["page"])
        for book in page_date['rows']:
            print(book)
