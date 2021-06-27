# -*- coding: utf-8 -*-
import os
import sys
import requests
import zipfile
import threading
import sys
import json
import io
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import os
from PIL import Image
from PIL import ImageFile
from pyrogram.types import InputMediaPhoto
import telegraph
from telegraph import Telegraph
from modules.control import run_await_rclone

session = requests.Session()
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 5.8; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
    'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
}

def compress_image(outfile, mb, quality=85, k=0.9):
    """不改变图片尺寸压缩到指定大小
    :param outfile: 压缩文件保存地址
    :param mb: 压缩目标，KB
    :param step: 每次调整的压缩比率
    :param quality: 初始压缩比率
    :return: 压缩文件地址，压缩文件大小
    """

    o_size = os.path.getsize(outfile) // 1024
    print(o_size, mb)
    if o_size <= mb:
        return outfile

    ImageFile.LOAD_TRUNCATED_IMAGES = True
    while o_size > mb:
        im = Image.open(outfile)
        x, y = im.size
        out = im.resize((int(x * k), int(y * k)), Image.ANTIALIAS)
        try:
            dir, suffix = os.path.splitext(outfile)
            os.remove(outfile)
            #print(outfile)
            outfile = '{}{}'.format(dir, suffix)
            out.save(outfile, quality=quality)
        except Exception as e:
            print(e)
            break
        o_size = os.path.getsize(outfile) // 1024
    return outfile

