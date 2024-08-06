import scrapy
from scrapy.exceptions import CloseSpider
from w3lib.html import remove_tags


class Property24Spider(scrapy.Spider):
    name = "property24_spider"
    allowed_domains = ["property24.co.ke"]
    start_urls = [f"https://www.property24.co.ke/houses-for-sale?Page={page}" for page in range(1, 1184)]

    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'property_details.json',
    }

    def parse(self, response):
        properties = response.css(".js_listingTile a::attr(href)").extract()
        for property_url in properties:
            yield response.follow(property_url, self.parse_property_details)

    def parse_property_details(self, response):
        try:
            p24_listingCard = response.css(".p24_listingCard")
            price = p24_listingCard.css(".p24_price::text").get()
            name = p24_listingCard.css(".sc_listingAddress h1::text").get()
            address = p24_listingCard.css("p::text").get()
            propert_details_dict = {"price": price, "name": name, "address": address}

            features = p24_listingCard.css(".sc_listingDetailsIcons .p24_featureDetails")
            features_keys = [feature.attrib["title"] for feature in features]
            features_values = [feature.css("::text").get() for feature in features]
            features_dict = dict(zip(features_keys, features_values))

            sizes = p24_listingCard.css(".sc_listingDetailsIcons .p24_size")
            size_keys = [size.attrib["title"] for size in sizes]
            size_values = [size.css("::text").get() for size in sizes]
            sizes_dict = dict(zip(size_keys, size_values))

            feature_details = response.css("#p24_listingDetails .p24_listingFeatures")
            features2_dict = {
                feature.css(".p24_feature::text").get().replace(":", ""): self.find_feature_amount(feature)
                for feature in feature_details
            }

            property_overview = response.css("#Property-Overview .p24_propertyOverviewRow")
            property_overview_dict = {
                item.css(".p24_propertyOverviewKey::text").get().rstrip(":"): item.css(".p24_info::text").get()
                for item in property_overview
            }

            # Extract the inner HTML and replace <br> tags with newlines
            excerpt_html = response.css(".sc_listingDetailsText").get()
            excerpt_cleaned = excerpt_html.replace("<br>", "\n").strip()
            
            # Remove any remaining HTML tags
            excerpt_text = remove_tags(excerpt_cleaned).replace("Read more...", "").replace("\n\n", "")

            excerpt_dict = {"excerpt": excerpt_text}

            data = {
                "url": response.url,
                **propert_details_dict,
                **features_dict,
                **sizes_dict,
                **features2_dict,
                **property_overview_dict,
                **excerpt_dict,
            }

            yield data

        except CloseSpider as e:
            self.logger.error(f"Error fetching details for URL: {response.url} - {str(e)}")

    def find_feature_amount(self, web_element):
        feature_amount = web_element.css(".p24_featureAmount::text").get()
        return feature_amount if feature_amount else "Yes"
