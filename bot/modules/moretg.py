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

import asyncio
import functools
import pyrogram

def patch(obj):
    def is_patchable(item):
        return getattr(item[1], 'patchable', False)

    def wrapper(container):
        for name,func in filter(is_patchable, container.__dict__.items()):
            old = getattr(obj, name, None)
            setattr(obj, 'old'+name, old)
            setattr(obj, name, func)
        return container
    return wrapper

def patchable(func):
    func.patchable = True
    return func

loop = asyncio.get_event_loop()


class ListenerCanceled(Exception):
    pass


pyrogram.errors.ListenerCanceled = ListenerCanceled

@patch(pyrogram.client.Client)
class Client():
    @patchable
    def __init__(self, *args, **kwargs):
        self.listening = {}
        self.using_mod = True

        self.old__init__(*args, **kwargs)

    @patchable
    async def listen(self, chat_id, filters=None, timeout=None):
        if type(chat_id) != int:
            chat = await self.get_chat(chat_id)
            chat_id = chat.id

        future = loop.create_future()
        future.add_done_callback(
            functools.partial(self.clear_listener, chat_id)
        )
        self.listening.update({
            chat_id: {"future": future, "filters": filters}
        })
        return await asyncio.wait_for(future, timeout)

    @patchable
    async def ask(self, chat_id, text, filters=None, timeout=None, *args, **kwargs):
        request = await self.send_message(chat_id, text, *args, **kwargs)
        response = await self.listen(chat_id, filters, timeout)
        response.request = request
        return response

    @patchable
    async def none(self, chat_id, filters=None, timeout=None, *args, **kwargs):

        response = await self.listen(chat_id, filters, timeout)

        return response

    @patchable
    def clear_listener(self, chat_id, future):
        if future == self.listening[chat_id]:
            self.listening.pop(chat_id, None)

    @patchable
    def cancel_listener(self, chat_id):
        listener = self.listening.get(chat_id)
        if not listener or listener['future'].done():
            return

        listener['future'].set_exception(ListenerCanceled())
        self.clear_listener(chat_id, listener['future'])


async def start_down_telegram_file(client, message,file_list):
    try:
        if len(file_list)==0:
            answer = await client.ask(chat_id=message.chat.id, text='请发送TG文件,或输入 /cancel 取消')
            #answer = await client.none(chat_id=message.chat.id)
        else:
            answer = await client.ask(chat_id=message.chat.id, text=f'已接收{len(file_list)}个文件，请继续发送TG文件，输入 /finish 结束,或输入 /cancel 取消')


        info = answer



        if info.media_group_id !=None:
            media=await client.get_media_group(chat_id=info.chat.id,message_id=info.message_id)
            print(media)
            for a in media:
                if not a.media:
                    await client.send_message(text="发送的不是文件", chat_id=message.chat.id, parse_mode='markdown')
                    await start_down_telegram_file(client, message, file_list)
                    return file_list
                else:
                    file_list.append(a)
            file_list = await start_down_telegram_file(client, message, file_list)
            return file_list



        elif info.text == "/cancel":
            await client.send_message(text="取消发送", chat_id=message.chat.id, parse_mode='markdown')

            return []
        elif info.text == "/finish":
            await client.send_message(text=f"接收文件完成,共有{len(file_list)}个文件", chat_id=message.chat.id, parse_mode='markdown')
            return file_list
        elif not info.media:
            await client.send_message(text="发送的不是文件", chat_id=message.chat.id, parse_mode='markdown')
            file_list = await start_down_telegram_file(client, message,file_list)
            return file_list

        else:
            try:
                file_list.append(info)

                temp_num = int(info.message_id)+1
                while True:
                    try:
                        temp_info = await client.get_messages(chat_id=message.chat.id,message_ids=temp_num)
                    except:
                        break
                    if not temp_info.media:
                        break
                    else:
                        file_list.append(temp_info)
                        temp_num = temp_num + 1

                temp_file= await start_down_telegram_file(client, message,file_list)
                file_list=temp_file
                return file_list

            except Exception as e:
                print(f"标记1 {e}")
                sys.stdout.flush()
                await client.send_message(text="下载文件失败", chat_id=message.chat.id, parse_mode='markdown')
                return file_list
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


async def tgfile_download(client, message, file_list):

    for new_message in file_list:
        if new_message.document != None:
            file_name = new_message.document.file_name
        elif new_message.video != None:

            file_name = new_message.video.file_name
        info = await client.send_message(text="开始下载", chat_id=message.chat.id, parse_mode='markdown')

        file = await client.download_media(message=new_message, progress=progress, progress_args=(client, info, file_name,))

        try:
            print("开始上传")
            file_dir = file
            files_num = 1
            t1 = threading.Thread(target=run_rclone, args=(file_dir, file_name, info, files_num, client, message,0),)
            t1.start()

            #os.remove(path=file)
            continue

        except Exception as e:
            print(e)
            print("Upload Issue!")
            return





# now in your sync code you should be able to use:

# commands=['downtgfile']
async def get_telegram_file(client, message):
    try:

        temp = await start_down_telegram_file(client,message,[])
        print(temp)
        print(type(temp))
        sys.stdout.flush()

        if len(temp)==0:
            return
        else:
            await tgfile_download(client, message, temp)

            return
    except Exception as e:
        print(f"start_down_telegram_file {e}")
        await client.send_message(text=f"下载文件失败:{e}", chat_id=message.chat.id, parse_mode='markdown')

        sys.stdout.flush()


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
