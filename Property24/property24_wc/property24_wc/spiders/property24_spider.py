import scrapy
from scrapy.exceptions import CloseSpider
from w3lib.html import remove_tags

class Property24SpiderSpider(scrapy.Spider):
    name = "property24_spider"
    allowed_domains = ["property24.com"]
    start_urls = [f"https://www.property24.com/for-sale/western-cape/9/p{page}?PropertyCategory=House%2cApartmentOrFlat%2cTownhouse" for page in range(1, 1425)]

    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'property_details_wc.json',
    }

    def parse(self, response):
        properties = response.css(".js_resultTile a::attr(href)").extract()
        for property_url in properties:
            yield response.follow(property_url, self.parse_property_details)

    def parse_property_details(self, response):
        try:
            p24_listingCard = response.css(".p24_listingCard")
            price = p24_listingCard.css(".p24_price::text").get()
            name = p24_listingCard.css("h1::text").get()
            # address = [i for i in response.css(".p24_listingCard .p24_mBM").extract()]
            propert_details_dict = {"price": price, "name": name}#, "address": address}

            features = p24_listingCard.css(".p24_icons .p24_featureDetails")
            features_keys = [feature.attrib["title"] for feature in features]
            features_values = [feature.css("span::text").get() for feature in features]
            features_dict = dict(zip(features_keys, features_values))

            # about = response.css(".p24_listingAbout .p24_size")
            # about_title = about.css("h5::text").get()
           
            listing = response.css('div.p24_listingCard')
            title1 = listing.css('h5::text').get()
            description = ' '.join(listing.css('div.js_readMoreText p::text').getall())

            features = response.css("p24_keyFeaturesContainer").extract()
            [i for i in features]

            features = {}
            for container in listing.css('div.p24_keyFeaturesContainer'):
                for feature in container.css('div.p24_listingFeatures'):
                    key = feature.css('span.p24_feature::text').get()
                    value = feature.css('span.p24_featureAmount::text').get()
                    if value is None:
                        value = True  # Some features like "Study" do not have an amount, set to True
                    features[key] = value

            property_overview_dict = {}
            for panel in response.css('div.panel'):
                for row in panel.css('div.p24_propertyOverviewRow'):
                    key = row.css('div.p24_propertyOverviewKey::text').get()
                    value = row.css('div.p24_info::text').get()
                    if key and value:
                        property_overview_dict[key]=value

            data = {
                "url": response.url,
                **propert_details_dict,
                **features_dict,
                # "about_title": about_title,
                "title": title1,
                "description": description,
                **features,
                **property_overview_dict,
                # **excerpt_dict,
            }

            yield data

        except CloseSpider as e:
            self.logger.error(f"Error fetching details for URL: {response.url} - {str(e)}")