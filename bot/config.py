# -*- coding: utf-8 -*-
import aria2p
from pyromod import listen
from pyrogram import Client
import base64
import os
import requests
import json


Aria2_host="http://127.0.0.1"
Aria2_port="8080"
Aria2_secret=os.environ.get('Aria2_secret')

def change_password():


    login_url = "http://127.0.0.1:9184/api/login"

    login_data = {"username": "admin", "password": "admin", "recaptcha": ""}

    html = requests.post(url=login_url, json=login_data)
    if html.status_code!=200:
        print(f"登录失败：{html.text}")
        return

    change_url = "http://127.0.0.1:9184/api/users/1"

    print(html.text)
    headers = {}
    headers['Cookie'] = f"auth={html.text}"

    zh_data = {
        "data": {
            "hideDotfiles": False,
            "id": 1,
            "locale": "zh-cn",
            "singleClick": False
        },
        "what": "user",
        "which": [
            "locale",
            "hideDotfiles",
            "singleClick"
        ]
    }

    change_result = requests.put(url=change_url, json=zh_data, headers=headers)
    
    if change_result.status_code==403:
        headers['X-Auth']=html.text
        change_result = requests.put(url=change_url, json=zh_data, headers=headers)

    print(change_result.text)

    change_data = {"data": {"id": 1, "password": str(Aria2_secret)}, "what": "user", "which": ["password"]}

    change_result = requests.put(url=change_url, json=change_data, headers=headers)

    if change_result.status_code == 403:
        headers['X-Auth'] = html.text
        change_result = requests.put(url=change_url, json=change_data, headers=headers)

    print(change_result.text)

change_password()

try:
    App_title=os.environ.get('Title')
    if App_title ==None:
        App_title=""
except:
    App_title=""

try:
    if os.environ.get('Rclone_share')=="True":
        Rclone_share=True
    else:
        Rclone_share=False
except:
    Rclone_share=False

print(f"是否rclone_share:{Rclone_share}")

try:
    Error_user_info=os.environ.get('Error_user_info')
    if Error_user_info ==None:
        Error_user_info="未在使用白名单"
except:
    Error_user_info="未在使用白名单"

Telegram_bot_api=os.environ.get('Telegram_bot_api')
Telegram_user_id=os.environ.get('Telegram_user_id')
Api_hash=os.environ.get('Api_hash')
Api_id=os.environ.get('Api_id')


aria2 = aria2p.API(
    aria2p.Client(
        host=Aria2_host,
        port=int(Aria2_port),
        secret=Aria2_secret
    )
)


client = Client("my_bot", bot_token=Telegram_bot_api,
             api_hash=Api_hash, api_id=Api_id

             )

client.start()

message = str(Aria2_secret)
message_bytes = message.encode('ascii')
base64_bytes = base64.b64encode(message_bytes)
base64_message = base64_bytes.decode('ascii')
if App_title!="" and "-" not in str(Telegram_user_id):
    ari2_ng_url=f"https://{App_title}.herokuapp.com/ng/#!/settings/rpc/set/https/{App_title}.herokuapp.com/443/jsonrpc/{base64_message}"

    client.send_message(chat_id=int(Telegram_user_id), text=f"Bot上线！！！\nAria2NG快捷面板：{ari2_ng_url}")

Bot_info=client.get_me()

BOT_name=Bot_info.username
client.stop()

