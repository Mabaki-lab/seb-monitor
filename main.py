import os
import asyncio
from playwright.async_api import async_playwright
import requests

# --- Telegram Secrets ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- URL der SEB-News ---
NEWS_URL = "https://www.savillsim-publikumsfonds.de/de/fonds/seb-immoinvest/news"

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

# --- Scraper-Funktion ---
async def scrape_news():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(NEWS_URL, wait_until="networkidle")

        # Alle News-Artikel
        articles = await page.query_selector_all("div.news-list-view article.news-cards__item")
        count = len(articles)
        print(f"Aktuell {count} News gefunden.")

        latest_msg = ""
        if count > 0:
            # Neueste News (erste in der Liste)
            latest_article = articles[0]
            h3 = await latest_article.query_selector("h3")
            title = await h3.inner_text() if h3 else "Keine Überschrift"
            link_tag = await latest_article.query_selector("a.news-list__title")
            link = await link_tag.get_attribute("href") if link_tag else None
            if link and link.startswith("/"):
                link = "https://www.savillsim-publikumsfonds.de" + link
            latest_msg = f"📰 Neueste News: {title}\n{link}"

        # Telegram-Nachricht erstellen
        msg = f"Es gibt aktuell {count} News auf der SEB ImmoInvest Seite."
        if count > 2:
            msg += f"\n\n{latest_msg}"

        send_telegram(msg)
        print("Telegram gesendet:", msg)

        await browser.close()

# --- Main-Funktion ---
def main():
    asyncio.run(scrape_news())

# --- Ausführen ---
if __name__ == "__main__":
    main()
