import time
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

urls_handle = open("all_urls.txt", "a+")
done_handle = open("done.txt", "a+")

for page_num in range(1, 1184):
    print("Page Number:", page_num)
    url = f"https://www.property24.co.ke/houses-for-sale?Page={page_num}"
    driver.get(url)
    block = driver.find_element(By.CLASS_NAME, "sc_searchResultsP24Style")
    properties = block.find_elements(By.CLASS_NAME, "js_listingTile")
    for property in properties:
        property_url = property.find_element(By.TAG_NAME, "a").get_attribute("href")
        urls_handle.write(property_url + "\n")
    time.sleep(1)