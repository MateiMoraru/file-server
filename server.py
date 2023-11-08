import socket, os

class Server:
    BUFFER_SIZE = 4096
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
        signup = self.recv(conn)
        
        if signup == 'yes':
            self.signup(conn)
        else:
            self.login(conn)

        
    def signup(self, conn: socket.socket):
        credentials = self.recv(conn)
        username = credentials.split(' ')[0]

        users_file_name = "login.txt"
    
        try:
            users_file = open(users_file_name, 'r', encoding = self.ENCODING)
        except FileNotFoundError:
            print("User file not found, creating one")
            users_file = open(users_file_name, 'w+', encoding = self.ENCODING)
            
        users_data = users_file.readlines()

        for line in users_data:
            fin_username = line.split(' ')[0]
            print(fin_username, username)
            if username == fin_username:
                self.send(conn, "Account Already Exists")
                self.signup(conn)
                return
        
        users_file = open(users_file_name, 'a', encoding = self.ENCODING)
        users_file.write(credentials + ' user\n')
        users_file.close()
        self.send(conn, "Account Created Successfully")

        self.login(conn)


    def login(self, conn: socket.socket, count: int = 0):
        credentials = self.recv(conn)
        username = credentials.split(' ')[0]
        password = credentials.split(' ')[1]

        print(0)

        users_file_name = "login.txt"
    
        try:
            users_file = open(users_file_name, 'r', encoding= self.ENCODING)

        except FileNotFoundError:
            print(FileNotFoundError)
            
        users_data = users_file.readlines()

        print(1)
        
        for line in users_data:
            if username in line:
                data = line.split(' ')
                print(2)
                
                if username == data[0] and password == data[1]:
                    print("sa moara ma sa")
                    self.send(conn, "Logged In Successfully")
                    print(1)
                    self.send(conn, data[2]) #User rights
                    print(2)
                    return True
                
        if count <= 2:
            self.send(conn, "Wrong Credentials")

            self.login(conn, count + 1)
        else:
            self.send(conn, "Account Not Recognised")
            return False


    def send(self, conn: socket.socket, message: str):
        bytes = message.encode(self.ENCODING)
        bytes_sent = conn.send(bytes)

        if bytes != bytes_sent:
            return False
        
        return True
    
    def recv(self, conn: socket.socket):
        try:
            message = conn.recv(self.BUFFER_SIZE).decode(self.ENCODING)
            return message
        except TimeoutError as e:
            print(e)

if __name__ == "__main__":
    server = Server()
    server.run()
    