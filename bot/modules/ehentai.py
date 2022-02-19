# -*- coding: utf-8 -*-
import requests
import time
import os
from bs4 import BeautifulSoup
import re
import zipfile
import os
import telegraph
import sys
from modules.control import run_await_rclone
from modules.pixiv import compress_image, put_telegraph
from lxml import etree
from pyrogram.types import InlineKeyboardMarkup,InlineKeyboardButton

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 '
                  'Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Upgrade-Insecure-Requests': '1'}

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

def progress(current, total,client,message,name):

    print(f"{current * 100 / total:.1f}%")
    pro=f"{current * 100 / total:.1f}%"
    try:
        client.edit_message_text(chat_id=message.chat.id,message_id=message.message_id,text=f"{name}\n上传中:{pro}")
    except Exception as e:
        print(f"{e}")

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

def saveFile(url, path):

    response = requests.get(url, headers=headers)
    with open(path, 'wb') as f:
        f.write(response.content)
        f.flush()


def getPicUrl(url):

    site_2 = requests.get(url, headers=headers)
    content_2 = site_2.text
    soup_2 = BeautifulSoup(content_2, 'lxml')
    imgs = soup_2.find_all(id="img")
    for img in imgs:
        picSrc = img['src']
        return picSrc

async def getWebsite(url, time1, spath,pagenum,client, info):

    site = requests.get(url, headers=headers)
    content = site.text
    soup = BeautifulSoup(content, 'lxml')
    divs = soup.find_all(class_='gdtm')
    title = soup.h1.get_text()
    rr = r"[\/\\\:\*\?\"\<\>\|]"
    new_title2 = re.sub(rr, "-", title)
    page = 0
    i = 0
    for div in divs:
        picUrl = div.a.get('href')
        page = page + 1
        print('下载中 ' + new_title2 + str(page) + '.jpg')


        try:
            saveFile(getPicUrl(picUrl), spath + new_title2 + '/' + str(page).zfill(3) + '.jpg')
            print('下载成功: ' + new_title2 + str(page) + '.jpg')
            barop = progessbar(page, pagenum)
            text=f"下载进度:\n{barop}"
            await client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                           parse_mode='markdown')

        except:
            print('无法下载' + new_title2 + str(page) + '.jpg')
        else:
            print('成功')
            i = i + 1
    print('成功 下载' + str(page) + ' 个文件,' + str(i))
    endTime1 = time.time()
    m, s = divmod(int(endTime1 - time1), 60)
    h, m = divmod(m, 60)
    print("%02d时%02d分%02d秒" % (h, m, s))
    if h != 0:
        last_time = "%d时%d分%d秒" % (h, m, s)
    elif h == 0 and m != 0:
        last_time = "%d分%d秒" % (m, s)
    else:
        last_time = "%d秒" % s

    text=f"下载完成:`{new_title2}`\n成功下载:`{str(page)}个文件`，耗时：`{last_time}`"
    await client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                   parse_mode='markdown')
    filepath=spath + new_title2
    return filepath


