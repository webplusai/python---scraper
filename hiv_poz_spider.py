import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging, dateparser, time

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "hiv_poz_spider"
    allowed_domains = ["forums.poz.com"]
    start_urls = [
        "http://forums.poz.com/index.php?board=16.0",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//table[@class="table_grid"]//span[contains(@id, "msg")]/a',
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="pagelinks"]/strong/following-sibling::a[1]'
                ), follow=True),
        )

    def getDate(self,date_str):
        # date_str="Fri Feb 12, 2010 1:54 pm"
        date = dateparser.parse(date_str)
        epoch = int(date.strftime('%s'))
        create_date = time.strftime("%Y-%m-%d'T'%H:%M%S%z",  time.gmtime(epoch))
        return create_date

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//div[contains(@class, "windowbg")]')
        items = []
        condition = 'hiv'
        topic = response.xpath('//div[@class="navigate_section"]//li[@class="last"]//span/text()').extract_first()
        url = response.url

        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//div[@class="poster"]/h4/a/text()').extract_first()
            if item['author']:
                item['author_link'] = post.xpath('.//div[@class="poster"]/h4/a/@href').extract_first()
                item['condition'] = condition

                create_date = self.getDate(self.cleanText(" ".join(post.xpath('.//div[@class="keyinfo"]/div[@class="smalltext"]/text()').extract()[1].replace(u'\xbb','').strip())))
                item['create_date'] = create_date

                item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="post"]/div[@class="inner"]/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
                item['tag']=''
                item['topic'] = topic
                item['url']=url
                logging.info(item.__str__)
                items.append(item)
        return items