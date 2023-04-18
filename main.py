from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from twilio.rest import Client
from dotenv import load_dotenv
import os
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# dotenv_path = Path('path/to/.env')
load_dotenv()


# 1- Selenium: For automation testing, web scraping, as well as interacting with web pages.
# 2- Beautiful Soup: A Python package for parsing HTML and XML documents.
# 3- Selenium Web Driver: uses a real web browser to access a website. This
# activity simulates an ordinary user browsing instead of a bot.

def get_url(search_text):
    url = f"https://www.amazon.com/s?k={search_text}&ref=nb_sb_noss_2"
    url += "&page{}"
    return url


def extract_record(single_item):
    try:
        price_parent = single_item.find('span', "a-price")
        price = price_parent.find('span', 'a-offscreen').text

    except AttributeError:
        return

    return price


def main(search_term, max_price):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.google.com")
    prices_list = []
    url = get_url(search_term)

    for page in range(1, 5):
        driver.get(url.format(page))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        results = soup.find_all("div", {"data-component-type": "s-search-result"})
        for item in results:
            record = extract_record(item)
            if record:
                prices_list.append(record)

    new_prices = [s.replace("$", "").replace(",", "") for s in prices_list]
    updated_prices = []

    prices_float = [float(i) for i in new_prices]

    for i in prices_float:
        if i <= max_price:
            updated_prices.append(i)

    account_sid = os.environ["ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    to_phone_no = os.environ["TO_PHONE_NO"]
    from_phone_no = os.environ["FROM_PHONE_NO"]
    client = Client(account_sid, auth_token)
    client.messages.create(
        to=to_phone_no,
        from_=from_phone_no,
        body=f"There are {len(updated_prices)} {search_term} within budget, ${max_price}"
    )


main("playstation 5 console", 1000)
