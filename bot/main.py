# -*- coding: utf-8 -*-
from apscheduler.schedulers.background import BackgroundScheduler
import sys
from modules.check import new_clock, second_clock
from config import client, Telegram_user_id, aria2,Error_user_info,App_title
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram import filters
from modules.pixiv import start_download_pixiv, start_download_id, start_download_pixivtg, start_download_pixivphoto, \
    start_download_pixivtele,author,pixiv_topall,start_download_pixiv_top,pixiv_topillustration
from modules.control import send_telegram_file, start_http_download, start_download, start_http_downloadtg, \
    check_upload, get_free_space_mb, odshare_download,odprivate_download,more_magnet
from modules.call import start_pause, start_remove, start_Resume, start_benzi_down, start_download_video,start_get_author_info,get_song_url_info,book_search_all_call
from modules.moretg import get_telegram_file, get_file_id, sendfile_by_id
from modules.picacg import seach_main
from modules.rclone import start_rclonecopy, start_rclonelsd, start_rclonels, start_rclonecopyurl
from modules.video import start_get_video_info
from modules.netease import get_song_info,search_song_list,edit_song_info,get_song_list_info,downloadplaylist
from modules.nhentai import download_nhentai_id,download_nhentai_id_call,get_search_nhentai_info
from modules.photo import send_photo,saucenao,ascii2d,anime,iqdb,search_all_photo
from modules.ehentai import single_download,single_download_call,get_search_ehentai_info
import hashlib
import os
import datetime


starttime = datetime.datetime.now()


async def chexk_group(_, client, query):
    print("检查使用权限")
    #print(query)
    try:
        if "-" in str(Telegram_user_id):
            info = await client.get_chat_member(chat_id=int(Telegram_user_id), user_id=query.from_user.id)



            sys.stdout.flush()
            return True
        else:
            if str(query.from_user.id)==str(Telegram_user_id):
                return True

    except Exception as e:
        await client.send_message(chat_id=query.from_user.id, text=Error_user_info)
        print(f"获取权限失败：{e}")
        return False


async def help(client, message):
    print(client)
    print(message)
    text = '''
直接发送磁力链接可直接添加任务，默认上传网盘，支持多个磁力（换行分隔）
直接发送图片可进行搜图    
********** pixiv相关 **********
/pixivauthor - 对Pixiv画师作品进行操作
在命令后加入作品ID，使用示例
/pixivauthor 9675329

/pixivtop - 对综合排行榜进行操作
/pixivtopillust - 对插画排行榜进行操作
在命令后加入抓取页数，1页50张图片，使用示例(下载排行榜前50)
/pixivtopall 1
/pixivtopillust 1
支持选择时间，请注意日期格式，使用示例
/pixivtopall 1 20210501
/pixivtopillust 1 20210501

/pixivpid - 发送pixiv该id的图片
在命令后加入作品ID，使用示例
/pixivpid 88339301

********** aria2相关 **********
/magfile - 推送种子文件至aria2下载
/mirror - 推送直链至aria2下载上传至网盘
/mirrortg - 推送直链至aria2下载发送到TG
/magnet - 推送磁力链接至aria2下载
/odshare - 下载od-sp公开分享链接上传到网盘，链接权限至少为任何人可查看
/odprivate - 下载域内的od、sp分享链接上传到网盘
示例：
/odshare 链接 密码 ，无密码则不加参数
/odprivate 账号 密码 链接

********** 图片相关 **********
直接发送图片即可选择搜索图片

/nhentai id tg - 下载nhentai中对应id的本子压缩包格式发送到TG
id可以换为链接，Bot会自动识别
/ehentai ehentai链接 tg - 下载nhentai中对应id的本子压缩包格式发送到TG
参数说明:tg-ZIP格式发送到TG，rclone-ZIP格式上传到网盘，tele-网页格式发送给我

/picacgsearch 搜索词 - 在哔咔中搜索本子，支持ZIP上传到网盘和发送到TG
/ehentaisearch 搜索词 - 在ehentai中搜索本子，支持ZIP上传到网盘和发送到TG
/nhentaisearch 搜索词 - 在nhentai中搜索本子，支持ZIP上传到网盘和发送到TG

********** 其它相关 **********
/
 - 发送TG文件并上传至网盘
发送 /downtgfile 后按提示发送文件即可


/rclonecopyurl - 用rclonecopyurl的方式直接上传直链文件
示例 /rclonecopyurl 文件直链

/getfileid - 发送文件获取fileid
发送 /getfileid  后按提示发送文件即可

/getfile - 发送fileid来获取文件
示例 /getfile  文件直链

/video - 使用youtube-dl下载视频
示例 /video  视频链接
目前测试youtube和哔哩哔哩(不包括番剧)完美适配

neteaseid - 通过id获取歌曲信息
示例 /neteaseid 1835951859
id为分享链接： http://music.163.com/song?id=1835951859&userid=84589227 中id=和&的中间值，歌单类似

searchsong - 搜索网易云音乐歌曲
示例 /searchsong 怪物

playlist - 获取歌单信息，后加歌单id
示例 /playlist 5320586978

Bot相关联系：https://t.me/Ben_chao'''
    try:
        await client.send_message(chat_id=int(message.chat.id), text=text)
    except Exception as e:
        print(f"help :{e}")


