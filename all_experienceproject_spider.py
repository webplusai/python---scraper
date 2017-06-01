import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging, dateparser, time

class ForumsSpider(CrawlSpider):
    name = "all_experienceproject_spider"
    allowed_domains = ["www.experienceproject.com"]
    start_urls = [
        "http://www.experienceproject.com/groups",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//div[@class="group-name"]/a', 
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            #Rule(LinkExtractor(
            #        restrict_xpaths='//td[@class="msgSm" and @align="right"]/b/strong/following-sibling::a[1]'
            #    ), follow=True),
        )

    def getDate(self,date_str):
        # date_str="Fri Feb 12, 2010 1:54 pm"
        date = dateparser.parse(date_str)
        epoch = int(date.strftime('%s'))
        create_date = time.strftime("%Y-%m-%d'T'%H:%M%S%z",  time.gmtime(epoch))
        return create_date

    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//div[@class="expression  titled-story-expression  story-expression  is-link "]/div[@class="expression-content"]')
        items = []
        topic = response.xpath('//h1[@class="group-title"]/a/text()').extract_first().strip()
        url = response.url
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//span[@class="member-username-with-status"]/a[@class="member-username  profile-hoverlay-enabled"]/text()').extract_first()
            if item['author']:
                item['author_link'] = post.xpath('.//span[@class="member-username-with-status"]/a[@class="member-username  profile-hoverlay-enabled"]/@href').extract_first()

                create_date = self.getDate(self.cleanText(" ".join(post.xpath('.//span[@class="date"]/span[@class="model-create-date"]/text()').extract_first().strip())))
                item['create_date'] = create_date
          
                item1 = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="content"]/h2/a/text()').extract()).replace("\t","").replace("\n","").replace("\r","").replace(u'\xa0',''))
                item2 = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="content"]/span/text()').extract()).replace("\t","").replace("\n","").replace("\r","").replace(u'\xa0',''))

                item['post'] = item1 + ' ' + item2
                item['tag']=''
                item['topic'] = topic.strip()
                item['url']=url
                logging.info(item.__str__)
                items.append(item)
        return items
