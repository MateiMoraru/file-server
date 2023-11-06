import socket

class Client:
    def __init__(self, ip, addr):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_addr = (ip, addr)

    
    def connect(self):
        self.socket.connect(self.server_addr)