async def single_download_call(client, call):
    try:
        message=call.message
        url = call.data.split(" ", 1)[1]



        spath = "/ehentai/"
        if os.path.exists(spath)==False:
            os.mkdir(spath)

        print('保存路径:', spath)
        startTime1 = time.time()
        print('--获取信息中--')

        info = await client.send_message(chat_id=message.chat.id, text='--获取信息中--', parse_mode='markdown')
        try:


            site = requests.get(url, headers=headers)
            content = site.text
            soup = BeautifulSoup(content, 'lxml')
            divs = soup.find_all(class_='gdtm')
            title = str(soup.h1.get_text())
            page = 0
            for div in divs:
                page = page + 1
        except Exception as e:
            print(f'错误,输入或网络问题:{e}')
            await client.edit_message_text(text=f'错误,输入或网络问题:{e}', chat_id=info.chat.id, message_id=info.message_id,
                                           parse_mode='markdown')

        else:
            print('本子名 ' + title + ',共 ' + str(page) + ' 页,开始爬取')
            text='本子名 ' + title + ',共 ' + str(page) + ' 页,开始爬取'
            await client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                           parse_mode='markdown')
            rr = r"[\/\\\:\*\?\"\<\>\|]"
            new_title = re.sub(rr, "-", title)
            if os.path.exists(spath + new_title):
                path = await getWebsite(url, startTime1, spath,page,client, info)
            else:
                os.mkdir(spath + new_title)
                path = await getWebsite(url, startTime1, spath,page,client, info)

        try:
            choice = call.data.split(" ")[2]
        except:


            try:
                name = zip_ya(path)
                print(name)
                print("压缩完成，开始上传")
                await client.edit_message_text(text="压缩完成，开始上传", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
                del_path(path)
            except Exception as e:
                await client.edit_message_text(text=f"压缩失败 : {e}", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
                return
            try:
                await client.send_document(chat_id=info.chat.id, document=name, caption=name, progress=progress,
                                           progress_args=(client, info, name,))

                print("uploading")
                return
            except Exception as e:
                print(f"{e}")
                sys.stdout.flush()
                await client.edit_message_text(text=f"文件上传失败 : {e}", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
            os.system("rm '" + name + "'")
            return

        if choice=="tg":
            try:
                name = zip_ya(path)
                print(name)
                print("压缩完成，开始上传")
                await client.edit_message_text(text="压缩完成，开始上传", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
                del_path(path)
            except Exception as e:
                await client.edit_message_text(text=f"压缩失败 : {e}", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
                return
            try:
                await client.send_document(chat_id=info.chat.id, document=name, caption=name, progress=progress,
                                           progress_args=(client, info, name,))

                print("uploading")
            except Exception as e:
                print(f"{e}")
                sys.stdout.flush()
                await client.edit_message_text(text=f"文件上传失败 : {e}", chat_id=info.chat.id,
                                               message_id=info.message_id,
                                               parse_mode='markdown')
            os.system("rm '" + name + "'")

        elif choice=="rclone":
            try:
                name = zip_ya(path)
                print(name)
                print("压缩完成，开始上传")
                await client.edit_message_text(text="压缩完成，开始上传", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
                del_path(path)
            except Exception as e:
                await client.edit_message_text(text=f"压缩失败 : {e}", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
                return
            try:
                await client.delete_messages(info.chat.id, info.message_id)
                await run_await_rclone(dir=name, title=name, info=info, file_num=1, client=client, message=info,gid=0)
                print("uploading")
            except Exception as e:
                print(f"{e}")
                sys.stdout.flush()
                client.send_message(info.chat.id, text=f"文件上传失败:\n{e}")
            
            os.system("rm '" + name + "'")

        elif choice=="tele" :
            img_list = []
            name_list = []

            filelists = os.listdir(path)
            sort_num_first = list(filelists)

            sort_num_first.sort()
            sorted_file = []
            for sort_num in sort_num_first:
                for file in filelists:
                    if str(sort_num) == file:
                        sorted_file.append( file)

            for file in sorted_file:
                    try:
                        if "jpg" not in str(file) and "png" not in str(file):
                            continue
                        file_dir = os.path.join(path, file)
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
                put_text = ""
                for  b in img_list:
                    put_text = put_text + f"<strong></strong><br /><img src=\"{b}\" /><br>\n\n"
                print(put_text)

                put_url = put_telegraph(title=f"{os.path.basename(path)}", md_text=put_text)
                print(put_url)
                await client.send_message(chat_id=message.chat.id, text=put_url)



            except Exception as e:
                print(f"标记8 {e}")
                sys.stdout.flush()
                await client.send_message(chat_id=message.chat.id, text="发布失败")
                del_path(path)
                return

            del_path(path)
            return

    except Exception as e:
        print(f"single_download:{e}")
        await client.send_message(chat_id=message.chat.id, text=f'下载失败:{e}', parse_mode='markdown')

async def single_download(client, message):
    try:
        url = message.text.split(" ", 1)[1]



        spath = "/ehentai/"
        if os.path.exists(spath)==False:
            os.mkdir(spath)

        print('保存路径:', spath)
        startTime1 = time.time()
        print('--获取信息中--')

        info = await client.send_message(chat_id=message.chat.id, text='--获取信息中--', parse_mode='markdown')
        try:


            site = requests.get(url, headers=headers)
            content = site.text
            soup = BeautifulSoup(content, 'lxml')
            divs = soup.find_all(class_='gdtm')
            title = str(soup.h1.get_text())
            page = 0
            for div in divs:
                page = page + 1
        except Exception as e:
            print(f'错误,输入或网络问题:{e}')
            await client.edit_message_text(text=f'错误,输入或网络问题:{e}', chat_id=info.chat.id, message_id=info.message_id,
                                           parse_mode='markdown')

        else:
            print('本子名 ' + title + ',共 ' + str(page) + ' 页,开始爬取')
            text='本子名 ' + title + ',共 ' + str(page) + ' 页,开始爬取'
            await client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                           parse_mode='markdown')
            rr = r"[\/\\\:\*\?\"\<\>\|]"
            new_title = re.sub(rr, "-", title)
            if os.path.exists(spath + new_title):
                path = await getWebsite(url, startTime1, spath,page,client, info)
            else:
                os.mkdir(spath + new_title)
                path = await getWebsite(url, startTime1, spath,page,client, info)

        try:
            choice = message.text.split(" ")[2]
        except:


            try:
                name = zip_ya(path)
                print(name)
                print("压缩完成，开始上传")
                await client.edit_message_text(text="压缩完成，开始上传", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
                del_path(path)
            except Exception as e:
                await client.edit_message_text(text=f"压缩失败 : {e}", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
                return
            try:
                await client.send_document(chat_id=info.chat.id, document=name, caption=name, progress=progress,
                                           progress_args=(client, info, name,))

                print("uploading")
                return
            except Exception as e:
                print(f"{e}")
                sys.stdout.flush()
                await client.edit_message_text(text=f"文件上传失败 : {e}", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
            os.system("rm '" + name + "'")
            return

        if choice=="tg":
            try:
                name = zip_ya(path)
                print(name)
                print("压缩完成，开始上传")
                await client.edit_message_text(text="压缩完成，开始上传", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
                del_path(path)
            except Exception as e:
                await client.edit_message_text(text=f"压缩失败 : {e}", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
                return
            try:
                await client.send_document(chat_id=info.chat.id, document=name, caption=name, progress=progress,
                                           progress_args=(client, info, name,))

                print("uploading")
            except Exception as e:
                print(f"{e}")
                sys.stdout.flush()
                await client.edit_message_text(text=f"文件上传失败 : {e}", chat_id=info.chat.id,
                                               message_id=info.message_id,
                                               parse_mode='markdown')
            os.system("rm '" + name + "'")

        elif choice=="rclone":
            try:
                name = zip_ya(path)
                print(name)
                print("压缩完成，开始上传")
                await client.edit_message_text(text="压缩完成，开始上传", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
                del_path(path)
            except Exception as e:
                await client.edit_message_text(text=f"压缩失败 : {e}", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
                return
            try:
                await client.delete_messages(info.chat.id, info.message_id)
                await run_await_rclone(dir=name, title=name, info=info, file_num=1, client=client, message=info,gid=0)
                print("uploading")
            except Exception as e:
                print(f"{e}")
                sys.stdout.flush()
                client.send_message(info.chat.id, text=f"文件上传失败:\n{e}")
            
            os.system("rm '" + name + "'")

        elif choice=="tele" :
            img_list = []
            name_list = []

            filelists = os.listdir(path)
            sort_num_first = list(filelists)

            sort_num_first.sort()
            sorted_file = []
            for sort_num in sort_num_first:
                for file in filelists:
                    if str(sort_num) == file:
                        sorted_file.append( file)

            for file in sorted_file:
                    try:
                        if "jpg" not in str(file) and "png" not in str(file):
                            continue
                        file_dir = os.path.join(path, file)
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
                put_text = ""
                for  b in img_list:
                    put_text = put_text + f"<strong></strong><br /><img src=\"{b}\" /><br>\n\n"
                print(put_text)

                put_url = put_telegraph(title=f"{os.path.basename(path)}", md_text=put_text)
                print(put_url)
                await client.send_message(chat_id=message.chat.id, text=put_url)



            except Exception as e:
                print(f"标记8 {e}")
                sys.stdout.flush()
                await client.send_message(chat_id=message.chat.id, text="发布失败")
                del_path(path)
                return

            del_path(path)
            return

    except Exception as e:
        print(f"single_download:{e}")
        await client.send_message(chat_id=message.chat.id, text=f'下载失败:{e}', parse_mode='markdown')


async def get_search_ehentai_info(client, message):
    if "CallbackQuery" in str(message):

        message=message.message
        keyword = str(message.caption).split("\n", 1)[0]
        keyword=str(keyword).replace("标题:","")
        print(f"搜索词：{keyword}")
    else:
        keyword = str(message.text).split(" ", 1)[1]

    search_url = f"https://e-hentai.org/?f_search={keyword}&advsearch=1&f_sname=on&f_stags=on&f_sdesc=on&f_spf=&f_spt="

    search_result = requests.get(search_url, headers=headers)

    lxml_result = etree.HTML(search_result.text)
    title_list = lxml_result.xpath('/html/body/div[2]/div[2]/table[2]/tr/td[3]/a/div[1]/text()')
    link_list = lxml_result.xpath('/html/body/div[2]/div[2]/table[2]/tr/td[3]/a/@href')
    img_list = lxml_result.xpath('/html/body/div[2]/div[2]/table[2]/tr/td[2]/div[2]/div[1]/img/@data-src')
    # print(title_list)
    if len(title_list)==0:
        await client.send_message(chat_id=message.chat.id, text="搜索无结果", parse_mode='markdown')
        return
    for title, link, img in zip(title_list, link_list, img_list):
        print(title, link, img)
        text = f"标题:{title}\n链接地址:{link}"
        new_inline_keyboard = [
            [
                InlineKeyboardButton(
                    text="上传网盘",
                    callback_data=f"ehentai {link} rclone"
                )], [
                InlineKeyboardButton(
                    text="发送本子到TG",
                    callback_data=f"ehentai {link} tg"
                )], [
                InlineKeyboardButton(
                    text="网页格式发送",
                    callback_data=f"ehentai {link} tele"
                )
            ]
        ]

        new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
        await client.send_photo(chat_id=message.chat.id, photo=str(img), caption=text, reply_markup=new_reply_markup,
                                parse_mode='markdown')



