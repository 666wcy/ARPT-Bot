# -*- coding: utf-8 -*-
import hmac
import zipfile
import uuid
import os
import hashlib
import json
import re
import time
import requests
import threading
import subprocess
import sys
from modules.control import run_rclone
from config import App_title
from pyrogram.types import InlineKeyboardMarkup,InlineKeyboardButton

def wake_clock():
    try:
        if App_title!="":
            print("任务正在进行,保持唤醒")
            print(requests.get(url=f"https://{App_title}.herokuapp.com/"))
            sys.stdout.flush()

    except Exception as e:
        print(f"wake_clock error :{e}")



# hmacsha256加密函数
def hmacsha256(key, string):
    key = bytes(key, encoding="utf8")
    string = bytes(string, encoding="utf8")
    signature = hmac.new(
        key,
        msg=string,
        digestmod=hashlib.sha256
    ).hexdigest()
    return signature

# 密钥计算函数
def password(url, method, time, nonce):
    key = "C69BAF41DA5ABD1FFEDC6D2FEA56B"
    str = url + time + nonce + method + key
    str = str.lower()
    mi = "~d}$Q7$eIni=V)9\\RK/P.RM4;9[7|@/CA}b~OW!3?EV`:<>M7pddUBL5n|0/*Cn"
    return hmacsha256(mi, str)

def del_path(path):
    if not os.path.exists(path):
        return
    if os.path.isfile(path):
        os.remove(path)
        # print( 'delete file %s' % path)
    else:
        items = os.listdir(path)
        for f in items:
            c_path = os.path.join(path, f)
            if os.path.isdir(c_path):
                del_path(c_path)
            else:
                os.remove(c_path)
                # print('delete file %s' % c_path)
        os.rmdir(path)
        # print( 'delete dir %s' % path)

def zip_ya(start_dir):
    start_dir = start_dir  # 要压缩的文件夹路径
    file_news = start_dir + '.zip'  # 压缩后文件夹的名字
    z = zipfile.ZipFile(file_news, 'w', zipfile.ZIP_DEFLATED)
    for dir_path, dir_names, file_names in os.walk(start_dir):
        f_path = dir_path.replace(start_dir, '')  # 这一句很重要，不replace的话，就从根目录开始复制
        f_path = f_path and f_path + os.sep or ''  # 实现当前文件夹以及包含的所有文件的压缩
        for filename in file_names:
            z.write(os.path.join(dir_path, filename), f_path + filename)
    z.close()
    return file_news

def getheaders(nurl, mothed):
    try:
        global Mytoken
        timestr = str(int(time.time()))
        url = "https://picaapi.picacomic.com/" + nurl
        nonce = str(uuid.uuid1()).replace("-", "")
        sign = password(nurl, mothed, timestr, nonce)
        headers = {
            "api-key": "C69BAF41DA5ABD1FFEDC6D2FEA56B",
            "accept": "application/vnd.picacomic.com.v1+json",
            "app-channel": "1",
            "time": timestr,
            "nonce": nonce,
            "signature": sign,
            "app-version": "2.2.1.3.3.4",
            "app-uuid": "cb69a7aa-b9a8-3320-8cf1-74347e9ee970",
            "image-quality": "original",
            "app-platform": "android",
            "app-build-version": "45",
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "okhttp/3.8.1",
        }
        headers.update({"authorization": Mytoken})
        return headers
    except:
        print("获取headers失败")

# 检查是否登录状态
def loginpic():
    try:
        global Mytoken
        timestr = str(int(time.time()))
        nurl = "auth/sign-in"
        mothed = "POST"
        url = "https://picaapi.picacomic.com/" + nurl
        nonce = str(uuid.uuid1()).replace("-", "")
        sign = password(nurl, mothed, timestr, nonce)
        headers = {
            "api-key": "C69BAF41DA5ABD1FFEDC6D2FEA56B",
            "accept": "application/vnd.picacomic.com.v1+json",
            "app-channel": "1",
            "time": timestr,
            "nonce": nonce,
            "signature": sign,
            "app-version": "2.2.1.3.3.4",
            "app-uuid": "cb69a7aa-b9a8-3320-8cf1-74347e9ee970",
            "image-quality": "original",
            "app-platform": "android",
            "app-build-version": "45",
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "okhttp/3.8.1",
        }
        body = {"email": "weidapao", "password": "@Wcy98151"}

        mytoken = requests.post(url, headers=headers, data=json.dumps(body), verify=False)
        # .json()['data']['token']
        print(mytoken)
        sys.stdout.flush()

        if mytoken.json()['message'] == "success":
            print("登陆成功")
            Mytoken = mytoken.json()['data']['token']
            f1 = open('token.txt', 'w')
            f1.write(Mytoken)
            f1.close()
        else:
            print("登录失败")
            sys.stdout.flush()
    except Exception as e:
        print(f"登录函数失败 {e}")
        sys.stdout.flush()

