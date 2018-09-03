from lxml import html
import json
import requests
import json,re
from dateutil import parser as dateparser
from time import sleep
import urllib3
urllib3.disable_warnings()
def ParseReviews(asin):
	amazon_url  = asin
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
	page = requests.get(amazon_url,headers = headers,verify=False)
	page_response = page.text

	parser = html.fromstring(page_response)
	XPATH_AGGREGATE = '//span[@id="acrCustomerReviewText"]'
	XPATH_REVIEW_SECTION_1 = '//div[contains(@id,"reviews-summary")]'
	XPATH_REVIEW_SECTION_2 = '//div[@data-hook="review"]'

	XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
	XPATH_PRODUCT_NAME = '//div//h1//a[@data-hook="product-link"]//text()'
	XPATH_PRODUCT_PRICE  = '//span[@id="priceblock_ourprice"]/text()'

	raw_product_price = parser.xpath(XPATH_PRODUCT_PRICE)
	product_price = ''.join(raw_product_price).replace(',','')

	raw_product_name = parser.xpath(XPATH_PRODUCT_NAME)
	product_name = ''.join(raw_product_name).strip()
	total_ratings  = parser.xpath(XPATH_AGGREGATE_RATING)
	reviews = parser.xpath(XPATH_REVIEW_SECTION_1)
	if not reviews:
		reviews = parser.xpath(XPATH_REVIEW_SECTION_2)
	ratings_dict = {}
	reviews_list = []

	if not reviews:
		raise ValueError('unable to find reviews in page')

	#grabing the rating  section in product page
	for ratings in total_ratings:
		extracted_rating = ratings.xpath('./td//a//text()')
		if extracted_rating:
			rating_key = extracted_rating[0]
			raw_raing_value = extracted_rating[1]
			rating_value = raw_raing_value
			if rating_key:
				ratings_dict.update({rating_key:rating_value})

	#Parsing individual reviews
	for review in reviews:
		XPATH_RATING  = './/i[@data-hook="review-star-rating"]//text()'
		XPATH_REVIEW_HEADER = './/a[@data-hook="review-title"]//text()'
		XPATH_REVIEW_POSTED_DATE = './/span[@data-hook="review-date"]//text()'
		XPATH_REVIEW_TEXT_1 = './/div//span[@data-hook="review-body"]//text()'
		XPATH_REVIEW_TEXT_2 = './/div//span[@data-action="columnbalancing-showfullreview"]/@data-columnbalancing-showfullreview'
		XPATH_REVIEW_COMMENTS = './/span[@data-hook="review-comment"]//text()'
		XPATH_AUTHOR  = './/span[@data-hook="review-comment"]//text()'
		XPATH_REVIEW_TEXT_3  = './/div[contains(@id,"dpReviews")]/div/text()'

		raw_review_author = review.xpath(XPATH_AUTHOR)
		raw_review_rating = review.xpath(XPATH_RATING)
		raw_review_header = review.xpath(XPATH_REVIEW_HEADER)
		raw_review_posted_date = review.xpath(XPATH_REVIEW_POSTED_DATE)
		raw_review_text1 = review.xpath(XPATH_REVIEW_TEXT_1)
		raw_review_text2 = review.xpath(XPATH_REVIEW_TEXT_2)
		raw_review_text3 = review.xpath(XPATH_REVIEW_TEXT_3)

		#cleaning data
		author = ' '.join(' '.join(raw_review_author).split())
		review_rating = ''.join(raw_review_rating).replace('out of 5 stars','')
		review_header = ' '.join(' '.join(raw_review_header).split())

		try:
			review_posted_date = dateparser.parse(''.join(raw_review_posted_date)).strftime('%d %b %Y')
		except:
			review_posted_date = None
		review_text = ' '.join(' '.join(raw_review_text1).split())

		#grabbing hidden comments if present
		if raw_review_text2:
			json_loaded_review_data = json.loads(raw_review_text2[0])
			json_loaded_review_data_text = json_loaded_review_data['rest']
			cleaned_json_loaded_review_data_text = re.sub('<.*?>','',json_loaded_review_data_text)
			full_review_text = review_text+cleaned_json_loaded_review_data_text
		else:
			full_review_text = review_text
		if not raw_review_text1:
			full_review_text = ' '.join(' '.join(raw_review_text3).split())

		raw_review_comments = review.xpath(XPATH_REVIEW_COMMENTS)
		review_comments = ''.join(raw_review_comments)
		review_comments = re.sub('[A-Za-z]','',review_comments).strip()
		review_dict = {

							'review_text':full_review_text,
							'review_posted_date':review_posted_date,
							'review_header':review_header,
							'review_rating':review_rating,

						}
		reviews_list.append(review_dict)

	data = {
				'ratings':ratings_dict,
				'reviews':reviews_list,
				'url':amazon_url,
				'price':product_price,
				'name':product_name
			}
	return data

def ReadAsin():
	#Add your own ASINs here
	extracted_data = []
	extracted_product = []
	user_url = input("Enter All Reviews URL: ")
	number_of_pages = int(input("Enter the # of pages to extract reviews from (There are 10 reviews per page): "))
	print("Downloading from URL "+user_url)
	for i in range(1,number_of_pages+1):
		extracted_dict = ParseReviews(str(user_url)+"&pageNumber="+str(i))
		if extracted_dict["name"] not in extracted_product:
			extracted_product.append(extracted_dict["name"])
			extracted_data.append(extracted_dict)
		else:
			position_of_product = extracted_product.index(extracted_dict['name'])
			extracted_data[position_of_product]['reviews'][-1:-1] = extracted_dict["reviews"]

		sleep(5)
	f = open('data_my.json','w')
	json.dump(extracted_data,f,indent=4)

if __name__ == '__main__':
	ReadAsin()
