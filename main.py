import os
import json
import requests
from bs4 import BeautifulSoup

PRICE_HISTORY = "prices.json"
MAX_PRICE = 1e9

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "ro-RO,ro;q=0.9",
    "Referer": "https://www.emag.ro/",
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

def get_vouchers(offer_id):
    # check offer id is good
    url = f"https://sapi.emag.ro/voucher-campaign/product-page/{offer_id}?source_id=7"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.emag.ro/",
    }

    response = requests.get(url = url, headers = headers)
    if response.status_code == 200:
        jason = response.json()
        if jason.get("code") == 200 and isinstance(jason.get("data"), dict):
            vouchers = jason["data"].get("available_vouchers", [])
            return vouchers
        
        if not isinstance(jason.get("data"), dict):
            return []
        
    else:
        print("Offer ID is not correct!")
    return []

def parse_price(price):
    return float(price.replace("Lei", "").strip().replace(",", "."))

def check_price(url) -> dict:

    headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://www.emag.ro/search/ninjago?ref=effective_search',
    'sec-ch-ua': '"Chromium";v="154", "Google Chrome";v="154", "Not A(Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36',
    # 'cookie': 'EMAGVISITOR=a%3A1%3A%7Bs%3A7%3A%22user_id%22%3Bi%3A2517854037843260319%3B%7D; listingPerPage=60; _pdr_internal=GA1.2.9869138312.1762980091; user_remember=%DB%11b%C5dy%B9%BA%A4%928%CA%A9%3D%ECl%AA%F9%C4i%F5%DE%C6r%DAD%1C-%CF%1C%96%94%7F%24%1C%A5%FA%DC%B9%0A%18%A6%13E%BD7%FF1%E1%19%D1%28%D6%E8A2%94%0B%FB4%BCn_%17%C6%E1%8A%DA%AD%E0%18%7C%B1H%AD%91~%BC%5D%FE%F6%C6%E4t.%F3%5C%CA%B4%A6%BF%99%BD%94O%C3%90%EDP%13%F3%DA%85%24%20%A6%40%BD%F4%A0mq%B30-%13%BA7_%F0%29%97ny%C4Du%AF%F6R%AE6%CAV%FF%27%B0-%2A%10%B7%FF%275%D6%BD%0F%A1%2B%28%84%02%FC%BC%AC%A3%02%9D%204%E15%B6%F3%A41%1F%E5; pdr_user_id=b2de8fcc23072b6e453014e9e9c04d6b; user_token=a191864c543536643775b6b760a7cae4; customer_has_orders=1; EMAG_CUSTOMER=104427003; sr=1470x856; vp=1470x735; udp=eAGNkUEKwzAMBP%2BiF1iWnNib17T04kOhkN6C%2F15HSesQaPBJXmF2tNINAUtG4ukGxTKDQQ%2BarPJaPeg9742wN56v9aEgYRWaMgaOsRrwbnCnKrz5bg7s1l%2FstMlSSsVKD1bPWHbhGsuBGylDfVPGDdrDrQzLv8UV0CjpMu3QMBkSpEmjauqh%2BjM1Odve3x0f02X4wxBGlbGH%2Br31L2uKw2VWTi1dPW1sqlLLB4y%2FmWk%3D; eab1693=b; gmexpiresoon={"v":{"v":0,"u":104427003,"l":1},"t":1781008386748,"e":"14d"}; eab1713=b; ltuid=2621775408672377819; EMAGUUID=1786039007-992199011-28485.465; site_version_11=not_mobile; eab1742=a; listingResetView=1; eab1737=b; eab1746=b; eab1768=a; eab1769=a; eab1770=b; eab1773=b; eab1778=a; listingDisplayId=2; eab1780=b; eab1782=b; _gcl_au=1.1.761649760.1789282967; eab1783=a; customer_delivery_info={"g":1,"lid":4966,"dp":"3d64dee6-88f6-4dd5-972c-42d678872641"}; eab1785=b; eab1787=b; AID=499b6be783beb9c73390d635b6720c84f8184d7f2109904d7c862b72c16c783f; EMAGROSESSID=0b9c13eb27d11cf2928b3e08d676d7b3; sapi-token=eyJ1c2VyX2lkIjoyNTE3ODU0MDM3ODQzMjYwMzE5LCJ1c2VyX2tleSI6Inc1c1JZc09GWkhuQ3VjSzZ3NUhDc0h4c0swSENpc080dzYwT3dxZkNzOE9GSVVVZVZCREN2V2hwd29CekJGc3RIc09jdzRIQ3RCM0Nya0xDdjhLcmNjS3pLTUsyVXdvR0dSMTh3clBEb2NPdHdwVmZmY0t6TmNLRXdyakRzc082dzY5aXc0M0N0MTdEdThLdGFXekNzMVV1d3B0U1pRPT0iLCJsYW5nX2NvZGVfa2V5IjoidzVzUllzT0ZaSG5DdWNLNnc1SENzSHhzSzBIQ2lzTzRLY0tBdzdIRHV4SWt3NlREc2NPSndxZzhHRE0yYk1Ld3c1UEN0UTNEdE1LdVNjS0NlOEsxTnNLaVJNS0hTOE90RzhLeFc4T0FNY0tZdzVuQ3Y4T3h3NW9rU3NLYXc0YkN2UmJEdVNiRHFSUENtc0tSQUNVNE5rXC9Dc1JzRkhWekR2QT09IiwiYXV0aF90b2tlbl9rZXkiOiJ3NXNSWXNPRlpIbkN1Y0s2dzVIQ3NIeHNLMEhDaXNPNHdvREN2c09JdzRRSHc3TmNNOE91d29cL0N2RzFEd29RT3c2VERoV0pQdzRFdWZjT3BjY0tzZWNLNGM4S2h3Njl2T2NLWHc3MHhIMHJDdW5OeEJrSXpLOE9QYkZmRG14ekNuTU9OdzVQRGdNT2ZPVFBEcXNPQVduUER0TUtNdzR6Q21jT3JZOEtGdzdQRGdjSyt3ckRDZzhLZ3c3RERrQ2NhdzZURGdoUERoTUsxdzZ4UFNCb2t3cVwvRGlzT0V3NUhEcDhPQ3dxUERsOEtod3JjemFzS1l3NUhEbUVUQ2pBPT0iLCJ1dWlkIjoiMTc4NjAzOTAwNy05OTIxOTkwMTEtMjg0ODUuNDY1In0%3D; auth-token=eyJ0eXAiOiJKV1QiLCJraWQiOiIxNzA4MzcwMzc0IiwiYWxnIjoiUlMyNTYifQ.eyJleHAiOjE3OTE3OTgzMzksIm5iZiI6MTc5MDU4ODY3OSwicnQiOiJkMWU4Yjk2YTVjOWM1MzA4ZWNhNGI4YjE0OWJjZDRhNTg1ZGM5NzgwIiwiY3VzdG9tZXJfaWQiOjEwNDQyNzAwMywiZW1haWwiOiJ1bmcwOS5ybEBnbWFpbC5jb20iLCJwIjoiMDc3MDcxNjU0NSIsInBpdiI6MSwidmlkIjoyNTE3ODU0MDM3ODQzMjYwMzE5LCJpc3MiOiJlTUFHIEF1dGgiLCJhdWQiOiJlTUFHIiwic2NvcGUiOiJ1c2VyOmluZm8gdXNlcjpzZWN1cml0eSBvcGVuaWQifQ.CIdClHXeCCebhLv0CyiYdnWjA2tIyTOfhGDtDiSxKV73_V-mmjRvwiYbdjmnGFoq30qon33vuT5EkMTmKcwAhO75gtCQZfFAjsbID7xc0tZsQXvKFp8hWyu45UC7W8BaBbH1qQ4ZdNgwdQcvQUkXMPEAcF-GlY1kmIB_GPR4I-e5MFeY5aJLJz1Dlwvdo5J6v1oykbDZG_m5i6f6ThfdIfsCaFUAl9wtJIF6VfnmYZX2mbR-XMZS5UuO2dVXGovQzMdhm14zaRm2wpHtIZprvntkC-1UnftDCYFWOdDGwUnu7-jIoppKX3CWiw50BldPyey73wkw0N1pLu8v5sH3Qg; delivery_locality_id=4966; gmfamily={"v":{"v":0,"u":104427003,"l":1},"t":1790588740738,"e":"30d"}; cart_summary=%7B%22t%22%3A1790588744%2C%22b%22%3A1%2C%22p%22%3A539.99%2C%22bfc%22%3A0%2C%22line%22%3A%7B%221%22%3A1%7D%7D; postlogin=2xFixWR5ubqTOJVjm13%2BzklG3BlNW%2BDwUCMGCNniCfhqJMFtD2ms%2BJYJJjnqXmNHb4sRgoTeWiLdtn8YwZIHYMONrgCvwl%2F0f7lq8n5t77cjQLd%2FY%2BNyrWphwVIgXIBmVZvaAVua0IWR6k%2B00fX7gZRdbnyZYJXWqYpxDS3u5GA%3D; _pdr_view_id=1790588813-31103.092-408037360',
}
    response = requests.get(
    url = url,
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
    
    print(max_discount)
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

            print(f"Price dropped from {float(old_data.get('best_price')):.2f} to {float(new_data.get('best_price')):.2f}")

    save_history(history)

linkuri = []
linkuri.append("https://www.emag.ro/legor-ninjago-fierarul-patru-arme-la-a-15-a-aniversare-71858-1259-piese-5702018031995/pd/DJBL1Q3BM/")
linkuri.append("https://www.emag.ro/set-de-constructie-legor-ninjagor-robotul-de-titan-al-lui-lloyd-la-a-15-a-aniversare-71860-jucarii-pentru-copii-jucarii-pentru-baieti-si-fete-idee-de-cadou-pentru-copii-5702018055694/pd/DXMSW83BM/")
linkuri.append("https://www.emag.ro/set-de-constructie-legor-ninjagor-robotii-titan-gemeni-71870-jucarii-pentru-copii-jucarii-pentru-baieti-si-fete-idee-de-cadou-pentru-copii-5702018055779/pd/DRP7132BM/")

run_check()