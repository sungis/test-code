#!/bin/bash
pnum=`ps aux |grep -v grep |grep ppqueue.py|wc -l`

if [ $pnum -lt  1 ];then
    cd /root/ad_service
    python ppqueue.py &
    sleep 10
    service keepalived restart
fi
                           
