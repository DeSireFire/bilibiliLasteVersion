# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class booksItem(scrapy.Item):
    bookName = scrapy.Field()#书籍名称
    bookAuthor = scrapy.Field()#书籍作者
    bookPublishing = scrapy.Field()#书籍出版社
    bookDate = scrapy.Field()#书籍出版时间
    bookPrice = scrapy.Field()#书籍价格
    bookInfo = scrapy.Field()#书籍信息
    bookEditor = scrapy.Field()#书籍编辑推荐
    bookDetail = scrapy.Field()#书籍详细
    bookCover = scrapy.Field()#书籍封面
    bookGrade =scrapy.Field()#书籍评分
    bookISBN = scrapy.Field()#书籍ISBN码
    bookType = scrapy.Field()#书籍分类
    bookTypeS = scrapy.Field()#书籍次级分类
    bookForm = scrapy.Field()#书籍数据来源


