import sys
import os
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
import base64
import re
import datetime
from urllib import parse
from bs4 import BeautifulSoup
import requests
session =requests.session()




async def send_photo(client, message):
  print(message)
  new_inline_keyboard = [
            [
                InlineKeyboardButton(
                    text="saucenao",
                    callback_data=f"saucenao"
                ),
                InlineKeyboardButton(
                    text="WhatAnime",
                    callback_data=f"WhatAnime"
                )

            ],
            [
                InlineKeyboardButton(
                    text="iqdb",
                    callback_data=f"iqdb"
                ),
                InlineKeyboardButton(
                    text="ascii2d",
                    callback_data=f"ascii2d"
                )

            ],
            [
                InlineKeyboardButton(
                    text="所有引擎",
                    callback_data=f"allsearchphoto"
                )
            ]
        ]

  new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
  await client.send_photo(caption=f"请选择搜索引擎", photo=message.photo.file_id, chat_id=message.chat.id,
                    parse_mode='markdown', reply_markup=new_reply_markup)



def saucenao(client, message):
    try:
        print(message)
        url="https://saucenao.com/search.php"
        #url = "https://saucenao.com"
        Header = {
            'Host': 'saucenao.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
             'Accept': 'text / html, application / xhtml + xml, application / xml;q = 0.9, * / *;q = 0.8',
            'Accept - Language': 'zh - CN, zh;q = 0.8, zh - TW;q = 0.7, zh - HK;q = 0.5, en - US;q = 0.3, en;q = 0.2',
             'Accept - Encoding': 'gzip, deflate, br',
            'Connection': 'keep - alive',

        }
        payloaddata = {

            'frame': 1,
            'hide': 0,
            'database': 999,
        }
        #files = { "file": ('saber.jpg', open("saber.jpg", "rb", , "image/png")}




        file = client.download_media(message=message.message)


        files={"file" : ("saber.jpg", open(file, "rb"), "image/png" )}

        #files = {"file": ("saucenao.jpg", file, "image/png")}
        client.send_message(chat_id=message.message.chat.id,text="正在搜索saucenao")
        r = session.post(url=url, headers=Header, data=payloaddata,files=files)
        #r = session .get(url=url,headers=Header)
        soup = BeautifulSoup(r.text, 'html.parser')
        #print(soup.prettify())
        result=0
        choice=0
        for img in soup.find_all('div', attrs={'class': 'result'}):  # 找到class="wrap"的div里面的所有<img>标签
            #print(img)
            if('hidden' in str(img['class']))==False:
                try:
                    name=img.find("div",attrs={'class': 'resulttitle'}).get_text()
                    img_url=str(img.img['src'])
                    describe_list=img.find("div",attrs={'class': 'resultcontentcolumn'})
                    url_list = img.find("div", attrs={'class': 'resultcontentcolumn'}).find_all("a",  attrs={'class': 'linkify'})
                    similarity = str(img.find("div", attrs={'class': 'resultsimilarityinfo'}).get_text())
                    print(name)
                except:
                    continue
                try:
                    describe = str(url_list[0].previous_sibling.string)
                    describe_id = str(url_list[0].string)
                    describe_url = str(url_list[0]['href'])
                    auther_url = str(url_list[1]['href'])
                    auther = str(url_list[1].previous_sibling.string)
                    auther_id = str(url_list[1].string)
                    '''print(name)
                    print(img_url)
                    print(describe)
                    print(describe_id)
                    print(similarity)
                    print(auther)
                    print(auther_id)
                    print(describe_url)'''
                    text = f"{name}\n{describe}[{describe_id}]({describe_url})\n{auther}:[{auther_id}]({auther_url})\n相似度{similarity}"
                except:
                    '''print(describe_list.get_text())
                    print(describe_list.strong.string)
                    print(describe_list.strong.next_sibling.string)
                    print(describe_list.small.string)
                    print(describe_list.small.next_sibling.next_sibling.string)'''
                    auther = str(describe_list.strong.string)
                    auther_id = str(describe_list.strong.next_sibling.string)
                    describe = str(describe_list.small.string) + "\n" + str(describe_list.small.next_sibling.next_sibling.string)
                    text = f"{name}\n{auther}:{auther_id}\n{describe}\n相似度{similarity}"

                #photo_file = session.get(img_url)
                client.send_photo(chat_id=message.message.chat.id,photo=img_url,parse_mode='markdown',caption=text)


                result=1
        if result==0:
            client.send_message(chat_id=message.message.chat.id, text="saucenao无结果")
        os.remove(file)
    except Exception as e:
        print(f"saucenao:{e}")
        os.remove(file)