async def start_download_pixiv_top(client, call):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 5.8; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
        'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
    }
    keywords = str(call.data)
    page_num = int(keywords.split(" ")[1])

    rand_data = str(keywords).split(" ")[2]
    if rand_data=="nodata":
        the_data=""
    else:
        the_data=f"&date={rand_data}"

    message_id = call.message.message_id
    message_chat_id = call.message.chat.id

    info = await client.send_message(chat_id=message_chat_id, text="开始下载", parse_mode='markdown')
    print(info)

    img_num = page_num*50
    img_su_num = 0
    img_er_num = 0
    if "monthall" in str(call.data):
        for ban in range(1, page_num+1):
            url = f"https://www.pixiv.net/ranking.php?mode=monthly&p={ban}{the_data}&format=json"  # 日榜json文件，一个50张
            try:
                html = session.get(url, headers=header)
            except:
                None
            josn = json.loads(html.text)
            josn = str(josn)
            imgurl = re.findall("'url': '(.*?)',", josn, re.S)
            name = re.findall("'title': '(.*?)',", josn, re.S)

            for c, d in zip(imgurl, name):
                c = str(c)
                id = re.findall("\d\d\d\d\d\d\d\d", c, re.S)[0]
                c = eval(repr(c).replace('c/240x480/img-master', 'img-original'))
                c = eval(repr(c).replace('_master1200', ''))
                author=f"pixiv_month{rand_data}"
                download_result = download(url=c, title=d,author=author,id= id)
                if download_result == True:
                    img_su_num = img_su_num + 1
                else:
                    img_er_num = img_er_num + 1

                text = f"Author:月榜\n" \
                       f"Number of pictures:{img_num}\n" \
                       f"Number of successes:{img_su_num}\n" \
                       f"Number of errors:{img_er_num}\n" \
                       f"Progessbar:\n{progessbar(img_su_num, img_num)}"
                try:
                    await client.edit_message_text(chat_id=info.chat.id, message_id=info.message_id, text=text,
                                               parse_mode="markdown")
                except:
                    None
    elif "dayall" in str(call.data):
        for ban in range(1, page_num+1):
            url = f"https://www.pixiv.net/ranking.php?mode=daily&p={ban}{the_data}&format=json" # 日榜json文件，一个50张
            try:
                html = session.get(url, headers=header)
            except:
                None
            josn = json.loads(html.text)
            josn = str(josn)
            imgurl = re.findall("'url': '(.*?)',", josn, re.S)
            name = re.findall("'title': '(.*?)',", josn, re.S)

            for c, d in zip(imgurl, name):
                c = str(c)
                id = re.findall("\d\d\d\d\d\d\d\d", c, re.S)[0]
                c = eval(repr(c).replace('c/240x480/img-master', 'img-original'))
                c = eval(repr(c).replace('_master1200', ''))
                author=f"pixiv_day{rand_data}"
                download_result = download(url=c, title=d,author=author,id= id)
                if download_result == True:
                    img_su_num = img_su_num + 1
                else:
                    img_er_num = img_er_num + 1

                text = f"Author:日榜\n" \
                       f"Number of pictures:{img_num}\n" \
                       f"Number of successes:{img_su_num}\n" \
                       f"Number of errors:{img_er_num}\n" \
                       f"Progessbar:\n{progessbar(img_su_num, img_num)}"

                try:
                    await client.edit_message_text(chat_id=info.chat.id, message_id=info.message_id, text=text,
                                                   parse_mode="markdown")
                except:
                    None
    elif "weekall" in str(call.data):
        for ban in range(1, page_num+1):
            url = f"https://www.pixiv.net/ranking.php?mode=weekly&p={ban}{the_data}&format=json"  # 日榜json文件，一个50张
            try:
                html = session.get(url, headers=header)
            except:
                None
            josn = json.loads(html.text)
            josn = str(josn)
            imgurl = re.findall("'url': '(.*?)',", josn, re.S)
            name = re.findall("'title': '(.*?)',", josn, re.S)

            for c, d in zip(imgurl, name):
                c = str(c)
                id = re.findall("\d\d\d\d\d\d\d\d", c, re.S)[0]
                c = eval(repr(c).replace('c/240x480/img-master', 'img-original'))
                c = eval(repr(c).replace('_master1200', ''))
                author=f"pixiv_week{rand_data}"
                download_result = download(url=c, title=d,author=author,id= id)
                if download_result == True:
                    img_su_num = img_su_num + 1
                else:
                    img_er_num = img_er_num + 1

                text = f"Author:周榜\n" \
                       f"Number of pictures:{img_num}\n" \
                       f"Number of successes:{img_su_num}\n" \
                       f"Number of errors:{img_er_num}\n" \
                       f"Progessbar:\n{progessbar(img_su_num, img_num)}"

                try:
                    await client.edit_message_text(chat_id=info.chat.id, message_id=info.message_id, text=text,
                                                   parse_mode="markdown")
                except:
                    None

    elif "dayillustration" in str(call.data):
        for ban in range(1, page_num+1):
            url = f"https://www.pixiv.net/ranking.php?mode=daily&p={ban}&content=illust{the_data}&format=json" # 日榜json文件，一个50张
            try:
                html = session.get(url, headers=header)
            except:
                None
            josn = json.loads(html.text)
            josn = str(josn)
            imgurl = re.findall("'url': '(.*?)',", josn, re.S)
            name = re.findall("'title': '(.*?)',", josn, re.S)

            for c, d in zip(imgurl, name):
                c = str(c)
                id = re.findall("\d\d\d\d\d\d\d\d", c, re.S)[0]
                c = eval(repr(c).replace('c/240x480/img-master', 'img-original'))
                c = eval(repr(c).replace('_master1200', ''))
                author=f"pixiv_day_illust{rand_data}"
                download_result = download(url=c, title=d,author=author,id= id)
                if download_result == True:
                    img_su_num = img_su_num + 1
                else:
                    img_er_num = img_er_num + 1

                text = f"Author:插画日榜\n" \
                       f"Number of pictures:{img_num}\n" \
                       f"Number of successes:{img_su_num}\n" \
                       f"Number of errors:{img_er_num}\n" \
                       f"Progessbar:\n{progessbar(img_su_num, img_num)}"

                try:
                    await client.edit_message_text(chat_id=info.chat.id, message_id=info.message_id, text=text,
                                                   parse_mode="markdown")
                except:
                    None
    elif "weekillustration" in str(call.data):
        for ban in range(1, page_num+1):
            url = f"https://www.pixiv.net/ranking.php?mode=weekly&p={ban}&content=illust{the_data}&format=json"  # 日榜json文件，一个50张
            try:
                html = session.get(url, headers=header)
            except:
                None
            josn = json.loads(html.text)
            josn = str(josn)
            imgurl = re.findall("'url': '(.*?)',", josn, re.S)
            name = re.findall("'title': '(.*?)',", josn, re.S)

            for c, d in zip(imgurl, name):
                c = str(c)
                id = re.findall("\d\d\d\d\d\d\d\d", c, re.S)[0]
                c = eval(repr(c).replace('c/240x480/img-master', 'img-original'))
                c = eval(repr(c).replace('_master1200', ''))
                author=f"pixiv_week_illust{rand_data}"
                download_result = download(url=c, title=d,author=author,id= id)
                if download_result == True:
                    img_su_num = img_su_num + 1
                else:
                    img_er_num = img_er_num + 1

                text = f"Author:插画周榜\n" \
                       f"Number of pictures:{img_num}\n" \
                       f"Number of successes:{img_su_num}\n" \
                       f"Number of errors:{img_er_num}\n" \
                       f"Progessbar:\n{progessbar(img_su_num, img_num)}"

                try:
                    await client.edit_message_text(chat_id=info.chat.id, message_id=info.message_id, text=text,
                                                   parse_mode="markdown")
                except:
                    None
    elif "monthillustration" in str(call.data):
        for ban in range(1, page_num+1):
            url = f"https://www.pixiv.net/ranking.php?mode=monthly&p={ban}&content=illust{the_data}&format=json"  # 日榜json文件，一个50张
            try:
                html = session.get(url, headers=header)
            except:
                None
            josn = json.loads(html.text)
            josn = str(josn)
            imgurl = re.findall("'url': '(.*?)',", josn, re.S)
            name = re.findall("'title': '(.*?)',", josn, re.S)

            for c, d in zip(imgurl, name):
                c = str(c)
                id = re.findall("\d\d\d\d\d\d\d\d", c, re.S)[0]
                c = eval(repr(c).replace('c/240x480/img-master', 'img-original'))
                c = eval(repr(c).replace('_master1200', ''))
                author=f"pixiv_month_illust{rand_data}"
                download_result = download(url=c, title=d,author=author,id= id)
                if download_result == True:
                    img_su_num = img_su_num + 1
                else:
                    img_er_num = img_er_num + 1

                text = f"Author:插画月榜\n" \
                       f"Number of pictures:{img_num}\n" \
                       f"Number of successes:{img_su_num}\n" \
                       f"Number of errors:{img_er_num}\n" \
                       f"Progessbar:\n{progessbar(img_su_num, img_num)}"

                try:
                    await client.edit_message_text(chat_id=info.chat.id, message_id=info.message_id, text=text,
                                                   parse_mode="markdown")
                except:
                    None

    elif "manmale" in str(call.data):
        for ban in range(1, page_num+1):
            url = f"https://www.pixiv.net/ranking.php?mode=male&p={ban}{the_data}&format=json"  # 日榜json文件，一个50张
            try:
                html = session.get(url, headers=header)
            except:
                None
            josn = json.loads(html.text)
            josn = str(josn)
            imgurl = re.findall("'url': '(.*?)',", josn, re.S)
            name = re.findall("'title': '(.*?)',", josn, re.S)

            for c, d in zip(imgurl, name):
                c = str(c)
                id = re.findall("\d\d\d\d\d\d\d\d", c, re.S)[0]
                c = eval(repr(c).replace('c/240x480/img-master', 'img-original'))
                c = eval(repr(c).replace('_master1200', ''))
                author=f"male{rand_data}"
                download_result = download(url=c, title=d,author=author,id= id)
                if download_result == True:
                    img_su_num = img_su_num + 1
                else:
                    img_er_num = img_er_num + 1

                text = f"Author:男性榜\n" \
                       f"Number of pictures:{img_num}\n" \
                       f"Number of successes:{img_su_num}\n" \
                       f"Number of errors:{img_er_num}\n" \
                       f"Progessbar:\n{progessbar(img_su_num, img_num)}"

                try:
                    await client.edit_message_text(chat_id=info.chat.id, message_id=info.message_id, text=text,
                                                   parse_mode="markdown")
                except:
                    None

    elif "female" in str(call.data):
        for ban in range(1, page_num+1):
            url = f"https://www.pixiv.net/ranking.php?mode=female&p={ban}{the_data}&format=json"  # 日榜json文件，一个50张
            try:
                html = session.get(url, headers=header)
            except:
                None
            josn = json.loads(html.text)
            josn = str(josn)
            imgurl = re.findall("'url': '(.*?)',", josn, re.S)
            name = re.findall("'title': '(.*?)',", josn, re.S)

            for c, d in zip(imgurl, name):
                c = str(c)
                id = re.findall("\d\d\d\d\d\d\d\d", c, re.S)[0]
                c = eval(repr(c).replace('c/240x480/img-master', 'img-original'))
                c = eval(repr(c).replace('_master1200', ''))
                author=f"female{rand_data}"
                download_result = download(url=c, title=d,author=author,id= id)
                if download_result == True:
                    img_su_num = img_su_num + 1
                else:
                    img_er_num = img_er_num + 1

                text = f"Author:女性榜\n" \
                       f"Number of pictures:{img_num}\n" \
                       f"Number of successes:{img_su_num}\n" \
                       f"Number of errors:{img_er_num}\n" \
                       f"Progessbar:\n{progessbar(img_su_num, img_num)}"

                try:
                    await client.edit_message_text(chat_id=info.chat.id, message_id=info.message_id, text=text,
                                                   parse_mode="markdown")
                except:
                    None

    elif "rookie" in str(call.data):
        for ban in range(1, page_num+1):
            url = f"https://www.pixiv.net/ranking.php?mode=rookie&p={ban}{the_data}&format=json"  # 日榜json文件，一个50张
            try:
                html = session.get(url, headers=header)
            except:
                None
            josn = json.loads(html.text)
            josn = str(josn)
            imgurl = re.findall("'url': '(.*?)',", josn, re.S)
            name = re.findall("'title': '(.*?)',", josn, re.S)

            for c, d in zip(imgurl, name):
                c = str(c)
                id = re.findall("\d\d\d\d\d\d\d\d", c, re.S)[0]
                c = eval(repr(c).replace('c/240x480/img-master', 'img-original'))
                c = eval(repr(c).replace('_master1200', ''))
                author=f"rookie{rand_data}"
                download_result = download(url=c, title=d,author=author,id= id)
                if download_result == True:
                    img_su_num = img_su_num + 1
                else:
                    img_er_num = img_er_num + 1

                text = f"Author:新人榜\n" \
                       f"Number of pictures:{img_num}\n" \
                       f"Number of successes:{img_su_num}\n" \
                       f"Number of errors:{img_er_num}\n" \
                       f"Progessbar:\n{progessbar(img_su_num, img_num)}"

                try:
                    await client.edit_message_text(chat_id=info.chat.id, message_id=info.message_id, text=text,
                                                   parse_mode="markdown")
                except:
                    None

    elif "original" in str(call.data):
        for ban in range(1, page_num+1):
            url = f"https://www.pixiv.net/ranking.php?mode=original&p={ban}{the_data}&format=json"  # 日榜json文件，一个50张
            try:
                html = session.get(url, headers=header)
            except:
                None
            josn = json.loads(html.text)
            josn = str(josn)
            imgurl = re.findall("'url': '(.*?)',", josn, re.S)
            name = re.findall("'title': '(.*?)',", josn, re.S)

            for c, d in zip(imgurl, name):
                c = str(c)
                id = re.findall("\d\d\d\d\d\d\d\d", c, re.S)[0]
                c = eval(repr(c).replace('c/240x480/img-master', 'img-original'))
                c = eval(repr(c).replace('_master1200', ''))
                author=f"original{rand_data}"
                download_result = download(url=c, title=d,author=author,id= id)
                if download_result == True:
                    img_su_num = img_su_num + 1
                else:
                    img_er_num = img_er_num + 1

                text = f"Author:原创榜\n" \
                       f"Number of pictures:{img_num}\n" \
                       f"Number of successes:{img_su_num}\n" \
                       f"Number of errors:{img_er_num}\n" \
                       f"Progessbar:\n{progessbar(img_su_num, img_num)}"

                try:
                    await client.edit_message_text(chat_id=info.chat.id, message_id=info.message_id, text=text,
                                                   parse_mode="markdown")
                except:
                    None

    if "tg" in str(keywords):
        print("开始压缩")
        sys.stdout.flush()
        name = zip_ya(author)
        print(name)
        print("压缩完成，开始上传")
        del_path(author)
        try:
            # run_upload_rclone(client=client, dir=name, title=name, info=info, file_num=1)
            await client.send_document(chat_id=info.chat.id, document=name, caption=name, progress=progress,
                                       progress_args=(client, info, name,))
            print("uploading")

        except Exception as e:
            print(f"{e}")
            sys.stdout.flush()
            await client.send_message(chat_id=message_chat_id, text="文件上传失败")
            return

        await client.delete_messages(chat_id=message_chat_id, message_ids=message_id)
        os.system("rm '" + name + "'")
        return
    elif "photo" in  str(keywords):
        await client.send_message(chat_id=message_chat_id, text="开始发送，请等待", parse_mode='markdown')
        try:
            img_list = []
            for root, dirs, files in os.walk(author):
                for file in files:
                    try:
                        file_dir = os.path.join(root, file)
                        print(file_dir, file)
                        changpath = os.path.join(os.getcwd(), file_dir)
                        img = Image.open(changpath)
                        if float(float(img.size[0]) / float(img.size[1])) > 20 or float(img.size[0]) + float(img.size[1])>10000:
                            os.remove(file_dir)
                            continue

                        if os.path.getsize(file_dir) < 1024 * 1024 * 10:
                            img_list.append(InputMediaPhoto(media=file_dir, caption=file))
                        else:
                            file_dir = compress_image(outfile=file_dir, mb=10000)
                            img_list.append(InputMediaPhoto(media=file_dir, caption=file))

                        if len(img_list) == 10:
                            await client.send_chat_action(chat_id=message_chat_id, action="upload_photo")
                            print("开始上传")
                            sys.stdout.flush()
                            await client.send_media_group(chat_id=message_chat_id, media=img_list)
                            img_list = []
                    except Exception as e:
                        print(f"标记3 {e}")
                        sys.stdout.flush()

            if len(img_list) != 0:
                await client.send_chat_action(chat_id=message_chat_id, action="upload_photo")
                print("开始上传")
                sys.stdout.flush()
                await client.send_media_group(chat_id=message_chat_id, media=img_list)


        except Exception as e:
            print(f"{e}")
            sys.stdout.flush()
            await client.send_message(chat_id=message_chat_id, text=f"图片发送失败：{e}")
            return

        await client.delete_messages(chat_id=message_chat_id, message_ids=message_id)
        del_path(author)
        await client.send_message(chat_id=message_chat_id, text="本次发送完成", parse_mode='markdown')
        return
    elif "tele" in str(keywords):
        img_list = []
        name_list = []
        for root, dirs, files in os.walk(author):
            for file in files:
                try:
                    file_dir = os.path.join(root, file)
                    print(file_dir, file)

                    if os.path.getsize(file_dir) < 1024 * 512 * 10:
                        print(file_dir, file)

                        info = telegraph.upload.upload_file(file_dir)
                        url = "https://telegra.ph" + info[0]

                        name_list.append(file)
                        img_list.append(url)
                    else:
                        file_dir = compress_image(outfile=file_dir, mb=5000)
                        print(file_dir, file)
                        info = telegraph.upload.upload_file(file_dir)
                        url = "https://telegra.ph" + info[0]

                        name_list.append(file)
                        img_list.append(url)



                except Exception as e:
                    print(f"标记4 {e}")

                    sys.stdout.flush()
                    continue
        try:
            put_text = "<p>Tips:5M以上的图片会被压缩</p><br>"
            for a, b in zip(name_list, img_list):
                put_text = put_text + f"<strong>{a}</strong><br /><img src=\"{b}\" /><br>\n\n"
            print(put_text)

            put_url = put_telegraph(title=f"{author} 作品集", md_text=put_text)
            await client.send_message(chat_id=message_chat_id, text=put_url)



        except Exception as e:
            print(f"标记8 {e}")
            sys.stdout.flush()
            await client.send_message(chat_id=message_chat_id, text="发布失败")
            del_path(author)
            return

        del_path(author)
        return
    else:
        print("开始压缩")
        sys.stdout.flush()
        name = zip_ya(author)
        print(name)
        print("压缩完成，开始上传")
        sys.stdout.flush()
        del_path(author)
        try:
            await run_await_rclone(client=client, dir=name, title=name, info=info, file_num=1, message=info)
            print("uploading")
        except Exception as e:
            print(f"{e}")
            sys.stdout.flush()
            await client.send_message(chat_id=message_chat_id, text="文件上传失败")

        await client.delete_messages(chat_id=message_chat_id, message_ids=message_id)
        os.system("rm '" + name + "'")


