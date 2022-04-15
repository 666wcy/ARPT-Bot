#!/bin/bash

nginx -c /etc/nginx/nginx.conf
nginx -s reload

/bin/bash /root/.aria2/tracker.sh "/root/.aria2/aria2.conf"

nohup aria2c --conf-path=/root/.aria2/aria2.conf --rpc-listen-port=8080 --rpc-secret=$Aria2_secret &
nohup rclone rcd --rc-addr=127.0.0.1:5572 --rc-user=root --rc-pass=$Aria2_secret --rc-allow-origin="https://elonh.github.io" &
nohup filebrowser -r /  -p 9184 >> /dev/null 2>&1 & 

python3 /bot/main.py