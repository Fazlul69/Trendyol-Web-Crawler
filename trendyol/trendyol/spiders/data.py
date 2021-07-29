import json
import scrapy
import time
import chompjs
from scrapy import Request
from scrapy.crawler import CrawlerProcess

class TrendyolSpider(scrapy.Spider):
    name = 'data'
    allowed_domains = ['trendyol.com']
    start_urls = ['https://www.trendyol.com/']

    # def parse(self, response):
    #     for link in response.css('li.tab-link a::attr(href)'):
    #         for page in range(1, 100):
    #             time.sleep(0.5)
    #             yield response.follow(link.get() + '?pi=' + str(page), callback=self.parse_sub_categories)

    # for cat
    # def parse(self, response):
    #     cat_url = 'https://www.trendyol.com/goz-makyaji-x-c1347'
    #     for page in range(1, 3):
    #         time.sleep(0.5)
    #         yield response.follow(cat_url + '?pi=' + str(page), callback=self.parse_sub_categories)

    #for brand
    def parse(self, response):
        cat_url = 'https://www.trendyol.com/sr?mid=223584'
        for page in range(1, 3):
            time.sleep(0.5)
            yield response.follow(cat_url + '&pi=' + str(page), callback=self.parse_sub_categories)

    def parse_sub_categories(self, response):
        for link2 in response.css('div.p-card-wrppr a::attr(href)'):
            yield response.follow(link2.get(), callback=self.final_parse)

    def final_parse(self, response):
        all_info = response.xpath("//script[contains(@type,'application/javascript')]/text()").extract_first()
        product_json = chompjs.parse_js_object(all_info)
        ides = product_json['product']['productGroupId']
        image = product_json['product']['images']
        de = product_json['product']['deliveryInformation']['deliveryDate']
        product_name = product_json['product']['nameWithProductCode']
        category = product_json['product']['category']['name']
        price = product_json['product']['price']['sellingPrice']['value']
        discount_price = product_json['product']['price']['discountedPrice']['value']
        brand = product_json['product']['brand']['name']
        description = product_json['product']['contentDescriptions']
        for i in description:
            product_information = i['description']

        varient_url = "https://public.trendyol.com/discovery-web-productgw-service/api/productGroup/" + str(ides)

        yield Request(url=varient_url, callback=self.parse_v, meta={
            'category': category,
            'product_name': product_name,
            'price': price,
            'discount_price': discount_price,
            'brand': brand,
            'image': image,
            # 'size': size,
            'de': de,
            'product_information': product_information,
        })

    def parse_v(self, response):
        json_tex5 = json.loads(response.body)
        try:
            dataa = json_tex5.get('result').get("slicingAttributes")[0].get("attributes")
            yield {
                'category': response.meta['category'],
                'product_name': response.meta['product_name'],
                'price': response.meta['price'],
                'discount_price': response.meta['discount_price'],
                'brand': response.meta['brand'],
                'image': response.meta['image'],
                'deliveryDate': response.meta['de'],
                'product_information': response.meta['product_information'],
                'renk': dataa
            }
        except:
            yield {
                'category': response.meta['category'],
                'product_name': response.meta['product_name'],
                'price': response.meta['price'],
                'discount_price': response.meta['discount_price'],
                'brand': response.meta['brand'],
                'image': response.meta['image'],
                'deliveryDate': response.meta['de'],
                'product_information': response.meta['product_information'],
                'renk': 'none'
            }


c = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0',
    'FEED_FORMAT': 'json',
    'FEED_URI': 'output.json',
})
c.crawl(TrendyolSpider)
c.start()
# scrapy crawl data -o output.json -s FEED_EXPORT_ENCODING=UTF-8
