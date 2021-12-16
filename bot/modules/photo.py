
import os
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import re

from lxml import etree
from bs4 import BeautifulSoup
import requests
session =requests.session()




async def send_photo(client, message):
  print(message)
  await client.delete_messages(chat_id=message.chat.id, message_ids=message.message_id)
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
        search_result = session.post(url=url, headers=Header, data=payloaddata,files=files)

        #print(soup.prettify())

        lxml_result = etree.HTML(search_result.text)
        title_list = lxml_result.xpath('//*[@id="middle"]/div/table/tr/td[2]/div[2]/div[1]/strong/text()')
        info_list = lxml_result.xpath('//*[@id="middle"]/div/table/tr/td[2]/div[2]/div[1]/small/text()')
        similarity_list = lxml_result.xpath('//*[@id="middle"]/div/table/tr/td[2]/div[1]/div[1]/text()')
        img_list = lxml_result.xpath('//*[@id="middle"]/div/table/tr/td[1]/div/a/img/@src')
        link_list = lxml_result.xpath('//*[@id="middle"]/div/table/tr/td[1]/div/a/@href')
        print(title_list)
        print(info_list)
        print(similarity_list)
        print(img_list)
        print(link_list)
        for title, info, similarity, img, link in zip(title_list, info_list, similarity_list, img_list, link_list):
            text = f"标题:`{title}`\n" \
                   f"简介:`{info}`\n" \
                   f"相似度:`{similarity}`\n" \
                   f"[更多信息]({link})"
            try:
                new_inline_keyboard = [
                    [
                        InlineKeyboardButton(
                            text="搜索ehentai",
                            callback_data=f"searche {str(title)[0:32]}"
                        )], [
                        InlineKeyboardButton(
                            text="搜索nhentai",
                            callback_data=f"searchn {str(title)[0:32]}"
                        )], [
                        InlineKeyboardButton(
                            text="搜索哔咔",
                            callback_data=f"searchp {str(title)[0:32]}"
                        )
                    ]
                ]

                new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)

                client.send_photo(chat_id=message.message.chat.id,photo=img,reply_markup=new_reply_markup,parse_mode='markdown',caption=text)
            except Exception as e:
                print(e)
                continue

        os.remove(file)
    except Exception as e:
        print(f"saucenao:{e}")
        try:
            os.remove(file)
        except:
            None


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






