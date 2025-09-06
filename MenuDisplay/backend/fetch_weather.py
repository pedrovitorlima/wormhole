import requests
from bs4 import BeautifulSoup

def fetch_weather(url):
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    day_main = soup.find("div", class_="day main")
    if not day_main:
        raise ValueError("Could not find day main div")

    # Max temperature
    max_temp_tag = day_main.find("em", class_="max")
    max_temp = max_temp_tag.text.strip() if max_temp_tag else None

    # Summary
    summary_tag = day_main.find("dd", class_="summary")
    summary = summary_tag.text.strip() if summary_tag else None

    # Chance of rain (look for dd.rain instead of dd.main)
    rain_dd = day_main.find("dd", class_="rain")
    chance_rain_tag = rain_dd.find("em", class_="pop") if rain_dd else None
    chance_rain = chance_rain_tag.text.strip() if chance_rain_tag else None

    return {
        "max_temp": max_temp,
        "summary": summary,
        "chance_rain": chance_rain
    }