import socket
import time
import sys
import asyncore
import logging
from async_server import Server as BackWorker

port_num = 9005

class BackendList:
    def __init__(self):
        self.servers=[]
        self.current = 0
        self.request = 0
    def running_async(self,port):
        bw = BackWorker(port)
    def setserver(self,portnumber):
        self.servers.append(('127.0.0.1',portnumber))
    def getserver(self):
        global port_num
        s = self.servers[self.current]
        self.current += 1
        self.request += 1
        print(self.request)
        if (self.current>=len(self.servers)):
            self.current=0
        if(self.request % 100 == 0):
            port_num += 1
            self.running_async(port_num)
            self.setserver(port_num)
        return s

class Backend(asyncore.dispatcher_with_send):
    def __init__(self,targetaddress):
        asyncore.dispatcher_with_send.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(targetaddress)
        self.connection = self

    def handle_read(self):
        try:
            self.client_socket.send(self.recv(8192))
        except:
            pass
    def handle_close(self):
        try:
            self.close()
            self.client_socket.close()
        except:
            pass

class ProcessTheClient(asyncore.dispatcher):
    def handle_read(self):
        data = self.recv(8192)
        if data:
            self.backend.client_socket = self
            self.backend.send(data)
    def handle_close(self):
        self.close()

class Server(asyncore.dispatcher):
    def __init__(self,portnumber):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('',portnumber))
        self.listen(1)
        self.bservers = BackendList()
        self.bservers.running_async(9002)
        self.bservers.running_async(9003)
        self.bservers.running_async(9004)
        self.bservers.running_async(9005)
        self.bservers.setserver(9002)
        self.bservers.setserver(9003)
        self.bservers.setserver(9004)
        self.bservers.setserver(9005)

        logging.warning("load balancer running on port {}" . format(portnumber))

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            logging.warning("connection from {}" . format(repr(addr)))

            #menentukan ke server mana request akan diteruskan
            bs = self.bservers.getserver()
            logging.warning("koneksi dari {} diteruskan ke {}" . format(addr, bs))
            backend = Backend(bs)

            #mendapatkan handler dan socket dari client
            handler = ProcessTheClient(sock)
            handler.backend = backend

def main():
    portnumber=44444
    svr = Server(portnumber)
    asyncore.loop()

if __name__=="__main__":
    main()