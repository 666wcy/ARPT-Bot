# -*- coding: utf-8 -*-

from config import aria2, BOT_name,Rclone_share,Aria2_secret
import sys
from pyrogram.types import InlineKeyboardMarkup,InlineKeyboardButton
import os
import time
import threading
import asyncio
import subprocess
import re
import urllib
import urllib.request
from pprint import pprint
from urllib import parse
import json
import requests
from pyppeteer import launch
import copy
import nest_asyncio

nest_asyncio.apply()
os.system("df -lh")
task=[]

async def getpassword(iurl, password):
    global pheader, url
    browser = await launch(options={'args': ['--no-sandbox']})
    page = await browser.newPage()
    await page.goto(iurl, {'waitUntil': 'networkidle0'})
    await page.focus("input[id='txtPassword']")
    await page.keyboard.type(password)
    verityElem = await page.querySelector("input[id='btnSubmitPassword']")
    print("密码输入完成，正在跳转")

    await asyncio.gather(
        page.waitForNavigation(),
        verityElem.click(),
    )
    url = await page.evaluate('window.location.href', force_expr=True)
    await page.screenshot({'path': 'example.png'})
    print("正在获取Cookie")
    # print(p.headers, p.url)
    _cookie = await page.cookies()
    pheader = ""
    for __cookie in _cookie:
        coo = "{}={};".format(__cookie.get("name"), __cookie.get("value"))
        pheader += coo
    await browser.close()
    return pheader,url


async def downloadFiles(client,info,password,originalPath, req, layers, start=1, num=-1, _id=0):
    #sudo apt-get install  gconf-service libasound2 libatk1.0-0 libatk-bridge2.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget -y
    #pyppeteer-install


    header = {
        'sec-ch-ua-mobile': '?0',
        'upgrade-insecure-requests': '1',
        'dnt': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'service-worker-navigation-preload': 'true',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'iframe',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'

    }

    if password != "":
        print("正在启动无头浏览器模拟输入密码")
        text="正在启动无头浏览器模拟输入密码   "
        await client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                       parse_mode='markdown')
        pheader ,temp_url= asyncio.get_event_loop().run_until_complete(getpassword(originalPath, password))
        print("无头浏览器关闭，正在获取文件列表")
        text = "无头浏览器关闭，正在获取文件列表"
        await client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                       parse_mode='markdown')

        header['cookie'] = pheader
        print(password)
        print(pheader)
        originalPath=temp_url
        password=""

    if req == None:
        req = requests.session()
    # print(header)

    reqf = req.get(originalPath, headers=header)
    if "-my" not in originalPath:
        isSharepoint = True
        print("sharepoint 链接")
    else:
        isSharepoint = False

    # f=open()
    if ',"FirstRow"' not in reqf.text:
        print("\t" * layers, "这个文件夹没有文件")
        return 0

    filesData = []
    redirectURL = reqf.url
    redirectSplitURL = redirectURL.split("/")
    query = dict(urllib.parse.parse_qsl(
        urllib.parse.urlsplit(redirectURL).query))
    downloadURL = "/".join(redirectSplitURL[:-1]) + "/download.aspx?UniqueId="
    if isSharepoint:
        pat = re.search('templateUrl":"(.*?)"', reqf.text)

        downloadURL = pat.group(1)
        downloadURL = urllib.parse.urlparse(downloadURL)
        downloadURL = "{}://{}{}".format(downloadURL.scheme,
                                         downloadURL.netloc, downloadURL.path).split("/")
        downloadURL = "/".join(downloadURL[:-1]) + \
                      "/download.aspx?UniqueId="
        print(downloadURL)

    # print(reqf.headers)

    s2 = urllib.parse.urlparse(redirectURL)
    header["referer"] = redirectURL
    header["cookie"] = reqf.headers["set-cookie"]
    header["authority"] = s2.netloc

    headerStr = ""
    for key, value in header.items():
        # print(key+':'+str(value))
        headerStr += key + ':' + str(value) + "\n"
    relativeFolder = ""
    rootFolder = query["id"]
    for i in rootFolder.split("/"):
        if i != "Documents":
            relativeFolder += i + "/"
        else:
            relativeFolder += i
            break
    relativeUrl = parse.quote(relativeFolder).replace(
        "/", "%2F").replace("_", "%5F").replace("-", "%2D")
    rootFolderUrl = parse.quote(rootFolder).replace(
        "/", "%2F").replace("_", "%5F").replace("-", "%2D")

    graphqlVar = '{"query":"query (\n        $listServerRelativeUrl: String!,$renderListDataAsStreamParameters: RenderListDataAsStreamParameters!,$renderListDataAsStreamQueryString: String!\n        )\n      {\n      \n      legacy {\n      \n      renderListDataAsStream(\n      listServerRelativeUrl: $listServerRelativeUrl,\n      parameters: $renderListDataAsStreamParameters,\n      queryString: $renderListDataAsStreamQueryString\n      )\n    }\n      \n      \n  perf {\n    executionTime\n    overheadTime\n    parsingTime\n    queryCount\n    validationTime\n    resolvers {\n      name\n      queryCount\n      resolveTime\n      waitTime\n    }\n  }\n    }","variables":{"listServerRelativeUrl":"%s","renderListDataAsStreamParameters":{"renderOptions":5707527,"allowMultipleValueFilterForTaxonomyFields":true,"addRequiredFields":true,"folderServerRelativeUrl":"%s"},"renderListDataAsStreamQueryString":"@a1=\'%s\'&RootFolder=%s&TryNewExperienceSingle=TRUE"}}' % (relativeFolder, rootFolder, relativeUrl, rootFolderUrl)


    # print(graphqlVar)
    s2 = urllib.parse.urlparse(redirectURL)
    tempHeader = copy.deepcopy(header)
    tempHeader["referer"] = redirectURL
    tempHeader["cookie"] = reqf.headers["set-cookie"]
    tempHeader["authority"] = s2.netloc
    tempHeader["content-type"] = "application/json;odata=verbose"
    # print(redirectSplitURL)

    graphqlReq = req.post(
        "/".join(redirectSplitURL[:-3]) + "/_api/v2.1/graphql", data=graphqlVar.encode('utf-8'), headers=tempHeader)
    graphqlReq = json.loads(graphqlReq.text)
    # print(graphqlReq)
    if "NextHref" in graphqlReq["data"]["legacy"]["renderListDataAsStream"]["ListData"]:
        nextHref = graphqlReq[
                       "data"]["legacy"]["renderListDataAsStream"]["ListData"][
                       "NextHref"] + "&@a1=%s&TryNewExperienceSingle=TRUE" % (
                           "%27" + relativeUrl + "%27")
        filesData.extend(graphqlReq[
                             "data"]["legacy"]["renderListDataAsStream"]["ListData"]["Row"])
        # print(filesData)

        listViewXml = graphqlReq[
            "data"]["legacy"]["renderListDataAsStream"]["ViewMetadata"]["ListViewXml"]
        renderListDataAsStreamVar = '{"parameters":{"__metadata":{"type":"SP.RenderListDataParameters"},"RenderOptions":1216519,"ViewXml":"%s","AllowMultipleValueFilterForTaxonomyFields":true,"AddRequiredFields":true}}' % (
            listViewXml).replace('"', '\\"')
        # print(renderListDataAsStreamVar, nextHref,1)

        # print(listViewXml)

        graphqlReq = req.post(
            "/".join(
                redirectSplitURL[:-3]) + "/_api/web/GetListUsingPath(DecodedUrl=@a1)/RenderListDataAsStream" + nextHref,
            data=renderListDataAsStreamVar.encode('utf-8'), headers=tempHeader)
        graphqlReq = json.loads(graphqlReq.text)
        # print(graphqlReq)

        while "NextHref" in graphqlReq["ListData"]:
            nextHref = graphqlReq["ListData"]["NextHref"] + "&@a1=%s&TryNewExperienceSingle=TRUE" % (
                    "%27" + relativeUrl + "%27")
            filesData.extend(graphqlReq["ListData"]["Row"])
            graphqlReq = req.post(
                "/".join(redirectSplitURL[
                         :-3]) + "/_api/web/GetListUsingPath(DecodedUrl=@a1)/RenderListDataAsStream" + nextHref,
                data=renderListDataAsStreamVar.encode('utf-8'), headers=tempHeader)
            # print(graphqlReq.text)
            graphqlReq = json.loads(graphqlReq.text)
            # print(graphqlReq)
        filesData.extend(graphqlReq["ListData"]["Row"])
    else:
        filesData = filesData.extend(graphqlReq[
                                         "data"]["legacy"]["renderListDataAsStream"]["ListData"]["Row"])

    fileCount = 0
    # print(headerStr)
    if filesData==None:
        pat = re.search(
            'g_listData = {"wpq":"","Templates":{},"ListData":{ "Row" : ([\s\S]*?),"FirstRow"', reqf.text)
        filesData = json.loads(pat.group(1))
    for i in filesData:
        if i['FSObjType'] == "1":

            _query = query.copy()
            _query['id'] = os.path.join(
                _query['id'], i['FileLeafRef']).replace("\\", "/")
            if not isSharepoint:
                originalPath = "/".join(redirectSplitURL[:-1]) + \
                               "/onedrive.aspx?" + urllib.parse.urlencode(_query)
            else:
                originalPath = "/".join(redirectSplitURL[:-1]) + \
                               "/AllItems.aspx?" + urllib.parse.urlencode(_query)


            fileCount += await downloadFiles(client, info,password, originalPath, req, layers + 1, _id=fileCount, start=start,
                                             num=num)
        else:
            fileCount += 1
            if num == -1 or start <= fileCount + _id < start + num:

                cc = downloadURL + (i["UniqueId"][1:-1].lower())
                download_path = f"/root/Download{str(query['id']).split('Documents', 1)[1]}"
                dd = dict(out=i["FileLeafRef"], header=headerStr, dir=download_path)

                aria2Link = "http://localhost:8080/jsonrpc"
                aria2Secret = os.environ.get('Aria2_secret')
                jsonreq = json.dumps({'jsonrpc': '2.0', 'id': 'qwer',
                                      'method': 'aria2.addUri',
                                      "params": ["token:" + aria2Secret, [cc], dd]})

                c = requests.post(aria2Link, data=jsonreq)
                pprint(json.loads(c.text))
                text = f"推送下载：`{i['FileLeafRef']}`\n下载路径:`{download_path}`\n推送结果:`{c.text}`"
                try:
                    await client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                                   parse_mode='markdown')
                except Exception as e:
                    print(f"修改信息失败:{e}")
                time.sleep(0.5)

    return fileCount

