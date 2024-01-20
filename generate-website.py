import concurrent.futures
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Get URL
#url = {WEBSITE_GENERATOR_URL}
#xpath = {XPATH_TO_BUTTON}
out_path = "additional1_domains.json"

website_list = []


def fetch_random_website(url_param, xpath_param):
    try:
        # Set up chrome_driver options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--disable-blink-features")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

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
        print(f"Error fetching website: {e}")
        return None


def get_website(i):
    website = fetch_random_website(url, xpath)
    if website:
        print(f"index: {i}, website: {website}")
        dictionary = {"position": i, "domain": website}
        website_list.append(dictionary)


# Multithreading with ThreadPoolExecutor
max_threads = os.cpu_count()
with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
    # Submit tasks to the thread pool
    futures = {executor.submit(get_website, i): i for i in range(5)}

    # Wait for all threads to finish
    concurrent.futures.wait(futures)


website_list.sort(key=lambda x: x['position'])

with open(out_path, 'w', encoding='utf-8') as out_file:
    json.dump(website_list, out_file)
    out_file.write(',\n')
