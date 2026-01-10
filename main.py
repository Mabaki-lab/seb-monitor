import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# --- Telegram Secrets aus GitHub Actions ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- SEB-ImmoInvest Preise URL ---
URL = "https://www.savillsim-publikumsfonds.de/de/fonds/seb-immoinvest/preise"

LOG_FILE = "logs.txt"

def get_current_price():
    """Extrahiert den Rücknahmepreis aus div.footenote"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (GitHub Actions Test)"}
        r = requests.get(URL, timeout=60, headers=headers)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        div = soup.select_one("div.footenote")
        if div:
            text = div.get_text(separator="\n")
            for line in text.split("\n"):
                if "Rücknahmepreis" in line:
                    # z. B. "Rücknahmepreis   Eur 0,61"
                    price = line.split("Eur")[-1].strip()
                    return price
    except Exception as e:
        print("Scraper Fehler:", e)
    return None

def send_telegram(message):
    """Telegram Nachricht senden"""
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram Secrets fehlen!")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)
        if not r.ok:
            print("Telegram Fehler:", r.text)
    except Exception as e:
        print("Telegram Fehler:", e)

def main():
    price = get_current_price()
    if price:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"💰 SEB-ImmoInvest Rücknahmepreis ({timestamp}): {price} EUR"
        send_telegram(message)
        # Logs speichern
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {price} EUR\n\n")
        print(f"Telegram gesendet: {price} EUR")
    else:
        print("Kein Preis gefunden.")

if __name__ == "__main__":
    main()
