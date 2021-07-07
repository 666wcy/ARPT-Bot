# -*- coding: utf-8 -*-

from config import aria2, BOT_name
import sys
from pyrogram.types import InlineKeyboardMarkup,InlineKeyboardButton
import os
import time
import threading
import asyncio
import subprocess
import re
import urllib
import urllib.request
from pprint import pprint
from urllib import parse
import json
import requests

import nest_asyncio

nest_asyncio.apply()
os.system("df -lh")
task=[]

async def downloadFiles(client,info,originalPath, req, layers, start=1, num=-1, _id=0):
    header = {
        'sec-ch-ua-mobile': '?0',
        'upgrade-insecure-requests': '1',
        'dnt': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'service-worker-navigation-preload': 'true',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'iframe',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'

    }

    if req == None:
        req = requests.session()
    # print(header)
    reqf = req.get(originalPath, headers=header)
    if "-my" not in originalPath:
        isSharepoint = True
        print("sharepoint 链接")
    else:
        isSharepoint = False

    # f=open()
    if ',"FirstRow"' not in reqf.text:
        print("\t" * layers, "这个文件夹没有文件")
        return 0

    pat = re.search(
        'g_listData = {"wpq":"","Templates":{},"ListData":{ "Row" : ([\s\S]*?),"FirstRow"', reqf.text)
    jsonData = json.loads(pat.group(1))
    redirectURL = reqf.url
    redirectSplitURL = redirectURL.split("/")
    query = dict(urllib.parse.parse_qsl(
        urllib.parse.urlsplit(redirectURL).query))
    downloadURL = "/".join(redirectSplitURL[:-1]) + "/download.aspx?UniqueId="
    if isSharepoint:
        pat = re.search('templateUrl":"(.*?)"', reqf.text)

        downloadURL = pat.group(1)
        downloadURL = urllib.parse.urlparse(downloadURL)
        downloadURL = "{}://{}{}".format(downloadURL.scheme,
                                         downloadURL.netloc, downloadURL.path).split("/")
        downloadURL = "/".join(downloadURL[:-1]) + \
                      "/download.aspx?UniqueId="
        print(downloadURL)

    # print(reqf.headers)

    s2 = urllib.parse.urlparse(redirectURL)
    header["referer"] = redirectURL
    header["cookie"] = reqf.headers["set-cookie"]
    header["authority"] = s2.netloc

    headerStr = ""
    for key, value in header.items():
        # print(key+':'+str(value))
        headerStr += key + ':' + str(value) + "\n"

    fileCount = 0
    # print(headerStr)
    for i in jsonData:
        if i['FSObjType'] == "1":
            print("\t" * layers, "文件夹：",
                  i['FileLeafRef'], "\t独特ID：", i["UniqueId"], "正在进入")
            _query = query.copy()
            _query['id'] = os.path.join(
                _query['id'], i['FileLeafRef']).replace("\\", "/")
            if not isSharepoint:
                originalPath = "/".join(redirectSplitURL[:-1]) + \
                               "/onedrive.aspx?" + urllib.parse.urlencode(_query)
            else:
                originalPath = "/".join(redirectSplitURL[:-1]) + \
                               "/AllItems.aspx?" + urllib.parse.urlencode(_query)


            fileCount += await downloadFiles(client, info, originalPath, req, layers + 1, _id=fileCount, start=start,
                                             num=num)
        else:
            fileCount += 1
            if num == -1 or start <= fileCount + _id < start + num:
                print("\t" * layers, "文件 [%d]：%s\t独特ID：%s\t正在推送" %
                      (fileCount + _id, i['FileLeafRef'], i["UniqueId"]))
                cc = downloadURL + (i["UniqueId"][1:-1].lower())
                download_path = f"/root/Download{str(query['id']).split('Documents', 1)[1]}"
                dd = dict(out=i["FileLeafRef"], header=headerStr, dir=download_path)
                print(cc, dd)
                aria2Link = "http://localhost:8080/jsonrpc"
                aria2Secret = os.environ.get('Aria2_secret')
                jsonreq = json.dumps({'jsonrpc': '2.0', 'id': 'qwer',
                                      'method': 'aria2.addUri',
                                      "params": ["token:" + aria2Secret, [cc], dd]})

                c = requests.post(aria2Link, data=jsonreq)
                pprint(json.loads(c.text))
                text = f"推送下载：`{i['FileLeafRef']}`\n下载路径:`{download_path}`\n推送结果:`{c.text}`"
                try:
                    await client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                                   parse_mode='markdown')
                except Exception as e:
                    print(f"修改信息失败:{e}")
                time.sleep(0.5)
            else:
                print("\t" * layers, "文件 [%d]：%s\t独特ID：%s\t非目标文件" %
                      (fileCount + _id, i['FileLeafRef'], i["UniqueId"]))
    return fileCount

