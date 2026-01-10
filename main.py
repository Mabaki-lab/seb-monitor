import requests
from datetime import datetime
import os

# --- Telegram Secrets aus GitHub Actions ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- URL für Test-Scraping (Berliner Zeit) ---
URL = "https://worldtimeapi.org/api/timezone/Europe/Berlin"

# --- Logdatei für Test ---
LOG_FILE = "logs_test.txt"

def get_current_time():
    """Lädt die aktuelle Zeit von Berlin"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (GitHub Actions Test)"}
        r = requests.get(URL, timeout=60, headers=headers)
        r.raise_for_status()
        data = r.json()
        return data.get("datetime")
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
    current_time = get_current_time()
    if current_time:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"⏰ Aktuelle Berliner Zeit ({timestamp}): {current_time}"
        send_telegram(message)
        # Logs speichern
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {current_time}\n\n")
        print("Telegram gesendet und Log geschrieben.")
    else:
        print("Kein Inhalt gefunden.")

if __name__ == "__main__":
    main()
