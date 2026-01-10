import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# --- Telegram Secrets ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- URL der News-Seite ---
NEWS_URL = "https://www.savillsim-publikumsfonds.de/de/fonds/seb-immoinvest/news"

def get_all_news():
    """Liest alle News auf der Seite aus"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(NEWS_URL, headers=headers, timeout=60)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        
        news_list = soup.select("div.news-list-view article.news-cards__item")
        if not news_list:
            print("Keine News gefunden auf der Seite.")
            return []

        result = []
        for item in news_list:
            # Überschrift
            title_tag = item.select_one("h3")
            title = title_tag.get_text(strip=True) if title_tag else "Keine Überschrift"

            # Datum
            date_tag = item.select_one("time")
            date = date_tag.get_text(strip=True) if date_tag else "Kein Datum"

            # Link
            link_tag = item.select_one("a.news-list__title")
            link = link_tag.get("href") if link_tag else None
            if link and link.startswith("/"):
                link = "https://www.savillsim-publikumsfonds.de" + link

            result.append({"title": title, "date": date, "link": link})
        return result

    except Exception as e:
        print("Fehler beim Abrufen der News:", e)
        return []

def send_telegram(message):
    """Sende Nachricht an Telegram"""
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram Secrets fehlen!")
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        resp = requests.post(url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)
        if not resp.ok:
            print("Telegram Fehler:", resp.text)
    except Exception as e:
        print("Telegram Fehler:", e)

def main():
    news = get_all_news()
    if not news:
        print("Keine News gefunden.")
        return

    # Nachricht zusammenbauen
    message = "📰 Aktuelle SEB-ImmoInvest News:\n\n"
    for item in news:
        message += f"{item['date']}: {item['title']}\n{item['link']}\n\n"

    send_telegram(message)
    print(f"Telegram gesendet: {len(news)} Nachrichten")

if __name__ == "__main__":
    main()