#插画排行榜
async def pixiv_topillustration(client, message):
    try:

        page_num=str(message.text).split(" ")[1]
        try:
            rand_data=str(message.text).split(" ")[2]
        except:
            rand_data="nodata"

        new_inline_keyboard = [
            [
                InlineKeyboardButton(
                    text="1",
                    callback_data=f"pixivtopdayillustration {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text="2",
                    callback_data=f"pixivtopweekillustration {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text="3",
                    callback_data=f"pixivtopmonthillustration {page_num} {rand_data}"
                )

            ],
            [
                InlineKeyboardButton(
                    text=f"4",
                    callback_data=f"pixivtopdayillustrationltg {page_num} {rand_data}"
                )
                ,
                InlineKeyboardButton(
                    text=f"5",
                    callback_data=f"pixivtopweekillustrationtg {page_num} {rand_data}"
                ),

                InlineKeyboardButton(
                    text=f"6",
                    callback_data=f"pixivtopmonthillustrationtg {page_num} {rand_data}"
                )

            ],
            [
                InlineKeyboardButton(
                    text="7",
                    callback_data=f"pixivtopdayillustrationphoto {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text="8",
                    callback_data=f"pixivtopweekillustrationphoto {page_num} {rand_data}"
                ),

                InlineKeyboardButton(
                    text="9",
                    callback_data=f"pixivtopmonthillustrationphoto {page_num} {rand_data}"
                )

            ],
            [
                InlineKeyboardButton(
                    text=f"10",
                    callback_data=f"pixivtopdayillustrationtele {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text=f"11",
                    callback_data=f"pixivtopweekillustrationtele {page_num} {rand_data}"
                ),

                InlineKeyboardButton(
                    text=f"12",
                    callback_data=f"pixivtopmonthillustrationtele {page_num} {rand_data}"
                )

            ]

        ]
        text=f"当前下载插画排行榜，请选择下载选项，当前下载页数为{page_num}页\n一页包含50张图片" \
             f"1-打包到网盘(插画日榜)\n" \
             f"2-打包到网盘(插画周榜)\n" \
             f"3-打包到网盘(插画月榜)\n" \
             f"4-打包发送给我(插画日榜)\n" \
             f"5-打包发送给我(插画周榜)\n" \
             f"6-打包发送给我(插画月榜)\n" \
             f"7-发送图片给我(插画日榜)\n" \
             f"8-发送图片给我(插画周榜)\n" \
             f"9-发送图片给我(插画月榜)\n" \
             f"10-网页方式发送(插画日榜)\n" \
             f"11-网页方式发送(插画周榜)\n" \

        new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
        await client.send_message(text=text, chat_id=message.chat.id,
                          parse_mode='markdown', reply_markup=new_reply_markup)

    except Exception as e:
        await client.send_message(chat_id=message.chat.id, text=f"获取作者信息失败:\n{e}")
        print(f"author error {e}")

