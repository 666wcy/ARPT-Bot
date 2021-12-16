from config import aria2,App_title,Aria2_secret
import requests
import sys
import psutil


#检查有无下载任务
def new_clock():
    try:
        downloads = aria2.get_downloads()
        for download in downloads:
            if download.status=="active":
                print(download.name, download.download_speed)
                print("任务正在进行,保持唤醒")
                print(requests.get(url=f"http://{App_title}.herokuapp.com/"))
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

        rc_url = f"http://root:{str(Aria2_secret)}@127.0.0.1:5572"
        job_status = requests.post(url=f"{rc_url}/core/stats").json()
        #print(job_status)
        if "transferring" in job_status:
            print("rclone 正在上传")
            print(requests.get(url=f"http://{App_title}.herokuapp.com/"))
            sys.stdout.flush()

        else:
            print("rclone 不在运行")
            sys.stdout.flush()
    except Exception as e:
        print(f"second_clock :{e}")