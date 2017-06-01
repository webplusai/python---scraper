import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging, dateparser, time

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "lungcancer_lungcancercanada_spider"
    allowed_domains = ["www.lungcancercanada.ca"]
    start_urls = [
        "http://www.lungcancercanada.ca/discussion-forum.aspx?did=8",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//td[@class="frm_thread_item"]/a',
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            #Rule(LinkExtractor(
            #        restrict_xpaths='//span[@id="MainContent_ContentPlaceHolder1_discussionList_dtpDis"]/a[last()]'
            #    ), follow=True),
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
        posts = sel.xpath('//table[contains(@id,"placeholderBody")]')
        items = []
        topic = response.xpath('//span[@class="frm_title"]/text()').extract_first()
        url = response.url
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//td[@class="frm_post_infopanel"]/span[@style="font-weight:bold"]/text()').extract_first()
            item['author_link'] = ''
            item['condition'] = condition

            create_date = self.getDate(self.cleanText(" ".join(post.xpath('.//td[@class="frm_post_bar"]/div[@style="float:left"]/text()').extract_first())))
            item['create_date'] = create_date
      
            item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//td[@class="frm_post_message"]//text()').extract()).replace("\t","").replace("\n","").replace("\r",""))
            item['tag']=''
            item['topic'] = topic
            item['url']=url
            logging.info(item.__str__)
            items.append(item)
        return items