async def odshare_download(client, message):

    try:
        odshare_url=str(message.text).split(" ")[1]
        info = await client.send_message(chat_id=message.chat.id, text="开始抓取下载链接", parse_mode='markdown')
        await downloadFiles(client,info,odshare_url, None, 0,start=1, num=-1)
        await client.edit_message_text(text="推送至Aria2完成，可到AriaNG面板查看", chat_id=info.chat.id, message_id=info.message_id,
                                       parse_mode='markdown')
    except Exception as e:
        print(f"odshare error {e}")
        await client.send_message(chat_id=message.chat.id, text="抓取下载链接失败", parse_mode='markdown')

def check_upload(api, gid):

    time.sleep(15)
    global task
    print(f"检查上传 {task}")
    sys.stdout.flush()
    try:
        currdownload=api.get_download(gid)
    except:
        print("任务已删除，不需要上传")
        sys.stdout.flush()
        return
    dir=currdownload.dir
    key=1
    if len(task)!=0:
        for a in task:
            if a == dir:
                key=0
                print("该任务存在，不需要上传")
                sys.stdout.flush()
                task.remove(a)
    if key==1:
        if "[METADATA]"==currdownload.name:
            return
        Rclone_remote = os.environ.get('Remote')
        Upload = os.environ.get('Upload')
        file_dir = f"{currdownload.dir}/{currdownload.name}"
        file_num = int(len(currdownload.files))
        print(f"上传该任务:{file_dir}")
        sys.stdout.flush()
        name=currdownload.name
        shell=f"bash upload.sh \"{gid}\" \"{file_num}\" '{file_dir}' "

        print(shell)
        cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                               stdout=subprocess.PIPE, universal_newlines=True, shell=True, bufsize=1)

        while True:
            time.sleep(2)
            if subprocess.Popen.poll(cmd) == 0:  # 判断子进程是否结束
                print("上传结束")
                return

