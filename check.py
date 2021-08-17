#!/usr/local/bin/python3
# coding: utf-8

__author__ = "Benny <benny.think@gmail.com>"

import logging
import os
import random
import time

import redis
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from pyrogram import Client, filters

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s(%(lineno)d) [%(levelname)s]: %(message)s')
logging.getLogger('apscheduler.executors.default').propagate = False
# logging.getLogger('pyrogram.client').propagate = False
# logging.getLogger('pyrogram.connection').propagate = False
# logging.getLogger('pyrogram.session').propagate = False

r = redis.StrictRedis(decode_responses=True)
api_id = os.getenv("API_ID", "111")
api_hash = os.getenv("API_HASH", "4567uhj")
alert_bot_token = os.getenv("TOKEN", "149Uaj9is")
MAX_MISS = 5
app = Client("check", api_id, api_hash)

website_list = [
    {"url": "https://yyets.dmesg.app/", "status_code": 200},
    {"url": "https://yyets.dmesg.app/api/top", "status_code": 200},
]

# bot name
bot_list = [
    "yyets_bot",
    "wp_tgbot",
    "tele_tweetbot",
    "benny_ytdlbot",
    "my_gakki_bot",
    "netease_ncm_bot",
    "wayback_machine_bot",
    "wayback_machine_bot",
    "benny_shudongbot",
    "KeepMeRunBot",
    "msg_shredder_bot",
    "restartme_bot",
]


def bot_send_start():
    for name in bot_list:
        time.sleep(random.random())
        app.send_message(name, "/start")
        r.incr(name, 1)
    bot_check()


@app.on_message(filters.bot)
def my_handler(client, message):
    name = message.chat.username
    if message:
        logging.info("%s is responding...", name)
        if int(r.get(name)) > 0:
            r.decr(name, 1)


def bot_check():
    time.sleep(5)
    for name in bot_list:
        if int(r.get(name)) >= MAX_MISS:
            err = "%s errors for %s" % (MAX_MISS, name)
            logging.error(err)
            send_alert(err)


def send_alert(message: str):
    api = f"https://api.telegram.org/bot{alert_bot_token}/sendMessage?chat_id=260260121&text={message}"
    resp = requests.get(api).json()
    logging.info(resp)


def website_check():
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
            send_alert(message)
            logging.error(message)
        else:
            logging.info("%s OK: %s bytes.", url, len(resp.content))


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(website_check, 'interval', seconds=60)
    scheduler.add_job(bot_send_start, 'interval', seconds=120)
    scheduler.start()
    app.run()
