from ftplib import FTP
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

def fetch_weather():
    ftp = FTP("ftp.bom.gov.au")
    ftp.login()
    ftp.cwd("anon/gen/fwo")

    filename = "IDN10064.xml"
    data = []
    ftp.retrbinary(f"RETR {filename}", data.append)
    ftp.quit()

    xml_content = b"".join(data).decode("utf-8")
    root = ET.fromstring(xml_content)

    now = datetime.now(timezone.utc).astimezone()  # aware datetime in local zone
    today = now.date()

    forecasts = []
    sydney_area = root.find(".//area[@aac='NSW_PT131']")  # Sydney (location)
    if sydney_area is None:
        print("Sydney area not found in XML")
        return forecasts

    for period in sydney_area.findall("forecast-period"):
        start_time = period.attrib.get("start-time-local")
        end_time = period.attrib.get("end-time-local")
        if not start_time or not end_time:
            continue

        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)

        # Only include forecast periods for today that are not in the past
        if end_dt <= now or start_dt.date() != today:
            continue

        condition = None
        min_temp = None
        max_temp = None
        rain_chance = None

        for text in period.findall("text"):
            if text.attrib.get("type") == "precis":
                condition = text.text
            elif text.attrib.get("type") == "probability_of_precipitation":
                rain_chance = text.text

        for element in period.findall("element"):
            if element.attrib.get("type") == "air_temperature_minimum":
                min_temp = element.text
            elif element.attrib.get("type") == "air_temperature_maximum":
                max_temp = element.text

        forecasts.append({
            "start_time": start_time,
            "end_time": end_time,
            "condition": condition,
            "min_temp": min_temp,
            "max_temp": max_temp,
            "rain_chance": rain_chance
        })

    return forecasts