#综合排行榜
async def pixiv_topall(client, message):
    try:

        page_num=str(message.text).split(" ")[1]
        try:
            rand_data=str(message.text).split(" ")[2]
        except:
            rand_data="nodata"

        #print(author_json)

        new_inline_keyboard = [
            [
                InlineKeyboardButton(
                    text="1",
                    callback_data=f"pixivtopdayall {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text="2",
                    callback_data=f"pixivtopweekall {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text="3",
                    callback_data=f"pixivtopmonthall {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text=f"4",
                    callback_data=f"pixivtopdayallltg {page_num} {rand_data}"
                )

            ],
            [

                InlineKeyboardButton(
                    text=f"5",
                    callback_data=f"pixivtopweekalltg {page_num} {rand_data}"
                ),

                InlineKeyboardButton(
                    text=f"6",
                    callback_data=f"pixivtopmonthalltg {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text="7",
                    callback_data=f"pixivtopdayallphoto {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text="8",
                    callback_data=f"pixivtopweekallphoto {page_num} {rand_data}"
                )

            ],
            [

                InlineKeyboardButton(
                    text="9",
                    callback_data=f"pixivtopmonthallphoto {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text=f"10",
                    callback_data=f"pixivtopdayalltele {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text=f"11",
                    callback_data=f"pixivtopweekalltele {page_num} {rand_data}"
                ),

                InlineKeyboardButton(
                    text=f"12",
                    callback_data=f"pixivtopmonthalltele {page_num} {rand_data}"
                )

            ],
            [
                InlineKeyboardButton(
                    text=f"13",
                    callback_data=f"pixivtopmanmale {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text=f"14",
                    callback_data=f"pixivtopmanmaletg {page_num} {rand_data}"
                ),

                InlineKeyboardButton(
                    text=f"15",
                    callback_data=f"pixivtopmanmalephoto {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text=f"16",
                    callback_data=f"pixivtopmanmaletele {page_num} {rand_data}"
                )

            ],
            [
                InlineKeyboardButton(
                    text=f"17",
                    callback_data=f"pixivtopfemale {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text=f"18",
                    callback_data=f"pixivtopfemaletg {page_num} {rand_data}"
                ),

                InlineKeyboardButton(
                    text=f"19",
                    callback_data=f"pixivtopfemalephoto {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text=f"20",
                    callback_data=f"pixivtopfemaletele {page_num} {rand_data}"
                )

            ],
            [
                InlineKeyboardButton(
                    text=f"21",
                    callback_data=f"pixivtoprookie {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text=f"22",
                    callback_data=f"pixivtoprookietg {page_num} {rand_data}"
                ),

                InlineKeyboardButton(
                    text=f"23",
                    callback_data=f"pixivtoprookiephoto {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text=f"24",
                    callback_data=f"pixivtoprookietele {page_num} {rand_data}"
                )

            ],
            [
                InlineKeyboardButton(
                    text=f"25",
                    callback_data=f"pixivtoporiginal {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text=f"26",
                    callback_data=f"pixivtoporiginaltg {page_num} {rand_data}"
                ),

                InlineKeyboardButton(
                    text=f"27",
                    callback_data=f"pixivtoporiginalphoto {page_num} {rand_data}"
                ),
                InlineKeyboardButton(
                    text=f"28",
                    callback_data=f"pixivtoporiginaltele {page_num} {rand_data}"
                )

            ]

        ]
        text=f"当前下载综合排行榜，请选择下载选项，当前下载页数为{page_num}页\n一页包含50张图片\n" \
             f"1-打包到网盘(日榜综合)\n" \
             f"2-打包到网盘(周榜综合)\n" \
             f"3-打包到网盘(月榜综合)\n" \
             f"4-打包发送给我(日榜综合)\n" \
             f"5-打包发送给我(周榜综合)\n" \
             f"6-打包发送给我(月榜综合)\n" \
             f"7-发送图片给我(日榜综合)\n" \
             f"8-发送图片给我(周榜综合)\n" \
             f"9-发送图片给我(月榜综合)\n" \
             f"10-网页方式发送(日榜综合)\n" \
             f"11-网页方式发送(周榜综合)\n" \
             f"12-网页方式发送(月榜综合)\n" \
             f"13-打包到网盘(男性榜)\n" \
             f"14-打包发送给我(男性榜)\n" \
             f"15-发送图片给我(男性榜)\n" \
             f"16-网页方式发送(男性榜)\n"    \
             f"17-打包到网盘(女性榜)\n" \
             f"18-打包发送给我(女性榜)\n" \
             f"19-发送图片给我(女性榜)\n" \
             f"20-网页方式发送(新人榜)\n" \
             f"21-打包到网盘(新人榜)\n" \
             f"22-打包发送给我(新人榜)\n" \
             f"23-发送图片给我(新人榜)\n" \
             f"24-网页方式发送(新人榜)\n" \
             f"25-打包到网盘(原创榜)\n" \
             f"26-打包发送给我(原创榜)\n" \
             f"27-发送图片给我(原创榜)\n" \
             f"28-网页方式发送(原创榜)\n"

        new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
        await client.send_message(text=text, chat_id=message.chat.id,
                          parse_mode='markdown', reply_markup=new_reply_markup)

    except Exception as e:
        await client.send_message(chat_id=message.chat.id, text=f"获取作者信息失败:\n{e}")
        print(f"author error {e}")

