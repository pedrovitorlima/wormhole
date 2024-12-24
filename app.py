from dotenv import load_dotenv
import os
import asyncio
import psycopg2
from psycopg2.extras import RealDictCursor
from pytz import timezone
import datetime

import logging

from reader import Receiver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def save_to_db(message):
  logger.info('Saving ' + message + ' to the database')
  try:
    
    # Parse payload as JSON
    device = message.get("device")
    sensor = message.get("sensor")
    reading = message.get("reading")
    date = message.get("date")
    
    if not date:
      tz = timezone("Australia/Sydney")
      date = datetime.datetime.now(datetime.timezone.utc).astimezone(tz)

    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    with conn.cursor() as cursor:
      query = """
          INSERT INTO reading (device, sensor, reading, date) 
          VALUES (%s, %s, %s, %s);
      """
      cursor.execute(query, (device, sensor, reading, date))
    conn.commit()
    conn.close()
    logger.info('Message saved')
  except Exception as e:
    logging.error('Error whilst saving to the database: ' + e)
    print(f"Error saving to DB: {e}")

async def main():
  receiver = Receiver(handle_message=save_to_db)
  await receiver.start()

if __name__ == '__main__':
  asyncio.run(main())