import os
import json
import requests
from bs4 import BeautifulSoup

PRICE_HISTORY = "prices.json"
MAX_PRICE = 1e9

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
})

def get_offer_id(product_url: str):


    # get main page
    resp = session.get(product_url)
    if resp.status_code != 200:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # get offer id
    offer_tag = soup.select_one("[data-offer-id]") or soup.select_one("input[name='offer_id']")
    if not offer_tag:
        print("Could not find offer ID on page.")
        return None
    
    offer_id = offer_tag.get("data-offer-id") or offer_tag.get("value")

    return offer_id

def extract_vouchers(node, targets = None):
    if targets is None:
        targets = {
            "available_vouchers",
            "vouchers",
            "voucher",
            "promotions",
            "campaign_vouchers",
            "notification"
        } 
    found = []

    if isinstance(node, dict):
        for key, value in node.items():
            if key in targets:
                if isinstance(value, list):
                    found.extend(value)
                elif isinstance(value, dict):
                    found.append(value)
            else:
                found.extend(extract_vouchers(value, targets))
    elif isinstance(node, list):
        for item in node:
            found.extend(extract_vouchers(item, targets))
    
    return found           

def get_vouchers(offer_id):
    # check offer id is good

    url = f"https://sapi.emag.ro/voucher-campaign/product-page/{offer_id}?source_id=7"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
    }

    SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY")
    proxy_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"

    response = requests.get(url = proxy_url, headers = headers)
    if response.status_code == 200:
        jason = response.json()
        if jason.get("code") == 200 and isinstance(jason.get("data"), dict):

            return extract_vouchers(jason["data"])
        
        if not isinstance(jason.get("data"), dict):
            return []
        
    else:
        print("Offer ID is not correct!")
    return []

def parse_price(price):
    return float(price.replace("Lei", "").strip().replace(",", "").replace(".", "")) / 100

def check_price(url) -> dict:

    SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY")

    if SCRAPER_API_KEY:
        proxy_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"

    headers = {
    
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}
    response = requests.get(
    url = proxy_url,
    headers=headers,
)

    if response.status_code != 200:
        print("Could not access page.")
        exit()

    soup = BeautifulSoup(response.text, "html.parser")

    data = {}

    #title
    title = soup.select_one("h1")
    if title:
        data["title"] = title.get_text(strip = True)    
        print(title.get_text(strip = True))
    else:
        print("ia la muie")
    
    #price
    price_html = soup.select_one("p.product-new-price")
    aux = price_html.get_text(strip = True)
    price = parse_price(aux)

    if price_html:
        data["base_price"] = price
        print(f"Pret: {price_html.get_text(strip = True)}")

    else:
        print("price not found")
    
    #posibil voucher

    vouchers = get_vouchers(get_offer_id(url))
    if len(vouchers) == 0:
        print("Nu am gasit voucher!")

    max_discount = 0
    for voucher in vouchers:
        discount = voucher["discount_value"]
        max_discount = max(max_discount, discount)
        print(f"Am gasit un voucher de {discount}%!")
        print(voucher.get("content").get("text"))
        print()
        print(f"Pret final: {(100 - discount) / 100 * price :.2f}")
    
    data["voucher_discount"] = max_discount
    data["best_price"] = (100 - max_discount) / 100 * price
    print()

    return data

def send_telegram_alert(message: str):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if (bot_token is None) or (chat_id is None):
        return
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",  
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"[!] Failed to send alert: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[!] Network error sending alert: {e}")

def load_history(filename = "prices.json") -> dict:
    if not os.path.exists(filename):
        return {}
    
    if os.path.exists(filename) and os.path.getsize(filename) == 0:
        return {}
    
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)
    
def save_history(data = dict, filename = "prices.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def run_check():
    history = load_history()
    
    for link in linkuri:
        old_data = history.get(link, {})
        new_data = check_price(link)
        if new_data.get("best_price", MAX_PRICE) < old_data.get("best_price", MAX_PRICE):
            history[link] = new_data
            
            msg = f"Price drop for {new_data.get('title', 'error')}! New price: {new_data.get('best_price', MAX_PRICE): .2f}."
            send_telegram_alert(msg)

            print(f"Price dropped from {float(old_data.get('best_price', MAX_PRICE)):.2f} to {float(new_data.get('best_price', MAX_PRICE)):.2f}")

    save_history(history)

linkuri = []
linkuri.append("https://www.emag.ro/legor-ninjago-fierarul-patru-arme-la-a-15-a-aniversare-71858-1259-piese-5702018031995/pd/DJBL1Q3BM/")
linkuri.append("https://www.emag.ro/set-de-constructie-legor-ninjagor-robotul-de-titan-al-lui-lloyd-la-a-15-a-aniversare-71860-jucarii-pentru-copii-jucarii-pentru-baieti-si-fete-idee-de-cadou-pentru-copii-5702018055694/pd/DXMSW83BM/")
linkuri.append("https://www.emag.ro/set-de-constructie-legor-ninjagor-robotii-titan-gemeni-71870-jucarii-pentru-copii-jucarii-pentru-baieti-si-fete-idee-de-cadou-pentru-copii-5702018055779/pd/DRP7132BM/")
linkuri.append("https://www.emag.ro/set-de-constructie-legor-ninjagor-impresionanta-batalie-a-dragonului-71872-jucarii-pentru-copii-jucarii-pentru-baieti-si-fete-idee-de-cadou-pentru-copii-5702018055793/pd/D6P7132BM/")
linkuri.append("https://www.emag.ro/set-de-constructie-legor-ninjagor-batalia-de-la-sabia-dragonului-71871-jucarii-pentru-copii-jucarii-pentru-baieti-si-fete-idee-de-cadou-pentru-copii-5702018055786/pd/D5P7132BM/")
linkuri.append("https://www.emag.ro/set-de-constructie-legor-speed-champions-bmw-m3-e30-77263-jucarii-pentru-copii-jucarii-pentru-baieti-si-fete-masini-de-jucarie-idee-de-cadou-pentru-copii-358-piese-5702018068427/pd/DCWDF02BM/")
linkuri.append("https://www.emag.ro/set-de-constructie-legor-speed-champions-ferrari-499p-77261-jucarii-pentru-copii-jucarii-pentru-baieti-si-fete-masina-de-jucarie-idee-de-cadou-pentru-copii-5702018068403/pd/DFX7132BM/")
linkuri.append("https://www.emag.ro/set-de-constructie-legor-speed-champions-65-ford-mustang-hoonicorn-v1-al-lui-ken-block-77262-jucarii-pentru-copii-jucarii-pentru-baieti-si-fete-masina-de-jucarie-idee-de-cadou-pentru-copii-57020180684/pd/DJX7132BM/")
linkuri.append("https://www.emag.ro/set-de-constructie-pentru-adulti-legor-star-warstm-boba-fetttm-75455-decoratiune-pentru-living-idee-de-cadou-pentru-barbati-si-femei-pasionati-de-jocuri-de-constructie-1544-piese-5702018063125/pd/DNWDF02BM/")
linkuri.append("https://www.emag.ro/legor-star-wars-tm-nava-stelara-a-lui-jango-fett-75433-707-piese-5702017901237/pd/DV05T03BM/")

run_check()