def check():
    try:
        global Mytoken
        try:
            f = open('token.txt')
            Mytoken = f.read()
            f.close()
        except:
            file = open('token.txt', 'w')
            file.close()
            loginpic()
            return
        timestr = str(int(time.time()))
        nurl = "categories"
        mothed = "GET"
        url = "https://picaapi.picacomic.com/" + nurl
        nonce = str(uuid.uuid1()).replace("-", "")
        sign = password(nurl, mothed, timestr, nonce)
        headers = {
            "api-key": "C69BAF41DA5ABD1FFEDC6D2FEA56B",
            "accept": "application/vnd.picacomic.com.v1+json",
            "app-channel": "1",
            "time": timestr,
            "nonce": nonce,
            "signature": sign,
            "app-version": "2.2.1.3.3.4",
            "app-uuid": "cb69a7aa-b9a8-3320-8cf1-74347e9ee970",
            "image-quality": "original",
            "app-platform": "android",
            "app-build-version": "45",
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "okhttp/3.8.1",
        }
        headers.update({"authorization": Mytoken})
        # shou_url="https://picaapi.picacomic.com/users/favourite?s=dd&page=1"
        # main_url="https://picaapi.picacomic.com/categories"
        main_html = requests.get(url=url, headers=headers, verify=False)
        # print(main_html.json())
        if main_html.json()["code"] != 200:
            print("token过期，即将重新登录")
            sys.stdout.flush()
            loginpic()
        else:
            print("token有效")
            sys.stdout.flush()
    except Exception as e:
        print(f"检查函数失败 {e}")
        sys.stdout.flush()

def down(url, imgname, title):
    try:
        headers = {
            "api-key": "C69BAF41DA5ABD1FFEDC6D2FEA56B",
            "accept": "application/vnd.picacomic.com.v1+json",
            "app-channel": "1",
            "app-version": "2.2.1.3.3.4",
            "app-uuid": "cb69a7aa-b9a8-3320-8cf1-74347e9ee970",
            "image-quality": "original",
            "app-platform": "android",
            "app-build-version": "45",
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "okhttp/3.8.1",
        }
        path = title
        if not os.path.exists(path):
            os.mkdir(path)
        for ci in range(3):
            try:
                r = requests.get(url, headers=headers)
                if r.status_code != 404:
                    with open('%s/%03d.jpg' % (title, imgname), 'wb') as f:
                        f.write(r.content)
                if r.status_code == 404:
                    url = eval(repr(url).replace('jpg', 'png'))
                    r = requests.get(url, )
                    with open('%s/%03d.png' % (title, imgname), 'wb') as f:
                        f.write(r.content)
                # time.sleep(0.5)
                break
            except Exception as e:
                print(f"下载失败，正在重试 {e}")
                sys.stdout.flush()
    except Exception as e:
        print(f"下载失败 {e}")
        sys.stdout.flush()

def downmany(url, imgname, title, zhang):
    try:
        headers = {
            "api-key": "C69BAF41DA5ABD1FFEDC6D2FEA56B",
            "accept": "application/vnd.picacomic.com.v1+json",
            "app-channel": "1",
            "app-version": "2.2.1.3.3.4",
            "app-uuid": "cb69a7aa-b9a8-3320-8cf1-74347e9ee970",
            "image-quality": "original",
            "app-platform": "android",
            "app-build-version": "45",
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "okhttp/3.8.1",
        }
        path = title
        if not os.path.exists(path):
            os.mkdir(path)
        path = title + "/" + zhang
        if not os.path.exists(path):
            os.mkdir(path)
        for ci in range(3):
            try:
                r = requests.get(url, headers=headers)
                if r.status_code != 404:
                    with open('%s/%s/%03d.jpg' % (title, zhang, imgname), 'wb') as f:
                        f.write(r.content)
                if r.status_code == 404:
                    url = eval(repr(url).replace('jpg', 'png'))
                    r = requests.get(url, )
                    with open('%s/%s/%03d.jpg' % (title, zhang, imgname), 'wb') as f:
                        f.write(r.content)
                # time.sleep(0.5)
                break
            except Exception as e:
                print(f"下载失败，正在重试 {e}")
                sys.stdout.flush()
    except Exception as e:
        print(f"下载多章失败 {e}")
        sys.stdout.flush()

