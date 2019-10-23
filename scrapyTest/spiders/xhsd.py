# -*- coding: utf-8 -*-
import scrapy,json


class XhsdSpider(scrapy.Spider):
    name = 'xhsd'
    allowed_domains = ['search.xhsd.com']
    start_urls = ['http://search.xhsd.com/']

    def start_requests(self):
        url = 'https://search.xhsd.com/search?frontCategoryId=33&pageNo='
        # for page in range(1,18580):
        for page in range(1,2):
            yield scrapy.Request(
                url=url+str(page),
                callback=self.parse_pages,
                meta={"page": str(page)}
            )

    def parse_pages(self, response):
        print('正在获取第 %s 页'%response.meta["page"])
        for book in range(1,73):

            book_info = {
                'book_url':'',
                'book_Img':'',
                'book_Name':'',
                'book_author':'',
                'book_price':'',
            }
            book_info['book_url'] = response.xpath("//li[contains(@class, 'product')][%s]/div[contains(@class, 'product-image')]/a/@href"%book).extract()[0]
            book_info['book_Img'] = response.xpath("//li[contains(@class, 'product')][%s]/div[contains(@class, 'product-image')]/a/img/@src"%book).extract()[0]
            book_info['book_Name'] = response.xpath("//li[contains(@class, 'product')][%s]/p/a/text()"%book).extract()[0]
            book_info['book_author'] = response.xpath("//li[contains(@class, 'product')][%s]/p[contains(@class, 'product-author')]/span/text()"%book).extract()
            book_info['book_price'] = response.xpath("//li[contains(@class, 'product')][%s]/p[contains(@class, 'product-price')]/span/text()"%book).extract()


            yield scrapy.Request(
                url='https:'+book_info['book_url'],
                callback=self.parse,
                meta={"page": response.meta['page'],'book_info':book_info},
                dont_filter=True
            )

    def parse(self, response):
        book_info = response.meta
        page_date = json.loads(response.xpath("//div[@class='spu-tab-item-detail']/@data-detail").extract()[0])
        book_info['content-detail'] = page_date
        print(response.url)



if __name__ == '__main__':
    for book in range(1, 73):
        print(book)