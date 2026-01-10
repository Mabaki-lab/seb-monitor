import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# --- Telegram Secrets aus GitHub Actions ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- URL für Test-Scraping (SEB-ImmoInvest) ---
URL = "https://www.savillsim-publikumsfonds.de/de/fonds/seb-immoinvest/preise"

# --- Temporäre Test-Logdatei ---
LOG_FILE = "logs_test.txt"

def get_div_content():
    """Scrape den div.footenote Inhalt"""
    try:
        r = requests.get(URL, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        div = soup.select_one("div.footenote")
        if div:
            return div.get_text(separator="\n").strip()
    except Exception as e:
        print("Scraper Fehler:", e)
    return None

def send_telegram(message):
    """Sende Nachricht über Telegram Bot"""
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
    content = get_div_content()
    if content:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"🔔 Test SEB-ImmoInvest ({timestamp}):\n{content}"
        send_telegram(message)
        # Logs speichern
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {content}\n\n")
        print("Telegram gesendet und Log geschrieben.")
    else:
        print("Kein Inhalt gefunden.")

if __name__ == "__main__":
    main()