async def status(client, message):
    endtime = datetime.datetime.now()

    m, s = divmod(int((endtime - starttime).seconds), 60)
    h, m = divmod(m, 60)
    print("%02d时%02d分%02d秒" % (h, m, s))
    if h != 0:
        last_time = "%d时%d分%d秒" % (h, m, s)
    elif h == 0 and m != 0:
        last_time = "%d分%d秒" % (m, s)
    else:
        last_time = "%d秒" % s
    text = f"Bot正在运行，已运行时间:`{last_time}`\n磁盘剩余空间:`{get_free_space_mb()}GB`"
    await client.send_message(chat_id=message.from_user.id, text=text, parse_mode='markdown')


def start_bot():
    # scheduler = BlockingScheduler()
    if App_title!="":
        scheduler = BackgroundScheduler()

        scheduler.add_job(new_clock, "interval", seconds=60)
        scheduler.add_job(second_clock, "interval", seconds=60)
        scheduler.start()
        print("开启监控")

    sys.stdout.flush()
    print("开始bot")
    print(Telegram_user_id)
    sys.stdout.flush()
    aria2.listen_to_notifications(on_download_complete=check_upload, threaded=True)

    start_message_handler = MessageHandler(
        status,

        filters=filters.command(["start"]) & filters.create(chexk_group) & filters.private
    )

    help_message_handler = MessageHandler(
        help,
        # filters=filters.command("start") & filters.create(chexk_group)
        filters=filters.command(["help"]) & filters.create(chexk_group) & filters.private
    )


    pixivid_message_handler = MessageHandler(
        start_download_id,
        filters=filters.command("pixivpid") & filters.create(chexk_group) & filters.private
    )

    magfile_message_handler = MessageHandler(
        send_telegram_file,
        filters=filters.command("magfile") & filters.create(chexk_group) & filters.private
    )

    http_download_message_handler = MessageHandler(
        start_http_download,
        filters=filters.command("mirror") & filters.create(chexk_group) & filters.private
    )
    magnet_download_message_handler = MessageHandler(
        start_download,
        filters=filters.command("magnet") & filters.create(chexk_group) & filters.private
    )

    telegram_file_message_handler = MessageHandler(
        get_telegram_file,
        filters=filters.command("downtgfile") & filters.create(chexk_group) & filters.private
    )
    seach_main_file_message_handler = MessageHandler(
        seach_main,
        filters=filters.command("picacgsearch") & filters.create(chexk_group) & filters.private
    )



    start_http_downloadtg_message_handler = MessageHandler(
        start_http_downloadtg,
        filters=filters.command("mirrortg") & filters.create(chexk_group) & filters.private
    )
    start_rclonecopy_message_handler = MessageHandler(
        start_rclonecopy,
        filters=filters.command("rclonecopy") & filters.create(chexk_group) & filters.private
    )

    start_rclonelsd_message_handler = MessageHandler(
        start_rclonelsd,
        filters=filters.command("rclonelsd") & filters.create(chexk_group) & filters.private
    )

    start_rclone_message_handler = MessageHandler(
        start_rclonels,
        filters=filters.command("rclone") & filters.create(chexk_group) & filters.private
    )

    start_rclonecopyurl_message_handler = MessageHandler(
        start_rclonecopyurl,
        filters=filters.command("rclonecopyurl") & filters.create(chexk_group) & filters.private
    )

    get_file_id_message_handler = MessageHandler(
        get_file_id,
        filters=filters.command("getfileid") & filters.create(chexk_group) & filters.private
    )
    sendfile_by_id_message_handler = MessageHandler(
        sendfile_by_id,
        filters=filters.command("getfile") & filters.create(chexk_group) & filters.private
    )



    start_get_video_info_message_handler = MessageHandler(
        start_get_video_info,
        filters=filters.command("video") & filters.create(chexk_group) & filters.private
    )

    start_download_od_shareurl_handler = MessageHandler(
        odshare_download,
        filters=filters.command("odshare") & filters.create(chexk_group) & filters.private
    )

    start_get_authorinfo_handler = MessageHandler(
        author,
        filters=filters.command("pixivauthor") & filters.create(chexk_group) & filters.private
    )

    start_get_pixiv_top_handler = MessageHandler(
        pixiv_topall,
        filters=filters.command("pixivtopall") & filters.create(chexk_group) & filters.private
    )

    start_pixiv_topillustration_handler = MessageHandler(
        pixiv_topillustration,
        filters=filters.command("pixivtopillust") & filters.create(chexk_group) & filters.private

    )

    get_song_info_handler = MessageHandler(
        get_song_info,
        filters=filters.command("neteaseid") & filters.create(chexk_group) & filters.private

    )

    search_song_list_handler = MessageHandler(
        search_song_list,
        filters=filters.command("searchsong") & filters.create(chexk_group) & filters.private

    )

    get_song_list_info_handler = MessageHandler(
        get_song_list_info,
        filters=filters.command("playlist") & filters.create(chexk_group) & filters.private

    )

    download_nhentai_id_handler = MessageHandler(
        download_nhentai_id,
        filters=filters.command("nhentai") & filters.create(chexk_group) & filters.private

    )

    single_download_handler = MessageHandler(
        single_download,
        filters=filters.command("ehentai") & filters.create(chexk_group) & filters.private
    )

    get_search_ehentai_info_handler = MessageHandler(
        get_search_ehentai_info,
        filters=filters.command("ehentaisearch") & filters.create(chexk_group) & filters.private
    )

    get_search_nhentai_info_handler = MessageHandler(
        get_search_nhentai_info,
        filters=filters.command("nhentaisearch") & filters.create(chexk_group) & filters.private
    )

    odprivate_download_handler = MessageHandler(
        odprivate_download,
        filters=filters.command("odprivate") & filters.create(chexk_group) & filters.private
    )

    book_search_all_call_handler = CallbackQueryHandler(
        callback=book_search_all_call,
        filters=filters.create(lambda _, __, query: "search" in query.data)
    )

    download_nhentai_id_call_handler = CallbackQueryHandler(
        callback=download_nhentai_id_call,
        filters=filters.create(lambda _, __, query: "nhentai" in query.data)
    )



    single_download_call_handler = CallbackQueryHandler(
        callback=single_download_call,
        filters=filters.create(lambda _, __, query: "ehentai" in query.data)
    )


    start_Resume_handler = CallbackQueryHandler(
        callback=start_Resume,
        filters=filters.create(lambda _, __, query: "Resume" in query.data)
    )

    start_pause_handler = CallbackQueryHandler(
        callback=start_pause,
        filters=filters.create(lambda _, __, query: "Pause" in query.data)
    )
    start_remove_handler = CallbackQueryHandler(
        callback=start_remove,
        filters=filters.create(lambda _, __, query: "Remove" in query.data)
    )

    start_benzi_down_handler = CallbackQueryHandler(
        callback=start_benzi_down,
        filters=filters.create(lambda _, __, query: "down" in query.data)
    )
    start_download_video_handler = CallbackQueryHandler(
        callback=start_download_video,
        filters=filters.create(lambda _, __, query: "video" in query.data or "mp3" in query.data)
    )

    start_call_author_handler = CallbackQueryHandler(
        callback=start_get_author_info,
        filters=filters.create(lambda _, __, query: "pixivuser" in query.data)
    )


    start_download_pixiv_top_handler = CallbackQueryHandler(
        callback=start_download_pixiv_top,
        filters=filters.create(lambda _, __, query: "pixivtop" in query.data)
    )


    get_song_url_info_handler = CallbackQueryHandler(
        callback=get_song_url_info,
        filters=filters.create(lambda _, __, query: "netease" in query.data)
    )

    edit_song_info_handler = CallbackQueryHandler(
        callback=edit_song_info,
        filters=filters.create(lambda _, __, query: "editsong" in query.data)
    )

    downloadplaylist_handler = CallbackQueryHandler(
        callback=downloadplaylist,
        filters=filters.create(lambda _, __, query: "playlist" in query.data)
    )



    saucenao_handler = CallbackQueryHandler(
        callback=saucenao,
        filters=filters.create(lambda _, __, query: "saucenao" == query.data)
    )
    ascii2d_handler = CallbackQueryHandler(
        callback=ascii2d,
        filters=filters.create(lambda _, __, query: "ascii2d" == query.data)
    )
    anime_handler = CallbackQueryHandler(
        callback=anime,
        filters=filters.create(lambda _, __, query: "WhatAnime" == query.data)
    )
    iqdb_handler = CallbackQueryHandler(
        callback=iqdb,
        filters=filters.create(lambda _, __, query: "iqdb" == query.data)
    )

    search_all_photo_handler = CallbackQueryHandler(
        callback=search_all_photo,
        filters=filters.create(lambda _, __, query: "allsearchphoto" == query.data)
    )

    start_send_photo_handler = MessageHandler(
        send_photo,
        filters=filters.photo & filters.create(chexk_group) & filters.private
    )

    start_more_magnet_handler = MessageHandler(
        more_magnet,
        filters=filters.text & filters.create(chexk_group) & filters.private
    )
    print(f"检查odprivate_download_handler -{App_title}-")
    if App_title == "":
        print("添加odprivate_download_handler")
        client.add_handler(odprivate_download_handler, group=1)

    client.add_handler(search_all_photo_handler, group=0)
    client.add_handler(start_download_video_handler, group=0)
    client.add_handler(start_Resume_handler, group=0)
    client.add_handler(start_pause_handler, group=0)
    client.add_handler(start_remove_handler, group=0)
    client.add_handler(start_benzi_down_handler, group=0)

    client.add_handler(start_message_handler, group=1)
    client.add_handler(help_message_handler, group=1)


    client.add_handler(pixivid_message_handler, group=1)
    client.add_handler(magfile_message_handler, group=3)

    client.add_handler(http_download_message_handler, group=1)
    client.add_handler(magnet_download_message_handler, group=1)
    client.add_handler(telegram_file_message_handler, group=1)
    client.add_handler(seach_main_file_message_handler, group=1)

    client.add_handler(start_http_downloadtg_message_handler, group=1)
    client.add_handler(start_rclonecopy_message_handler, group=1)
    client.add_handler(start_rclonelsd_message_handler, group=1)
    client.add_handler(start_rclone_message_handler, group=1)
    client.add_handler(start_rclonecopyurl_message_handler, group=1)
    client.add_handler(get_file_id_message_handler, group=1)
    client.add_handler(sendfile_by_id_message_handler, group=1)

    client.add_handler(start_get_video_info_message_handler, group=1)
    client.add_handler(start_download_od_shareurl_handler, group=1)
    client.add_handler(start_get_authorinfo_handler, group=1)
    client.add_handler(start_call_author_handler, group=1)
    client.add_handler(start_get_pixiv_top_handler, group=1)
    client.add_handler(start_download_pixiv_top_handler, group=1)
    client.add_handler(start_pixiv_topillustration_handler, group=1)
    client.add_handler(get_song_url_info_handler, group=1)
    client.add_handler(get_song_info_handler, group=1)
    client.add_handler(search_song_list_handler, group=1)
    client.add_handler(edit_song_info_handler, group=1)
    client.add_handler(get_song_list_info_handler, group=1)
    client.add_handler(downloadplaylist_handler, group=1)
    client.add_handler(download_nhentai_id_handler, group=1)

    client.add_handler(start_send_photo_handler, group=1)
    client.add_handler(saucenao_handler, group=1)
    client.add_handler(ascii2d_handler, group=1)
    client.add_handler(anime_handler, group=1)
    client.add_handler(iqdb_handler, group=1)
    client.add_handler(single_download_handler, group=1)
    client.add_handler(single_download_call_handler, group=1)
    client.add_handler(get_search_ehentai_info_handler, group=1)
    client.add_handler(get_search_nhentai_info_handler, group=1)
    client.add_handler(download_nhentai_id_call_handler, group=1)
    client.add_handler(book_search_all_call_handler, group=1)
    client.add_handler(start_more_magnet_handler, group=1)





    client.run()


if __name__ == '__main__':
    start_bot()

