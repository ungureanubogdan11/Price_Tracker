import re
import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "ro-RO,ro;q=0.9",
    "Referer": "https://www.emag.ro/",
})

def get_offer_id(product_url: str):
    # 1. Fetch main page
    resp = session.get(product_url)
    if resp.status_code != 200:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # 2. Extract Offer ID
    offer_tag = soup.select_one("[data-offer-id]") or soup.select_one("input[name='offer_id']")
    if not offer_tag:
        print("Could not find offer ID on page.")
        return None
    
    offer_id = offer_tag.get("data-offer-id") or offer_tag.get("value")

    # 3. Fetch the vouchers JSON
    
    print(offer_id)

    return []