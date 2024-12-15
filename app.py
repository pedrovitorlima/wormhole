from dotenv import load_dotenv
import os
import asyncio
import psycopg2
import datetime
from psycopg2.extras import RealDictCursor

from reader import Receiver

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def save_to_db(message):
  try:
    # Parse payload as JSON
    device = message.get("device")
    sensor = message.get("sensor")
    reading = message.get("reading")
    date = message.get("date") or datetime.datetime.now()

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

async def main():
  receiver = Receiver(handle_message=save_to_db)
  await receiver.start()

if __name__ == '__main__':
  asyncio.run(main())