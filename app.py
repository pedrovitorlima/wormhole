import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import asyncio
from gmqtt import Client as MQTTClient
import psycopg2
import json
from psycopg2.extras import RealDictCursor

load_dotenv()

MQTT_BROKER = os.getenv("BROKER_NAME")
MQTT_PORT = 1883
MQTT_TOPIC = "prod/sensor_wormhole"
MQTT_USER = os.getenv("BROKER_USER")
MQTT_PASSWORD = os.getenv("BROKER_PASSWORD")
DATABASE_URL = os.getenv("DATABASE_URL")

def save_to_db(device, sensor, reading, date):
  try:
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    with conn.cursor() as cursor:
      query = """
          INSERT INTO reading (device, sensor, reading, date) 
          VALUES (%s, %s, %s, %s);
      """
      cursor.execute(query, (device, sensor, reading, date))
    conn.commit()
    conn.close()
  except Exception as e:
    print(f"Error saving to DB: {e}")

# Define an asynchronous MQTT client
class MyMQTTClient:

  def __init__(self, client_id):
    self.client = MQTTClient(client_id)
    self.client.set_auth_credentials(MQTT_USER, MQTT_PASSWORD)
    self.client.on_connect = self.on_connect
    self.client.on_message = self.on_message
    self.client.on_disconnect = self.on_disconnect
    self.client.on_subscribe = self.on_subscribe

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
      # Parse payload as JSON
      message = json.loads(payload.decode())
      device = message.get("device")
      sensor = message.get("sensor")
      reading = message.get("reading")
      date = message.get("date")
      if device and sensor and reading and date:
        save_to_db(device, sensor, reading, date)
      else:
        print("Invalid message format")
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

# Async entry point
async def main():
  mqtt_client = MyMQTTClient(client_id='wormhole-consumer')
  await mqtt_client.start()

if __name__ == '__main__':
  asyncio.run(main())