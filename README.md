# Amazon-Products-Reviews-Scrapper
To scrape the reviews of a Amazon product given it All reviews URL.
*This is inspired from the post https://www.scrapehero.com/how-to-scrape-amazon-product-reviews-using-python/*
## Working
1. Open the product webpage on Amazon.in. Click on "See all reviews" at the near end of the product page. When the new page is loaded make note of the URL. We notice that there are 10 reviews per page and there are page-buttons, at the near bottom of the page, which take us to the next set of 10 reviews. Make note of the maximum number of such page-buttons present.

2. Run the code amazon_reviews_my.py
3. Enter the URL of the noted above.
4. Enter the number of sections of reviews you need (2 sections means it will return you 20 reviews (If the product has those many :p. ))
5. data_my.json will store all your data.

This code gives the rewuired amount of reviews of a product once you give the right inputs. Though it is not optimised, any contributions from you is all is appreciated.
