import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import asyncio
from gmqtt import Client as MQTTClient
import json

load_dotenv()

MQTT_BROKER = os.getenv("BROKER_NAME")
MQTT_PORT = 1883
MQTT_TOPIC = "prod/sensor_wormhole"
MQTT_USER = os.getenv("BROKER_USER")
MQTT_PASSWORD = os.getenv("BROKER_PASSWORD")
MQTT_CONSUMER_NAME = os.getenv("CONSUMER_NAME")

# Define an asynchronous MQTT client
class Receiver:

  def __init__(self, handle_message = None):
    self.client = MQTTClient(MQTT_CONSUMER_NAME)
    self.client.set_auth_credentials(MQTT_USER, MQTT_PASSWORD)
    self.client.on_connect = self.on_connect
    self.client.on_message = self.on_message
    self.client.on_disconnect = self.on_disconnect
    self.client.on_subscribe = self.on_subscribe
    self.handle_message = handle_message

  async def connect(self):
    # Connect to the MQTT broker
    print('trying to connect')
    await self.client.connect(MQTT_BROKER, MQTT_PORT)
    print ('connected')

  async def subscribe(self, topic):
    # Subscribe to the topic
    self.client.subscribe(topic)

  def on_connect(self, client, flags, rc, properties):
    print(f'Connected with result code {rc}')

  def on_message(self, client, topic, payload, qos, properties):
    print(f'Received message on {topic}: {payload.decode()}')
    try:
      message = json.loads(payload.decode())

      if self.handle_message != None:
        self.handle_message(message)
      else:
        print(json.dumps(message))

    except Exception as e:
      print(f"Error processing message: {e}")


  def on_disconnect(self, client, packet, exc=None):
    print(f'Disconnected from MQTT Broker')

  def on_subscribe(self, client, mid, qos, properties):
    print(f'Subscribed to {MQTT_TOPIC}')

  async def start(self):
    await self.connect()
    await self.subscribe(MQTT_TOPIC)
    # Keep the connection alive
    await asyncio.Event().wait()
