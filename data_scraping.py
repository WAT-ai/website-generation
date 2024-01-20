import os
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
from webdriver_manager.chrome import ChromeDriverManager

screenshot_folder = "website-data/screenshots"
html_folder = "website-data/html"
css_folder = "website-data/css"


def get_html_css_from_url(url, timeout=60):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  

        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')

        css_styles = ''
        style_tags = soup.find_all('style')
        for style_tag in style_tags:
            css_styles += style_tag.get_text() + '\n'

        link_tags = soup.find_all('link', rel='stylesheet')
        for link_tag in link_tags:
            css_url = link_tag.get('href')
            if css_url:
                css_response = requests.get(css_url)
                css_response.raise_for_status()
                css_styles += css_response.text + '\n'

        return html_content, css_styles

    except requests.exceptions.RequestException as e:
        print(f"Error fetching content from {url}: {e}")
        return None, None


def take_screenshot(url, screenshot_folder, screenshot_filename):
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--disable-blink-features")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        driver = webdriver.Chrome(options=chrome_options)

        driver.get(url)

        screenshot_path = os.path.join(screenshot_folder, screenshot_filename)
        driver.save_screenshot(screenshot_path)

        driver.quit()

        print(f"Screenshot saved to: {screenshot_path}")

    except Exception as e:
        print(f"Error taking screenshot: {e}")

def save_to_file(content, folder, filename):
    try:
        file_path = os.path.join(folder, filename)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        print(f"Content saved to: {file_path}")
    except Exception as e:
        print(f"Error saving to file: {e}")


def get_template_websites(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        links = soup.find_all('a', {'img': True, 'href': True})
        print(soup.find_all('a', {'img': True}))
        template_websites = [link['href'] for link in links]

        return template_websites

    except requests.exceptions.RequestException as e:
        print(f"Error fetching content from {url}: {e}")
        return None


def get_website_data(website, index):
    html_filename = f"html_add_{index}.txt"
    css_filename = f"css_add_{index}.txt"

    html, css = get_html_css_from_url(website)

    if html and css:
        save_to_file(html, html_folder, html_filename)
        save_to_file(css, css_folder, css_filename)
        take_screenshot(website, screenshot_folder, f"screenshot_add_{index}.png")


with open('additional_domains.json', 'r') as file:
    json_data = json.load(file)

websites = [f"https://{entry['domain']}" if not entry['domain'].startswith(('http://', 'https://')) else entry['domain'] for entry in json_data]

# set the number of threads
max_threads = min(os.cpu_count(), len(websites))

# Create a ThreadPoolExecutor with the specified maximum number of threads
with ThreadPoolExecutor(max_threads) as executor:
    # Submit tasks to the thread pool
    futures = {executor.submit(get_website_data, website, i): website for i, website in enumerate(websites)}

    # Wait for all threads to finish
    wait(futures)