async def odshare_download(client, message):

    try:
        odshare_url=str(message.text).split(" ")[1]
        try:
            password=str(message.text).split(" ")[2]
        except:
            password=""
        info = await client.send_message(chat_id=message.chat.id, text="开始抓取下载链接", parse_mode='markdown')
        fileCount= await downloadFiles(client,info,password,odshare_url, None, 0,start=1, num=-1)
        await client.edit_message_text(text=f"推送至Aria2完成，可到AriaNG面板查看\n本次推送{fileCount}个任务", chat_id=info.chat.id, message_id=info.message_id,
                                       parse_mode='markdown')
    except Exception as e:
        print(f"odshare error {e}")
        await client.send_message(chat_id=message.chat.id, text="抓取下载链接失败", parse_mode='markdown')


async def login_of_share(client,info,link,admin,password):
    try:

        url = "http://portal.office.com/onedrive"
        # browser = await launch(headless=False,options={'args': ['--no-sandbox']})
        browser = await launch(options={'args': ['--no-sandbox']})
        page = await browser.newPage()
        print(admin,password)

        await page.goto(url, {'waitUntil': 'networkidle0'})


        await page.type("input[id='i0116']", admin)
        await client.edit_message_text(text=f"已输入账号", chat_id=info.chat.id,
                                       message_id=info.message_id,
                                       parse_mode='markdown')

        await page.click("#idSIButton9")
        await asyncio.sleep(3)

        await page.type("input[id='i0118']", password)

        print("密码输入完成，正在跳转")


        await page.click("#idSIButton9")
        await client.edit_message_text(text=f"密码输入完成，正在跳转", chat_id=info.chat.id,
                                       message_id=info.message_id,
                                       parse_mode='markdown')
        await asyncio.sleep(3)

        # await page.click("input[value='登录']")
        # await page.keyboard.press('Enter')

        await asyncio.wait([
            page.click("#idSIButton9"),
            page.waitForNavigation({'timeout': 50000}),
        ])
        await client.edit_message_text(text=f"选择保持登录状态", chat_id=info.chat.id,
                                       message_id=info.message_id,
                                       parse_mode='markdown')
        await asyncio.sleep(5)
        while not await page.querySelector('.od-ItemContent-title'):
            pass

        url = await page.evaluate('window.location.href', force_expr=True)
        print(url)

        res = await page.goto(link, {'waitUntil': 'networkidle0'})

        url = await page.evaluate('window.location.href', force_expr=True)
        print(url)

        print("点击完成")

        print(res.request.headers)

        header = res.request.headers

        _cookie = await page.cookies()
        pheader = ""
        for __cookie in _cookie:
            coo = "{}={};".format(__cookie.get("name"), __cookie.get("value"))
            pheader += coo

        header['cookie'] = pheader
        reqf = requests.get(url, headers=header)
        print(reqf)
        if reqf.status_code!=200:
            return header,""
        await browser.close()
        return header,url
    except Exception as e:
        print(f"login_of_share {e}")
        await client.send_message(chat_id=info.chat.id, text=f"login_of_share {e}", parse_mode='markdown')


