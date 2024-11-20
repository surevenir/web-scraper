from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import requests
from PIL import Image
from io import BytesIO

NUM_IMAGES = 100
SEARCH_TERM = "gantungan kunci souvenir bali"
FOLDER_NAME = "images/" + SEARCH_TERM

HEADLESS = True
THUMBNAIL_SELECTORS =[ "g-img.mNsIhb img.YQ4gaf", "g-img.tb08Pd img.YQ4gaf"]
FULL_IMAGE_SELECTOR = "img.sFlh5c.FyHeAf.iPVvYb"
GOOGLE_IMAGES_URL = "https://images.google.com"
SCROLL_WAIT_TIME = 3
SCROLL_SCRIPT = "window.scrollTo(0, document.body.scrollHeight);"

options = webdriver.ChromeOptions()
if HEADLESS:
    options.add_argument("--headless")

def save_image(folder, url, count):
    try:
        response = requests.get(url, timeout=10)
        img = Image.open(BytesIO(response.content))
        img_format = img.format if img.format else 'JPEG'
        filename = os.path.join(folder, f'image_{count}.{img_format.lower()}')
        img.save(filename)
        print(f"Saved: {filename}")
    except Exception as e:
        print(f"Failed to save image {count}: {e}")

def scrape_google_images(search_term, num_images, folder_name=FOLDER_NAME):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(GOOGLE_IMAGES_URL)
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(search_term + Keys.RETURN)

        last_height = driver.execute_script("return document.body.scrollHeight")
        while sum(len(driver.find_elements(By.CSS_SELECTOR, selector)) for selector in THUMBNAIL_SELECTORS) < num_images:
            driver.execute_script(SCROLL_SCRIPT)
            time.sleep(SCROLL_WAIT_TIME)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        thumbnails = []
        for selector in THUMBNAIL_SELECTORS:
            thumbnails += driver.find_elements(By.CSS_SELECTOR, selector)
        print(f"Found {len(thumbnails)} thumbnails.")

        count = 0
        for thumbnail in thumbnails:
            try:
                thumbnail.click()
                time.sleep(2)  

                full_image = driver.find_element(By.CSS_SELECTOR, FULL_IMAGE_SELECTOR)
                src = full_image.get_attribute("src")

                if src.startswith("http"): 
                    save_image(folder_name, src, count + 1)

                count += 1
                if count >= num_images:
                    break
            except Exception as e:
                print(f"Error processing image {count}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_google_images(SEARCH_TERM, NUM_IMAGES)