async def author(client, message):
    try:

        author_id=str(message.text).split(" ")[1]
        author_url=f"https://www.pixiv.net/users/{author_id}"

        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 5.8; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
            'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
        }

        author_result=requests.get(url=author_url,headers=header)
        #print(author_result.text)


        author_about = re.findall("<meta name=\"preload-data\" id=\"meta-preload-data\" content='(.*?)'", author_result.text, re.S)[0]

        #print(author_about)
        author_json=json.loads(str(author_about))
        #print(author_json)


        author_text=f"画师:`{author_json['user'][str(author_id)]['name']}`\n" \
                    f"画师ID:`{author_id}`\n" \
                    f"粉丝数:`{author_json['user'][str(author_id)]['following']}`\n"  \
                    f"画师简介:\n`{author_json['user'][str(author_id)]['comment']}`\n"
        print(author_text)
        author_image=author_json['user'][str(author_id)]['imageBig']
        print(author_image)
        new_inline_keyboard = [
            [
                InlineKeyboardButton(
                    text="打包到网盘",
                    callback_data=f"pixivuser {author_id}"
                ),
                InlineKeyboardButton(
                    text=f"打包发送给我",
                    callback_data=f"pixivusertg {author_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="发送图片给我",
                    callback_data=f"pixivuserphoto {author_id}"
                ),
                InlineKeyboardButton(
                    text=f"网页方式发送",
                    callback_data=f"pixivusertele {author_id}"
                )
            ]

        ]
        img = requests.get(url=author_image,headers=header)
        img_name = f"{message.chat.id}{message.message_id}.png"
        with open(img_name, 'wb') as f:
            f.write(img.content)
            f.close()
        new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
        await client.send_photo(caption=author_text[0:1024], photo=img_name, chat_id=message.chat.id,
                          parse_mode='markdown', reply_markup=new_reply_markup)
        os.remove(img_name)
    except Exception as e:
        await client.send_message(chat_id=message.chat.id, text=f"获取作者信息失败:\n{e}")
        print(f"author error {e}")


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

