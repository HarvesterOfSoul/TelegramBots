from telethon import TelegramClient, sync
from datetime import datetime, timedelta, timezone
import asyncio, logging, random

#logging.basicConfig(level=logging.DEBUG)

client = TelegramClient(api_id=,
                        api_hash='',
                        connection_retries=1000,
                        session='').start()

ChatWars_Channel = client.get_entity('@chtwrsbot')
Control_Channel_URL = 'https://t.me/joinchat/'

async def schedule_arena(days=1):
    for day_count in range(1,days+1):
        current_time = datetime.now().replace(second=0, microsecond=0)
        target_time = current_time.replace(hour=4, minute=random.randint(0,59)).astimezone(timezone.utc)
        delta_t = target_time + timedelta(days=day_count)
        await client.send_message(Control_Channel_URL, message="/arena", schedule=delta_t)
        print("Scheduled /arena for {} UTC".format(delta_t))



async def schedule_valley(days=1):
    for day_count in range(1,days+1):
        current_time = datetime.now().replace(second=0, microsecond=0)
        target_time1 = current_time.replace(hour=6, minute=random.randint(0,59)).astimezone(timezone.utc)
        delta_t1 = target_time1 + timedelta(days=day_count)
        target_time2 = current_time.replace(hour=14, minute=random.randint(0,59)).astimezone(timezone.utc)
        delta_t2 = target_time2 + timedelta(days=day_count)
        target_time3 = current_time.replace(hour=21, minute=random.randint(0,59)).astimezone(timezone.utc)
        delta_t3 = target_time3 + timedelta(days=day_count)

        await client.send_message(Control_Channel_URL, message="/valley", schedule=delta_t1)
        await client.send_message(Control_Channel_URL, message="/valley", schedule=delta_t2)
        await client.send_message(Control_Channel_URL, message="/valley", schedule=delta_t3)
        print("Scheduled /valley for {} UTC".format(delta_t1))
        print("Scheduled /valley for {} UTC".format(delta_t2))
        print("Scheduled /valley for {} UTC".format(delta_t3))

async def schedule_all(days=1):

    await schedule_arena(days=days)
    await schedule_valley(days=days)

# run
print("started")
asyncio.get_event_loop().run_until_complete(schedule_all(days=30))
