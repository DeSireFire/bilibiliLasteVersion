# -*- coding: utf-8 -*-
import scrapy,json


class JdbooksSpider(scrapy.Spider):
    name = 'jdBooks'
    allowed_domains = ['book.jd.com','list.jd.com','item.jd.com']
    start_urls = ['http://book.jd.com/']

    def start_requests(self):
        # url = 'https://list.jd.com/list.html?cat=1713,3258,3304'

        # 获取JD所有类别书籍
        url = 'https://book.jd.com/booksort.html'
        yield scrapy.Request(
            url=url,
            callback=self.parse_type_url,
        )

    def parse_type_url(self, response):
        bookType = response.xpath("//dt/a/text()").extract()
        for mType in bookType:
            for subT,url in zip(response.xpath("//dd[%s]/em/a/text()"%(bookType.index(mType)+1)).extract(),response.xpath("//dd[%s]/em/a/@href"%(bookType.index(mType)+1)).extract()):
                yield scrapy.Request(
                    url='https:'+url,
                    callback=self.book_list,
                    meta={'item':{
                        'bookType':mType,
                        'bookTypeS':subT,
                    }}
                )

    def book_list(self, response):

        baseInfo = response.meta['item']
        bookNames = response.xpath("//li[contains(@class, 'gl-item')]//div[@class='p-name']/a/em/text()").extract()
        bookAuthors = response.xpath("//li[contains(@class, 'gl-item')]//div[@class='p-bookdetails']/span[@class='p-bi-name']/span/a/text()").extract()
        bookPublishings = response.xpath("//li[contains(@class, 'gl-item')]//div[@class='p-bookdetails']/span[@class='p-bi-store']/a/text()").extract()
        bookDates = response.xpath("//li[contains(@class, 'gl-item')]//div[@class='p-bookdetails']/span[@class='p-bi-date']/text()").extract()
        bookJDids = response.xpath("//li[contains(@class, 'gl-item')]/div/@data-sku").extract()
        bookPrices = self.bookPriceGet(bookJDids)
        bookGrades = self.bookRateGet(bookJDids)
        bookCover = response.xpath("//li[contains(@class, 'gl-item')]//div[@class='p-img']/a/img/@src").extract()
        bookURL = response.xpath("//li[contains(@class, 'gl-item')]//div[@class='p-name']/a/@href").extract()


        for n,a,pu,d,pr,c,url,jid,g in zip(bookNames,bookAuthors,bookPublishings,bookDates,bookPrices,bookCover,bookURL,bookJDids,bookGrades):
            temp = self.bookDetailGet(jid)
            print(temp)
            baseInfo.update({
                'bookName':n.strip(),
                'bookAuthor':a.strip(),
                'bookPublishing':pu,
                'bookDate':d.strip(),
                'bookPrice':pr,
                'bookGrade':g,
                'bookDetail':temp,
                'bookEditor':self.hasKeyDict('编辑推荐',temp),
                'bookCover':len(self.imgToBase64('https:'+c)),#todo 去掉len
            })
            yield scrapy.Request(
                url='https:' + url,
                callback=self.book_item,
                meta={'item':baseInfo})

    def book_item(self, response):

        if 'login' in response.url:
            print('发现登陆重定向！')
            print(response.url)
            self.crawler.engine.close_spider(self, '发现登陆重定向！URL:%s' % (response.url))


        baseInfo = response.meta['item']
        baseInfo['bookInfo'] = {i.split(':')[0]:i.split(':')[1] for i in response.xpath("string(//ul[@id='parameter2'])").get(default=None).replace(' ','').replace('：\n',':').replace('：',':').split('\n') if i != ''}
        baseInfo['bookPublishing'] = self.hasKeyDict('出版社',baseInfo['bookInfo'])
        baseInfo['bookISBN'] = self.hasKeyDict('ISBN',baseInfo['bookInfo'])
        baseInfo['bookEditor'] = self.hasKeyDict('bookEditor',baseInfo['bookInfo'])

        from scrapyTest.items import booksItem
        item = booksItem()
        item['bookName'] = baseInfo['bookName']
        item['bookAuthor'] = baseInfo['bookAuthor']
        item['bookPublishing'] = baseInfo['bookPublishing']
        item['bookDate'] = baseInfo['bookDate']
        item['bookPrice'] = baseInfo['bookPrice']
        item['bookInfo'] = baseInfo['bookInfo']
        item['bookEditor'] = baseInfo['bookEditor']
        item['bookDetail'] = baseInfo['bookDetail']
        item['bookCover'] = baseInfo['bookCover']
        item['bookGrade'] = baseInfo['bookGrade']
        item['bookISBN'] = baseInfo['bookISBN']
        item['bookType'] = baseInfo['bookType']
        item['bookTypeS'] = baseInfo['bookTypeS']
        item['bookForm'] = '京东'
        # yield item




    ## 工具函数
    @classmethod
    def hasKeyDict(self,keyName,d):
        '''
        看看字典是否存在key
        :param keyName:
        :param d:
        :return:
        '''
        if keyName in d.keys():
            return d[keyName]
        else:
            return ''


    @classmethod
    def imgToBase64(self,url):
        '''
        封面图获取并转base64
        :param url: 字符串，图片url
        :return: base64码
        '''
        import requests, base64
        myheader = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Host': '%s'%url.split('/')[2],
            'Connection': 'close',
            'Cache-Control': 'max-age=0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
        }
        req = requests.get(url="%s" % url, headers=myheader)
        base64_data = base64.b64encode(req.content)
        return 'data:image/jpg;base64,' + bytes.decode(base64_data)

    @classmethod
    def bookPriceGet(self,data_skus):
        '''
        根据书籍的data-sku获取价格
        :param data_skus: 京东书籍ID
        :return:价格列表
        '''
        import requests,json
        myheader = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
        }

        req = requests.get(url="https://p.3.cn/prices/mgets?callback=jQuery&skuIds=%s" % '%2C'.join(data_skus), headers=myheader)
        try:
            return [x['op'] for x in json.loads(req.text[7:-3])]
        except:
            print(req.text)

    @classmethod
    def bookRateGet(self,data_skus):
        '''
        根据书籍的data-sku获取评分
        :param data_skus: 京东书籍ID
        :return:价格列表
        '''
        import requests,json
        myheader = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
        }

        req = requests.get(url="https://sclub.jd.com/comment/productCommentSummaries.action?referenceIds=12135337%s" % '%2C'.join(data_skus), headers=myheader)
        try:
            temp = json.loads(req.text)
            return [x['GoodRateShow'] for x in temp['CommentsCount']]
        except:
            print(req.text)

    @classmethod
    def bookDetailGet(self,data_skus):
        '''
        根据书籍的data-sku获取详细介绍
        :param data_skus: 京东书籍ID
        :return:价格列表
        '''
        import requests,json,re
        myheader = {
            'Referer': 'https://item.jd.com/%s.html'%data_skus,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
        }
        req = requests.get(url="https://dx.3.cn/desc/%s?cdn=2&callback=showdesc" %(data_skus), headers=myheader)
        try:
            temp = json.loads(req.text[9:-1])['content'].replace(' ','').split('\n')
            res = {}
            tk = ''  # 临时键名
            for i in temp:
                t = re.sub(r'</?\w+[^>]*>', '', i)
                if t and '产品特色' != t and '查看全部↓' != t and '…' not in t and '插图' not in t:
                    if len(t) <= 4:
                        tk = t
                        res[tk] = []
                        continue
                    else:
                        res[tk].append(t)
            return res
        except Exception as e:
            raise "e:%s url:%s c:%s"%(e,req.url,req.text)


if __name__ == '__main__':
    # temp = ['12135337','12430168','11452840']
    # a = JdbooksSpider.bookPriceGet(temp)
    # print(a)
    a = JdbooksSpider.bookDetailGet('12135337')
    # a = JdbooksSpider.bookRateGet('12135337')
    print(a)