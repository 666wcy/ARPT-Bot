import asyncio
import subprocess
import os
import sys
import nest_asyncio
import threading
import time
import re
from modules.control import run_rclone
from config import aria2, BOT_name
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

nest_asyncio.apply()
os.system("df -lh")


async def start_down_telegram_file(client, message):
    try:
        answer = await client.ask(chat_id=message.chat.id, text='请发送TG文件,或输入 /cancel 取消')

        info = answer
        print(info)
        sys.stdout.flush()
        if info.text == "/cancel":
            await client.send_message(text="取消发送", chat_id=message.chat.id, parse_mode='markdown')
            return "False"
        elif info.document == None and info.video == None:
            await client.send_message(text="发送的不是文件", chat_id=message.chat.id, parse_mode='markdown')
            return "False"

        else:
            try:
                return info

            except Exception as e:
                print(f"标记1 {e}")
                sys.stdout.flush()
                await client.send_message(text="下载文件失败", chat_id=message.chat.id, parse_mode='markdown')
                return "False"
    except Exception as e:
        print(f"start_down_telegram_file {e}")
        sys.stdout.flush()


def progress(current, total, client, message, name):
    print(f"{current * 100 / total:.1f}%")
    pro = f"{current * 100 / total:.1f}%"
    try:
        client.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"{name}\n下载中:{pro}")
    except:
        None


def tgfile_download(client, message, new_message):
    if new_message.document != None:
        file_name = new_message.document.file_name
    elif new_message.video != None:

        file_name = new_message.video.file_name
    info = client.send_message(text="开始下载", chat_id=message.chat.id, parse_mode='markdown')

    file = client.download_media(message=new_message, progress=progress, progress_args=(client, info, file_name,))

    try:
        print("开始上传")
        file_dir = file
        files_num = 1
        run_rclone(file_dir, file_name, info=info, file_num=files_num, client=client, message=message)
        os.remove(path=file)
        return

    except Exception as e:
        print(e)
        print("Upload Issue!")
        return


def get_msg(client, message):
    return asyncio.run(start_down_telegram_file(client, message))


# now in your sync code you should be able to use:

# commands=['downtgfile']
def get_telegram_file(client, message):
    '''loop = asyncio.get_event_loop()
    temp = loop.run_until_complete(start_down_telegram_file(client, message))'''
    temp = get_msg(client, message)
    sys.stdout.flush()
    if temp == "False":
        return
    else:

        t1 = threading.Thread(target=tgfile_download, args=(client, message, temp))
        t1.start()
        return


async def get_file_id(client, message):
    try:
        answer = await client.ask(chat_id=message.chat.id, text='请发送TG文件,或输入 /cancel 取消')

        info = answer
        print(info)
        sys.stdout.flush()
        if info.text == "/cancel":
            await client.send_message(text="取消发送", chat_id=message.chat.id, parse_mode='markdown')
            return
        elif info.document == None:
            await client.send_message(text="发送的不是文件", chat_id=message.chat.id, parse_mode='markdown')
            return

        else:
            try:
                print(answer)
                await client.send_message(text=f"获取ID文件成功\nFileid:{answer.document.file_id}", chat_id=message.chat.id,
                                          parse_mode='markdown')
                return

            except Exception as e:
                print(f"标记2 {e}")
                sys.stdout.flush()
                await client.send_message(text="获取ID文件失败", chat_id=message.chat.id, parse_mode='markdown')
                return
    except Exception as e:
        print(f"start_down_telegram_file {e}")
        sys.stdout.flush()


async def sendfile_by_id(client, message):
    try:
        file = message.text.split()[1]
        print(f"sendfile_by_id {file} ")
        sys.stdout.flush()
        await client.send_document(chat_id=message.chat.id, document=file)
        return



    except Exception as e:
        print(f"sendfile_by_id :{e}")
        await client.send_message(text=f"文件发送失败\n{e}", chat_id=message.chat.id, parse_mode='markdown')

        sys.stdout.flush()
        return
