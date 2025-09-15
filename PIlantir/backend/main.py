import paho.mqtt.client as mqtt
import time
import os
from dotenv import load_dotenv
from fetch_weather import fetch_weather
from typing import Optional, Any
import json

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

WEATHER_TOPIC = os.getenv("PUBLISH_TOPIC")
DISHWASHER_TOPIC = os.getenv("DISHWASHER_TOPIC")
LISTEN_TOPIC = os.getenv("LISTEN_TOPIC")

def on_message(client: mqtt.Client, _: Any, message: mqtt.MQTTMessage, __: Optional[Any] = None) -> None:
    try:
        payload = json.loads(message.payload.decode().strip())
        print(f"Processing message {payload}")
        action = payload.get("command")  # will fail if payload isn't a dict
        
        print(f"Received message on topic {message.topic} with action: {action}")
        if action == "load_all":
            weather_data = fetch_weather()
            client.publish(WEATHER_TOPIC, json.dumps(weather_data))
            client.publish(DISHWASHER_TOPIC, json.dumps({"next": "woman"}))

        if action == "update_weather":
            weather_data = fetch_weather()
            client.publish(WEATHER_TOPIC, json.dumps(weather_data))
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Failed to parse payload: {message.payload.decode().strip()} ({e})")
        return
        
def on_connect(_: mqtt.Client, __: Any, ___: dict[str, int], reason_code: int, ____: Optional[Any] = None) -> None:
    print(f"Connected with result code {reason_code}")

def main() -> None:
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
            data = fetch_weather()
            client.publish(WEATHER_TOPIC, json.dumps(data))
            minutes = 5
            for _ in range(60 * minutes):  
                time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()