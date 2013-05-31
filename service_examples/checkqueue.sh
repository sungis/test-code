#!/bin/bash

ps aux |grep -v grep |grep ppqueue.py

if [ $? -ne  0 ];then
    service keepalived stop
fi
