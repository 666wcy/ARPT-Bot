# -*- coding: utf-8 -*-
import aria2p
from pyromod import listen
from pyrogram import Client
import base64
import os
import json


Aria2_host="http://127.0.0.1"
Aria2_port="8080"
Aria2_secret=os.environ.get('Aria2_secret')

try:
    App_title=os.environ.get('Title')
    if App_title ==None:
        App_title=""
except:
    App_title=""

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
if App_title!="":
    ari2_ng_url=f"https://{App_title}.herokuapp.com/ng/#!/settings/rpc/set/https/{App_title}.herokuapp.com/443/jsonrpc/{base64_message}"

    client.send_message(chat_id=int(Telegram_user_id), text=f"Bot上线！！！\nAria2NG快捷面板：{ari2_ng_url}")
Bot_info=client.get_me()

BOT_name=Bot_info.username
client.stop()

