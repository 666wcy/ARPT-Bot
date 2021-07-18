<!--
 * @Date: 2021-06-05 12:04:51
 * @LastEditors: Ben
 * @LastEditTime: 2021-07-18 11:13:14
-->


# 介绍

一个基于Python3的Bot。目前支持以Docker的方式部署在vps上。

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=666wcy&repo=ARPT-Bot)](https://github.com/666wcy/ARPT-Bot)

主要功能:

- [X] 文件管理
  - [X] 修改主界面为 [filebrowser](https://github.com/filebrowser/filebrowser)，账号为**admin**，密码为**admin**,主界面路径：http://ip:port,请自行修改密码
  - [X] ~~[FolderMagic](https://github.com/FolderMagic/FolderMagic)自带的webdav：路径:http://ip:port/webdav 。账号密码同FolderMagic，不支持网页端，需要支持webdav的软件(在Raildrive上测试成功)~~ 由于其只支持amd64架构，使用[filebrowser](https://github.com/filebrowser/filebrowser)将其代替

- [X] 网页面板
  - [X] 支持 [AriaNg](https://github.com/mayswind/AriaNg) 面板,地址为：https://ip:port/ng/
  - [X] ~~新增 [ServerStatus-Hotaru](https://github.com/cokemine/ServerStatus-Hotaru) 作为容器探针。探针地址:http://ip:port/status/~~ 鸡肋功能，删除
  - [X] 用**Nginx**为内部端口反代，替换原来的的Python Flask，更加轻量


- [X] Aria2
  - [X] 自动化安装Aria2，自定义密钥
  - [X] 用Bot进行简单的Aria2端控制(添加任务、暂停任务、删除任务)
  - [X] 显示下载进度
  - [X] 任务完成后通过rclone上传(**显示上传进度**)，最新版rclone已支持世纪互联
  - [X] 支持aria2面板类工具rpc连接(get、post方式)
  - [X] 支持自动上传面板类工具rpc连接添加的任务自动上传(不显示进度)。通过面板添加的任务上传方式更改为P大的上传脚本，保持原有路径。
  - [X] 采用P大的配置，自动添加tracker。
  - [X] 下载OneDrive、sharepoint公开分享链接中的文件，保持文件路径推送到Aria2.已实现。采用项目地址：[OneDriveShareLinkPushAria2](https://github.com/gaowanliang/OneDriveShareLinkPushAria2)
  - [ ] Rss自动下载，已有成品，尚未对接

- [X] Rclone
  - [X] rclone官方lsd，lsf方法的适配
  - [X] rclone copy的适配，即双盘互传，支持查看传输进度
  - [X] rclone copyurl方式上传文件，实时显示进度
  - [X] 支持aria2面板类工具rpc连接(get、post方式)
  - [ ] TG按键式查看rclone目录
  - [ ] 将当前目录文件命名为emby扫描格式
  - [ ] 通过Bot添加rclone配置、清空rclone配置
  - [ ] 获取单个或多个文件夹的分享链接(gd,od)
  
- [X] Pixiv
  - [X] 根据pid获取图片
  - [X] 下载画师的全部作品，支持打包上传网盘、打包发送tg、图片方式发送tg、telegraph(网页)方式发送图片。打包格式为zip。
  - [X] 下载日榜，周榜、月榜，支持打包上传网盘、打包发送tg、图片方式发送tg、telegraph(网页)方式发送图片。打包格式为zip。
  - [X] 支持指定日期的榜单下载

- [X] 影音相关
  - [X] 使用YouTube-dl下载视频，支持上传网盘或发送到tg。默认最高画质，目前完美适配YouTube和哔哩哔哩(不含番剧)
  - [X] 网易云音乐下载，支持id下载，搜索下载，整个歌单下载，支持发送到tg和上传网盘
  - [X] 新增将视频转为MP3格式发送、上传
  - [ ] 视频与字幕混流
  - [ ] 常用影音格式格式互转

- [X] Telegram
  - [X] 只有当前用户的命令生效
  - [X] 发送file id获取文件
  - [X] 发送文件获取file id
  - [X] 发送TG文件上传到网盘
  - [X] 支持命令查看Bot运行时间和剩余空间
  - [ ] 添加Bot白名单
  - [ ] 支持群组内使用。Ps:已有群组版本，正在考虑如何混合适配

- [X] 图片相关
  - [X] 合并[搜图机器人](https://github.com/666wcy/search_photo-telegram-bot-heroku)，支持[saucenao](https://saucenao.com/)、[WhatAnime](https://trace.moe/)、[ascii2d](https://ascii2d.net/)、[iqdb](http://www.iqdb.org/)
  - [X] 搜索下载哔咔的本子，支持ZIP文件格式发送到TG和上传网盘
  - [X] 对接 [nhentai](https://github.com/RicterZ/nhentai),下载nhentai本子并支持以ZIP文件格式发送TG、ZIP格式上传网盘、网页格式发送到TG
 


# Bot command

通过在 **@BotFather** 设置命令

```
start - 查看Bot状态
help - 获取Bot的使用帮助
pixivauthor - 对pixiv画师作品操作
pixivtopall - 对pixiv排行榜进行操作
pixivtopillust - 对插画排行榜进行操作
pixivpid - 发送pixiv该id的图片
magfile - 推送种子文件至aria2下载后上传至网盘
mirror - 推送直链至aria2下载上传至网盘
mirrortg - 推送直链至aria2下载发送到TG
magnet - 推送磁力链接至aria2下载后上传至网盘
downtgfile - 发送TG文件并上传至网盘
rclonecopy - 用rclone在网盘间传输
rclonelsd - 用rclone显示网盘文件夹
rclone - 用rclone显示文件夹内详细信息
rclonecopyurl - 用rclonecopyurl的方式直接上传直链文件
getfileid - 发送文件获取fileid
getfile - 发送fileid来获取文件
video - 发送视频链接
neteaseid - 通过id获取歌曲信息
searchsong - 搜索网易云音乐歌曲
playlist - 获取歌单信息
odshare - 下载公开的od分享链接文件并上传网盘
```

# 安装

Docker 部署命令：

~~评论区反馈docker不支持arm架构，推测原因为原docker为amd64架构,目前只在amd64上测试成功~~
目前理论支持所含架构，具体没有进行真机测试

```
docker run -d \
    --name arpt \
    -e Api_hash=xxx \
    -e Api_id=xxx \
    -e Aria2_secret=xxx \
    -e Remote=yun \
    -e Telegram_bot_api=xxx \
    -e Telegram_user_id=xxx \
    -e Upload=xxx \
    -p 8868:8868 \
   benchao/arpt:v2.0.3

```

配置解释

```
Api_hash Api_id 这两项在https://my.telegram.org中注册应用后得到

Aria2_secret    Aria2的密匙

Telegram_bot_api    Bot的API，在@BotFather申请获得

Telegram_user_id    使用者的TG id，可在@userinfobot处获得

Remote  上传目的地的rclone盘符

Upload  上传文件夹名称，后面不需要加/
```

在Docker运行后访问ip:port访问文件管理器，~~在/.config/rclone下文件夹新建rclone.conf,粘贴自己的rclone配置。~~
PS:有人反馈此处配置不成功，可尝试在/root/.config/rclone也添加配置，bot运行 **/rclone 盘符** ，可以查看是否成功
关于上传方法，将.conf文件拖入浏览器即可。

![成功效果](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/image.2abs656qyrb4.png)

Docker目前不支持自动更新，目前更新需要自行重装新镜像版本

可自行查看最新镜像版本号：[查看地址](https://hub.docker.com/repository/docker/benchao/arpt)

# 杂项说明

关于在面板配置Aria2的设置，ip为vps端口，端口为docker设定的端口
举例,若docker中命令为
`-p 8868:8868 \`
则端口为8868
面板密钥填docker创建时你的Aria2_secret值

# bug说明
1.下载文件时概率性出现99%，实际已完成上传，尚未解决

~~2.pixiv发送图片给我时概率性出现[400 PHOTO_INVALID_DIMENSIONS]: The photo dimensions are invalid (caused by "messages.UploadMedia")的错误，尚未找到原因~~1.1.7版本以后已修复，不符合尺寸的图片不进行发送(暴力解决)

# 效果展示

![](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/bot下载种子.501pcym934k0.png)

![](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/image.2zx3yt2f8ow0.png)

![](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/image.52jb1gwlv4o0.png)

![](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/bot视频下载.7b1arubsqa00.png)

![](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/bot文件下载.327tinslwa00.png)

![](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/image.771n1tka9dg0.png)

# 更新说明

v2.0.4

合并[搜图机器人](https://github.com/666wcy/search_photo-telegram-bot-heroku)，支持[saucenao](https://saucenao.com/)、[WhatAnime](https://trace.moe/)、[ascii2d](https://ascii2d.net/)、[iqdb](http://www.iqdb.org/)

搜索下载哔咔的本子，支持ZIP文件格式发送到TG和上传网盘

对接 [nhentai](https://github.com/RicterZ/nhentai),下载nhentai本子并支持以ZIP文件格式发送TG、ZIP格式上传网盘、网页格式发送到TG


v2.0.3

对接[OneDriveShareLinkPushAria2](https://github.com/gaowanliang/OneDriveShareLinkPushAria2)的更新，支持sharepoint分享链接。

修复网易云歌单显示不全的问题。

v2.0.1

修复docker构建时rclone安装失败，修复网易云歌单下载到无版权音乐时整个歌单下载停止

v2.0.0

Bot开源，支持arm64，目前没有机子测试，理论可行

v1.1.7

修复pixiv发送到tg时因为尺寸不符合tg api要求报错，取消发送不符合尺寸的图片。

尝试修复下载卡99%的概率性问题，效果未知。

新增网易云音乐的下载，目前支持搜索下载，id下载，整个歌单下载，支持发送到tg和上传到网盘。API接口项目：[NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi),目前使用的是本人的API，有黑胶会员，后续会支持自定义API地址。

QQ音乐如果有稳定接口项目，也可推荐对接Bot

![](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/xxx.6kk2hr659yw0.png)

![](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/image.l6bobb2z9vk.png)

![](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/image.7b3nuhohe4o0.png)

v1.1.6

将pixivtop命令更改为pixivtopall,优化按键选择方式，新增插画榜和男性榜、女性榜、新人榜、原创榜，支持指定日期榜单下载

![](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/image.1q6zlq2sggow.png)

v1.1.5

取消pixivuser、pixivusertg、pixivuserphoto、pixivusertele

优化为单个命令pixivauthor

![](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/image.7huyt6u0ne40.png)

新增pixiv排行榜的下载(日榜、月榜、周榜),后续将增加插画榜和男性榜、女性榜等

![](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/image.1iniuqwtbojk.png)

v1.1.4

新增下载OneDrive 公开分享链接中的文件，保持文件路径推送到Aria2.已实现。采用项目地址：[OneDriveShareLinkPushAria2](https://github.com/gaowanliang/OneDriveShareLinkPushAria2)

修复**downtgfile**命令下载视频失败的错误

优化/rclone命令的显示

# 感谢下面大佬的贡献

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=ytdl-org&repo=youtube-dl)](https://github.com/ytdl-org/youtube-dl)

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=pyrogram&repo=pyrogram)](https://github.com/pyrogram/pyrogram)

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=pawamoy&repo=aria2p)](https://github.com/pawamoy/aria2p)

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=FolderMagic&repo=FolderMagic)](https://github.com/FolderMagic/FolderMagic)

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=mayswind&repo=AriaNg)](https://github.com/mayswind/AriaNg)

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=cokemine&repo=ServerStatus-Hotaru)](https://github.com/cokemine/ServerStatus-Hotaru)

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=P3TERX&repo=aria2.conf)](https://github.com/P3TERX/aria2.conf)

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=filebrowser&repo=filebrowser)](https://github.com/filebrowser/filebrowser)

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=gaowanliang&repo=OneDriveShareLinkPushAria2)](https://github.com/gaowanliang/OneDriveShareLinkPushAria)




