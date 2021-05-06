#!/usr/local/bin/python3
# coding: utf-8

__author__ = "Benny <benny.think@gmail.com>"

import asyncio
import logging

import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import TelegramClient, events

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s(%(lineno)d) [%(levelname)s]: %(message)s')
logging.getLogger('apscheduler.executors.default').propagate = False

api_id = 111
api_hash = "19111e9"
bot_token = "37011I"

client = TelegramClient('client-hc', api_id, api_hash,
                        device_model="Benny-health-check", system_version="89", app_version="1.0.0")

website_list = [
    {"url": "https://yyets.dmesg.app/", "status_code": 200},
    {"url": "https://yyets.dmesg.app/api/top", "status_code": 200},
]

# bot name
bot_list = [
    {"bot_name": "yyets_bot", "pattern": "(?i).*欢迎使用，直接发送想要的剧集标题给我就可以了.*"},
    {"bot_name": "benny_ytdlbot", "pattern": "(?i).*Wrapper for youtube-dl.*"},
]

check_status = {}  # bot_name, status

for item in bot_list:
    pattern = item["pattern"]
    bot_name = item["bot_name"]


    @client.on(events.NewMessage(incoming=True, pattern=pattern, from_users=bot_name))
    async def my_event_handler(event):
        entity = await client.get_entity(event.input_chat)
        logging.info("%s is working.", entity.username)
        check_status[entity.username] = ""


async def send_health_check():
    # send /start command to everyone in bot list
    for name, value in check_status.items():
        if value:
            await bot_warning(name)

    for item in bot_list:
        bot_name = item["bot_name"]
        await client.send_message(bot_name, '/start')
        check_status[bot_name] = "check"
        await asyncio.sleep(1)


async def bot_warning(name):
    logging.warning("%s seems to be down.", name)
    message = "%s is down!!!" % name
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id=260260121&text={message}"
    requests.get(url)


async def website_check():
    for item in website_list:
        url = item["url"]
        resp = None
        message = ""
        try:
            resp = requests.get(url)
        except Exception as e:
            message = f"{url} request error: \n{e}\n"

        if getattr(resp, "status_code", 0) != 200:
            content = getattr(resp, "content", None)
            message += f"{url} content error: \n{content}\n"

        if message:
            api = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id=260260121&text={message}"
            requests.get(api).json()
            logging.error(message)
        else:
            logging.info("%s OK: %s bytes.", url, len(resp.content))


if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_health_check, 'interval', seconds=300)
    scheduler.add_job(website_check, 'interval', seconds=60)
    scheduler.start()
    client.start()
    client.run_until_disconnected()