# 下载模块
def download(url, title,author, id):
    global session,header
    path = author
    if not os.path.exists(path):
        os.mkdir(path)
    title = str(title)
    id = str(id)
    title = eval(repr(title).replace('\\', ''))
    title = eval(repr(title).replace('/', ''))
    title = eval(repr(title).replace('?', ''))
    title = eval(repr(title).replace('*', ''))
    title = eval(repr(title).replace('・', ''))
    title = eval(repr(title).replace('！', ''))
    title = eval(repr(title).replace('|', ''))
    title = eval(repr(title).replace(' ', ''))
    r = session.get(url, headers=header)
    if r.status_code==404:
        url=str(url).replace("jpg","png")
        r = session.get(url, headers=header)
        if r.status_code==404:
            return False
    try:
        if "jpg" in url:
            with open(f'{author}/{title}.jpg', 'wb') as f:
                f.write(r.content)
            print("下载成功" + title)


            return True
        elif "png" in url:
            with open(f'{author}/{title}.png', 'wb') as f:
                f.write(r.content)
            print( "下载成功" + title +url)
            return True

    except Exception as e:
        print("下载失败:" + title )
        print(e)
        return False

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




async def start_download_pixiv(client, call):


        keywords = str(call.data)
        keywords = keywords.split(" ")[1]
        print(keywords)
        artistid=keywords
        idurl = f"https://www.pixiv.net/ajax/user/{artistid}/profile/all"
        print(idurl)
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 5.8; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
        }
        html2 = requests.get(url=idurl, headers=header)
        print(html2)
        message_id = call.message.message_id
        message_chat_id = call.message.chat.id

        illusts=html2.json()['body']['illusts']

        info = await client.send_message(chat_id=message_chat_id, text="开始下载", parse_mode='markdown')
        print(info)
        print(info.chat)
        img_num=len(illusts)
        img_su_num=0
        img_er_num=0
        for id in illusts:
            print(id)
            info_url = f"https://www.pixiv.net/touch/ajax/illust/details?illust_id={id}"
            ht = requests.get(url=info_url, headers=header)
            info_json=ht.json()
            img_url=info_json['body']['illust_details']['url_big']
            title=info_json['body']['illust_details']['meta']['title']+f"id-{id}"

            #.author_details.profile_img.main
            author=f"{info_json['body']['author_details']['user_name']}"

            title=str(title).replace("#","").replace(author,"").replace(":","").replace("@","").replace("/","")
            author=str(author).replace(":","").replace("@","").replace("/","")
            print(img_url)

            download_result=download(url=img_url,title=title,author=keywords,id=id)
            if download_result==True:
                img_su_num=img_su_num+1
            else:
                img_er_num=img_er_num+1

            text=f"Author:{author}\n" \
                 f"Number of pictures:{img_num}\n" \
                 f"Number of successes:{img_su_num}\n" \
                 f"Number of errors:{img_er_num}\n" \
                 f"Progessbar:\n{progessbar(img_su_num,img_num)}"

            await client.edit_message_text(chat_id=info.chat.id, message_id=info.message_id, text=text, parse_mode="markdown")
        print("开始压缩")
        sys.stdout.flush()
        name = zip_ya(keywords)
        print(name)
        print("压缩完成，开始上传")
        sys.stdout.flush()
        del_path(keywords)
        try:
            await run_await_rclone(client=client,dir=name,title=name,info=info,file_num=1,message=info)
            print("uploading")
        except Exception as e:
            print(f"{e}")
            sys.stdout.flush()
            await client.send_message(chat_id=message_chat_id, text="文件上传失败")

        await client.delete_messages(chat_id=message_chat_id, message_ids=message_id)
        os.system("rm '" + name + "'")


