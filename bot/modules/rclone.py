import time
import subprocess
import sys
import re
import json
import os
import threading



def hum_convert(value):
    value=float(value)
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f%s" % (value, units[i])
        value = value / size

#@bot.message_handler(commands=['rclonecopy'],func=lambda message:str(message.chat.id) == str(Telegram_user_id))
def start_rclonecopy(client, message):
    try:
        firstdir = message.text.split()[1]
        seconddir= message.text.split()[2]
        print(f"rclone {firstdir} {seconddir}")
        sys.stdout.flush()

        t1 = threading.Thread(target=run_rclonecopy, args=(firstdir,seconddir,client,message))
        t1.start()
    except Exception as e:
        print(f"rclonecopy :{e}")
        sys.stdout.flush()

def run_rclonecopy(onedir,twodir,client, message):

    name=f"{str(message.message_id)}_{str(message.chat.id)}"
    shell=f"rclone copy {onedir} {twodir}  -v --stats-one-line --stats=3s --log-file=\"{name}.log\" "
    print(shell)
    sys.stdout.flush()
    try:
        client.send_message(chat_id=message.chat.id, text=shell)
        info=client.send_message(chat_id=message.chat.id ,text=shell)
        print(info)
        sys.stdout.flush()
    except Exception as e:
        print(f"信息发送错误 {e}")
        sys.stdout.flush()
        return



    cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                           stdout=subprocess.PIPE, universal_newlines=True, shell=True, bufsize=1)
    # 实时输出
    temp_text=None
    while True:
        time.sleep(3)
        fname = f'{name}.log'
        with open(fname, 'r') as f:  #打开文件
            try:
                lines = f.readlines() #读取所有行

                for a in range(-1,-10,-1):
                    last_line = lines[a] #取最后一行
                    if last_line !="\n":
                        break

                print (f"上传中\n{last_line}")
                sys.stdout.flush()
                if temp_text != last_line and "ETA" in last_line:
                    print(last_line)
                    sys.stdout.flush()
                    log_time,file_part,upload_Progress,upload_speed,part_time=re.findall("(.*?)INFO.*?(\d.*?),.*?(\d+%),.*?(\d.*?s).*?ETA.*?(\d.*?)",last_line , re.S)[0]
                    text=f"源地址:`{onedir}`\n" \
                         f"目标地址:`{twodir}`\n" \
                         f"更新时间：`{log_time}`\n" \
                     f"传输部分：`{file_part}`\n" \
                     f"传输进度：`{upload_Progress}`\n" \
                     f"传输速度：`{upload_speed}`\n" \
                     f"剩余时间:`{part_time}`"
                    try:
                        client.edit_message_text(text=text,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
                    except Exception as e:
                        print(f"信息修改错误 {e}")
                        continue
                    temp_text = last_line
                f.close()

            except Exception as e:
                print(e)
                f.close()
                continue

        if subprocess.Popen.poll(cmd) == 0:  # 判断子进程是否结束
            print("上传结束")
            client.send_message(text=f"rclone运行结束",chat_id=info.chat.id)
            os.remove(f"{name}.log")
            return

    return cmd.returncode


def run_rclonecopyurl(url,client, message):

    Rclone_remote=os.environ.get('Remote')
    Upload=os.environ.get('Upload')
    twodir =f"{Rclone_remote}:{Upload}"
    name=f"{str(message.message_id)}_{str(message.chat.id)}"
    shell=f"rclone copyurl \"{url}\" {twodir} --auto-filename --no-clobber -v --stats-one-line --stats=1s --log-file=\"{name}.log\" "
    print(shell)
    sys.stdout.flush()
    try:
        info=client.send_message(chat_id=message.chat.id ,text=shell)
        print(info)
        sys.stdout.flush()
    except Exception as e:
        print(f"信息发送错误 {e}")
        sys.stdout.flush()
        return



    cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                           stdout=subprocess.PIPE, universal_newlines=True, shell=True, bufsize=1)
    # 实时输出
    temp_text=None
    while True:
        time.sleep(3)
        fname = f'{name}.log'
        with open(fname, 'r') as f:  #打开文件
            try:
                lines = f.readlines() #读取所有行

                for a in range(-1,-10,-1):
                    last_line = lines[a] #取最后一行
                    if last_line !="\n":
                        break

                print (f"上传中\n{last_line}")
                sys.stdout.flush()
                if temp_text != last_line and "ETA" in last_line:
                    print(last_line)
                    sys.stdout.flush()
                    log_time,file_part,upload_Progress,upload_speed,part_time=re.findall("(.*?)INFO.*?(\d.*?),.*?(\d+%),.*?(\d.*?s).*?ETA.*?(\d.*?)",last_line , re.S)[0]
                    text=f"源地址:`{url}`\n" \
                         f"目标地址:`{twodir}`\n" \
                         f"更新时间：`{log_time}`\n" \
                     f"传输部分：`{file_part}`\n" \
                     f"传输进度：`{upload_Progress}`\n" \
                     f"传输速度：`{upload_speed}`\n" \
                     f"剩余时间:`{part_time}`"
                    try:
                        client.edit_message_text(text=text,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
                    except Exception as e:
                        print(f"信息修改错误 {e}")
                        continue
                    temp_text = last_line
                f.close()

            except Exception as e:
                print(e)
                f.close()
                continue

        if subprocess.Popen.poll(cmd) == 0:  # 判断子进程是否结束
            print("上传结束")
            client.send_message(text=f"rclone运行结束",chat_id=info.chat.id)
            os.remove(f"{name}.log")
            return

    return cmd.returncode

#@bot.message_handler(commands=['rclonecopyurl'],func=lambda message:str(message.chat.id) == str(Telegram_user_id))
def start_rclonecopyurl(client, message):
    try:
        url = message.text.split()[1]
        print(f"rclonecopyurl {url} ")
        sys.stdout.flush()

        t1 = threading.Thread(target=run_rclonecopyurl, args=(url,client,message))
        t1.start()
    except Exception as e:
        print(f"rclonecopy :{e}")
        sys.stdout.flush()


#@bot.message_handler(commands=['rclonelsd'],func=lambda message:str(message.chat.id) == str(Telegram_user_id))
async def start_rclonelsd(client, message):
    try:
        firstdir = message.text.split()[1]
        child1 = subprocess.Popen(f'rclone lsd {firstdir}',shell=True, stdout=subprocess.PIPE)
        out = child1.stdout.read()
        print(out)
        i = str(out,encoding='utf-8').replace("          ","")
        print(i)
        await client.send_message(chat_id=message.chat.id,text=f"`{str(i)}`",parse_mode='markdown')
    except Exception as e:
        print(f"rclonelsd :{e}")
        sys.stdout.flush()

#@bot.message_handler(commands=['rclone'],func=lambda message:str(message.chat.id) == str(Telegram_user_id))
async def start_rclonels(client, message):
    try:
        firstdir = message.text.split()[1]
        child1 = subprocess.Popen(f'rclone lsjson {firstdir}',shell=True, stdout=subprocess.PIPE)
        out = child1.stdout.read()
        print(out)
        i = str(out,encoding='utf-8').replace("","")
        print(i)
        info=i.replace("[\n","").replace("\n]","")
        print(info)
        info_list=info.split(",\n")
        print(info_list)
        text=""
        for a in info_list:
            new=json.loads(a)
            print(new)
            filetime=str(new['ModTime']).replace("T"," ").replace("Z"," ")
            text=text+f"{filetime}--{new['Name']}\n"
        await client.send_message(chat_id=message.chat.id,text=f"`{text}`",parse_mode='markdown')
    except Exception as e:
        print(f"rclone :{e}")
        sys.stdout.flush()


