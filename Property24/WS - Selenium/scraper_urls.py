import time
from selenium import webdriver
from selenium.webdriver.common.by import By

def get_driver():
    return webdriver.Chrome()

def process_pages(start_page, end_page, file_handle):
    driver = get_driver()
    try:
        for page_num in range(start_page, end_page):
            print("Page Number:", page_num)
            url = f"https://www.property24.co.ke/houses-for-sale?Page={page_num}"
            driver.get(url)
            block = driver.find_element(By.CLASS_NAME, "sc_searchResultsP24Style")
            properties = block.find_elements(By.CLASS_NAME, "js_listingTile")
            for property in properties:
                property_url = property.find_element(By.TAG_NAME, "a").get_attribute("href")
                file_handle.write(property_url + "\n")
            time.sleep(1)
    finally:
        driver.quit()

start_page = 478
end_page = 1183

with open("property_urls.txt", "a+") as f:
    current_start_page = start_page
    while current_start_page < end_page:
        next_end_page = min(current_start_page + 100, end_page)
        process_pages(current_start_page, next_end_page, f)
        current_start_page = next_end_page
