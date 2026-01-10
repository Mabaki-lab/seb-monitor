import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# --- Telegram Daten aus GitHub Secrets ---
BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# Test-URL (kann SEB-ImmoInvest sein oder eine Testseite)
URL = "https://www.savillsim-publikumsfonds.de/de/fonds/seb-immoinvest/preise"
LOG_FILE = "logs_test.txt"

def get_div_content():
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
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)
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
        print("Telegram gesendet und Test-Log erstellt.")

if __name__ == "__main__":
    main()