def seach(client, message):
    try:
        print("检查登录")
        sys.stdout.flush()
        check()
        # bot.reply_to(message, message.text)
        keywords = str(message.text)
        # print(message.chat.type)
        keywords = keywords.replace("/search ", "")
        PostData = {
            "categories": "",  # 限定的分区，可以不加
            "keyword": keywords,  # 必选参数，搜索的关键词
            "sort": ""  # 可选参数，与block里面的type一样
        }
        nurl = "comics/advanced-search?page=1"
        headers = getheaders(nurl, "POST")
        url = "https://picaapi.picacomic.com/" + nurl
        main_html = requests.post(url=url, headers=headers, data=json.dumps(PostData), verify=False)
        # print(main_html.text)
        for img_json in main_html.json()["data"]["comics"]["docs"]:
            # print(img_json)
            img_url = img_json['thumb']["fileServer"] + "/static/" + img_json['thumb']['path']

            # print(img_url)
            title = img_json["title"]
            book_id = img_json["_id"]
            description = img_json["description"]

            text = f"title:{title}\ndescription:{description}\nbook_id:{book_id}"
            # print(text)

            new_inline_keyboard = [
                [
                    InlineKeyboardButton(
                        text="下载本子",
                        callback_data=f"down"
                    ),
                    InlineKeyboardButton(
                        text="发送本子到TG",
                        callback_data=f"tgdown"
                    )
                ]
            ]

            new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
            client.send_photo(chat_id=message.chat.id, photo=img_url, caption=text, reply_markup=new_reply_markup)

    except Exception as e:
        print(f"seach {e}")
        sys.stdout.flush()


def progress(current, total,client,message,name):

    print(f"{current * 100 / total:.1f}%")
    pro=f"{current * 100 / total:.1f}%"
    try:
        client.edit_message_text(chat_id=message.chat.id,message_id=message.message_id,text=f"{name}\n上传中:{pro}")
    except Exception as e:
        print("e")