async def odpriva_downloadFiles(client,info,admin,password,originalPath, req, layers, start=1, num=-1, _id=0):
    try:
        header={}
        if req == None:
            req = requests.session()
            header, originalPath = await login_of_share(client,info,originalPath, admin=admin, password=password)
            if originalPath=="":
                await client.edit_message_text(text=f"登录错误", chat_id=info.chat.id,
                                               message_id=info.message_id,
                                               parse_mode='markdown')
                return
        # print(header)

        reqf = req.get(originalPath, headers=header)
        if "-my" not in originalPath:
            isSharepoint = True
            print("sharepoint 链接")
        else:
            isSharepoint = False

        # f=open()
        if ',"FirstRow"' not in reqf.text:
            print("\t" * layers, "这个文件夹没有文件")
            return 0

        filesData = []
        redirectURL = reqf.url
        redirectSplitURL = redirectURL.split("/")
        query = dict(urllib.parse.parse_qsl(
            urllib.parse.urlsplit(redirectURL).query))
        downloadURL = "/".join(redirectSplitURL[:-1]) + "/download.aspx?UniqueId="
        if isSharepoint:
            pat = re.search('templateUrl":"(.*?)"', reqf.text)

            downloadURL = pat.group(1)
            downloadURL = urllib.parse.urlparse(downloadURL)
            downloadURL = "{}://{}{}".format(downloadURL.scheme,
                                             downloadURL.netloc, downloadURL.path).split("/")
            downloadURL = "/".join(downloadURL[:-1]) + \
                          "/download.aspx?UniqueId="


        # print(reqf.headers)

        s2 = urllib.parse.urlparse(redirectURL)
        header["referer"] = redirectURL
        #header["cookie"] = reqf.headers["set-cookie"]
        header["authority"] = s2.netloc

        headerStr = ""
        for key, value in header.items():
            # print(key+':'+str(value))
            headerStr += key + ':' + str(value) + "\n"
        relativeFolder = ""
        rootFolder = query["id"]
        for i in rootFolder.split("/"):
            if i != "Documents":
                relativeFolder += i + "/"
            else:
                relativeFolder += i
                break
        relativeUrl = parse.quote(relativeFolder).replace(
            "/", "%2F").replace("_", "%5F").replace("-", "%2D")
        rootFolderUrl = parse.quote(rootFolder).replace(
            "/", "%2F").replace("_", "%5F").replace("-", "%2D")

        graphqlVar = '{"query":"query (\n        $listServerRelativeUrl: String!,$renderListDataAsStreamParameters: RenderListDataAsStreamParameters!,$renderListDataAsStreamQueryString: String!\n        )\n      {\n      \n      legacy {\n      \n      renderListDataAsStream(\n      listServerRelativeUrl: $listServerRelativeUrl,\n      parameters: $renderListDataAsStreamParameters,\n      queryString: $renderListDataAsStreamQueryString\n      )\n    }\n      \n      \n  perf {\n    executionTime\n    overheadTime\n    parsingTime\n    queryCount\n    validationTime\n    resolvers {\n      name\n      queryCount\n      resolveTime\n      waitTime\n    }\n  }\n    }","variables":{"listServerRelativeUrl":"%s","renderListDataAsStreamParameters":{"renderOptions":5707527,"allowMultipleValueFilterForTaxonomyFields":true,"addRequiredFields":true,"folderServerRelativeUrl":"%s"},"renderListDataAsStreamQueryString":"@a1=\'%s\'&RootFolder=%s&TryNewExperienceSingle=TRUE"}}' % (
        relativeFolder, rootFolder, relativeUrl, rootFolderUrl)

        # print(graphqlVar)
        s2 = urllib.parse.urlparse(redirectURL)
        tempHeader = copy.deepcopy(header)
        tempHeader["referer"] = redirectURL
        #tempHeader["cookie"] = reqf.headers["set-cookie"]
        tempHeader["authority"] = s2.netloc
        tempHeader["content-type"] = "application/json;odata=verbose"
        # print(redirectSplitURL)

        graphqlReq = req.post(
            "/".join(redirectSplitURL[:-3]) + "/_api/v2.1/graphql", data=graphqlVar.encode('utf-8'), headers=tempHeader)
        graphqlReq = json.loads(graphqlReq.text)
        # print(graphqlReq)
        if "NextHref" in graphqlReq["data"]["legacy"]["renderListDataAsStream"]["ListData"]:
            nextHref = graphqlReq[
                           "data"]["legacy"]["renderListDataAsStream"]["ListData"][
                           "NextHref"] + "&@a1=%s&TryNewExperienceSingle=TRUE" % (
                               "%27" + relativeUrl + "%27")
            filesData.extend(graphqlReq[
                                 "data"]["legacy"]["renderListDataAsStream"]["ListData"]["Row"])
            # print(filesData)

            listViewXml = graphqlReq[
                "data"]["legacy"]["renderListDataAsStream"]["ViewMetadata"]["ListViewXml"]
            renderListDataAsStreamVar = '{"parameters":{"__metadata":{"type":"SP.RenderListDataParameters"},"RenderOptions":1216519,"ViewXml":"%s","AllowMultipleValueFilterForTaxonomyFields":true,"AddRequiredFields":true}}' % (
                listViewXml).replace('"', '\\"')
            # print(renderListDataAsStreamVar, nextHref,1)

            # print(listViewXml)

            graphqlReq = req.post(
                "/".join(
                    redirectSplitURL[:-3]) + "/_api/web/GetListUsingPath(DecodedUrl=@a1)/RenderListDataAsStream" + nextHref,
                data=renderListDataAsStreamVar.encode('utf-8'), headers=tempHeader)
            graphqlReq = json.loads(graphqlReq.text)
            # print(graphqlReq)

            while "NextHref" in graphqlReq["ListData"]:
                nextHref = graphqlReq["ListData"]["NextHref"] + "&@a1=%s&TryNewExperienceSingle=TRUE" % (
                        "%27" + relativeUrl + "%27")
                filesData.extend(graphqlReq["ListData"]["Row"])
                graphqlReq = req.post(
                    "/".join(redirectSplitURL[
                             :-3]) + "/_api/web/GetListUsingPath(DecodedUrl=@a1)/RenderListDataAsStream" + nextHref,
                    data=renderListDataAsStreamVar.encode('utf-8'), headers=tempHeader)
                # print(graphqlReq.text)
                graphqlReq = json.loads(graphqlReq.text)
                # print(graphqlReq)
            filesData.extend(graphqlReq["ListData"]["Row"])
        else:
            filesData = filesData.extend(graphqlReq[
                                             "data"]["legacy"]["renderListDataAsStream"]["ListData"]["Row"])

        fileCount = 0
        # print(headerStr)
        if filesData == None:
            pat = re.search(
                'g_listData = {"wpq":"","Templates":{},"ListData":{ "Row" : ([\s\S]*?),"FirstRow"', reqf.text)
            filesData = json.loads(pat.group(1))
        for i in filesData:
            if i['FSObjType'] == "1":

                _query = query.copy()
                _query['id'] = os.path.join(
                    _query['id'], i['FileLeafRef']).replace("\\", "/")
                if not isSharepoint:
                    originalPath = "/".join(redirectSplitURL[:-1]) + \
                                   "/onedrive.aspx?" + urllib.parse.urlencode(_query)
                else:
                    originalPath = "/".join(redirectSplitURL[:-1]) + \
                                   "/AllItems.aspx?" + urllib.parse.urlencode(_query)

                fileCount += await odpriva_downloadFiles(client, info,admin,password, originalPath, req, layers + 1, _id=fileCount, start=start,
                                                 num=num)
            else:
                fileCount += 1
                if num == -1 or start <= fileCount + _id < start + num:
                    print("\t" * layers, "文件 [%d]：%s\t独特ID：%s\t正在推送" %
                          (fileCount + _id, i['FileLeafRef'], i["UniqueId"]))
                    cc = downloadURL + (i["UniqueId"][1:-1].lower())
                    download_path = f"/root/Download{str(query['id']).split('Documents', 1)[1]}"
                    dd = dict(out=i["FileLeafRef"], header=headerStr, dir=download_path)
                    print(cc, dd)
                    aria2Link = "http://localhost:8080/jsonrpc"
                    aria2Secret = os.environ.get('Aria2_secret')
                    jsonreq = json.dumps({'jsonrpc': '2.0', 'id': 'qwer',
                                          'method': 'aria2.addUri',
                                          "params": ["token:" + aria2Secret, [cc], dd]})

                    c = requests.post(aria2Link, data=jsonreq)

                    text = f"推送下载：`{i['FileLeafRef']}`\n下载路径:`{download_path}`\n推送结果:`{c.text}`"
                    try:
                        await client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                                       parse_mode='markdown')
                    except Exception as e:
                        print(f"修改信息失败:{e}")
                    time.sleep(0.5)

        return fileCount
    except Exception as e:
        print(f"odpriva_downloadFiles {e}")
        await client.send_message(chat_id=info.chat.id, text=f"odpriva_downloadFiles {e}", parse_mode='markdown')


