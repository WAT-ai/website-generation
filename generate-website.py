import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from threading import Thread

# Get URL
url = {WEBSITE_GENERATOR_URL}
xpath = {XPATH_TO_BUTTON}
out_path = "additional_domains.json"
website_out = []


def fetch_random_website(url_param, xpath_param):
    try:
        # Set up chrome_driver options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')

        driver = webdriver.Chrome(options=chrome_options)

        # Get the URL to the website
        driver.get(url_param)

        # Get element that generates the random websites
        website_link_gen = driver.find_element(By.XPATH, xpath_param)
        website_link_gen.click()

        # Set up wait
        wait = WebDriverWait(driver, 10)
        wait.until(EC.number_of_windows_to_be(2))

        cur_window = driver.current_window_handle

        for window_handle in driver.window_handles:
            if window_handle != cur_window:
                driver.switch_to.window(window_handle)
                break

        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")

        return driver.current_url
    except Exception as e:
        print(f"Error fetching website")
        return None

def get_website():
    website = fetch_random_website(url, xpath)
    if website:
        # Get rid of stuff at the beginning of the website (https://www. for instance)
        temp_website = website.split('/', 2)

        if len(temp_website) < 3:
            return

        temp_website = temp_website[2]

        print(f"index: {i}, website: {temp_website}")

        dictionary = {"position": i, "domain": temp_website}
        website_out.append(dictionary)

# Multithreading
thread_list = []

for i in range(20000):
    filter_thread = Thread(target=get_website, args=())
    thread_list.append(filter_thread)
    filter_thread.start()

for thread in thread_list:
    thread.join()

with open(out_path, 'w', encoding='utf-8') as out_file:
    json.dump(website_out, out_file)
