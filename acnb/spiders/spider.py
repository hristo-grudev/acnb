import re

import scrapy

from scrapy.loader import ItemLoader

from ..items import AcnbItem
from itemloaders.processors import TakeFirst


class AcnbSpider(scrapy.Spider):
	name = 'acnb'
	start_urls = ['https://www.acnb.com/resource-center/education/blog']

	def parse(self, response):
		post_links = response.xpath('//div[@class="blog-info"]')
		for post in post_links:
			url = post.xpath('.//div[@class="blog-link"]/a/@href').get()
			date = post.xpath('.//div[@class="blog-author-date"]//text()[normalize-space()]').getall()
			date = [p.strip() for p in date]
			date = ' '.join(date).strip()
			date = re.findall(r'[A-Za-z]+\s\d{1,2},\s\d{4}', date) or ['']
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date[0]})

		next_page = response.xpath('//li[@class="pager-next"]/a/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//div[@class="intro-section"]//h1/text()').get()
		description = response.xpath('//div[@class="blog-content"]//text()[normalize-space() and not(ancestor::div[@class="blog-info"] | ancestor::dvi[@class="blog-author-section"])]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()
		# date = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "blog-info", " " ))]//p/text()').get()
		# date = re.findall(r'[A-Za-z]+\s\d{1,2},\s\d{4}', date) or ['']

		item = ItemLoader(item=AcnbItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
