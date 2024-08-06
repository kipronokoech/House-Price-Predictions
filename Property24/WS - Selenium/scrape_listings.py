import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import numpy as np

# url = "https://www.property24.co.ke/4-bedroom-house-for-sale-in-lavington-114710803"
with open("done_urls.txt") as f:
    done = np.array([i.strip() for i in f.readlines()])

with open("property_urls.txt") as f:
    all_urls = np.array([i.strip() for i in f.readlines()])

not_done = np.setdiff1d(all_urls, done)

error_file = open("errors.txt", "a+")
data_file = open("data.txt", "a+")

driver = webdriver.Chrome()

for index, url in enumerate(not_done,1):
    try:
        driver.get(url)
        p24_listingCard = driver.find_element(By.CLASS_NAME, "p24_listingCard")
        price = p24_listingCard.find_element(By.CLASS_NAME, "p24_price").text
        name = p24_listingCard.find_element(By.CLASS_NAME, "sc_listingAddress").find_element(By.TAG_NAME, "h1").text
        address = p24_listingCard.find_element(By.TAG_NAME, "p").text
        propert_details_dict = {"price": price, "name": name, "address": address}

        # Features.
        features = p24_listingCard.find_element(By.CLASS_NAME, "sc_listingDetailsIcons").find_elements(By.CLASS_NAME, "p24_featureDetails")
        features_keys= [i.get_attribute("title") for i in features]
        features_values = [i.text for i in features]
        features_dict = dict(zip(features_keys, features_values))

        # Sizes
        sizes = p24_listingCard.find_element(By.CLASS_NAME, "sc_listingDetailsIcons").find_elements(By.CLASS_NAME, "p24_size")
        size_keys= [i.get_attribute("title") for i in sizes]
        size_values = [i.text for i in sizes]
        sizes_dict = dict(zip(size_keys, size_values))
        feature_details = driver.find_element(By.ID, "p24_listingDetails")

        def find_feature_amount(web_element):
            try:
                return web_element.find_element(By.CLASS_NAME, "p24_featureAmount").text
            except NoSuchElementException:
                return "Yes"

        feature_details = [(i.find_element(By.CLASS_NAME,"p24_feature").text.replace(":","")+"2", find_feature_amount(i)) \
                        for i in feature_details.find_elements(By.CLASS_NAME, "p24_listingFeatures")]
        features2_dict = {key.rstrip(':'): value for key, value in feature_details}

        property_overview = driver.find_element(By.ID, "Property-Overview")
        items = [(i.find_element(By.CLASS_NAME, "p24_propertyOverviewKey").text ,i.find_element(By.CLASS_NAME, "p24_info").text) \
                for i in property_overview.find_elements(By.CLASS_NAME, "p24_propertyOverviewRow")]
        property_overview_dict = {key.rstrip(':'): value for key, value in items}

        excerpt = driver.find_element(By.CLASS_NAME, "sc_listingDetailsText").text.replace("Read more...", "").replace("\n\n", "")
        excerpt_dict = {"excerpt": excerpt}

        data = propert_details_dict | features_dict | sizes_dict | features2_dict | property_overview_dict | excerpt_dict

        data_file.write(f"{data}\n")
        with open("done_urls.txt", "a+") as f:
            f.write(url+"\n")
        time.sleep(1)
    except:
        error_file.write(f"{url}\n")