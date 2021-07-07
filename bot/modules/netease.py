import requests
from config import aria2
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import time
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import Picture, FLAC
from modules.control import run_rclone

def progress(current, total,client,message,name):

    print(f"{current * 100 / total:.1f}%")
    pro=f"{current * 100 / total:.1f}%"
    try:
        client.edit_message_text(chat_id=message.chat.id,message_id=message.message_id,text=f"{name}\n上传中:{pro}")
    except Exception as e:
        print(f"{e}")

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

def hum_convert(value):
    value=float(value)
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f%s" % (value, units[i])
        value = value / size


async def search_song_list(client, message):
    try:
        keyword = message.text.split(" ", 1)[1]
        search_song_url = f"https://benchaonetease.vercel.app/search?keywords={keyword}"
        search_song_info = requests.get(url=search_song_url)
        print(search_song_info.json()['result']['songs'])
        num = 1
        new_inline_keyboard=[]
        temp_list=[]
        text=f"歌曲搜索结果:\n"
        for a in list(search_song_info.json()['result']['songs']):
            print(f"{num}-`{a['name']}-{a['artists'][0]['name']}`\n")
            text=text+f"{num}-`{a['name']}-{a['artists'][0]['name']}`\n"
            temp_list.append(InlineKeyboardButton(
                    text=f"{num}",
                    callback_data=f"editsong {a['id']}"
                ))
            if num%5==0:
                new_inline_keyboard.append(temp_list)
                temp_list=[]
            if num==15:
                break
            num=num+1


        new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
        await client.send_message(text=text, chat_id=message.chat.id,
                                  parse_mode='markdown', reply_markup=new_reply_markup)
    except Exception as e:
        print(f"search_song_list error {e}")
        await client.send_message(text=f"搜索歌曲失败:·{e}·", chat_id=message.chat.id,
                                  parse_mode='markdown')

async def edit_song_info(client, call):
    message_id = call.message.message_id
    message_chat_id = call.message.chat.id
    client.answer_callback_query(callback_query_id=call.id, text="开始获取歌曲信息", cache_time=3)
    try:
        keywords = str(call.data)
        song_id = int(keywords.split(" ")[1])




        song_name_info_url = f"https://benchaonetease.vercel.app/song/detail?ids={song_id}"
        song_name_info = requests.get(url=song_name_info_url)
        song_name = song_name_info.json()['songs'][0]['name']
        author=song_name_info.json()['songs'][0]['ar'][0]['name']
        song_img=song_name_info.json()['songs'][0]['al']['picUrl']
        new_inline_keyboard = [
            [
                InlineKeyboardButton(
                    text="上传到网盘",
                    callback_data=f"neteaserclone {song_id}"
                ),
                InlineKeyboardButton(
                    text="发送给我",
                    callback_data=f"neteasetg {song_id}"
                )

            ]
        ]

        new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
        await client.send_photo(caption=f"歌曲:`{song_name}`\n歌手:`{author}`", photo=str(song_img), chat_id=message_chat_id,
                          parse_mode='markdown', reply_markup=new_reply_markup)

    except Exception as e:
        print(f"edit_song_info error {e}")
        await client.edit_message_text(text=f"获取歌曲信息失败 {e}`", chat_id=message_chat_id,
                                 message_id=message_id,
                                 parse_mode='markdown')

def add_flac_cover(filename, albumart):
    audio = File(filename)

    image = Picture()
    image.type = 3
    if albumart.endswith('png'):
        mime = 'image/png'
    else:
        mime = 'image/jpg'
    image.desc = 'front cover'
    with open(albumart, 'rb') as f:  # better than open(albumart, 'rb').read() ?
        image.data = f.read()

    audio.add_picture(image)
    audio.save()


def http_downloadsong(client, message,url, file_name,picpath,towhere):

    path="/music/"
    if not os.path.exists(path):   # 看是否有该文件夹，没有则创建文件夹
         os.mkdir(path)
    info = client.send_message(chat_id=message.chat.id, text="添加任务", parse_mode='markdown')
    start = time.time()  # 下载开始时间
    response = requests.get(url, stream=True)
    size = 0  # 初始化已下载大小
    chunk_size = 1024  # 每次下载的数据大小
    content_size = int(response.headers['content-length'])  # 下载文件总大小
    try:
        if response.status_code == 200:  # 判断是否响应成功
            print('Start download,[File size]:{size:.2f} MB'.format(
                size=content_size / chunk_size / 1024))  # 开始下载，显示下载文件大小
            filepath = path + file_name  # 设置图片name，注：必须加上扩展名
            temp = time.time()
            with open(filepath, 'wb') as file:  # 显示进度条
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    size += len(data)
                    if int(time.time())-int(temp) > 1:
                        text=f'{file_name}\n'+'[下载进度]:%.2f%%' % ( float(size / content_size * 100))
                        client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                                 parse_mode='markdown')
                        temp = time.time()


        end = time.time()  # 下载结束时间
        text = f'{file_name}\n' + f"大小:`{hum_convert(content_size)}`\n" + '[下载进度]:`%.2f%%`' % (
            float(size / content_size * 100))

        client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                 parse_mode='markdown')
    except:
        print('Error!')
        return

    try:
        if "tg" in str(towhere):
            print("开始上传")

            client.send_audio(chat_id= info.chat.id,
                              audio=filepath,
                              caption=file_name,
                              file_name =file_name ,thumb=picpath,title=file_name ,progress=progress,
                                       progress_args=(client, info, file_name,))
            os.remove(filepath)
        elif "rclone" in str(towhere):

            run_rclone(filepath, "music", info=info, file_num=1, client=client, message=message)
            os.remove(filepath)




    except Exception as e:
        print(e)
        print("Upload Issue!")

    return None

