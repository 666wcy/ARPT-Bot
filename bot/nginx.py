import os

port = int(os.environ.get('PORT'))

with open("/etc/nginx/nginx.conf", "r+") as f:
    f1 = f.read()
    a = f1
    print(a)

    b = str(a).replace("8868",str(port))

with open("/etc/nginx/nginx.conf", "w+") as fw:
    fw.write(b)
