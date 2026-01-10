import os
import asyncio
from playwright.async_api import async_playwright
import json
import requests

# --- Telegram Secrets ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- URL der SEB-News ---
NEWS_URL = "https://www.savillsim-publikumsfonds.de/de/fonds/seb-immoinvest/news"

# --- Log-Datei zum Speichern der bereits gesendeten News-IDs ---
LOG_FILE = "news_log.json"

# --- Telegram Nachricht senden ---
def send_telegram(message: str):
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

# --- Log-Datei laden ---
def load_sent_ids():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

# --- Log-Datei speichern ---
def save_sent_ids(ids):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(ids, f)

# --- Scraper-Funktion ---
async def scrape_news():
    sent_ids = load_sent_ids()
    new_sent_ids = sent_ids.copy()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(NEWS_URL, wait_until="networkidle")  # wartet bis alles geladen ist

        # Alle News-Artikel
        articles = await page.query_selector_all("div.news-list-view article.news-cards__item")
        if not articles:
            print("Keine News gefunden.")
            await browser.close()
            return

        new_messages = []

        for article in articles:
            # Überschrift
            h3 = await article.query_selector("h3")
            title = await h3.inner_text() if h3 else "Keine Überschrift"

            # Datum
            time_tag = await article.query_selector("time")
            date = await time_tag.inner_text() if time_tag else "Kein Datum"

            # Link
            link_tag = await article.query_selector("a.news-list__title")
            link = await link_tag.get_attribute("href") if link_tag else None
            if link and link.startswith("/"):
                link = "https://www.savillsim-publikumsfonds.de" + link

            # ID aus Link ableiten
            news_id = link.split("/")[-1] if link else title

            if news_id not in sent_ids:
                msg = f"📰 {date}: {title}\n{link}"
                new_messages.append(msg)
                new_sent_ids.append(news_id)

        await browser.close()

    # Telegram senden
    for msg in new_messages:
        send_telegram(msg)
        print("Telegram gesendet:", msg)

    # Log aktualisieren
    if new_messages:
        save_sent_ids(new_sent_ids)
    else:
        print("Keine neuen Nachrichten.")

# --- Main-Funktion ---
def main():
    asyncio.run(scrape_news())

if __name__ == "__main__":
    main()
