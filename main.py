# description: The code generates new csv each time when it operates

import re
import csv
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service


def extract_float(s):
    """
    Extract float value from a string.
    s: String
    """
    return float(re.sub(r"[^\d.]", "", s))


def extract_all(s):
    """
    Extract the float value after the dollar sign in a string.
    s: String
    """
    match = re.search(r"\$(\d+\.\d+)", s)
    if match:
        return float(match.group(1))
    else:
        return float(re.sub(r"[^\d]", "", s))


def get_source(URL, click_time):
    """
    Fetch the page source of a URL using Selenium.
    URL: String
    click_time: float
    """
    service = Service()
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(URL)

    while True:
        time.sleep(click_time)  # wait for website to respond
        try:
            btn = driver.find_element(By.CSS_SELECTOR, '.button_E6SE9.loadMore_3AoXT')
            btn.click()
        except NoSuchElementException:  # no more buttons or website refreshing
            break
    page_source = driver.page_source
    driver.close()
    return page_source


def write_csv(products):
    """
    Create a new CSV file with product information.
        products: List
    """
    unique_time = datetime.now().strftime("%Y%m%d%H%M%S")
    new_filename = f'product_{unique_time}.csv'

    with open(new_filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Product Number', 'Name', 'Price', 'Original Price', 'Ratings', 'Viewers'])

        for idx, (name, price, original_price, rating, viewer) in enumerate(products, start=1):
            csvwriter.writerow([idx, name, price, original_price, rating, viewer])


URL = 'https://www.bestbuy.ca/en-ca/category/televisions/21344'
min_items = 0
curr_scan = -1
soup = None
click_time = 0.5

while curr_scan < min_items:    # Check whether successfully crawl enough data
    curr_scan = 0               # initialize curr_scan
    page_source = get_source(URL, click_time)
    soup = BeautifulSoup(page_source, "html.parser")
    min_items = extract_all(soup.find('span', attrs={'class': 'materialOverride_STCNx toolbarTitle_2lgWp'}).get_text())

    for i in soup.find_all('div', attrs={'itemtype': 'http://schema.org/Product'}):
        curr_scan += 1

    print("__________")
    print(click_time)
    print(min_items)
     # print(curr_scan)

    click_time += 0.5  # increase click time for next re-crawl


products = []

# Extract corresponding datas within each product
for i in soup.find_all('div', attrs={'itemtype': 'http://schema.org/Product'}):
    name_temp = price_temp = original_temp = rating_temp = review_count_temp = None
    name_div = i.find('div', itemprop='name')
    if name_div:
        name_temp = name_div.get_text().strip()
    price_div = i.find('span', attrs={'data-automation': 'product-price'})
    if price_div:
        price = price_div.get_text().strip()
        price_temp = extract_float(price.split("$")[-1])
    original_div = i.find('span', attrs={'data-automation': 'product-saving'})
    if original_div:
        original_temp = extract_all(original_div.get_text().strip())
        original_temp = price_temp + original_temp


    rating_div = i.find('meta', attrs={'itemprop': 'ratingValue'})
    if rating_div:
        rating_temp = rating_div['content']
        print(rating_temp)

    review_count_div = i.find('meta', attrs={'itemprop': 'reviewCount'})
    # print("debug_1")
    if review_count_div:
        review_count_temp = review_count_div["content"]
        # print("debug_2")
    products.append((name_temp, price_temp, original_temp, rating_temp, review_count_temp))


write_csv(products)    # create new CSV for current info
