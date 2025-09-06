import paho.mqtt.client as mqtt
import time
import os
from dotenv import load_dotenv
from fetch_weather import fetch_weather
import json

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
WEATHER_TOPIC = os.getenv("PUBLISH_TOPIC", "wormhole/weather")
LISTEN_TOPIC = os.getenv("LISTEN_TOPIC", "palantir/command")
API_URL = os.getenv("API_URL", "http://www.bom.gov.au/nsw/forecasts/sydney.shtml")
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "username")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "password")

def on_message(client, userdata, message, properties=None):
    try:
        payload = json.loads(message.payload.decode().strip())
        action = payload.get("action")  # will fail if payload isn't a dict
        
        if action == "update_weather":
            weather_data = fetch_weather(API_URL)
        client.publish(WEATHER_TOPIC, json.dumps(weather_data))
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Failed to parse payload: {message.payload.decode().strip()} ({e})")
        return
        
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe("$SYS/#")

def main():
    print(f'Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT} with username {MQTT_USERNAME}')
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.on_connect = on_connect
    
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    client.subscribe(LISTEN_TOPIC)

    try:
        while True:
            data = fetch_weather(API_URL)
            client.publish(WEATHER_TOPIC, json.dumps(data))
            for _ in range(600):  # 600 x 1s = 10 minutes
                time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()