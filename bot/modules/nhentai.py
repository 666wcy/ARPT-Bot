import subprocess
import time
import sys
import re
import zipfile
import os
import telegraph
from modules.control import run_await_rclone
from modules.pixiv import compress_image, put_telegraph

def del_path(path):
    if not os.path.exists(path):
        return
    if os.path.isfile(path):
        os.remove(path)
        # print( 'delete file %s' % path)
    else:
        items = os.listdir(path)
        for f in items:
            c_path = os.path.join(path, f)
            if os.path.isdir(c_path):
                del_path(c_path)
            else:
                os.remove(c_path)
                # print('delete file %s' % c_path)
        os.rmdir(path)
        # print( 'delete dir %s' % path)

def progress(current, total,client,message,name):

    print(f"{current * 100 / total:.1f}%")
    pro=f"{current * 100 / total:.1f}%"
    try:
        client.edit_message_text(chat_id=message.chat.id,message_id=message.message_id,text=f"{name}\n上传中:{pro}")
    except Exception as e:
        print(f"{e}")

def zip_ya(start_dir):
    start_dir = start_dir  # 要压缩的文件夹路径
    file_news = start_dir + '.zip'  # 压缩后文件夹的名字
    z = zipfile.ZipFile(file_news, 'w', zipfile.ZIP_DEFLATED)
    for dir_path, dir_names, file_names in os.walk(start_dir):
        f_path = dir_path.replace(start_dir, '')  # 这一句很重要，不replace的话，就从根目录开始复制
        f_path = f_path and f_path + os.sep or ''  # 实现当前文件夹以及包含的所有文件的压缩
        for filename in file_names:
            z.write(os.path.join(dir_path, filename), f_path + filename)
    z.close()
    return file_news

async def download_nhentai_id(client, message):
    try:
        nhentai_id= message.text.split(" ")[1]
        info = await client.send_message(text="获取到ID，正在下载", chat_id=message.chat.id,
                            parse_mode='markdown' )
        shell = f"nhentai --id={nhentai_id} --format \'%t\'"
        print(shell)
        cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True, stdout=subprocess.PIPE,
                               universal_newlines=True, shell=True, bufsize=1)
        # 实时输出

        while True:

            if subprocess.Popen.poll(cmd) == 0:  # 判断子进程是否结束

                result = str(cmd.stdout.read())
                break

        print(result)
        if "All done" in result:
            path = re.findall("Path \'(.*?)\' does not exist, creating", result, re.S)[0]
            print(f"下载路径:{path}")
            await client.edit_message_text(text=f"下载成功,下载路径:\n{path}", chat_id=info.chat.id, message_id=info.message_id,
                                     parse_mode='markdown')
        else:
            print("下载失败")
            await client.edit_message_text(text="下载失败", chat_id=info.chat.id, message_id=info.message_id,
                                     parse_mode='markdown')
            return
        try:
            choice = message.text.split(" ")[2]
        except:


            try:
                name = zip_ya(path)
                print(name)
                print("压缩完成，开始上传")
                await client.edit_message_text(text="压缩完成，开始上传", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
                del_path(path)
            except Exception as e:
                await client.edit_message_text(text=f"压缩失败 : {e}", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
                return
            try:
                await client.send_document(chat_id=info.chat.id, document=name, caption=name, progress=progress,
                                           progress_args=(client, info, name,))

                print("uploading")
                return
            except Exception as e:
                print(f"{e}")
                sys.stdout.flush()
                await client.edit_message_text(text=f"文件上传失败 : {e}", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
            os.system("rm '" + name + "'")
            return

        if choice=="tg":
            try:
                name = zip_ya(path)
                print(name)
                print("压缩完成，开始上传")
                await client.edit_message_text(text="压缩完成，开始上传", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
                del_path(path)
            except Exception as e:
                await client.edit_message_text(text=f"压缩失败 : {e}", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
                return
            try:
                await client.send_document(chat_id=info.chat.id, document=name, caption=name, progress=progress,
                                           progress_args=(client, info, name,))

                print("uploading")
            except Exception as e:
                print(f"{e}")
                sys.stdout.flush()
                await client.edit_message_text(text=f"文件上传失败 : {e}", chat_id=info.chat.id,
                                               message_id=info.message_id,
                                               parse_mode='markdown')
            os.system("rm '" + name + "'")

        elif choice=="rclone":
            try:
                name = zip_ya(path)
                print(name)
                print("压缩完成，开始上传")
                await client.edit_message_text(text="压缩完成，开始上传", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
                del_path(path)
            except Exception as e:
                await client.edit_message_text(text=f"压缩失败 : {e}", chat_id=info.chat.id, message_id=info.message_id,
                                               parse_mode='markdown')
                return
            try:
                await run_await_rclone(dir=name, title=name, info=info, file_num=1, client=client, message=info)
                print("uploading")
            except Exception as e:
                print(f"{e}")
                sys.stdout.flush()
                client.send_message(info.chat.id, text=f"文件上传失败:\n{e}")
            client.delete_message(info.chat.id, info.message_id)
            os.system("rm '" + name + "'")

        elif choice=="tele" :
            img_list = []
            name_list = []

            filelists = os.listdir(path)
            sort_num_first = list(filelists)

            sort_num_first.sort()
            sorted_file = []
            for sort_num in sort_num_first:
                for file in filelists:
                    if str(sort_num) == file:
                        sorted_file.append( file)

            for file in sorted_file:
                    try:
                        if "jpg" not in str(file) and "png" not in str(file):
                            continue
                        file_dir = os.path.join(path, file)
                        print(file_dir, file)

                        if os.path.getsize(file_dir) < 1024 * 512 * 10:
                            print(file_dir, file)

                            info = telegraph.upload.upload_file(file_dir)
                            url = "https://telegra.ph" + info[0]

                            name_list.append(file)
                            img_list.append(url)
                        else:
                            file_dir = compress_image(outfile=file_dir, mb=5000)
                            print(file_dir, file)
                            info = telegraph.upload.upload_file(file_dir)
                            url = "https://telegra.ph" + info[0]

                            name_list.append(file)
                            img_list.append(url)



                    except Exception as e:
                        print(f"标记4 {e}")

                        sys.stdout.flush()
                        continue
            try:
                put_text = "<p>Tips:5M以上的图片会被压缩</p><br>"
                for  b in img_list:
                    put_text = put_text + f"<strong></strong><br /><img src=\"{b}\" /><br>\n\n"
                print(put_text)

                put_url = put_telegraph(title=f"{os.path.basename(path)}", md_text=put_text)
                print(put_url)
                await client.send_message(chat_id=message.chat.id, text=put_url)



            except Exception as e:
                print(f"标记8 {e}")
                sys.stdout.flush()
                await client.send_message(chat_id=message.chat.id, text="发布失败")
                del_path(path)
                return

            del_path(path)
            return



    except Exception as e :
        print(f"download_hentai_id error : {e}")
        await client.send_message(text=f"download_hentai_id error : {e}", chat_id=message.chat.id,
                            parse_mode='markdown')