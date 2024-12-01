import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os

# load_dotenv()

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "prod/sensor_wormhole"
MQTT_USER = "iluvatar"
MQTT_PASSWORD = os.getenv("MQTT_BROKER_PASSWORD")

print(f'setting user {MQTT_USER} and pass {MQTT_PASSWORD} and opa {os.getenv("ANYTHING")}')
print(f'connecting with ${MQTT_BROKER} broker')

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.username_pw_set(MQTT_USER, MQTT_PASSWORD)
mqttc.connect(MQTT_BROKER, MQTT_PORT, 60)
mqttc.publish(MQTT_TOPIC, "how's going")
print('message is sent')
mqttc.loop_forever()
