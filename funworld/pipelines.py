# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class FunworldPipeline(object):
	def close_spider(self, spider):
		# open csv file
		fp = open("data.csv", 'wb')

		# write header in csv file
		fp.write('"Category 1","Category 2","Category 3","Category 4","Name","UPC"\n')

		for full_category in sorted(spider.data):
			category = full_category.split("//")
			
			for product in spider.data[full_category]:
				for upc in product['upc']:
					line = '"%s","%s","%s","%s","%s","%s"\n' % \
									(category[0].replace("None", ""), category[1].replace("None", ""), category[2].replace("None", ""),\
									category[3].replace("None", ""), self.filter(product['name']), upc)
									
					print upc
					# encode data string with utf8
					fp.write(line)
				
		fp.close()
		
	def filter(self, raw_str):

		res = raw_str.replace(",", " ")
		res = res.replace("\"", " ")
		
		return res