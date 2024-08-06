import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

# Initialize Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize the first driver for collecting URLs with headless mode
driver1 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Initialize the second driver for fetching property details with headless mode
driver2 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# urls_handle = open("all_urls.txt", "a+")
# done_handle = open("done.txt", "a+")
# Open a file to store the property URLs
with open("property_urls.txt", "a+") as urls_handle, open("property_details.txt", "a+") as details_handle:
    for page_num in range(1, 1184):
        print("Page Number:", page_num)
        url = f"https://www.property24.co.ke/houses-for-sale?Page={page_num}"
        driver1.get(url)
        
        # Locate the search results block
        block = driver1.find_element(By.CLASS_NAME, "sc_searchResultsP24Style")
        properties = block.find_elements(By.CLASS_NAME, "js_listingTile")
        
        for property in properties:
            property_url = property.find_element(By.TAG_NAME, "a").get_attribute("href")
            urls_handle.write(property_url + "\n")
            
            # Fetch property details using the second driver
            driver2.get(property_url)
            try:
                p24_listingCard = driver2.find_element(By.CLASS_NAME, "p24_listingCard")
                price = p24_listingCard.find_element(By.CLASS_NAME, "p24_price").text
                name = p24_listingCard.find_element(By.CLASS_NAME, "sc_listingAddress").find_element(By.TAG_NAME, "h1").text
                address = p24_listingCard.find_element(By.TAG_NAME, "p").text
                propert_details_dict = {"price": price, "name": name, "address": address}

                # Features
                features = p24_listingCard.find_element(By.CLASS_NAME, "sc_listingDetailsIcons").find_elements(By.CLASS_NAME, "p24_featureDetails")
                features_keys = [i.get_attribute("title") for i in features]
                features_values = [i.text for i in features]
                features_dict = dict(zip(features_keys, features_values))

                # Sizes
                sizes = p24_listingCard.find_element(By.CLASS_NAME, "sc_listingDetailsIcons").find_elements(By.CLASS_NAME, "p24_size")
                size_keys = [i.get_attribute("title") for i in sizes]
                size_values = [i.text for i in sizes]
                sizes_dict = dict(zip(size_keys, size_values))

                feature_details = driver2.find_element(By.ID, "p24_listingDetails")

                def find_feature_amount(web_element):
                    try:
                        return web_element.find_element(By.CLASS_NAME, "p24_featureAmount").text
                    except NoSuchElementException:
                        return "Yes"

                feature_details = [(i.find_element(By.CLASS_NAME,"p24_feature").text.replace(":", "") + "2", find_feature_amount(i)) \
                                    for i in feature_details.find_elements(By.CLASS_NAME, "p24_listingFeatures")]
                features2_dict = {key.rstrip(':'): value for key, value in feature_details}

                property_overview = driver2.find_element(By.ID, "Property-Overview")
                items = [(i.find_element(By.CLASS_NAME, "p24_propertyOverviewKey").text ,i.find_element(By.CLASS_NAME, "p24_info").text) \
                        for i in property_overview.find_elements(By.CLASS_NAME, "p24_propertyOverviewRow")]
                property_overview_dict = {key.rstrip(':'): value for key, value in items}

                excerpt = driver2.find_element(By.CLASS_NAME, "sc_listingDetailsText").text.replace("Read more...", "").replace("\n\n", "")
                excerpt_dict = {"excerpt": excerpt}

                data = {**propert_details_dict, **features_dict, **sizes_dict, **features2_dict, **property_overview_dict, **excerpt_dict}

                details_handle.write(str(data) + "\n")

            except NoSuchElementException as e:
                print(f"Error fetching details for URL: {property_url} - {str(e)}")
            
            # time.sleep(1)
        
        # Restart the driver every 50 pages to prevent slowdown
        if page_num % 50 == 0:
            driver1.quit()
            driver1 = webdriver.Chrome()

# Close the drivers
driver1.quit()
driver2.quit()