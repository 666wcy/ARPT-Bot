from config import aria2,App_title
import requests
import sys
import psutil


#检查有无下载任务
def new_clock():
    try:
        if App_title!="":
            downloads = aria2.get_downloads()
            for download in downloads:
                if download.status=="active":
                    print(download.name, download.download_speed)
                    print("任务正在进行,保持唤醒")
                    print(requests.get(url=f"https://{App_title}.herokuapp.com/"))
                    sys.stdout.flush()
                    break
        else:
            print("无正在下载任务")
            sys.stdout.flush()
    except Exception as e:
            print(f"new_clock error :{e}")

#检查rclone
def second_clock():
    try:
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name'])
            except psutil.NoSuchProcess:
                pass
            else:
                if App_title!="":
                    if "rclone" in str(pinfo['name']):
                        print("rclone 正在上传")
                        print(requests.get(url=f"https://{App_title}.herokuapp.com/"))
                        sys.stdout.flush()
                        break
        else:
            print("rclone 不在运行")
            sys.stdout.flush()
    except Exception as e:
        print(f"second_clock :{e}")