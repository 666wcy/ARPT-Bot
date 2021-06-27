from flask import Flask,Response,send_file
from requests import get,post
import flask,requests
import os

status =""
app = Flask(__name__)
SITE_NAME = 'http://127.0.0.1:8080/'

main_site= 'http://127.0.0.1:5000/'

@app.route('/jsonrpc',methods=['POST'])
def proxypost():
    path="jsonrpc"
    #print("post")
    #print(f'{SITE_NAME}{path}')
    url=f'{SITE_NAME}{path}?'
    #print(request.form)
    student = flask.request.data
    #print(student)
    #获取到POST过来的数据，因为我这里传过来的数据需要转换一下编码。根据晶具体情况而定
    return (post(url=url,data=student).content)

app.route('/about', methods=['GET'])
def index():
    return send_file("index.html")

@app.route('/jsonrpc/',methods=['GET'])
def proxyget():
    path="jsonrpc"
    #print(f'{SITE_NAME}{path}')
    url=f'{SITE_NAME}{path}?'
    #print(request.args)
    par=flask.request.args
    #http://127.0.0.1:5000/jsonrpc?jsonrpc=2.0&method=aria2.getGlobalStat&id=QXJpYU5nXzE2MTM4ODAwNTBfMC44NTY2NjkzOTUyMjEzNDg3&params=WyJ0b2tlbjp3Y3k5ODE1MSJd&
    return get(url=url,params=par).content

@app.route('/<path:path>',methods=['GET'])
def proxy(path):
    if flask.request.method == 'GET':
        resp = requests.get(f'{main_site}{path}')
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response

@app.route('/', methods=['GET'])
def index():
    if flask.request.method == 'GET':
        resp = requests.get(f'{main_site}')
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response

if __name__ == '__main__':

    port = int(os.environ.get('PORT'))
    app.run(host='0.0.0.0', port=port, debug=True)
