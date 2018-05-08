#!/bin/bash
source /root/data/server/virtualenv/bin/activate

if [ ! -d /data/logs/msg_srv_d ]; then
	mkdir -p /data/logs/msg_srv_d
fi

exec python3 ./main.py $*