def downloadplaylist(client, call):
    info =  client.send_message(chat_id=call.message.chat.id, text="开始下载", parse_mode='markdown')

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 5.8; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
        "cookie": "__remember_me=true; MUSIC_U=f5798cb7775288f521fdcc5e3ce3df53b94446c1f5306aea19f4b0354b15433833a649814e309366; __csrf=b23ac1873ea3b243dbd6412b488600b1; NMTID=00O-ApuqR6H-n1NEEJFpS0RgQBBbVwAAAF6OLF0aw"
    }
    playlist =str(call.data).split()[1]
    song_list_url = f"https://benchaonetease.vercel.app/playlist/detail?id={playlist}"
    print(song_list_url)
    song_list_info = requests.get(url=song_list_url, headers=headers)
    print(song_list_info.json())
    print(song_list_info.json()['playlist']['name'])
    song_list = list(song_list_info.json()['playlist']['trackIds'])
    song_id_list = []

    for a in song_list:
        song_id_list.append(str(a['id']))

    path = f"/playlist{playlist}/"
    if not os.path.exists(path):  # 看是否有该文件夹，没有则创建文件夹
        os.mkdir(path)
    for song_id in song_id_list:

        song_info_url = f"https://benchaonetease.vercel.app/song/url?id={song_id}"
        song_info = requests.get(url=song_info_url, headers=headers)
        try:
            if song_info.json()['data'][0]['url'] == None:
                client.edit_message_text(text=f"此歌曲不支持获取歌曲链接", chat_id=info.chat.id,
                                         message_id=info.message_id,
                                         parse_mode='markdown')
                continue
            url = song_info.json()['data'][0]['url']
        except Exception as e:
            client.edit_message_text(text=f"无法获取刚获取歌曲链接:\n`{e}`", chat_id=info.chat.id,
                                         message_id=info.message_id,
                                         parse_mode='markdown')
            continue

        song_name_info_url = f"https://benchaonetease.vercel.app/song/detail?ids={song_id}"
        song_name_info = requests.get(url=song_name_info_url)
        song_name = f"{song_name_info.json()['songs'][0]['name']}.{str(song_info.json()['data'][0]['type']).lower()}"

        song_name=str(song_name).replace("\\", "").replace("/", "").replace('?', '').replace('*', '').replace('・', '').replace('！', '').replace('|', '').replace(' ', '')

        img_url = song_name_info.json()['songs'][0]['al']['picUrl']
        img = requests.get(url=img_url)
        img_name = f"{info.chat.id}{info.message_id}.png"
        with open(img_name, 'wb') as f:
            f.write(img.content)
            f.close()
        picpath = img_name

        client.edit_message_text(chat_id=info.chat.id, message_id=info.message_id, text=f"{song_name}开始下载", parse_mode='markdown')




        start = time.time()  # 下载开始时间
        response = requests.get(url, stream=True)
        size = 0  # 初始化已下载大小
        chunk_size = 1024  # 每次下载的数据大小
        content_size = int(response.headers['content-length'])  # 下载文件总大小
        try:
            if response.status_code == 200:  # 判断是否响应成功
                print('Start download,[File size]:{size:.2f} MB'.format(
                    size=content_size / chunk_size / 1024))  # 开始下载，显示下载文件大小
                filepath = path + song_name  # 设置图片name，注：必须加上扩展名
                temp = time.time()
                with open(filepath, 'wb') as file:  # 显示进度条
                    for data in response.iter_content(chunk_size=chunk_size):
                        file.write(data)
                        size += len(data)
                        if int(time.time()) - int(temp) > 1:
                            text = f'{song_name}\n'+f"大小:`{hum_convert(content_size)}`\n" + '[下载进度]:`%.2f%%`' % (float(size / content_size * 100))
                            client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                                     parse_mode='markdown')
                            temp = time.time()

            end = time.time()  # 下载结束时间
            text = f'{song_name}下载完成,times: %.2f秒' % (end - start)  # 输出下载用时时间
            client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                     parse_mode='markdown')
            if "tg" in str(call.data):
                print("开始上传")

                client.send_audio(chat_id=info.chat.id,
                                  audio=filepath,
                                  caption=song_name,
                                  file_name=song_name, thumb=picpath, title=song_name, progress=progress,
                                  progress_args=(client, info, song_name,))
                os.remove(filepath)
                os.remove(picpath)
            else:
                os.remove(picpath)
        except Exception as e:
            print(f'Error! {e}')
            client.edit_message_text(text=f'Error! `{e}`', chat_id=info.chat.id,
                                         message_id=info.message_id,
                                         parse_mode='markdown')
            continue

    if "rclone" in str(call.data):
        run_rclone(path, f"歌单{playlist}", info=info, file_num=2, client=client, message=info)
        os.system(f"rm -rf \"{path}\"")
    if "tg" in str(call.data):
        client.send_message(chat_id=call.message.chat.id, text="上传结束", parse_mode='markdown')


