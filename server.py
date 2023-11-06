import socket, os

class Server:
    BUFFER_SIZE = 1024
    ENCODING = "UTF-8"

    def __init__(self, ip: str = "127.0.0.1", port: int = 8080):        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.addr = (ip, port)
        

    def run(self):
        self.socket.bind(self.addr)
        self.socket.listen()
        
        while True:
            conn, addr = self.socket.accept()

            self.handle_conn(conn)


    def handle_conn(self, conn: socket.socket):
        logged = False


    def login(self, user, password):
        users_file_name = "login.txt"
    
        try:
            users_file = open(users_file_name, 'r', encoding= self.ENCODING)

        except FileExistsError:
            print("User file not found, creating one")

            users_file = open(users_file_name, 'w+', encoding= self.ENCODING)
            
        users_data = users_file.readlines()
        
        for line in users_data:
            if user in line:
                data = line.split(' ')
                
                if user == data[0] and password == data[1]:
                    return True
                
        return False


    def send(self, conn: socket.socket, message: str):
        bytes = message.encode(self.ENCODING)
        bytes_sent = conn.send(bytes)

        if len(bytes) != len(bytes_sent):
            return False
        
        return True
    
    def recv(self, conn: socket.socket):
        try:
            conn.recv()
        except TimeoutError as e:
            print(e)