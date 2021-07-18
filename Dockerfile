FROM ubuntu

RUN apt-get update
RUN apt-get install sudo
RUN sudo apt-get update
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone
RUN apt-get install wget -y
RUN apt-get install git -y
RUN apt-get install curl -y
RUN apt-get install unzip -y
RUN sudo apt install python3 -y
RUN sudo apt install python3-dev -y
RUN sudo apt install python3-pip -y
RUN sudo apt install python3-pillow -y



RUN apt install tzdata -y
RUN apt-get install aria2 -y
RUN apt-get install nginx -y

COPY root /
RUN apt install ffmpeg -y
RUN sudo chmod 777 /install.sh
RUN bash install.sh

RUN mv /nginx.conf /etc/nginx/


RUN mkdir /root/.aria2
COPY config /root/.aria2/
RUN pip3 install --upgrade pip

RUN sudo apt-get install gcc libffi-dev libssl-dev  -y

RUN pip3 install -U pyrogram tgcrypto
#RUN pip3 install pillow
RUN pip3 install telegraph
RUN pip3 install aria2p
RUN pip3 install mutagen
RUN pip3 install requests
RUN pip3 install youtube_dl
RUN pip3 install apscheduler
RUN pip3 install pyromod
RUN pip3 install psutil
RUN pip3 install nest_asyncio

RUN pip3 install nhentai --upgrade
RUN pip3 install beautifulsoup4 --upgrade

RUN mkdir /index
COPY /index.html /index

RUN mkdir /bot
COPY bot /bot
RUN chmod 0777 /bot/ -R

RUN sudo chmod 777 /root/.aria2/

COPY /config/upload.sh /
RUN chmod 0777 /upload.sh

COPY /start.sh /
CMD chmod 0777 start.sh && bash start.sh