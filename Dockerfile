FROM ubuntu

# Basic Setup

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone

RUN apt-get update && apt-get install -y sudo && sudo apt-get update
RUN sudo apt-get install -y wget git curl unzip python3 python3-dev python3-pip python3-pillow gcc libffi-dev libssl-dev  
RUN sudo apt-get install -y tzdata aria2 nginx ffmpeg

# PyPI Packages

RUN sudo apt-get install -y gconf-service libasound2 libatk1.0-0 libatk-bridge2.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils
RUN pip3 install -U pip
RUN pip3 install -U pyrogram tgcrypto telegraph aria2p mutagen requests yt-dlp apscheduler pyromod psutil nest_asyncio pyppeteer ffmpeg-python

RUN sudo apt-get install -y libxml2-dev libxslt-dev
RUN pip3 install -U beautifulsoup4
RUN pip3 install -U lxml
RUN pip3 install -U nhentai
RUN sudo apt-get clean

## install.sh: script to install Rclone and filebrowser
COPY root /
RUN sudo chmod 777 /install.sh
RUN bash install.sh


# Configuration 

## upload.sh: Use Rclone to upload files after Aria2 download is complete
COPY config/upload.sh /
COPY config/rclone /root/.config/rclone
RUN chmod 0777 /upload.sh

## for nginx 
COPY config/nginx /etc/nginx

## for AriaNG
RUN mkdir /index
COPY index.html /index

## for aria2
RUN mkdir /root/.aria2
COPY config/aria2 /root/.aria2/
RUN sudo chmod 777 /root/.aria2/

## Bot 
RUN mkdir /bot
COPY bot /bot
RUN chmod 0777 /bot/ -R

# Start Daemon
COPY start.sh /
CMD chmod 0777 start.sh && bash start.sh