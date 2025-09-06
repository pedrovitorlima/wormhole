import paho.mqtt.client as mqtt
import time
import os
from dotenv import load_dotenv
import fetch_weather
import json

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
WEATHER_TOPIC = os.getenv("PUBLISH_TOPIC", "wormhole/weather")
LISTEN_TOPIC = os.getenv("LISTEN_TOPIC", "palantir/command")
API_URL = os.getenv("API_URL", "http://www.bom.gov.au/nsw/forecasts/sydney.shtml")
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "username")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "password")

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    action = payload.get("action")

    if action == "update_weather":
        weather_data = fetch_weather()
        client.publish(WEATHER_TOPIC, weather_data)

def main():
    print(f'Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT} with username {MQTT_USERNAME}')
    client = mqtt.Client()
    client.on_message = on_message
    client.username_pw_set("username", "password")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    client.subscribe(LISTEN_TOPIC)
    client.subscribe(LISTEN_TOPIC)

    try:
        while True:
            data = fetch_weather()
            client.publish(WEATHER_TOPIC, data)
            for _ in range(600):  # 600 x 1s = 10 minutes
                time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()