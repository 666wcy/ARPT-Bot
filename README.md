<!--

 * @Date: 2021-06-05 12:04:51
 * @LastEditors: Ben
 * @LastEditTime: 2021-11-10 21:16:31
   -->

[![GitHub Stars](https://img.shields.io/github/stars/666wcy/ARPT-Bot.svg?color=inactived&labelColor=555555&logoColor=ffffff&style=for-the-badge&logo=github)](https://github.com/linuxserver/docker-qbittorrent) [![Docker Pulls](https://img.shields.io/docker/pulls/benchao/arpt.svg?color=inactived&labelColor=555555&logoColor=ffffff&style=for-the-badge&label=pulls&logo=docker)](https://hub.docker.com/repository/docker/benchao/arpt) [![GitHub Release](https://img.shields.io/docker/v/benchao/arpt?color=inactived&labelColor=555555&logoColor=ffffff&style=for-the-badge&label=最新版本&logo=docker)](https://github.com/linuxserver/docker-qbittorrent/releases)

# 更新说明

v2.1.0

根据push提交说明，不再赘述

<details>
<summary>历史记录</summary>

v2.0.9

修改rclone调用方式，改为rc http api调用。

新增对[RcloneNg](https://github.com/ElonH/RcloneNg)的支持。

映射rclone rc，支持自定义对rclone rc进行操作,具体操作可参考[rclone rc教程](https://rclone.org/rc/)

***

此版本后支持自动更新，Python文件的变动只需重启即可更新，其它硬性更新才会通过docker更新版本

修复aria2面板添加的任务与conf文件的配置冲突导致本地文件被删除 [#18](https://github.com/666wcy/ARPT-Bot/issues/18)[#16](https://github.com/666wcy/ARPT-Bot/issues/16)

修复odprivate命令失效(与后续指令冲突导致失效) [#17](https://github.com/666wcy/ARPT-Bot/issues/17)

修复默认面板账号密码为默认，存在安全隐患，修改为账号：`admin`，密码:你设置的`Aria2_secret`的值



v2.0.8

修复rclone剩余时间显示问题

新增支持多文件同时发送上传TG

新增支持多种子文件同时发送

同步原作者[更新](https://github.com/gaowanliang/OneDriveShareLinkPushAria2/commit/a8dd447040ccd0aca89a3e2680a871200ca8c446)，修复od分享链接文件数直到30的问题，感谢原作者



v2.0.7

修复Bot添加的任务重复调用上传

新增群组功能，支持设置整个群组的人员拥有使用权限，支持自定义设定拒绝词

新增上传完成后返回分享链接(仅支持OD)，权限为：同域、只读

修复Nhentai下载本子失败以及下载完成后本子文件未删除问题

新增发送磁力链接直接链添加任务，默认上传网盘，支持批量磁力

v2.0.6

新增带有密码的公开分享链接的od、sp分享链接下载

新增需要登录账号的分享链接下载，需要同域账号的账号和密码

优化上述推送完成的显示


v2.0.5

新增本子的搜索，此版本支持哔咔、ehentai、nhentai

nhentai支持直接识别链接下载



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

</details>


# 介绍

一个基于Python3的Bot。目前支持以Docker的方式部署在vps上。

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=666wcy&repo=ARPT-Bot)](https://github.com/666wcy/ARPT-Bot)

主要功能:

- [x] 文件管理
  - [x] 修改主界面为 [filebrowser](https://github.com/filebrowser/filebrowser)，账号为**admin**，密码为你设定的`Aria2_secret`,主界面路径：http://ip:port,请自行修改密码

- [x] 网页面板
  - [x] 支持 [AriaNg](https://github.com/mayswind/AriaNg) 面板,地址为：https://ip:port/ng/
  - [x] 用**Nginx**为内部端口反代，替换原来的的Python Flask，更加轻量
- [x] 支持[RcloneNg](https://github.com/ElonH/RcloneNg)，登录时地址为`http://ip:port`,请自行修改`ip`和`port`，用户名为root,密码为你设定的`Aria2_secret`


- [x] Aria2
  - [x] 自动化安装Aria2，自定义密钥
  - [x] 用Bot进行简单的Aria2端控制(添加任务、暂停任务、删除任务)
  - [x] 支持批量添加任务
  - [x] 显示下载进度
  - [x] 任务完成后通过rclone上传(**显示上传进度**)，最新版rclone已支持世纪互联
  - [x] 支持aria2面板类工具rpc连接(get、post方式)
  - [x] 支持自动上传面板类工具rpc连接添加的任务自动上传(不显示进度)。通过面板添加的任务上传方式更改为P大的上传脚本，保持原有路径。
  - [x] 采用P大的配置，自动添加tracker。
  - [x] 下载OneDrive、sharepoint公开分享链接中的文件，保持文件路径推送到Aria2.已实现。采用项目地址：[OneDriveShareLinkPushAria2](https://github.com/gaowanliang/OneDriveShareLinkPushAria2)
  - [ ] Rss自动下载，已有成品，尚未对接

- [x] Rclone
  - [x] rclone官方lsd，lsf方法的适配
  - [x] rclone copy的适配，即双盘互传，支持查看传输进度
  - [x] rclone copyurl方式上传文件，实时显示进度
  - [x] 支持aria2面板类工具rpc连接(get、post方式)
  - [ ] TG按键式查看rclone目录
  - [ ] 将当前目录文件命名为emby扫描格式
  - [ ] 通过Bot添加rclone配置、清空rclone配置
  - [ ] 获取单个或多个文件夹的分享链接(gd,od)

- [x] Pixiv
  - [x] 根据pid获取图片
  - [x] 下载画师的全部作品，支持打包上传网盘、打包发送tg、图片方式发送tg、telegraph(网页)方式发送图片。打包格式为zip。
  - [x] 下载日榜，周榜、月榜，支持打包上传网盘、打包发送tg、图片方式发送tg、telegraph(网页)方式发送图片。打包格式为zip。
  - [x] 支持指定日期的榜单下载

- [x] 影音相关
  - [x] 使用YouTube-dl下载视频，支持上传网盘或发送到tg。默认最高画质，目前完美适配YouTube和哔哩哔哩(不含番剧)
  - [x] 网易云音乐下载，支持id下载，搜索下载，整个歌单下载，支持发送到tg和上传网盘
  - [x] 新增将视频转为MP3格式发送、上传
  - [ ] 视频与字幕混流
  - [ ] 常用影音格式格式互转

- [x] Telegram
  - [x] 只有当前用户的命令生效
  - [x] 发送file id获取文件
  - [x] 发送文件获取file id
  - [x] 发送TG文件上传到网盘
  - [x] 支持命令查看Bot运行时间和剩余空间
  - [x] 支持群组内使用。Ps:已有群组版本，正在考虑如何混合适配
  - [ ] 添加Bot白名单

- [x] 图片相关
  - [x] 合并[搜图机器人](https://github.com/666wcy/search_photo-telegram-bot-heroku)，支持[saucenao](https://saucenao.com/)、[WhatAnime](https://trace.moe/)、[ascii2d](https://ascii2d.net/)、[iqdb](http://www.iqdb.org/)
  - [x] 搜索下载哔咔的本子，支持ZIP文件格式发送到TG和上传网盘
  - [x] 对接 [nhentai](https://github.com/RicterZ/nhentai),下载nhentai本子并支持以ZIP文件格式发送TG、ZIP格式上传网盘、网页格式发送到TG
  - [x] 本子的搜索，支持哔咔、ehentai、nhentai
  - [x] saucenao搜图支持快捷搜索

 


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
odshare - 下载公开的od、sp分享链接文件并上传网盘
odprivate - 下载域内的od、sp分享链接上传到网盘
nhentai - 下载nhentai中对应id的本子
ehentai - 下载nhentai中对应id的本子
picacgsearch - 在哔咔中搜索本子，支持ZIP上传到网盘和发送到TG
ehentaisearch - 在ehentai中搜索本子，支持ZIP上传到网盘和发送到TG、发送网页
nhentaisearch - 在nhentai中搜索本子，支持ZIP上传到网盘和发送到TG、发送网页
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
    -e Rclone_share=False \
    -e Error_user_info="你没有使用权限" \
    -p 8868:8868 \
   benchao/arpt:v2.0.8

```

配置解释

```
Api_hash Api_id 这两项在https://my.telegram.org中注册应用后得到

Aria2_secret    Aria2的密匙

Telegram_bot_api    Bot的API，在@BotFather申请获得

Telegram_user_id    使用者的TG id，可在@userinfobot处获得，设置为群组ID则该群组所有人员可用，需要设置Bot的群组权限

Remote  上传目的地的rclone盘符

Upload  上传文件夹名称，后面不需要加/

Rclone_share 可不填，True 为上传网盘后返回分享链接(onedrive)，False 为关闭该功能，不设置该变量则默认关闭

Error_user_info 可不填，可设置非允许使用者发送消息时的提示，不设置该变量则使用默认语句

```

在Docker运行后访问ip:port访问文件管理器，~~在/.config/rclone下文件夹新建rclone.conf,粘贴自己的rclone配置。~~
PS:有人反馈此处配置不成功，可尝试在/root/.config/rclone也添加配置，bot运行 **/rclone 盘符:** ，可以查看是否成功
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



# 效果展示

![](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/bot下载种子.501pcym934k0.png)

![](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/image.2zx3yt2f8ow0.png)

![](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/image.52jb1gwlv4o0.png)

![](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/bot视频下载.7b1arubsqa00.png)

![](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/bot文件下载.327tinslwa00.png)

![](https://cdn.jsdelivr.net/gh/666wcy/img_share@main/img/image.771n1tka9dg0.png)


# 感谢下面大佬的贡献

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=ytdl-org&repo=youtube-dl)](https://github.com/ytdl-org/youtube-dl)

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=pyrogram&repo=pyrogram)](https://github.com/pyrogram/pyrogram)

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=pawamoy&repo=aria2p)](https://github.com/pawamoy/aria2p)

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=FolderMagic&repo=FolderMagic)](https://github.com/FolderMagic/FolderMagic)

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=mayswind&repo=AriaNg)](https://github.com/mayswind/AriaNg)

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=cokemine&repo=ServerStatus-Hotaru)](https://github.com/cokemine/ServerStatus-Hotaru)

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=P3TERX&repo=aria2.conf)](https://github.com/P3TERX/aria2.conf)

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=filebrowser&repo=filebrowser)](https://github.com/filebrowser/filebrowser)

[![Readme Card](https://github-readme-stats.vercel.app/api/pin/?username=gaowanliang&repo=OneDriveShareLinkPushAria2)](https://github.com/gaowanliang/OneDriveShareLinkPushAria2)



