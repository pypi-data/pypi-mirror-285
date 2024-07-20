from tourist.core import TouristScraper


AWS_APIGW_HOST = ""
X_SECRET = "supersecret"

tourist_scraper = TouristScraper(AWS_APIGW_HOST, X_SECRET)


def get_text_from_page(): ...
