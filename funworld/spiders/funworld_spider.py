import scrapy

class DmozSpider(scrapy.Spider):
	name = "funworld"
	allowed_domains = ["www.fun-world.net"]
	start_urls = [
		"http://www.fun-world.net/"
	]
	
	def __init__(self):
		self.data = dict()
		self.log = open("log.txt", "wb")

	# parse index page and crawl major categories
	def parse(self, response):
		category_blocks = response.xpath("//ul[@class='b-home__main-navi']//li")
		
		for block in category_blocks:
			url = self.validate(block.xpath(".//a/@href"))
			category_name = self.validate(block.xpath(".//span[2]/text()"))
			
			# make a request for scraping sub categories.
			request = scrapy.Request(url, callback=self.sub_category, dont_filter=True)
			request.meta["major_category"] = category_name
			yield request
			
	# parse product list page and crawl sub categories
	def sub_category(self, response):
		major_category = response.meta["major_category"]
		
		menu = response.xpath("//ul[@class='b-accordion']//li")
		for category in menu:
			second_category = self.validate(category.xpath(".//a/text()"))
			

			third_blocks = category.xpath(".//ul//li")
			
			# if there are the 3rd level categories
			if len(third_blocks) > 0:
				for block in third_blocks:
				
					fourth_blocks = category.xpath(".//ul//li")
					third_category = self.validate(block.xpath(".//a/text()"))
					if len(fourth_blocks) > 0:
						for fourth in fourth_blocks:
							fourth_category = self.validate(fourth.xpath(".//a/text()"))
							url = self.validate(fourth.xpath(".//a/@href"))
							full_category = '//'.join([major_category, second_category, third_category, fourth_category])
							self.data[full_category] = []
							
							# make a request for scraping product list.
							request = scrapy.Request(url, callback=self.parse_products)
							request.meta["full_category"] = full_category
							request.meta["page"] = 1
							yield request
					else:	
						url = self.validate(block.xpath(".//a/@href"))
						full_category = '//'.join([major_category, second_category, third_category, "None"])
						self.data[full_category] = []
						
						# make a request for scraping product list.
						request = scrapy.Request(url, callback=self.parse_products, dont_filter=True)
						request.meta["full_category"] = full_category
						request.meta["page"] = 1
						yield request
						
					
			else:	#otherwise
				url = self.validate(category.xpath(".//a/@href"))
				full_category = '//'.join([major_category, second_category, "None", "None"])
				self.data[full_category] = []
				
				# make a request for scraping product list.
				request = scrapy.Request(url, callback=self.parse_products, dont_filter=True)
				request.meta["full_category"] = full_category
				request.meta["page"] = 1
				yield request
	
	# get the list of products
	def parse_products(self, response):
		full_category = response.meta["full_category"]
		current_page = response.meta["page"]
		
		next_button = response.xpath("//li[contains(@class, 'b-toolbar__pager__item_type_next')]")
		
		# crawl the list of products
		products = response.xpath("//li[@class='b-product__list__item']")
		for item in products:
			url = self.validate(item.xpath(".//dd[@class='b-product__preview']//a/@href"))
			# make a request for scraping product list.
			request = scrapy.Request(url, callback=self.parse_product)
			request.meta["full_category"] = full_category
			yield request
		
		# if this page is last page, exit scraping product list page
		if len(next_button) == 0:
			return
			
		# make a request for the next page
		
		# generate url with a page number.
		url = response.url
		if "?p" in url:
			url = response.url.split("?p")[0]

		url = "%s?p=%d" % (url, current_page + 1) 
		request = scrapy.Request(url, callback=self.parse_products, dont_filter=True)
		request.meta["full_category"] = full_category
		request.meta["page"] = current_page + 1
		yield request
		
	# crawl the product data.
	def parse_product(self, response):
		full_category = response.meta["full_category"]
		product = dict()
		
		product['name'] = self.validate(response.xpath("//h2[@class='b-single-product__title']/text()"))
		temp = self.validate(response.xpath("//ul[@class='b-single-product__description__list']//li[1]//strong/text()")).split("#")
		if len(temp) > 1:
			product['item_id'] = temp[1].strip()
			
		product['upc'] = []
		description = response.xpath("//ul[@class='b-single-product__description__list']//li[contains(@class, 'std')]//ul")
		for block in description:
			title = self.validate(block.xpath(".//strong/text()"))
	
			if 'upc' in title.lower():
				upcs = block.xpath(".//li")

				if len(upcs) > 0:
					for upc in upcs[1:]:
						temp = self.validate(upc.xpath("./text()")).split(" ")
						tp_str = ""
						for token in temp:
							try:
								last = int(token)
								tp_str += token
							except:
								tp_str += " " + token
						
						product['upc'].append(tp_str.strip())
			elif title != "":
				self.log.write("upc error: title(%s)" % title)
						
		self.data[full_category].append(product)
			
	# validate the value of html node
	#		return string value, if data is validated
	#		return "", otherwise
	def validate(self, node):
		if len(node) > 0:
			temp = node[0].extract().strip().encode("utf8")
			return temp
		else:
			return ""