async def odprivate_download(client, message):
    try:

        try:
            login_info=str(message.text).split(" ")
            print(f"odprivate_download{login_info}")
            admin=login_info[1]
            password=login_info[2]
            odprivate_url=login_info[3]
        except Exception as e:
            print(e)
            text="身份信息获取失败\n" \
                 "使用方法为:/odprivate 邮箱 密码 链接"
            await client.send_message(chat_id=message.chat.id, text=text, parse_mode='markdown')
        info = await client.send_message(chat_id=message.chat.id, text="开始抓取下载链接", parse_mode='markdown')
        fileCount= await odpriva_downloadFiles(client,info,admin,password,odprivate_url, None, 0,start=1, num=-1)
        await client.edit_message_text(text=f"推送至Aria2完成，可到AriaNG面板查看\n本次推送{fileCount}个任务", chat_id=info.chat.id, message_id=info.message_id,
                                       parse_mode='markdown')
    except Exception as e:
        print(f"odprivate error {e}")
        await client.send_message(chat_id=message.chat.id, text=f"odprivate error {e}", parse_mode='markdown')

def run_shell(gid,file_num,file_dir):
    shell = f"bash upload.sh \"{gid}\" \"{file_num}\" '{file_dir}' "

    print(shell)
    cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                           stdout=subprocess.PIPE, universal_newlines=True, shell=True, bufsize=1)
    while True:
        time.sleep(2)
        if subprocess.Popen.poll(cmd) == 0:  # 判断子进程是否结束
            print("上传结束")
            return

def check_upload(api, gid):

    time.sleep(10)
    global task
    print(f"检查上传 {task}")
    sys.stdout.flush()
    try:
        currdownload=api.get_download(gid)
    except:
        print("任务已删除，不需要上传")
        sys.stdout.flush()
        return

    key=1
    if len(task)!=0:
        for a in task:
            if a == gid:
                key=0
                print("该任务存在，不需要上传")
                sys.stdout.flush()
                #task.remove(a)
                return
    if key==1:
        if "[METADATA]"==currdownload.name:
            return

        file_dir = f"{currdownload.dir}/{currdownload.name}"
        file_num = int(len(currdownload.files))
        print(f"上传该任务:{file_dir}")
        sys.stdout.flush()



        t1 = threading.Thread(target=run_shell, args=(gid,file_num,file_dir))
        t1.start()


async def run_await_rclone(dir,title,info,file_num,client, message,gid):
    global task
    task.append(gid)
    print(task)
    sys.stdout.flush()
    Rclone_remote=os.environ.get('Remote')
    Upload=os.environ.get('Upload')

    rc_url = f"http://root:{Aria2_secret}@127.0.0.1:5572"
    info = await client.send_message(chat_id=message.chat.id, text="开始上传", parse_mode='markdown')
    name=f"{str(info.message_id)}_{str(info.chat.id)}"

    if int(file_num)==1:
        rcd_copyfile_url = f"{rc_url}/operations/copyfile"
        drv, left = os.path.split(dir)
        data = {
            "srcFs": drv,
            "srcRemote": left,
            "dstFs": f"{Rclone_remote}:{Upload}",
            "dstRemote": left,
            "_async": True,
        }

        html = requests.post(url=rcd_copyfile_url, json=data)
        result = html.json()

        jobid = result["jobid"]

        rcd_status_url = f"{rc_url}/job/status"


        while requests.post(url=rcd_status_url, json={"jobid": jobid}).json()['finished'] == False:

            job_status = requests.post(url=f"{rc_url}/core/stats", json={"group": f"job/{jobid}"}).json()
            print(job_status)
            if "transferring" in job_status:

                if job_status['transferring'][0]['eta'] == None:
                    eta = "暂无"
                else:
                    eta = cal_time(job_status['transferring'][0]['eta'])
                print(f"剩余时间:{eta}")

                text = f"任务ID:`{jobid}`\n" \
                       f"任务名称:`{title}`\n" \
                       f"传输部分:`{hum_convert(job_status['transferring'][0]['bytes'])}/{hum_convert(job_status['transferring'][0]['size'])}`\n" \
                       f"传输进度:`{job_status['transferring'][0]['percentage']}%`\n" \
                       f"传输速度:`{hum_convert(job_status['transferring'][0]['speed'])}/s`\n" \
                       f"平均速度:`{hum_convert(job_status['transferring'][0]['speedAvg'])}/s`\n"

                try:
                    await client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                             parse_mode='markdown')

                except:
                    continue

            else:
                print("等待信息加载")

            time.sleep(1)


    else:
        rcd_copyfile_url = f"{rc_url}/sync/copy"

        data = {
            "srcFs": dir,
            "dstFs": f"{Rclone_remote}:{Upload}/{title}",
            "createEmptySrcDirs": True,
            "_async": True,
        }

        html = requests.post(url=rcd_copyfile_url, json=data)
        result = html.json()
        jobid = result["jobid"]

        rcd_status_url = f"{rc_url}/job/status"


        while requests.post(url=rcd_status_url, json={"jobid": jobid}).json()['finished'] == False:

            job_status = requests.post(url=f"{rc_url}/core/stats", json={"group": f"job/{jobid}"}).json()
            print(job_status)
            if "transferring" in job_status:

                if job_status['eta'] == None:
                    eta = "暂无"
                else:
                    eta = cal_time(job_status['eta'])
                print(f"剩余时间:{eta}")

                text = f"任务ID:`{jobid}`\n" \
                       f"任务名称:`{title}`\n" \
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
    print("上传结束")
    try:
        if Rclone_share==False:
            await client.send_message(text=f"任务完成\n{text}",chat_id=info.chat.id)
            return
        else:
            if int(file_num) == 1:
                file_name = os.path.basename(dir)
                upload_shell = f"rclone link  \"{Rclone_remote}:{Upload}/{file_name}\" --onedrive-link-scope=\"organization\"  --onedrive-link-type=\"view\""
            else:
                upload_shell = f"rclone link  \"{Rclone_remote}:{Upload}/{title}\"  --onedrive-link-scope=\"organization\"  --onedrive-link-type=\"view\""
            print(f"获取分享链接:{upload_shell}")
            val = os.popen(upload_shell)
            share_url = val.read()
            await client.send_message(text=f"{title}\n上传结束\n文件链接：{share_url}\n{text}", chat_id=info.chat.id)
            os.remove(f"{name}.log")
            task.remove(gid)
            return
    except Exception as e:
        print(e)
        try:
            os.remove(f"{name}.log")
            task.remove(gid)
            return
        except:
            return