async def run_await_rclone(dir,title,info,file_num,client, message):
    global task
    task.append(dir)
    print(task)
    sys.stdout.flush()
    Rclone_remote=os.environ.get('Remote')
    Upload=os.environ.get('Upload')
    info = await client.send_message(chat_id=message.chat.id, text="开始上传", parse_mode='markdown')
    name=f"{str(info.message_id)}_{str(info.chat.id)}"
    if int(file_num)==1:
        shell=f"rclone copy \"{dir}\" \"{Rclone_remote}:{Upload}\"  -v --stats-one-line --stats=1s --log-file=\"{name}.log\" "
    else:
        shell=f"rclone copy \"{dir}\" \"{Rclone_remote}:{Upload}/{title}\"  -v --stats-one-line --stats=1s --log-file=\"{name}.log\" "
    print(shell)
    cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                           stdout=subprocess.PIPE, universal_newlines=True, shell=True, bufsize=1)
    # 实时输出
    temp_text=None
    while True:
        time.sleep(2)
        fname = f'{name}.log'
        with open(fname, 'r') as f:  #打开文件
            try:
                lines = f.readlines() #读取所有行

                for a in range(-1,-10,-1):
                    last_line = lines[a] #取最后一行
                    if last_line !="\n":
                        break


                if temp_text != last_line and "ETA" in last_line:
                    print(f"上传中\n{last_line} end")
                    sys.stdout.flush()
                    log_time, file_part, upload_Progress, upload_speed, part_time = re.findall("(.*?)INFO.*?(\d.*?),.*?(\d+%),.*?(\d.*?),.*?ETA(.*)", last_line, re.S)[0]

                    text=f"{title}\n" \
                         f"更新时间：`{log_time}`\n" \
                         f"上传部分：`{file_part}`\n" \
                         f"上传进度：`{upload_Progress}`\n" \
                         f"上传速度：`{upload_speed}`\n" \
                         f"剩余时间:`{part_time}`"
                    try:
                        print(f"修改信息 {text}")
                        sys.stdout.flush()
                        try:
                            await client.edit_message_text(text=text,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
                        except:
                            None
                    except Exception as e:
                        print(f"修改信息失败 {e}")
                        sys.stdout.flush()
                    temp_text = last_line
                f.close()

            except Exception as e:
                print(f"检查进度失败 {e}")
                sys.stdout.flush()
                f.close()
                continue

        if subprocess.Popen.poll(cmd) == 0:  # 判断子进程是否结束
            print("上传结束")
            try:
                client.send_message(text=f"{title}\n上传结束",chat_id=info.chat.id)
            except:
                None
            os.remove(f"{name}.log")
            task.remove(dir)
            return

    return


def the_download(client, message,url):

    try:
        download = aria2.add_magnet(url)
    except Exception as e:
        print(e)
        if (str(e).endswith("No URI to download.")):
            print("No link provided!")
            client.send_message(chat_id=message.chat.id,text="No link provided!",parse_mode='Markdown')
            return None
    prevmessagemag = None
    info=client.send_message(chat_id=message.chat.id,text="添加任务",parse_mode='markdown')

    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=f"Remove",
                callback_data=f"Remove {download.gid}"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    client.edit_message_text(text="排队中", chat_id=info.chat.id, message_id=info.message_id,
                             parse_mode='markdown', reply_markup=reply_markup)


    temp_text=""
    while download.is_active:
        try:
            download.update()
            print("Downloading metadata")
            if temp_text!="Downloading metadata":
                try:
                    client.edit_message_text(text="Downloading metadata",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=reply_markup)
                    temp_text="Downloading metadata"
                except:
                    None
            barop = progessbar(download.completed_length,download.total_length)

            updateText = f"{download.status} \n" \
                         f"'{download.name}'\n" \
                         f"Progress : {hum_convert(download.completed_length)}/{hum_convert(download.total_length)} \n" \
                         f"Peers:{download.connections}\n" \
                         f"Speed {hum_convert(download.download_speed)}/s\n" \
                         f"{barop}\n" \
                         f"剩余空间:{get_free_space_mb()}GB"
            if prevmessagemag != updateText:
                print(updateText)
                try:
                    client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=reply_markup)
                    prevmessagemag = updateText
                except:
                    None
            time.sleep(2)
        except:

            try:
                download.update()
            except Exception as e:
                if (str(e).endswith("is not found")):
                    print("Metadata Cancelled/Failed")
                    print("Metadata couldn't be downloaded")
                    if temp_text!="Metadata Cancelled/Failed":
                        try:
                            client.edit_message_text(text="Metadata Cancelled/Failed",chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown')
                            temp_text="Metadata Cancelled/Failed"
                        except:
                            None
                    return None
            time.sleep(2)


    time.sleep(2)
    match = str(download.followed_by_ids[0])
    downloads = aria2.get_downloads()
    currdownload = None
    for download in downloads:
        if download.gid == match:
            currdownload = download
            break
    print("Download complete")

    new_inline_keyboard = [
        [
            InlineKeyboardButton(
                text="Resume",
                callback_data=f"Resume {currdownload.gid}"
            ),
            InlineKeyboardButton(
                text=f"Pause",
                callback_data=f"Pause {currdownload.gid}"
            ),
            InlineKeyboardButton(
                text=f"Remove",
                callback_data=f"Remove {currdownload.gid}"
            )
        ]
    ]

    new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
    try:
        client.edit_message_text(text="Download complete", chat_id=info.chat.id, message_id=info.message_id,
                             parse_mode='markdown', reply_markup=new_reply_markup)
    except:
        None

    prevmessage = None

    while currdownload.is_active or not currdownload.is_complete:

        try:
            currdownload.update()
        except Exception as e:
            if (str(e).endswith("is not found")):
                print("Magnet Deleted")
                print("Magnet download was removed")
                try:
                    client.edit_message_text(text="Magnet download was removed",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
                except:
                    None
                break
            print(e)
            print("Issue in downloading!")

        if currdownload.status == 'removed':
            print("Magnet was cancelled")
            print("Magnet download was cancelled")
            try:
                client.edit_message_text(text="Magnet download was cancelled",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
            except:
                None
            break

        if currdownload.status == 'error':
            print("Mirror had an error")
            currdownload.remove(force=True, files=True)
            print("Magnet failed to resume/download!\nRun /cancel once and try again.")
            try:
                client.edit_message_text(text="Magnet failed to resume/download!\nRun /cancel once and try again.",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
            except:
                None
            break

        print(f"Magnet Status? {currdownload.status}")

        if currdownload.status == "active":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{download.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Peers:{currdownload.connections}\n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"剩余空间:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    try:
                        client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                        prevmessage = updateText
                    except:
                        None
                time.sleep(2)
            except Exception as e:
                if (str(e).endswith("is not found")):
                    break
                print(e)
                print("Issue in downloading!")
                time.sleep(2)
        elif currdownload.status == "paused":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{download.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Peers:{currdownload.connections}\n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"剩余空间:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    try:
                        client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                        prevmessage = updateText
                    except:
                        None
                time.sleep(2)
            except Exception as e:
                print(e)
                print("Download Paused Flood")
                time.sleep(2)
        time.sleep(2)



    if currdownload.is_complete:
        print(currdownload.name)
        try:
            print("开始上传")
            file_dir=f"{currdownload.dir}/{currdownload.name}"
            files_num=int(len(currdownload.files))
            run_rclone(file_dir,currdownload.name,info=info,file_num=files_num,client=client,message=message)
            currdownload.remove(force=True,files=True)

        except Exception as e:
            print(e)
            print("Upload Issue!")
    return None


#@bot.message_handler(commands=['magnet'],func=lambda message:str(message.chat.id) == str(Telegram_user_id))
def start_download(client, message):
    try:
        keywords = str(message.text)
        if str(BOT_name) in keywords:
            keywords = keywords.replace(f"/magnet@{BOT_name} ", "")
            print(keywords)
            t1 = threading.Thread(target=the_download, args=(client, message,keywords))
            t1.start()
        else:
            keywords = keywords.replace(f"/magnet ", "")
            print(keywords)
            t1 = threading.Thread(target=the_download, args=(client, message,keywords))
            t1.start()

    except Exception as e:
        print(f"magnet :{e}")

def run_rclone(dir,title,info,file_num,client, message):
    global task
    task.append(dir)
    print(task)
    sys.stdout.flush()
    Rclone_remote=os.environ.get('Remote')
    Upload=os.environ.get('Upload')
    name=f"{str(info.message_id)}_{str(info.chat.id)}"
    if int(file_num)==1:
        shell=f"rclone copy \"{dir}\" \"{Rclone_remote}:{Upload}\"  -v --stats-one-line --stats=1s --log-file=\"{name}.log\" "
    else:
        shell=f"rclone copy \"{dir}\" \"{Rclone_remote}:{Upload}/{title}\"  -v --stats-one-line --stats=1s --log-file=\"{name}.log\" "
    print(shell)
    cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                           stdout=subprocess.PIPE, universal_newlines=True, shell=True, bufsize=1)
    # 实时输出
    temp_text=None
    while True:
        time.sleep(1)
        fname = f'{name}.log'
        with open(fname, 'r') as f:  #打开文件
            try:
                lines = f.readlines() #读取所有行

                for a in range(-1,-10,-1):
                    last_line = lines[a] #取最后一行
                    if last_line !="\n":
                        break

                print (f"上传中\n{last_line}")
                if temp_text != last_line and "ETA" in last_line:
                    log_time,file_part,upload_Progress,upload_speed,part_time=re.findall("(.*?)INFO.*?(\d.*?),.*?(\d+%),.*?(\d.*?s).*?ETA.*?(\d.*?)",last_line , re.S)[0]
                    text=f"{title}\n" \
                         f"更新时间：`{log_time}`\n" \
                         f"上传部分：`{file_part}`\n" \
                         f"上传进度：`{upload_Progress}`\n" \
                         f"上传速度：`{upload_speed}`\n" \
                         f"剩余时间:`{part_time}`"
                    try:
                        client.edit_message_text(text=text,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
                        temp_text = last_line
                    except:
                        None
                f.close()

            except Exception as e:
                print(e)
                f.close()
                continue

        if subprocess.Popen.poll(cmd) == 0:  # 判断子进程是否结束
            print("上传结束")
            try:
                client.send_message(text=f"{title}\n上传结束",chat_id=info.chat.id)
            except:
                None
            os.remove(f"{name}.log")
            task.remove(dir)
            return

    return

#@bot.message_handler(commands=['mirror'],func=lambda message:str(message.chat.id) == str(Telegram_user_id))
def start_http_download(client, message):
    try:
        keywords = str(message.text)
        if str(BOT_name) in keywords:
            keywords = keywords.replace(f"/mirror@{BOT_name} ", "")
            print(keywords)
            t1 = threading.Thread(target=http_download, args=(client, message,keywords))
            t1.start()
        else:
            keywords = keywords.replace(f"/mirror ", "")
            print(keywords)
            t1 = threading.Thread(target=http_download, args=(client, message,keywords))
            t1.start()

    except Exception as e:
        print(f"start_http_download :{e}")

def file_download(client, message,file_dir):
    #os.system("df -lh")
    try:
        print("开始下载")
        sys.stdout.flush()
        currdownload = aria2.add_torrent(torrent_file_path=file_dir)
        info=client.send_message(chat_id=message.chat.id, text="开始下载", parse_mode='markdown')
        print("发送信息")
        sys.stdout.flush()
    except Exception as e:
        print(e)
        if (str(e).endswith("No URI to download.")):
            print("No link provided!")
            client.send_message(chat_id=message.chat.id,text="No link provided!",parse_mode='markdown')

        return
    new_inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Resume",
                callback_data=f"Resume {currdownload.gid}"
            ),
        InlineKeyboardButton(
            text=f"Pause",
            callback_data=f"Pause {currdownload.gid}"
        ),
        InlineKeyboardButton(
            text=f"Remove",
            callback_data=f"Remove {currdownload.gid}"
        )
        ]
    ]

    new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
    try:
        client.edit_message_text(text="Download complete",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown' ,reply_markup=new_reply_markup)
    except:
        None
    prevmessage = None

    while currdownload.is_active or not currdownload.is_complete:
        time.sleep(2)
        try:
            currdownload.update()
        except Exception as e:
            if (str(e).endswith("is not found")):
                print("Magnet Deleted")
                print("Magnet download was removed")
                try:
                    client.edit_message_text(text="Magnet download was removed",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
                except:
                    None
                break
            print(e)
            print("Issue in downloading!")

        if currdownload.status == 'removed':
            print("Magnet was cancelled")
            print("Magnet download was cancelled")
            try:
                client.edit_message_text(text="Magnet download was cancelled",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
            except:
                None
            break

        if currdownload.status == 'error':
            print("Mirror had an error")
            currdownload.remove(force=True, files=True)
            print("Magnet failed to resume/download!\nRun /cancel once and try again.")
            try:
                client.edit_message_text(text="Magnet failed to resume/download!\nRun /cancel once and try again.",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown' ,reply_markup=new_reply_markup)
            except:
                None
            break

        print(f"Magnet Status? {currdownload.status}")

        if currdownload.status == "active":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{currdownload.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Peers:{currdownload.connections}\n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"剩余空间:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    try:
                        client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown' ,reply_markup=new_reply_markup)
                        prevmessage = updateText
                    except:
                        None
                time.sleep(2)
            except Exception as e:
                if (str(e).endswith("is not found")):
                    break
                print(e)
                print("Issue in downloading!")
                time.sleep(2)
        elif currdownload.status == "paused":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{currdownload.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Peers:{currdownload.connections}\n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"剩余空间:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    try:
                        client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                        prevmessage = updateText
                    except:
                        None
                time.sleep(2)
            except Exception as e:
                print(e)
                print("Download Paused Flood")
                time.sleep(2)




    if currdownload.is_complete:
        print(currdownload.name)
        try:
            print("开始上传")
            file_dir=f"{currdownload.dir}/{currdownload.name}"
            files_num=int(len(currdownload.files))
            run_rclone(file_dir,currdownload.name,info=info,file_num=files_num,client=client, message=message)
            currdownload.remove(force=True,files=True)
            return

        except Exception as e:
            print(e)
            print("Upload Issue!")
            return
    return None

def http_download(client, message,url):
    try:
        currdownload = aria2.add_uris([url])
        info = client.send_message(chat_id=message.chat.id, text="添加任务", parse_mode='markdown')
    except Exception as e:
        print(e)
        if (str(e).endswith("No URI to download.")):
            print("No link provided!")
            client.send_message(chat_id=message.chat.id,text="No link provided!",parse_mode='markdown')
            return None
    new_inline_keyboard = [
        [
            InlineKeyboardButton(
                text="Resume",
                callback_data=f"Resume {currdownload.gid}"
            ),
            InlineKeyboardButton(
                text=f"Pause",
                callback_data=f"Pause {currdownload.gid}"
            ),
            InlineKeyboardButton(
                text=f"Remove",
                callback_data=f"Remove {currdownload.gid}"
            )
        ]
    ]

    new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
    client.edit_message_text(text="排队中", chat_id=info.chat.id, message_id=info.message_id,
                             parse_mode='markdown', reply_markup=new_reply_markup)


    prevmessage=None
    while currdownload.is_active or not currdownload.is_complete:

        try:
            currdownload.update()
        except Exception as e:
            if (str(e).endswith("is not found")):
                print("url Deleted")
                print("url download was removed")
                try:
                    client.edit_message_text(text="url download was removed",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
                except:
                    None
                break
            print(e)
            print("url in downloading!")

        if currdownload.status == 'removed':
            print("url was cancelled")
            print("url download was cancelled")
            try:
                client.edit_message_text(text="Magnet download was cancelled",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
            except:
                None
            break

        if currdownload.status == 'error':
            print("url had an error")
            currdownload.remove(force=True, files=True)
            print("url failed to resume/download!.")
            try:
                client.edit_message_text(text="Magnet failed to resume/download!\nRun /cancel once and try again.",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
            except:
                None
            break

        print(f"url Status? {currdownload.status}")

        if currdownload.status == "active":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{currdownload.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"剩余空间:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    try:
                        client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                        prevmessage = updateText
                    except:
                        None
                time.sleep(2)
            except Exception as e:
                if (str(e).endswith("is not found")):
                    break
                print(e)
                print("Issue in downloading!")
                time.sleep(2)
        elif currdownload.status == "paused":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{currdownload.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"剩余空间:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    try:
                        client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                        prevmessage = updateText
                    except:
                        None
                time.sleep(2)
            except Exception as e:
                print(e)
                print("Download Paused Flood")
                time.sleep(2)
        time.sleep(2)

    if currdownload.is_complete:
        print(currdownload.name)
        try:
            print("开始上传")
            file_dir=f"{currdownload.dir}/{currdownload.name}"
            run_rclone(file_dir,currdownload.name,info=info,file_num=1,client=client, message=message)
            currdownload.remove(force=True,files=True)

        except Exception as e:
            print(e)
            print("Upload Issue!")
    return None


def progessbar(new, tot):
    """Builds progressbar
    Args:
        new: current progress
        tot: total length of the download
    Returns:
        progressbar as a string of length 20
    """
    length = 20
    progress = int(round(length * new / float(tot)))
    percent = round(new/float(tot) * 100.0, 1)
    bar = '=' * progress + '-' * (length - progress)
    return '[%s] %s %s\r' % (bar, percent, '%')


def hum_convert(value):
    value=float(value)
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f%s" % (value, units[i])
        value = value / size

def get_free_space_mb():
    result=os.statvfs('/root/')
    block_size=result.f_frsize
    total_blocks=result.f_blocks
    free_blocks=result.f_bfree
    # giga=1024*1024*1024
    giga=1000*1000*1000
    total_size=total_blocks*block_size/giga
    free_size=free_blocks*block_size/giga
    print('total_size = %s' % int(total_size))
    print('free_size = %s' % free_size)
    return int(free_size)

def progress(current, total,client,message,name):

    print(f"{current * 100 / total:.1f}%")
    pro=f"{current * 100 / total:.1f}%"
    try:
        client.edit_message_text(chat_id=message.chat.id,message_id=message.message_id,text=f"{name}\n上传中:{pro}")
    except Exception as e:
        print("e")





async def temp_telegram_file(client, message):
    answer = await client.ask(chat_id=message.chat.id, text='请发送种子文件,或输入 /cancel 取消')
    print(answer)
    print(answer.text)
    if answer.document == None:
        await client.send_message(text="发送的不是文件", chat_id=message.chat.id, parse_mode='markdown')
        return "False"
    elif answer.text == "/cancel":
        await client.send_message(text="取消发送", chat_id=message.chat.id, parse_mode='markdown')
        return "False"
    else:
        try:

            file_dir = await client.download_media(message=answer)
            print(file_dir)
            sys.stdout.flush()
            return file_dir
        except Exception as e:
            print(f"{e}")
            sys.stdout.flush()
            await client.send_message(text="下载文件失败", chat_id=message.chat.id, parse_mode='markdown')
            return "False"

#commands=['magfile']
def send_telegram_file(client, message):
    loop = asyncio.get_event_loop()
    temp = loop.run_until_complete(temp_telegram_file(client, message))
    print(temp)
    sys.stdout.flush()
    if temp =="False":
        return
    else:
        file_dir=temp
        t1 = threading.Thread(target=file_download, args=(client, message, file_dir))
        t1.start()
        return




def http_downloadtg(client, message,url):
    try:
        currdownload = aria2.add_uris([url])
        info = client.send_message(chat_id=message.chat.id, text="添加任务", parse_mode='markdown')
    except Exception as e:
        print(e)
        if (str(e).endswith("No URI to download.")):
            print("No link provided!")
            client.send_message(chat_id=message.chat.id,text="No link provided!",parse_mode='markdown')
            return None
    new_inline_keyboard = [
        [
            InlineKeyboardButton(
                text="Resume",
                callback_data=f"Resume {currdownload.gid}"
            ),
            InlineKeyboardButton(
                text=f"Pause",
                callback_data=f"Pause {currdownload.gid}"
            ),
            InlineKeyboardButton(
                text=f"Remove",
                callback_data=f"Remove {currdownload.gid}"
            )
        ]
    ]

    new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
    client.edit_message_text(text="排队中", chat_id=info.chat.id, message_id=info.message_id,
                             parse_mode='markdown', reply_markup=new_reply_markup)


    prevmessage=None
    while currdownload.is_active or not currdownload.is_complete:

        try:
            currdownload.update()
        except Exception as e:
            if (str(e).endswith("is not found")):
                print("url Deleted")
                print("url download was removed")
                try:
                    client.edit_message_text(text="url download was removed",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
                except:
                    None
                break
            print(e)
            print("url in downloading!")

        if currdownload.status == 'removed':
            print("url was cancelled")
            print("url download was cancelled")
            try:
                client.edit_message_text(text="Magnet download was cancelled",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
            except:
                None
            break

        if currdownload.status == 'error':
            print("url had an error")
            currdownload.remove(force=True, files=True)
            print("url failed to resume/download!.")
            try:
                client.edit_message_text(text="Magnet failed to resume/download!\nRun /cancel once and try again.",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
            except:
                None
            break

        print(f"url Status? {currdownload.status}")

        if currdownload.status == "active":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{currdownload.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"剩余空间:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    try:
                        client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                        prevmessage = updateText
                    except:
                        None
                time.sleep(2)
            except Exception as e:
                if (str(e).endswith("is not found")):
                    break
                print(e)
                print("Issue in downloading!")
                time.sleep(2)
        elif currdownload.status == "paused":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{currdownload.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"剩余空间:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    try:
                        client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                        prevmessage = updateText
                    except:
                        None
                time.sleep(2)
            except Exception as e:
                print(e)
                print("Download Paused Flood")
                time.sleep(2)
        time.sleep(2)

        time.sleep(1)
    if currdownload.is_complete:
        print(currdownload.name)
        try:
            print("开始上传")
            file_dir=f"{currdownload.dir}/{currdownload.name}"
            client.send_document(chat_id=info.chat.id, document=file_dir, caption=currdownload.name, progress=progress,
                                       progress_args=(client, info, currdownload.name,))

            currdownload.remove(force=True,files=True)

        except Exception as e:
            print(e)
            print("Upload Issue!")
            currdownload.remove(force=True, files=True)
    return None

#@bot.message_handler(commands=['mirrortg'],func=lambda message:str(message.chat.id) == str(Telegram_user_id))
def start_http_downloadtg(client, message):
    try:
        keywords = str(message.text)
        if str(BOT_name) in keywords:
            keywords = keywords.replace(f"/mirrortg@{BOT_name} ", "")
            print(keywords)
            t1 = threading.Thread(target=http_downloadtg, args=(client, message,keywords))
            t1.start()
        else:
            keywords = keywords.replace(f"/mirrortg ", "")
            print(keywords)
            t1 = threading.Thread(target=http_downloadtg, args=(client, message,keywords))
            t1.start()

    except Exception as e:
        print(f"start_http_download :{e}")