async def get_song_info(client, message):

    try:
        song_id = message.text.split()[1]
        check_url=f"https://benchaonetease.vercel.app/check/music?id={song_id}"
        check_song_info=requests.get(url=check_url)
        print(check_song_info.json())

        song_name_info_url = f"https://benchaonetease.vercel.app/song/detail?ids={song_id}"
        song_name_info = requests.get(url=song_name_info_url)
        song_name = song_name_info.json()['songs'][0]['name']
        author = song_name_info.json()['songs'][0]['ar'][0]['name']
        song_img = song_name_info.json()['songs'][0]['al']['picUrl']
        new_inline_keyboard = [
            [
                InlineKeyboardButton(
                    text="上传到网盘",
                    callback_data=f"neteaserclone {song_id}"
                ),
                InlineKeyboardButton(
                    text="发送给我",
                    callback_data=f"neteasetg {song_id}"
                )

            ]
        ]

        new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
        await client.send_photo(caption=f"歌曲:`{song_name}`\n歌手:`{author}`", photo=str(song_img), chat_id=message.chat.id,
                                parse_mode='markdown', reply_markup=new_reply_markup)

    except Exception as e:
        print(f"get_song_info error {e}")
        await client.edit_message_text(text=f"获取歌曲信息失败 {e}`", chat_id=message.chat.id,
                                 message_id=message.id,
                                 parse_mode='markdown')



async def get_song_list_info(client, message):
    try:
        info =await client.send_message(chat_id=message.chat.id, text="开始获取歌单信息", parse_mode='markdown')

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 5.8; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
            "cookie": "__remember_me=true; MUSIC_U=f5798cb7775288f521fdcc5e3ce3df53b94446c1f5306aea19f4b0354b15433833a649814e309366; __csrf=b23ac1873ea3b243dbd6412b488600b1; NMTID=00O-ApuqR6H-n1NEEJFpS0RgQBBbVwAAAF6OLF0aw"
        }
        playlist = message.text.split()[1]
        song_list_url = f"https://benchaonetease.vercel.app/playlist/detail?id={playlist}"
        print(song_list_url)
        song_list_info = requests.get(url=song_list_url, headers=headers)
        #print(song_list_info.json())
        song_json=song_list_info.json()
        #print(song_list_info.json()['playlist']['name'])
        song_list = list(song_json['privileges'])
        song_id_text = ""
        num = 1
        list_num = len(song_json['playlist']['trackIds'])
        print(f"歌曲数:{list_num}")
        for a in song_list:
            if num < len(song_list):
                song_id_text = song_id_text + str(a['id']) + ","
            else:
                song_id_text = song_id_text + str(a['id'])
            num = num + 1
        print(song_id_text)

        song_name_info_url = f"https://benchaonetease.vercel.app/song/detail?ids={song_id_text}"
        song_name_info = requests.get(url=song_name_info_url, headers=headers)
        print(song_name_info.json())
        song_info_list = list(song_name_info.json()['songs'])

        num = 1
        text=f"歌单名称:`{song_list_info.json()['playlist']['name']}`\n" \
             f"歌曲数:`{list_num}`\n" \
             f"只显示前15条\n"
        for a in song_info_list :

            text=text+f"{num}-`{a['name']}-{a['ar'][0]['name']}`\n"
            if num==15:
                break
            num=num+1

        new_inline_keyboard = [
            [
                InlineKeyboardButton(
                    text="上传到网盘",
                    callback_data=f"playlistrclone {playlist}"
                ),
                InlineKeyboardButton(
                    text="发送给我",
                    callback_data=f"playlisttg {playlist}"
                )

            ]
        ]

        new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)

        await client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                 parse_mode='markdown', reply_markup=new_reply_markup)



    except Exception as e:
        print(f"get_song_info error {e}")
        await client.send_message(text=f"获取歌单信息失败 {e}`", chat_id=message.chat.id,
                                 message_id=message.id,
                                 parse_mode='markdown')