def the_download(client, message,url):

    try:
        download = aria2.add_magnet(url)
    except Exception as e:
        print(e)
        if (str(e).endswith("No URI to download.")):
            print("No link provided!")
            client.send_message(chat_id=message.chat.id,text="No link provided!",parse_mode='Markdown')
            return None
    prevmessagemag = None
    info=client.send_message(chat_id=message.chat.id,text="添加任务",parse_mode='markdown')

    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=f"Remove",
                callback_data=f"Remove {download.gid}"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    client.edit_message_text(text="排队中", chat_id=info.chat.id, message_id=info.message_id,
                             parse_mode='markdown', reply_markup=reply_markup)


    temp_text=""
    while download.is_active:
        try:
            download.update()
            print("Downloading metadata")
            if temp_text!="Downloading metadata":
                try:
                    client.edit_message_text(text="Downloading metadata",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=reply_markup)
                    temp_text="Downloading metadata"
                except:
                    None
            barop = progessbar(download.completed_length,download.total_length)

            updateText = f"{download.status} \n" \
                         f"'{download.name}'\n" \
                         f"Progress : {hum_convert(download.completed_length)}/{hum_convert(download.total_length)} \n" \
                         f"Peers:{download.connections}\n" \
                         f"Speed {hum_convert(download.download_speed)}/s\n" \
                         f"{barop}\n" \
                         f"剩余空间:{get_free_space_mb()}GB"
            if prevmessagemag != updateText:
                print(updateText)
                try:
                    client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=reply_markup)
                    prevmessagemag = updateText
                except:
                    None
            time.sleep(2)
        except:

            try:
                download.update()
            except Exception as e:
                if (str(e).endswith("is not found")):
                    print("Metadata Cancelled/Failed")
                    print("Metadata couldn't be downloaded")
                    if temp_text!="Metadata Cancelled/Failed":
                        try:
                            client.edit_message_text(text="Metadata Cancelled/Failed",chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown')
                            temp_text="Metadata Cancelled/Failed"
                        except:
                            None
                    return None
            time.sleep(2)


    time.sleep(2)
    match = str(download.followed_by_ids[0])
    downloads = aria2.get_downloads()
    currdownload = None
    for download in downloads:
        if download.gid == match:
            currdownload = download
            break
    print("Download complete")

    new_inline_keyboard = [
        [
            InlineKeyboardButton(
                text="Resume",
                callback_data=f"Resume {currdownload.gid}"
            ),
            InlineKeyboardButton(
                text=f"Pause",
                callback_data=f"Pause {currdownload.gid}"
            ),
            InlineKeyboardButton(
                text=f"Remove",
                callback_data=f"Remove {currdownload.gid}"
            )
        ]
    ]

    new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
    try:
        client.edit_message_text(text="Download complete", chat_id=info.chat.id, message_id=info.message_id,
                             parse_mode='markdown', reply_markup=new_reply_markup)
    except Exception as e:
        print(e)

    prevmessage = None

    while True:

        try:
            currdownload.update()
        except Exception as e:
            if (str(e).endswith("is not found")):
                print("Magnet Deleted")
                print("Magnet download was removed")
                try:
                    client.edit_message_text(text="Magnet download was removed",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
                except:
                    None
                break
            print(e)
            print("Issue in downloading!")
            continue

        if currdownload.status == 'removed':
            print("Magnet was cancelled")
            print("Magnet download was cancelled")
            try:
                client.edit_message_text(text="Magnet download was cancelled",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
            except:
                None
            break

        if currdownload.status == 'error':
            print("Mirror had an error")
            currdownload.remove(force=True, files=True)
            print("Magnet failed to resume/download!\nRun /cancel once and try again.")
            try:
                client.edit_message_text(text="Magnet failed to resume/download!\nRun /cancel once and try again.",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
            except:
                None
            break

        print(f"Magnet Status? {currdownload.status}")

        if currdownload.status == "active":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{download.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Peers:{currdownload.connections}\n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"剩余空间:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    try:
                        client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                        prevmessage = updateText
                    except:
                        None
                time.sleep(2)
            except Exception as e:
                if (str(e).endswith("is not found")):
                    break
                print(e)
                print("Issue in downloading!")
                time.sleep(2)
        elif currdownload.status == "paused":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{download.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Peers:{currdownload.connections}\n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"剩余空间:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    try:
                        client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                        prevmessage = updateText
                    except:
                        None
                time.sleep(2)
            except Exception as e:
                print(e)
                print("Download Paused Flood")
                time.sleep(2)
        if currdownload.status=="complete":
            break
        time.sleep(2)


    print("开始上传")
    file_dir=f"{currdownload.dir}/{currdownload.name}"
    files_num=int(len(currdownload.files))
    run_rclone(file_dir,currdownload.name,info=info,file_num=files_num,client=client,message=message,gid=currdownload.gid)
    currdownload.remove(force=True,files=True)


    return

def cal_time(upload_time):
    m, s = divmod(int(upload_time), 60)
    h, m = divmod(m, 60)
    #print("%02d时%02d分%02d秒" % (h, m, s))
    if h != 0:
        last_time = "%d时%d分%d秒" % (h, m, s)
    elif h == 0 and m != 0:
        last_time = "%d分%d秒" % (m, s)
    else:
        last_time = "%d秒" % s
    return last_time

def start_download(client, message):
    try:
        keywords = str(message.text)
        if str(BOT_name) in keywords:
            keywords = keywords.replace(f"/magnet@{BOT_name} ", "")
            print(keywords)
            t1 = threading.Thread(target=the_download, args=(client, message,keywords))
            t1.start()
        else:
            keywords = keywords.replace(f"/magnet ", "")
            print(keywords)
            t1 = threading.Thread(target=the_download, args=(client, message,keywords))
            t1.start()

    except Exception as e:
        print(f"magnet :{e}")

def only_progessbar(new, tot):
    """Builds progressbar
    Args:
        new: current progress
        tot: total length of the download
    Returns:
        progressbar as a string of length 20
    """
    length = 20
    progress = int(round(length * new / float(tot)))
    percent = round(new/float(tot) * 100.0, 1)
    bar = '=' * progress + '-' * (length - progress)
    return percent

def run_rclone(dir,title,info,file_num,client, message,gid):
    global task
    task.append(gid)
    print(task)
    sys.stdout.flush()
    rc_url = f"http://root:{Aria2_secret}@127.0.0.1:5572"


    Rclone_remote=os.environ.get('Remote')
    Upload=os.environ.get('Upload')
    name=f"{str(info.message_id)}_{str(info.chat.id)}"


    if int(file_num)==1:
        rcd_copyfile_url = f"{rc_url}/operations/copyfile"
        drv, left = os.path.split(dir)
        data = {
            "srcFs": drv,
            "srcRemote": left,
            "dstFs": f"{Rclone_remote}:{Upload}",
            "dstRemote": left,
            "_async": True,
        }
        print(data)

        html = requests.post(url=rcd_copyfile_url, json=data)
        result = html.json()

        jobid = result["jobid"]

        rcd_status_url = f"{rc_url}/job/status"


        while requests.post(url=rcd_status_url, json={"jobid": jobid}).json()['finished'] == False:

            job_status = requests.post(url=f"{rc_url}/core/stats", json={"group": f"job/{jobid}"}).json()
            print(job_status)
            if "transferring" in job_status:

                if job_status['transferring'][0]['eta'] == None:
                    eta = "暂无"
                else:
                    eta = cal_time(job_status['transferring'][0]['eta'])
                print(f"剩余时间:{eta}")

                text = f"任务ID:`{jobid}`\n" \
                       f"任务名称:`{title}`\n" \
                       f"传输部分:`{hum_convert(job_status['transferring'][0]['bytes'])}/{hum_convert(job_status['transferring'][0]['size'])}`\n" \
                       f"传输进度:`{job_status['transferring'][0]['percentage']}%`\n" \
                       f"传输速度:`{hum_convert(job_status['transferring'][0]['speed'])}/s`\n" \
                       f"平均速度:`{hum_convert(job_status['transferring'][0]['speedAvg'])}/s`\n"

                try:
                    client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                             parse_mode='markdown')

                except:
                    continue

            else:
                print("等待信息加载")

            time.sleep(1)


    else:
        rcd_copyfile_url = f"{rc_url}/sync/copy"

        data = {
            "srcFs": dir,
            "dstFs": f"{Rclone_remote}:{Upload}/{title}",
            "createEmptySrcDirs": True,
            "_async": True,
        }

        html = requests.post(url=rcd_copyfile_url, json=data)
        result = html.json()
        jobid = result["jobid"]

        rcd_status_url = f"{rc_url}/job/status"


        while requests.post(url=rcd_status_url, json={"jobid": jobid}).json()['finished'] == False:

            job_status = requests.post(url=f"{rc_url}/core/stats", json={"group": f"job/{jobid}"}).json()
            print(job_status)
            if "transferring" in job_status:

                if job_status['eta'] == None:
                    eta = "暂无"
                else:
                    eta = cal_time(job_status['eta'])
                print(f"剩余时间:{eta}")

                text = f"任务ID:`{jobid}`\n" \
                       f"任务名称:`{title}`\n" \
                       f"传输部分:`{hum_convert(job_status['bytes'])}/{hum_convert(job_status['totalBytes'])}`\n" \
                       f"传输进度:`{only_progessbar(job_status['bytes'], job_status['totalBytes'])}%`\n" \
                       f"传输速度:`{hum_convert(job_status['speed'])}/s`"

                try:
                    client.edit_message_text(text=text, chat_id=info.chat.id, message_id=info.message_id,
                                             parse_mode='markdown')

                except:
                    continue

            else:
                print("等待信息")

            time.sleep(1)
    requests.post(url=f"{rc_url}/core/stats-delete", json={"group": f"job/{jobid}"}).json()
    requests.post(url=f"{rc_url}/fscache/clear").json()
    print("上传结束")
    try:
        if Rclone_share==False:
            client.send_message(text=f"{title}\n上传结束",chat_id=info.chat.id)
            return
        else:
            if int(file_num) == 1:
                file_name = os.path.basename(dir)
                upload_shell = f"rclone link  \"{Rclone_remote}:{Upload}/{file_name}\" --onedrive-link-scope=\"organization\"  --onedrive-link-type=\"view\""
            else:
                upload_shell = f"rclone link  \"{Rclone_remote}:{Upload}/{title}\"  --onedrive-link-scope=\"organization\"  --onedrive-link-type=\"view\""
            print(f"获取分享链接:{upload_shell}")
            val = os.popen(upload_shell)
            share_url = val.read()
            client.send_message(text=f"{title}\n上传结束\n文件链接：{share_url}", chat_id=info.chat.id)
            os.remove(f"{name}.log")
            task.remove(gid)
            return
    except Exception as e:
        print(e)
        try:
            os.remove(f"{name}.log")
            task.remove(gid)
            return
        except:
            return




def start_http_download(client, message):
    try:
        keywords = str(message.text)
        if str(BOT_name) in keywords:
            keywords = keywords.replace(f"/mirror@{BOT_name} ", "")
            print(keywords)
            t1 = threading.Thread(target=http_download, args=(client, message,keywords))
            t1.start()
        else:
            keywords = keywords.replace(f"/mirror ", "")
            print(keywords)
            t1 = threading.Thread(target=http_download, args=(client, message,keywords))
            t1.start()

    except Exception as e:
        print(f"start_http_download :{e}")

def file_download(client, message,file_dir):
    #os.system("df -lh")
    try:
        print("开始下载")
        sys.stdout.flush()
        currdownload = aria2.add_torrent(torrent_file_path=file_dir)
        info=client.send_message(chat_id=message.chat.id, text="开始下载", parse_mode='markdown')
        print("发送信息")
        sys.stdout.flush()
    except Exception as e:
        print(e)
        if (str(e).endswith("No URI to download.")):
            print("No link provided!")
            client.send_message(chat_id=message.chat.id,text="No link provided!",parse_mode='markdown')

        return
    new_inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Resume",
                callback_data=f"Resume {currdownload.gid}"
            ),
        InlineKeyboardButton(
            text=f"Pause",
            callback_data=f"Pause {currdownload.gid}"
        ),
        InlineKeyboardButton(
            text=f"Remove",
            callback_data=f"Remove {currdownload.gid}"
        )
        ]
    ]

    new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
    try:
        client.edit_message_text(text="Download complete",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown' ,reply_markup=new_reply_markup)
    except:
        None
    prevmessage = None

    while currdownload.is_active or not currdownload.is_complete:
        time.sleep(2)
        try:
            currdownload.update()
        except Exception as e:
            if (str(e).endswith("is not found")):
                print("Magnet Deleted")
                print("Magnet download was removed")
                try:
                    client.edit_message_text(text="Magnet download was removed",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
                except:
                    None
                break
            print(e)
            print("Issue in downloading!")

        if currdownload.status == 'removed':
            print("Magnet was cancelled")
            print("Magnet download was cancelled")
            try:
                client.edit_message_text(text="Magnet download was cancelled",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
            except:
                None
            break

        if currdownload.status == 'error':
            print("Mirror had an error")
            currdownload.remove(force=True, files=True)
            print("Magnet failed to resume/download!\nRun /cancel once and try again.")
            try:
                client.edit_message_text(text="Magnet failed to resume/download!\nRun /cancel once and try again.",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown' ,reply_markup=new_reply_markup)
            except:
                None
            break

        print(f"Magnet Status? {currdownload.status}")

        if currdownload.status == "active":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{currdownload.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Peers:{currdownload.connections}\n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"剩余空间:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    try:
                        client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown' ,reply_markup=new_reply_markup)
                        prevmessage = updateText
                    except:
                        None
                time.sleep(2)
            except Exception as e:
                if (str(e).endswith("is not found")):
                    break
                print(e)
                print("Issue in downloading!")

        elif currdownload.status == "paused":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{currdownload.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Peers:{currdownload.connections}\n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"剩余空间:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    try:
                        client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                        prevmessage = updateText
                    except:
                        None

            except Exception as e:
                print(e)
                print("Download Paused Flood")





    if currdownload.is_complete:
        print(currdownload.name)
        try:
            print("开始上传")
            file_dir=f"{currdownload.dir}/{currdownload.name}"
            files_num=int(len(currdownload.files))
            run_rclone(file_dir,currdownload.name,info=info,file_num=files_num,client=client, message=message,gid=currdownload.gid)
            currdownload.remove(force=True,files=True)
            return

        except Exception as e:
            print(e)
            print("Upload Issue!")
            return
    return None

def http_download(client, message,url):
    try:
        currdownload = aria2.add_uris([url])
        info = client.send_message(chat_id=message.chat.id, text="添加任务", parse_mode='markdown')
    except Exception as e:
        print(e)
        if (str(e).endswith("No URI to download.")):
            print("No link provided!")
            client.send_message(chat_id=message.chat.id,text="No link provided!",parse_mode='markdown')
            return None
    new_inline_keyboard = [
        [
            InlineKeyboardButton(
                text="Resume",
                callback_data=f"Resume {currdownload.gid}"
            ),
            InlineKeyboardButton(
                text=f"Pause",
                callback_data=f"Pause {currdownload.gid}"
            ),
            InlineKeyboardButton(
                text=f"Remove",
                callback_data=f"Remove {currdownload.gid}"
            )
        ]
    ]

    new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
    client.edit_message_text(text="排队中", chat_id=info.chat.id, message_id=info.message_id,
                             parse_mode='markdown', reply_markup=new_reply_markup)


    prevmessage=None
    while currdownload.is_active or not currdownload.is_complete:

        try:
            currdownload.update()
        except Exception as e:
            if (str(e).endswith("is not found")):
                print("url Deleted")
                print("url download was removed")
                try:
                    client.edit_message_text(text="url download was removed",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
                except:
                    None
                break
            print(e)
            print("url in downloading!")

        if currdownload.status == 'removed':
            print("url was cancelled")
            print("url download was cancelled")
            try:
                client.edit_message_text(text="Magnet download was cancelled",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
            except:
                None
            break

        if currdownload.status == 'error':
            print("url had an error")
            currdownload.remove(force=True, files=True)
            print("url failed to resume/download!.")
            try:
                client.edit_message_text(text="Magnet failed to resume/download!\nRun /cancel once and try again.",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
            except:
                None
            break

        print(f"url Status? {currdownload.status}")

        if currdownload.status == "active":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{currdownload.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"剩余空间:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    try:
                        client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                        prevmessage = updateText
                    except:
                        None
                time.sleep(2)
            except Exception as e:
                if (str(e).endswith("is not found")):
                    break
                print(e)
                print("Issue in downloading!")
                time.sleep(2)
        elif currdownload.status == "paused":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{currdownload.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"剩余空间:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    try:
                        client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                        prevmessage = updateText
                    except:
                        None
                time.sleep(2)
            except Exception as e:
                print(e)
                print("Download Paused Flood")
                time.sleep(2)
        time.sleep(2)

    if currdownload.is_complete:
        print(currdownload.name)
        try:
            print("开始上传")
            file_dir=f"{currdownload.dir}/{currdownload.name}"
            run_rclone(file_dir,currdownload.name,info=info,file_num=1,client=client, message=message,gid=currdownload.gid)
            currdownload.remove(force=True,files=True)

        except Exception as e:
            print(e)
            print("Upload Issue!")
    return None


def progessbar(new, tot):
    """Builds progressbar
    Args:
        new: current progress
        tot: total length of the download
    Returns:
        progressbar as a string of length 20
    """
    length = 20
    progress = int(round(length * new / float(tot)))
    percent = round(new/float(tot) * 100.0, 1)
    bar = '=' * progress + '-' * (length - progress)
    return '[%s] %s %s\r' % (bar, percent, '%')


def hum_convert(value):
    value=float(value)
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f%s" % (value, units[i])
        value = value / size

def get_free_space_mb():
    result=os.statvfs('/root/')
    block_size=result.f_frsize
    total_blocks=result.f_blocks
    free_blocks=result.f_bfree
    # giga=1024*1024*1024
    giga=1000*1000*1000
    total_size=total_blocks*block_size/giga
    free_size=free_blocks*block_size/giga
    print('total_size = %s' % int(total_size))
    print('free_size = %s' % free_size)
    return int(free_size)

def progress(current, total,client,message,name):

    print(f"{current * 100 / total:.1f}%")
    pro=f"{current * 100 / total:.1f}%"
    try:
        client.edit_message_text(chat_id=message.chat.id,message_id=message.message_id,text=f"{name}\n上传中:{pro}")
    except Exception as e:
        print("e")


async def more_magnet(client, message):
    try:
        text=message.text
        if "magnet" in text:
            if "\n" in text:

                magnet_list=str(text).split("\n")

                for magnet in magnet_list:
                    t1 = threading.Thread(target=the_download, args=(client, message, magnet))
                    t1.start()

            else:
                t1 = threading.Thread(target=the_download, args=(client, message,text))
                t1.start()
            await client.delete_messages(chat_id=message.chat.id, message_ids=message.message_id)
    except Exception as e :
        print(f"more_magnet error :{e}")
        await client.send_message(chat_id=message.chat.id, text=f"more_magnet error :{e}")


async def temp_telegram_file(client, message,file_list):
    try:
        if len(file_list) == 0:
            answer = await client.ask(chat_id=message.chat.id, text='请发送TG文件,或输入 /cancel 取消')
        else:
            answer = await client.ask(chat_id=message.chat.id,
                                      text=f'已接收{len(file_list)}个文件，请继续发送TG文件，输入 /finish 开始任务,或输入 /cancel 取消')
        info = answer
        if info.media_group_id != None:
            media = await client.get_media_group(chat_id=info.chat.id, message_id=info.message_id)
            print(media)
            for a in media:
                if a.document == None and a.video == None:
                    await client.send_message(text="发送的不是文件", chat_id=message.chat.id, parse_mode='markdown')
                    await temp_telegram_file(client, message,file_list)
                    return file_list
                else:
                    file_list.append(a)
            await temp_telegram_file(client, message,file_list)
            return file_list

        elif info.text == "/cancel":
            await client.send_message(text="取消发送", chat_id=message.chat.id, parse_mode='markdown')
            return []
        elif info.text == "/finish":
            await client.send_message(text=f"接收文件完成,共有{len(file_list)}个文件", chat_id=message.chat.id, parse_mode='markdown')
            return file_list
        elif info.document == None and info.video == None:
            await client.send_message(text="发送的不是文件", chat_id=message.chat.id, parse_mode='markdown')
            await temp_telegram_file(client, message,file_list)
            return file_list

        else:
            try:
                file_list.append(info)
                temp_file= await temp_telegram_file(client, message,file_list)
                file_list=temp_file
                return file_list

            except Exception as e:
                print(f"标记1 {e}")
                sys.stdout.flush()
                await client.send_message(text="下载文件失败", chat_id=message.chat.id, parse_mode='markdown')
                return file_list
    except Exception as e:
        print(f"下载文件失败 {e}")
        sys.stdout.flush()





async def send_telegram_file(client, message):
    try:

        temp = await temp_telegram_file(client,message,[])

        sys.stdout.flush()

        if len(temp)==0:
            return
        elif len(temp)==1:
            file_dir = await client.download_media(message=temp[0])

            t1 = threading.Thread(target=file_download, args=(client, message, file_dir))
            t1.start()
            return

        else:
            for a in temp:
                file_dir = await client.download_media(message=a)
                t1 = threading.Thread(target=file_download, args=(client, message, file_dir))
                t1.start()
            return
    except Exception as e:
        print(f"start_down_telegram_file {e}")
        await client.send_message(text=f"下载文件失败:{e}", chat_id=message.chat.id, parse_mode='markdown')

        sys.stdout.flush()




def http_downloadtg(client, message,url):
    try:
        currdownload = aria2.add_uris([url])
        info = client.send_message(chat_id=message.chat.id, text="添加任务", parse_mode='markdown')
    except Exception as e:
        print(e)
        if (str(e).endswith("No URI to download.")):
            print("No link provided!")
            client.send_message(chat_id=message.chat.id,text="No link provided!",parse_mode='markdown')
            return None
    new_inline_keyboard = [
        [
            InlineKeyboardButton(
                text="Resume",
                callback_data=f"Resume {currdownload.gid}"
            ),
            InlineKeyboardButton(
                text=f"Pause",
                callback_data=f"Pause {currdownload.gid}"
            ),
            InlineKeyboardButton(
                text=f"Remove",
                callback_data=f"Remove {currdownload.gid}"
            )
        ]
    ]

    new_reply_markup = InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
    client.edit_message_text(text="排队中", chat_id=info.chat.id, message_id=info.message_id,
                             parse_mode='markdown', reply_markup=new_reply_markup)


    prevmessage=None
    while currdownload.is_active or not currdownload.is_complete:

        try:
            currdownload.update()
        except Exception as e:
            if (str(e).endswith("is not found")):
                print("url Deleted")
                print("url download was removed")
                try:
                    client.edit_message_text(text="url download was removed",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
                except:
                    None
                break
            print(e)
            print("url in downloading!")

        if currdownload.status == 'removed':
            print("url was cancelled")
            print("url download was cancelled")
            try:
                client.edit_message_text(text="Magnet download was cancelled",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
            except:
                None
            break

        if currdownload.status == 'error':
            print("url had an error")
            currdownload.remove(force=True, files=True)
            print("url failed to resume/download!.")
            try:
                client.edit_message_text(text="Magnet failed to resume/download!\nRun /cancel once and try again.",chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown')
            except:
                None
            break

        print(f"url Status? {currdownload.status}")

        if currdownload.status == "active":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{currdownload.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"剩余空间:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    try:
                        client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                        prevmessage = updateText
                    except:
                        None
                time.sleep(2)
            except Exception as e:
                if (str(e).endswith("is not found")):
                    break
                print(e)
                print("Issue in downloading!")
                time.sleep(2)
        elif currdownload.status == "paused":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"{currdownload.status} \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"剩余空间:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    try:
                        client.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='markdown', reply_markup=new_reply_markup)
                        prevmessage = updateText
                    except:
                        None
                time.sleep(2)
            except Exception as e:
                print(e)
                print("Download Paused Flood")
                time.sleep(2)
        time.sleep(2)

        time.sleep(1)
    if currdownload.is_complete:
        print(currdownload.name)
        try:
            print("开始上传")
            file_dir=f"{currdownload.dir}/{currdownload.name}"
            client.send_document(chat_id=info.chat.id, document=file_dir, caption=currdownload.name, progress=progress,
                                       progress_args=(client, info, currdownload.name,))

            currdownload.remove(force=True,files=True)

        except Exception as e:
            print(e)
            print("Upload Issue!")
            currdownload.remove(force=True, files=True)
    return None

#@bot.message_handler(commands=['mirrortg'],func=lambda message:str(message.chat.id) == str(Telegram_user_id))
def start_http_downloadtg(client, message):
    try:
        keywords = str(message.text)
        if str(BOT_name) in keywords:
            keywords = keywords.replace(f"/mirrortg@{BOT_name} ", "")
            print(keywords)
            t1 = threading.Thread(target=http_downloadtg, args=(client, message,keywords))
            t1.start()
        else:
            keywords = keywords.replace(f"/mirrortg ", "")
            print(keywords)
            t1 = threading.Thread(target=http_downloadtg, args=(client, message,keywords))
            t1.start()

    except Exception as e:
        print(f"start_http_download :{e}")