def ascii2d(client, message):
    try:
        url = "https://ascii2d.net/"
        # url = "https://saucenao.com"
        Header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
        }
        html = session.get(url, headers=Header)
        print(html)
        authenticity_token = re.findall("<input type=\"hidden\" name=\"authenticity_token\" value=\"(.*?)\" />", html.text, re.S)[0]
        payloaddata = {

            'authenticity_token': authenticity_token,
            'utf8': "✓",
        }
        # files = {"file": "file": ('saber.jpg', open("saber.jpg", "rb", , "image/png")}
        client.send_message(chat_id=message.message.chat.id, text="正在搜索ascii2d")


        file = client.download_media(message=message.message)


        files={"file" : ("saber.jpg", open(file, "rb"), "image/png" )}

        url = "https://ascii2d.net/search/multi"
        r = session.post(url=url, headers=Header, data=payloaddata, files=files)
        soup = BeautifulSoup(r.text, 'html.parser')
        # print(soup.prettify())
        pan = 0
        for img in soup.find_all('div', attrs={'class': 'row item-box'}):  # 找到class="wrap"的div里面的所有<img>标签
            # print(img)
            if pan != 0:
                img_url = "https://ascii2d.net" + str(img.img['src'])
                the_list = img.find_all('a')
                title = str(the_list[0].get_text())
                title_url = str(the_list[0]["href"])
                auther = str(the_list[1].get_text())
                auther_url = str(the_list[1]["href"])

                #photo_file = session.get(img_url)
                text=f"titile:[{title}]({title_url})\nauther:[{auther}]({auther_url})"
                client.send_photo(chat_id=message.message.chat.id, caption=text, parse_mode='Markdown',photo=img_url)
            pan = pan + 1
            if pan == 3:
                break
        os.remove(file)
    except Exception as e:
        print(f"ascii2d faild{e}")
        os.remove(file)


def anime(client, message):
    try:
        client.send_message(chat_id=message.message.chat.id, text="正在搜索 trace.moe")
        url = "https://trace.moe/api/search"
        # url = "https://saucenao.com"
        file = client.download_media(message=message.message)

        r=requests.post("https://api.trace.moe/search",
                      files={"image": open(file, "rb")}
                      )


        # r = session .get(url=url,headers=Header)

        information = r.json()
        anilist_id = information['result'][0]["anilist"]
        filename = information['result'][0]['filename']



        episode = information['result'][0]['episode']

        similarity=information['result'][0]['similarity']
        similarity_num="%.2f%%" % (similarity * 100)
        img_url = information['result'][0]['image']
        print(img_url)
        video_url =information['result'][0]['video']
        print(video_url)


        more_url = f"https://anilist.co/anime/{anilist_id}"
        text = f"{similarity_num}\n" \
               f"Title:{filename}\n" \
               f"集数:{episode}\n" \
               f"[更多信息]({more_url})\n"
        print(text)
        #photo_file = session.get(img_url)
        client.send_photo(chat_id=message.message.chat.id, photo=img_url, parse_mode='Markdown', caption=text)
        #photo_file = session.get(video)
        client.send_video(chat_id=message.message.chat.id,video=video_url)

        me = requests.get("https://api.trace.moe/me").json()
        me_info=f"我的IP:`{me['id']}`\n" \
                f"您可以发出的并行搜索请求数:`{me['concurrency']}`\n" \
                f"您本月的搜索配额:`{me['quota']}`\n" \
                f"您本月使用的搜索配额:`{me['quotaUsed']}`"

        client.send_message(chat_id=message.message.chat.id, text=me_info,parse_mode='markdown')
        os.remove(file)
    except Exception as e:
        print(f"anime faild:{e}")
        os.remove(file)

def iqdb(client, message):
    try:
        client.send_message(chat_id=message.message.chat.id, text="正在搜索 iqdb", parse_mode="Markdown")
        url = "http://iqdb.org/"
        # url = "https://saucenao.com"



        file = client.download_media(message=message.message)


        files = {"file": (
            "iqdb.jpg", open(file, "rb"), "image/png")}


        # files = {"file": "file": ('saber.jpg', open("saber.jpg", "rb", , "image/png")}

        r = requests.post(url=url, files=files)


        soup = BeautifulSoup(r.text, 'html.parser')
        a=1
        for img in soup.find_all('td', attrs={'class': 'image'}):  # 找到class="wrap"的div里面的所有<img>标签
            #print(img)
            if a==7:
                break
            try:
                #print(img.a.get('href'))
                img_html=img.a.get('href')
                if "http:" not in img_html and "https:" not in img_html:

                    img_html="https:"+img_html

                img_url="http://iqdb.org"+img.img.get('src')

                text=f"[图片详情]({img_html})"
                #photo_file = session.get(img_url)
                client.send_photo(chat_id=message.message.chat.id, photo=img_url, parse_mode='Markdown', caption=text)
                a=a+1
            except:
                None

        client.send_message(chat_id=message.message.chat.id, text="搜索完成", parse_mode="markdown")
        os.remove(file)

    except Exception as e:
        print(f"iqdb faild:{e}")
        os.remove(file)
        

def search_all_photo(client, message):
    saucenao(client, message)
    ascii2d(client, message)
    anime(client, message)
    iqdb(client, message)
    client.send_message(chat_id=message.message.chat.id, text="所有引擎搜索完成", parse_mode="Markdown")






