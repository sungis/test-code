# -*- coding: UTF-8 -*-
import zmq  
import re
import sys


def send_request(header,q):
  SERVER_ENDPOINT = "tcp://localhost:5555"
#  SERVER_ENDPOINT = "tcp://10.0.1.77:5555"
#  SERVER_ENDPOINT = "tcp://117.79.157.235:5560"
  CLIENT_IDENTITY = "AD_Client_pyzmq" 
  c=zmq.Context()
  s=c.socket(zmq.REQ)
  s.set(zmq.IDENTITY,CLIENT_IDENTITY)
  s.connect(SERVER_ENDPOINT)
  m=[header,q]
  s.send_multipart(m)
  return s.recv()

import threading
from time import sleep,ctime

class advClient(threading.Thread):
    def __init__(self,id):
        threading.Thread.__init__(self)
        #SERVER_ENDPOINT = "tcp://10.0.1.77:5555"
        SERVER_ENDPOINT = "tcp://localhost:5555"
        CLIENT_IDENTITY = "AD_Client_pyzmq" 
        c=zmq.Context()
        self.s=c.socket(zmq.REQ)
        self.s.set(zmq.IDENTITY,CLIENT_IDENTITY+'__'+str(id))
        self.s.connect(SERVER_ENDPOINT)
    def run(self):
        for i in range(100):
            request='{"action":"adv","q":{"referurl":"http://blog.csdn.net/zhangchaoyangsun/article/details/8879615","keyword":[""]},"filter":{"city":[""],"province":[""]},"sort":1,"output":{"format":"json","offset":0,"size":6}}'
            m=['search',request]
            self.s.send_multipart(m)
            print self.s.recv()

if __name__  == '__main__':
    action = sys.argv[1]
    if action == 'update':
        f = open('./data/jobs.txt')
        re_jobs=re.compile('{"action":"updateDoc".*{"format":"json","offset":0,"size":10}}')
        for i in f:
            m = re_jobs.search(i)
            if m:
                request = m.group()
                print send_request('update',request)

    elif action == 'remove' :
        request = '{"action":"removeDoc","name":"job","keyId":"67943"}'
        print send_request('remove',request)

    elif action == 'adv':
        request='{"action":"adv","q":{"referurl":"http://blog.csdn.net/zhangchaoyangsun/article/details/8879615","keyword":[""]},"filter":{"city":[""],"province":[""]},"sort":1,"output":{"format":"json","offset":0,"size":6}}'
        print send_request('search',request)

    elif action=='all':
        request='{ "action" : "all" , "sort" : 1 , "output" : { "format" : "json" , "offset" : 0 , "size" : 10}}'
        print send_request('search',request)

    elif action=='hunterjob':
        request='{ "action" : "hunterjob" , "sort" : 1 , "output" : { "format" : "json" , "offset" : 0 , "size" : 10}}'
        print send_request('search',request)

    elif action=='uniqueorgid':
        request='{ "action" : "uniqueorgid" , "sort" : 1 , "output" : { "format" : "json" , "offset" : 0 , "size" : 10}}'
        print send_request('search',request)

    elif action=='test':
        while(True):
            print 'input:'
            request = sys.stdin.readline()
            print request
            print send_request('search',request)
    elif action == 'thread':
        threads=[]
        n=100
        for i in range(n):
            t=advClient(i)
            threads.append(t)
            t.start()
        for i in range(n):
            threads[i].join()

    else:
        f = open('skill.txt')
        for k in f:
            request='{ "action" : "searchJob" , "q" : { "keyword" : "'+k+'"} , "sort" : 1 , "output" : { "format" : "json" , "offset" : 0 , "size" : 10}}'
            print k
            print send_request('search',request)
            ch = sys.stdin.read(1)