async def start_download_id(client, message):
    # print(message)
    keywords = str(message.text)
    keywords = keywords.replace("/pixivpid ", "")
    print(keywords)
    info_url = f"https://www.pixiv.net/touch/ajax/illust/details?illust_id={keywords}"
    ht = requests.get(url=info_url, headers=header)
    info_json = ht.json()
    imgurl = info_json['body']['illust_details']['url_big']
    r = session.get(url=imgurl, headers=header)
    title = info_json['body']['illust_details']['meta']['title']

    # .author_details.profile_img.main
    author = f"{info_json['body']['author_details']['user_name']}"
    if "jpg" in imgurl:
        with open(f'{keywords}.jpg', 'wb') as f:
            f.write(r.content)
            imgname=f"{keywords}.jpg"
    elif "png" in imgurl:
        with open(f'{keywords}.png', 'wb') as f:
            f.write(r.content)
            imgname = f"{keywords}.png"
    send_text=f"{title}\nAuthor:{author}\nPid:{keywords}"
    await client.send_photo(chat_id=message.chat.id,photo=imgname , caption=send_text)
    os.system("rm '" + imgname + "'")

def progress(current, total,client,message,name):

    print(f"{current * 100 / total:.1f}%")
    pro=f"{current * 100 / total:.1f}%"
    try:
        client.edit_message_text(chat_id=message.chat.id,message_id=message.message_id,text=f"{name}\n上传中:{pro}")
    except Exception as e:
        print("e")

async def start_download_pixivtg(client, call):
    # print(message)
    keywords = str(call.data)
    keywords = keywords.split(" ")[1]
    print(keywords)
    artistid = keywords
    idurl = f"https://www.pixiv.net/ajax/user/{artistid}/profile/all"
    print(idurl)
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 5.8; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
    }
    html2 = requests.get(url=idurl, headers=header)
    print(html2)
    message_id = call.message.message_id
    message_chat_id = call.message.chat.id

    illusts = html2.json()['body']['illusts']
    info = await client.send_message(chat_id=message_chat_id, text="开始下载")
    img_num = len(illusts)
    img_su_num = 0
    img_er_num = 0
    for id in illusts:
        print(id)
        info_url = f"https://www.pixiv.net/touch/ajax/illust/details?illust_id={id}"
        ht = requests.get(url=info_url, headers=header)
        info_json = ht.json()
        img_url = info_json['body']['illust_details']['url_big']
        title = info_json['body']['illust_details']['meta']['title'] + f"id-{id}"

        # .author_details.profile_img.main
        author = f"{info_json['body']['author_details']['user_name']}"

        title = str(title).replace("#", "").replace(author, "").replace(":", "").replace("@", "").replace("/", "")
        author = str(author).replace(":", "").replace("@", "").replace("/", "")
        print(img_url)

        download_result = download(url=img_url, title=title, author=keywords, id=id)
        if download_result == True:
            img_su_num = img_su_num + 1
        else:
            img_er_num = img_er_num + 1

        text = f"Author:{author}\n" \
               f"Number of pictures:{img_num}\n" \
               f"Number of successes:{img_su_num}\n" \
               f"Number of errors:{img_er_num}\n" \
               f"Progessbar:\n{progessbar(img_su_num, img_num)}"

        await client.edit_message_text(chat_id=info.chat.id, message_id=info.message_id, text=text, parse_mode="markdown")
    print("开始压缩")
    sys.stdout.flush()
    name = zip_ya(keywords)
    print(name)
    print("压缩完成，开始上传")
    del_path(keywords)
    try:
        #run_upload_rclone(client=client, dir=name, title=name, info=info, file_num=1)
        await client.send_document(chat_id=info.chat.id, document=name, caption=name, progress=progress, progress_args=(client,info,name,))
        print("uploading")

    except Exception as e:
        print(f"{e}")
        sys.stdout.flush()
        await client.send_message(chat_id=message_chat_id, text="文件上传失败")
        return

    await client.delete_messages(chat_id=message_chat_id, message_ids=message_id)
    os.system("rm '" + name + "'")
    return


