import zmq
import time
import sys
import random
from multiprocessing import Process

def server_push(port="5556"):
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.bind('tcp://127.0.0.1:%s' % port)
    print("Runner server on port:",port)
    # Serves five requests
    for reqnum in range(10):
        if reqnum < 6:
            socket.send_unicode("Continue")
        else:
            socket.send_unicode("Exit")
            break
        time.sleep(1)
        
def server_pub(port="5558"):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://127.0.0.1:%s" % port)
    publisher_id = random.randrange(0,9999)
    for reqnum in range(10):
        topic = random.randrange(8,10)
        messagedata = "server#%s" % publisher_id
        print("%s %s" % (topic, messagedata))
        time.sleep(1)
        
def client(port_push, port_sub):
    context = zmq.Context()
    socket_pull = context.socket(zmq.PULL)
    socket_pull.connect("tcp://127.0.0.1:%s" % port_push)
    print("Connected to server with port %s" % port_push)
    socket_sub = context.socket(zmq.SUB)
    socket_sub.connect("tcp://127.0.0.1:%s" % port_sub)
    socket_sub.setsockopt_string(zmq.SUBSCRIBE, "9")
    print("Connected to publisher with port %s" % port_sub)
    
    poller = zmq.Poller()
    poller.register(socket_pull, zmq.POLLIN)
    poller.register(socket_pull, zmq.POLLIN)
    
    should_continue = True
    while should_continue:
        socks = dict(poller.poll())
        if socket_pull in socks and socks[socket_pull] == zmq.POLLIN:
            message = socket_pull.recv_unicode()
            print("Received control command: %s" % message)
            if message == "Exit":
                print("Received exit command. Now exiting client.")
                should_continue = False
                
        if socket_sub in socks and socks[socket_pub] == zmq.POLLIN:
            string = socket_sub.unicode_recv()
            topic, messagedata = string.split()
            print("Processing...",topic,messagedata)
            
if __name__ == "__main__":
    server_push_port = "5556"
    server_pub_port = "5558"
    Process(target=server_push,args=(server_push_port,)).start()
    Process(target=server_pub,args=(server_pub_port,)).start()
    Process(target=client,args=(server_push_port,server_pub_port,)).start()