def add_download(client,call):

        import re
        check()
        caption = str(call.message.caption)
        comicid = re.findall("book_id:(.*)", caption, re.S)[0]
        title = re.findall("title:(.*?)\n", caption, re.S)[0]

        message_id = call.message.message_id
        message_chat_id = call.message.chat.id

        title = title.replace(" ", "").replace("\\", "").replace("/", "").replace("|", "").replace(" ", "")
        mulu_page = 1
        info=client.send_message(chat_id=message_chat_id, text=" 开始下载")

        #已下载话数
        hua_down_num=0

        while True:

            nurl = "comics/" + str(comicid) + f"/eps?page={mulu_page}"
            url = "https://picaapi.picacomic.com/" + nurl
            headers = getheaders(nurl, "GET")
            # shou_url="https://picaapi.picacomic.com/users/favourite?s=dd&page=1"
            # main_url="https://picaapi.picacomic.com/categories"
            main_html = requests.get(url=url, headers=headers, verify=False)
            data=main_html.json()["data"]["eps"]["total"]
            print(main_html.text)
            benzihua_num=main_html.json()["data"]["eps"]["total"]
            print(f"本子话数{benzihua_num}")
            sys.stdout.flush()



            for eps in main_html.json()['data']['eps']['docs']:

                epsid = eps['order']
                page = 1
                img_name = 1
                zhang = eps["title"]
                wake_clock()
                download_process_text=f"当前下载话:{zhang}\n" \
                                      f"下载进度:{hua_down_num}/{benzihua_num}\n"

                client.edit_message_text(text=download_process_text,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')

                #该循环下载单话
                while True:
                    nurl = "comics/" + str(comicid) + "/order/" + str(epsid) + "/pages?page=" + str(page)

                    url = "https://picaapi.picacomic.com/" + nurl
                    headers = getheaders(nurl, "GET")
                    img = requests.get(url=url, headers=headers, verify=False)
                    img_lu = img.json()["data"]["pages"]["docs"]
                    for picture in img_lu:
                        img_url = str(picture['media']['fileServer']) + "/static/" + str(picture['media']['path'])
                        print(img_name)
                        print(img_url)
                        downmany(img_url, img_name, title, zhang)
                        img_name = img_name + 1
                    page = page + 1
                    print(img.json()["data"]["pages"]["page"])
                    print(img.json()["data"]["pages"]["pages"])

                    print(f"该话页数")

                    if img.json()["data"]["pages"]["page"] == img.json()["data"]["pages"]["pages"]:

                        break
                hua_down_num=hua_down_num+1


            book_pages = int(main_html.json()["data"]["eps"]["pages"])
            if book_pages == mulu_page:
                break
            mulu_page = mulu_page + 1
        print("开始压缩")
        sys.stdout.flush()
        name = zip_ya(title)
        print(name)
        print("压缩完成，开始上传")
        del_path(title)
        try:
            run_rclone(dir=name,title=title,info=info,file_num=1,client=client,message=call)
            print("uploading")
        except Exception as e:
            print(f"{e}")
            sys.stdout.flush()
            client.send_message(message_chat_id, text="文件上传失败")
        client.delete_message(message_chat_id, message_id)
        os.system("rm '" + name + "'")


def add_downloadtg(client, call):
    import re
    check()
    caption = str(call.message.caption)
    comicid = re.findall("book_id:(.*)", caption, re.S)[0]
    title = re.findall("title:(.*?)\n", caption, re.S)[0]

    message_id = call.message.message_id
    message_chat_id = call.message.chat.id

    title = title.replace(" ", "").replace("\\", "").replace("/", "").replace("|", "").replace(" ", "")
    mulu_page = 1
    info = client.send_message(chat_id=message_chat_id, text=" 开始下载")

    # 已下载话数
    hua_down_num = 0

    while True:

        nurl = "comics/" + str(comicid) + f"/eps?page={mulu_page}"
        url = "https://picaapi.picacomic.com/" + nurl
        headers = getheaders(nurl, "GET")
        # shou_url="https://picaapi.picacomic.com/users/favourite?s=dd&page=1"
        # main_url="https://picaapi.picacomic.com/categories"
        main_html = requests.get(url=url, headers=headers, verify=False)
        data = main_html.json()["data"]["eps"]["total"]
        print(main_html.text)
        benzihua_num = main_html.json()["data"]["eps"]["total"]
        print(f"本子话数{benzihua_num}")
        sys.stdout.flush()

        for eps in main_html.json()['data']['eps']['docs']:

            epsid = eps['order']
            page = 1
            img_name = 1
            zhang = eps["title"]
            wake_clock()
            download_process_text = f"当前下载话:{zhang}\n" \
                                    f"下载进度:{hua_down_num}/{benzihua_num}\n"

            client.edit_message_text(text=download_process_text, chat_id=info.chat.id, message_id=info.message_id,
                                     parse_mode='markdown')

            # 该循环下载单话
            while True:
                nurl = "comics/" + str(comicid) + "/order/" + str(epsid) + "/pages?page=" + str(page)

                url = "https://picaapi.picacomic.com/" + nurl
                headers = getheaders(nurl, "GET")
                img = requests.get(url=url, headers=headers, verify=False)
                img_lu = img.json()["data"]["pages"]["docs"]
                for picture in img_lu:
                    img_url = str(picture['media']['fileServer']) + "/static/" + str(picture['media']['path'])
                    print(img_name)
                    print(img_url)
                    downmany(img_url, img_name, title, zhang)
                    img_name = img_name + 1
                page = page + 1
                print(img.json()["data"]["pages"]["page"])
                print(img.json()["data"]["pages"]["pages"])

                print(f"该话页数")

                if img.json()["data"]["pages"]["page"] == img.json()["data"]["pages"]["pages"]:
                    break
            hua_down_num = hua_down_num + 1

        book_pages = int(main_html.json()["data"]["eps"]["pages"])
        if book_pages == mulu_page:
            break
        mulu_page = mulu_page + 1
    print("开始压缩")
    sys.stdout.flush()
    name = zip_ya(title)
    print(name)
    print("压缩完成，开始上传")
    del_path(title)
    try:
        client.send_document(chat_id=info.chat.id, document=name, caption=title, progress=progress,
                             progress_args=(client, info, title,))

        print("uploading")
    except Exception as e:
        print(f"{e}")
        sys.stdout.flush()
        client.send_message(message_chat_id, text="文件上传失败")
    client.delete_message(message_chat_id, message_id)
    os.system("rm '" + name + "'")


#@bot.message_handler(commands=['search'])
def seach_main(client, message):

    t1 = threading.Thread(target=seach, args=(client, message))
    t1.start()
    return


