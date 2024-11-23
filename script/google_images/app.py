from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os
import requests
from PIL import Image
from io import BytesIO
from rembg import remove

# Geolocation coordinates for Bali, Indonesia
BALI_LATITUDE = -8.3405
BALI_LONGITUDE = 115.0920
ACCURACY = 1000000  # Meters

NUM_IMAGES = 500
SEARCH_TERM = "kipas bali"
FOLDER_NAME = "images/" + SEARCH_TERM

HEADLESS = True
THUMBNAIL_SELECTORS = ["g-img.mNsIhb img.YQ4gaf", "g-img.tb08Pd img.YQ4gaf"]
FULL_IMAGE_SELECTOR = "img.sFlh5c.FyHeAf.iPVvYb"
GOOGLE_IMAGES_URL = "https://images.google.com"
SCROLL_WAIT_TIME = 5
SCROLL_SCRIPT = "window.scrollTo(0, document.body.scrollHeight);"

options = Options()
if HEADLESS:
    options.add_argument("--headless")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.geolocation": 1,  # Allow geolocation
})

def set_geolocation(driver, latitude, longitude, accuracy):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "accuracy": accuracy
    }
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", params)

def process_and_save_image(folder, url, count):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Membaca gambar ke dalam format PIL
        img = Image.open(BytesIO(response.content))

        # Konversi gambar ke format byte untuk diproses oleh rembg
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        # Menghapus latar belakang menggunakan rembg
        img_no_bg = remove(img_bytes.getvalue())
        img_no_bg = Image.open(BytesIO(img_no_bg)).convert("RGBA")

        # Membuat kanvas putih polos
        white_background = Image.new("RGBA", img_no_bg.size, (255, 255, 255, 255))

        # Menempelkan gambar tanpa latar belakang ke kanvas putih
        img_with_white_bg = Image.alpha_composite(white_background, img_no_bg)

        # Resize gambar menjadi 224x224
        img_resized = img_with_white_bg.resize((224, 224))

        # Konversi kembali ke mode RGB untuk menyimpan sebagai JPG
        img_resized = img_resized.convert("RGB")

        # Menyimpan gambar
        filename = os.path.join(folder, f'image_{count}.jpg')
        img_resized.save(filename, format='JPEG')
        print(f"Processed and saved: {filename}")
    except Exception as e:
        print(f"Failed to process and save image {count}: {e}")

def scrape_google_images(search_term, num_images, folder_name=FOLDER_NAME):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    driver = webdriver.Chrome(options=options)

    try:
        # Set the browser geolocation to Bali, Indonesia
        set_geolocation(driver, BALI_LATITUDE, BALI_LONGITUDE, ACCURACY)

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
                    process_and_save_image(folder_name, src, count + 1)

                count += 1
                if count >= num_images:
                    break
            except Exception as e:
                print(f"Error processing image {count}: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_google_images(SEARCH_TERM, NUM_IMAGES)
