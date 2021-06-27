
from config import aria2
from modules.picacg import add_download,add_downloadtg
from modules.video import Download_video
from modules.pixiv import start_download_pixiv,  start_download_pixivtg, start_download_pixivphoto, \
    start_download_pixivtele
from modules.netease import http_downloadsong
import sys
import requests
import time
import os


def file_del(gid):
    print("开始删除")
    try:
        dele = aria2.get_download(gid=str(gid))
        torrent_name=dele.name
        del_result=dele.remove(force=True, files=True)
        if del_result==True:
            print(f"{torrent_name}\n删除成功")
            return f"删除成功"
        else:
            print(f"{torrent_name}\n删除失败")
            return f"删除失败"
    except Exception as e:
        print (e)
        return f"\n删除失败：{e}"

def file_resume(gid):
    print("开始任务")
    try:
        the_resume = aria2.get_download(gid=str(gid))
        torrent_name=the_resume.name
        resume_result=the_resume.resume()
        if resume_result==True:
            print(f"{torrent_name}\n开始成功")
            return f"开始成功"
        else:
            print(f"{torrent_name}\n开始失败")
            return f"开始失败"
    except Exception as e:
        print (e)
        return f"\n开始失败：{e}"

def file_pause(gid):
    print("暂停任务")
    try:
        the_pause = aria2.get_download(gid=str(gid))
        torrent_name=the_pause.name
        resume_result=the_pause.pause()
        if resume_result==True:
            print(f"{torrent_name}\n暂停成功")
            return f"暂停成功"
        else:
            print(f"{torrent_name}\n暂停失败")
            return f"暂停失败"
    except Exception as e:
        print (e)
        return f"\n暂停失败：{e}"

def start_remove(client, message):
    the_gid = str(message.data).replace("Remove ", "")
    info_text = file_del(gid=the_gid)
    client.answer_callback_query(callback_query_id=message.id, text=info_text, cache_time=3)

def start_Resume(client, message):
    the_gid = str(message.data).replace("Resume ", "")
    info_text = file_resume(gid=the_gid)
    client.answer_callback_query(callback_query_id=message.id, text=info_text, cache_time=3)

def start_pause(client, message):
    the_gid = str(message.data).replace("Pause ", "")
    info_text = file_pause(gid=the_gid)
    client.answer_callback_query(callback_query_id=message.id, text=info_text, cache_time=3)

def start_benzi_down(client, message):
    if "down" == message.data:

        client.answer_callback_query(callback_query_id=message.id, text="开始下载", cache_time=3)

        add_download(client=client, call=message)

    elif "tgdown" == message.data:

        client.answer_callback_query(callback_query_id=message.id, text="开始下载", cache_time=3)

        add_downloadtg(client=client, call=message)

async def start_get_author_info(client, message):
    if "pixivusertg" in message.data :

        await client.answer_callback_query(callback_query_id=message.id, text="开始下载", cache_time=3)

        await start_download_pixivtg(client=client, call=message)

    elif "pixivuserphoto" in message.data:

        await client.answer_callback_query(callback_query_id=message.id, text="开始下载", cache_time=3)

        await start_download_pixivphoto(client=client, call=message)
    elif "pixivusertele" in message.data:

        await client.answer_callback_query(callback_query_id=message.id, text="开始下载", cache_time=3)

        await start_download_pixivtele(client=client, call=message)
    else:

        await client.answer_callback_query(callback_query_id=message.id, text="开始下载", cache_time=3)

        await start_download_pixiv(client=client, call=message)



def get_song_url_info(client, call):

    try:
        client.answer_callback_query(callback_query_id=call.id, text="开始获取歌曲信息", cache_time=3)
        message_id = call.message.message_id
        message_chat_id = call.message.chat.id
        song_id = call.data.split()[1]
        t = time.time()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 5.8; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
            "cookie": "__remember_me=true; MUSIC_U=f5798cb7775288f521fdcc5e3ce3df53b94446c1f5306aea19f4b0354b15433833a649814e309366; __csrf=b23ac1873ea3b243dbd6412b488600b1; NMTID=00O-ApuqR6H-n1NEEJFpS0RgQBBbVwAAAF6OLF0aw"
            }
        song_info_url = f"https://benchaonetease.vercel.app/song/url?id={song_id}&br=999000&timestamp={str(int(round(t * 1000)))}"
        song_info = requests.get(url=song_info_url,headers=headers)
        try:
            if song_info.json()['data'][0]['url']==None:

                client.edit_message_text(text="此歌曲不支持获取歌曲链接", chat_id=message_chat_id,
                                                   message_id=message_id,
                                                   parse_mode='markdown')
                return
            url = song_info.json()['data'][0]['url']
        except Exception as e:
            client.edit_message_text(text=f"无法获取刚获取歌曲链接:\n`{e}`", chat_id=message_chat_id,
                                           message_id=message_id,
                                           parse_mode='markdown')
            return

        song_name_info_url=f"https://benchaonetease.vercel.app/song/detail?ids={song_id}"
        song_name_info=requests.get(url=song_name_info_url)
        song_name=f"{song_name_info.json()['songs'][0]['name']}.{str(song_info.json()['data'][0]['type']).lower()}"

        img_url=song_name_info.json()['songs'][0]['al']['picUrl']
        img = requests.get(url=img_url)
        img_name = f"{message_chat_id}{message_id}.png"
        with open(img_name, 'wb') as f:
            f.write(img.content)
            f.close()
        picPath = img_name


        info = client.send_message(chat_id=call.message.chat.id, text=f"{song_name}开始下载", parse_mode='markdown')
        http_downloadsong(client=client,message=info,url=url,file_name=song_name,picpath=picPath,towhere=call.data)
        os.remove(picPath)
        return
    except Exception as e:
        print(f"get_song_url_info error {e}")
        client.edit_message_text(text=f"get_song_url_info error {e}`", chat_id=message_chat_id,
                                 message_id=message_id,
                                 parse_mode='markdown')
        return





def start_download_video(client, message):
    down=Download_video(client, message)
    down.download_video()

