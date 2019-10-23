# -*- coding: utf-8 -*-
import scrapy,json


class JdbooksSpider(scrapy.Spider):
    name = 'jdBooks'
    allowed_domains = ['book.jd.com']
    start_urls = ['http://book.jd.com/']

    def start_requests(self):
        # url = 'https://book.jd.com/booktop/0-0-0.html?category=1713-0-0-0-10001-1'
        url = 'https://list.jd.com/list.html?cat=1713,3258,3304'
        yield scrapy.FormRequest(
            url=url,
            callback=self.parse_pages,
        )

    def parse_pages(self, response):

        for i in range(1,61):
            page_date = response.xpath("normalize-space(//li[@class='gl-item'][%s]/div/div[@class='p-name']/a/em/text())"%i).extract()
            print(page_date)