import zmq
import sys
import time


if __name__ == '__main__':
    if sys.argv[1] =='1':
        context = zmq.Context.instance()
        syscend = context.socket(zmq.PUB)
        syscend.bind("tcp://*:5557")
        
        print 'pub'

        while True:
            m = ['update',str(time.time())]
            syscend.send_multipart(str(time.time()))
            time.sleep(1e-3)
    else:
        context = zmq.Context.instance()
        subscriber = context.socket(zmq.SUB)
        subscriber.connect("tcp://localhost:5557")
        subscriber.setsockopt(zmq.SUBSCRIBE, '')
        
        print 'sub'
        while True:
            print subscriber.recv_multipart()