async def start_download_pixivphoto(client, call):
    # print(message)
    keywords = str(call.data)
    keywords = keywords.split(" ")[1]
    print(keywords)
    artistid = keywords
    idurl = f"https://www.pixiv.net/ajax/user/{artistid}/profile/all"
    print(idurl)
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 5.8; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
    }
    html2 = requests.get(url=idurl, headers=header)
    print(html2)
    message_id = call.message.message_id
    message_chat_id = call.message.chat.id

    illusts = html2.json()['body']['illusts']
    info = await client.send_message(chat_id=message_chat_id , text="开始下载")
    img_num = len(illusts)
    img_su_num = 0
    img_er_num = 0
    for id in illusts:
        print(id)
        info_url = f"https://www.pixiv.net/touch/ajax/illust/details?illust_id={id}"
        ht = requests.get(url=info_url, headers=header)
        info_json = ht.json()
        img_url = info_json['body']['illust_details']['url_big']
        title = info_json['body']['illust_details']['meta']['title'] + f"id-{id}"

        # .author_details.profile_img.main
        author = f"{info_json['body']['author_details']['user_name']}"

        title = str(title).replace("#", "").replace(author, "").replace(":", "").replace("@", "").replace("/", "")
        author = str(author).replace(":", "").replace("@", "").replace("/", "")
        print(img_url)

        download_result = download(url=img_url, title=title, author=keywords, id=id)
        if download_result == True:
            img_su_num = img_su_num + 1
        else:
            img_er_num = img_er_num + 1

        text = f"Author:{author}\n" \
               f"Number of pictures:{img_num}\n" \
               f"Number of successes:{img_su_num}\n" \
               f"Number of errors:{img_er_num}\n" \
               f"Progessbar:\n{progessbar(img_su_num, img_num)}"

        await client.edit_message_text(chat_id=info.chat.id, message_id=info.message_id, text=text, parse_mode="markdown")


    try:
        img_list=[]
        for root, dirs, files in os.walk(keywords):
            for file in files:
                try:
                    file_dir = os.path.join(root, file)
                    print(file_dir, file)

                    changpath = os.path.join(os.getcwd(), file_dir)
                    img = Image.open(changpath)
                    if float(float(img.size[0]) / float(img.size[1])) > 20 or float(img.size[0]) + float(img.size[1])>10000:
                        os.remove(file_dir)
                        continue

                    if os.path.getsize(file_dir) < 1024*1024* 10:
                        img_list.append(InputMediaPhoto(media=file_dir, caption=file))
                    else:
                        file_dir=compress_image(outfile=file_dir,mb=10000)
                        img_list.append(InputMediaPhoto(media=file_dir, caption=file))

                    if len(img_list)==10:
                        await client.send_chat_action(chat_id=message_chat_id ,action="upload_photo")
                        print("开始上传")
                        sys.stdout.flush()
                        await client.send_media_group(chat_id=message_chat_id ,media=img_list)
                        img_list = []
                except Exception as e:
                    print(f"标记3 {e}")
                    sys.stdout.flush()

        if len(img_list) != 0:
            await client.send_chat_action(chat_id=message_chat_id , action="upload_photo")
            print("开始上传")
            sys.stdout.flush()
            await client.send_media_group(chat_id=message_chat_id , media=img_list)


    except Exception as e:
        print(f"{e}")
        sys.stdout.flush()
        await client.send_message(chat_id=message_chat_id , text="图片上传失败")
        return

    await client.delete_messages(chat_id=message_chat_id , message_ids=message_id)
    del_path(keywords)
    return

def put_telegraph(title,md_text):
  tele = Telegraph()

  tele.create_account(short_name='Bot')
  response = tele.create_page(
      title=title,
      html_content=md_text
  )

  text_url='https://telegra.ph/{}'.format(response['path'])
  return text_url


async def start_download_pixivtele(client, call):

    keywords = str(call.data)
    keywords = keywords.split(" ")[1]
    artistid = keywords
    idurl = f"https://www.pixiv.net/ajax/user/{artistid}/profile/all"
    print(idurl)
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 5.8; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
    }
    html2 = requests.get(url=idurl, headers=header)
    print(html2)
    message_id = call.message.message_id
    message_chat_id = call.message.chat.id

    illusts = html2.json()['body']['illusts']
    info = await client.send_message(chat_id=message_chat_id, text="开始下载")
    img_num = len(illusts)
    img_su_num = 0
    img_er_num = 0
    for id in illusts:
        print(id)
        info_url = f"https://www.pixiv.net/touch/ajax/illust/details?illust_id={id}"
        ht = requests.get(url=info_url, headers=header)
        info_json = ht.json()
        img_url = info_json['body']['illust_details']['url_big']
        title = info_json['body']['illust_details']['meta']['title'] + f"id-{id}"

        # .author_details.profile_img.main
        author = f"{info_json['body']['author_details']['user_name']}"

        title = str(title).replace("#", "").replace(author, "").replace(":", "").replace("@", "").replace("/", "")
        author = str(author).replace(":", "").replace("@", "").replace("/", "")
        print(img_url)

        download_result = download(url=img_url, title=title, author=keywords, id=id)
        if download_result == True:
            img_su_num = img_su_num + 1
        else:
            img_er_num = img_er_num + 1

        text = f"Author:{author}\n" \
               f"Number of pictures:{img_num}\n" \
               f"Number of successes:{img_su_num}\n" \
               f"Number of errors:{img_er_num}\n" \
               f"Progessbar:\n{progessbar(img_su_num, img_num)}"

        await client.edit_message_text(chat_id=info.chat.id, message_id=info.message_id, text=text, parse_mode="markdown")



    img_list=[]
    name_list = []

    for root, dirs, files in os.walk(keywords):
        for file in files:
            try:
                file_dir = os.path.join(root, file)
                print(file_dir, file)

                if os.path.getsize(file_dir) < 1024*512* 10:
                    print(file_dir, file)

                    info = telegraph.upload.upload_file(file_dir)
                    url = "https://telegra.ph" + info[0]

                    name_list.append(file)
                    img_list.append(url)
                else:
                    file_dir=compress_image(outfile=file_dir,mb=5000)
                    print(file_dir, file)
                    info = telegraph.upload.upload_file(file_dir)
                    url = "https://telegra.ph" + info[0]

                    name_list.append(file)
                    img_list.append(url)



            except Exception as e:
                print(f"标记4 {e}")

                sys.stdout.flush()
                continue
    try:
        put_text = "<p>Tips:5M以上的图片会被压缩</p><br>"
        for a, b in zip(name_list, img_list):
            put_text = put_text + f"<strong>{a}</strong><br /><img src=\"{b}\" /><br>\n\n"
        print(put_text)

        put_url=put_telegraph(title=f"{keywords} 作品集", md_text=put_text)
        await client.send_message(chat_id=message_chat_id, text=put_url)



    except Exception as e:
        print(f"标记8 {e}")
        sys.stdout.flush()
        await client.send_message(chat_id=message_chat_id, text="发布失败")
        del_path(keywords)
        return

    del_path(keywords)
    return


