import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os

load_dotenv()

MQTT_BROKER = os.getenv("BROKER_NAME")
MQTT_PORT = 1883
MQTT_TOPIC = "prod/sensor_wormhole"
MQTT_USER = os.getenv("BROKER_USER")
MQTT_PASSWORD = os.getenv("BROKER_PASSWORD")

print(f'setting user {MQTT_USER} and pass {MQTT_PASSWORD}')
print(f'connecting with {MQTT_BROKER} broker')

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.username_pw_set(MQTT_USER, MQTT_PASSWORD)

mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect(MQTT_BROKER, MQTT_PORT, 60)

# # Blocking call that processes network traffic, dispatches callbacks and
# # handles reconnecting.
# # Other loop*() functions are available that give a threaded interface and a
# # manual interface.
mqttc.loop_forever()