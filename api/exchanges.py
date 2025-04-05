import requests
from bs4 import BeautifulSoup

site = requests.get("https://bank.gov.ua/en/markets/exchangerates").text
soup = BeautifulSoup(site, features="html.parser")
exchange_sheet = soup.find_all("tr")

def find_currensy_exchange_info(currency: str, exchange_sheet: BeautifulSoup) -> BeautifulSoup:
    for item in exchange_sheet:
        currency_info = item.find_all("td")
        for i in currency_info:
            if i.text == currency:
                return item

def get_NBU_usd_exchange_rate() -> float:
    usd_exchange_info = find_currensy_exchange_info("USD", exchange_sheet)
    exchange_rate = usd_exchange_info.find_all("td")[-1].text
    return float(exchange_rate)
