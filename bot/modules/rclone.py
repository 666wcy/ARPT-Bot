import time
import subprocess
import sys
import re
import json
import os
import threading
import requests
from config import Rclone_share,Aria2_secret
from modules.control import cal_time,only_progessbar


def hum_convert(value):
    value=float(value)
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f%s" % (value, units[i])
        value = value / size


async def start_rclonecopy(client, message):
    try:
        firstdir = message.text.split()[1]
        seconddir= message.text.split()[2]
        print(f"rclone {firstdir} {seconddir}")
        sys.stdout.flush()
        rc_url = f"http://root:{Aria2_secret}@127.0.0.1:5572"
        info = await client.send_message(chat_id=message.chat.id, text=f"添加任务:", parse_mode='markdown')

        rcd_copyfile_url = f"{rc_url}/sync/copy"

        data = {
            "srcFs": firstdir,
            "dstFs": seconddir,
            "createEmptySrcDirs": True,
            "_async": True,
        }

        html = requests.post(url=rcd_copyfile_url, json=data)
        result = html.json()
        jobid = result["jobid"]

        rcd_status_url = f"{rc_url}/job/status"

        while requests.post(url=rcd_status_url, json={"jobid": jobid}).json()['finished'] == False:

            job_status = requests.post(url=f"{rc_url}/core/stats", json={"group": f"job/{jobid}"}).json()
            
            if "transferring" in job_status:

                if job_status['eta'] == None:
                    eta = "暂无"
                else:
                    eta = cal_time(job_status['eta'])
                

                text = f"任务ID:`{jobid}`\n" \
                       f"源地址:`{firstdir}`\n" \
                       f"目标地址:`{seconddir}`\n" \
                       f"传输部分:`{hum_convert(job_status['bytes'])}/{hum_convert(job_status['totalBytes'])}`\n" \
                       f"传输进度:`{only_progessbar(job_status['bytes'], job_status['totalBytes'])}%`\n" \
                       f"传输速度:`{hum_convert(job_status['speed'])}/s`\n" \
                       f"剩余时间:`{eta}`"

                try:
                    await client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                                   parse_mode='markdown')

                except:
                    continue

            else:
                print("等待信息")

            time.sleep(1)

        requests.post(url=f"{rc_url}/core/stats-delete", json={"group": f"job/{jobid}"}).json()
        requests.post(url=f"{rc_url}/fscache/clear").json()

    except Exception as e:
        print(f"rclonecopy :{e}")
        sys.stdout.flush()




async def start_rclonecopyurl(client, message):
    try:
        url = message.text.split()[1]
        print(f"rclonecopyurl {url} ")
        sys.stdout.flush()

        rc_url = f"http://root:{Aria2_secret}@127.0.0.1:5572"

        Rclone_remote = os.environ.get('Remote')
        Upload = os.environ.get('Upload')
        title = os.path.basename(url)
        info = await client.send_message(chat_id=message.chat.id, text=f"添加任务:`{title}`", parse_mode='markdown')

        rcd_copyfile_url = f"{rc_url}/operations/copyurl"

        data = {
            "fs": f"{Rclone_remote}:{Upload}",

            "remote": "",
            "url": url,
            "autoFilename": True,
            "_async": True,
        }

        html = requests.post(url=rcd_copyfile_url, json=data)

        result = html.json()

        jobid = result["jobid"]

        rcd_status_url = f"{rc_url}/job/status"

        while requests.post(url=rcd_status_url, json={"jobid": jobid}).json()['finished'] == False:

            job_status = requests.post(url=f"{rc_url}/core/stats", json={"group": f"job/{jobid}"}).json()

            if "transferring" in job_status:

                if job_status['transferring'][0]['eta'] == None:
                    eta = "暂无"
                else:
                    eta = cal_time(job_status['transferring'][0]['eta'])


                text = f"任务ID:`{jobid}`\n" \
                       f"任务名称:`{title}`\n" \
                       f"传输部分:`{hum_convert(job_status['transferring'][0]['bytes'])}/{hum_convert(job_status['transferring'][0]['size'])}`\n" \
                       f"传输进度:`{job_status['transferring'][0]['percentage']}%`\n" \
                       f"传输速度:`{hum_convert(job_status['transferring'][0]['speed'])}/s`\n" \
                       f"平均速度:`{hum_convert(job_status['transferring'][0]['speedAvg'])}/s`\n" \
                       f"剩余时间:`{eta}`"


                try:
                    await client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                             parse_mode='markdown')

                except:
                    continue

            else:
                print("等待信息加载")

            time.sleep(1)
        requests.post(url=f"{rc_url}/core/stats-delete", json={"group": f"job/{jobid}"}).json()
        requests.post(url=f"{rc_url}/fscache/clear").json()
        print("上传结束")

    except Exception as e:
        print(f"rclonecopy :{e}")
        sys.stdout.flush()

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


