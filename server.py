import socket, os, time

class Server:
    BUFFER_SIZE = 4096
    ENCODING = "UTF-8"

    def __init__(self, ip: str = "127.0.0.1", port: int = 8080):        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = (ip, port)
        

    def run(self):
        self.socket.bind(self.addr)
        self.socket.listen()
        print(f"Server Listening For Connections on {self.addr}.")
        
        while True:
            conn, addr = self.socket.accept()

            self.handle_conn(conn)


    def handle_conn(self, conn: socket.socket):
        logged = False
        user_name = "None"
        user_rights = "None"
        path = 'server/'

        signup = self.recv(conn)
        
        if signup == 'yes':
            self.signup(conn)
            user_name, user_rights = self.login(conn)
        else:
            user_name, user_rights = self.login(conn)

        while True:
            command = self.recv(conn).split(' ')

            if command[0] == "create":
                if command[1] == "repo":
                    os.mkdir(path + command[2])
                    self.send(conn, f"Created repo {command[2]}")
                elif command[1] == "file":
                    open(path + command[2], 'w').close()
                    self.send(conn, f"Created file {command[2]}")
                else:
                    self.send(conn, f"Wrong Usage, run help")

            if command[0] == "kill" or command[0] == "k":
                self.send(conn, "Destroy Client")
                print(f"{user_rights} {user_name} Disconnected")

        
    def signup(self, conn: socket.socket):
        print("Signup")
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
            if username == fin_username:
                self.send(conn, "Account Already Exists")
                self.signup(conn)
                return
        
        users_file = open(users_file_name, 'a', encoding = self.ENCODING)
        users_file.write(credentials + ' user\n')
        users_file.close()
        self.send(conn, "Account Created Successfully")


    def login(self, conn: socket.socket, count: int = 0):
        print("Login")
        credentials = self.recv(conn)
        username = credentials.split(' ')[0]
        password = credentials.split(' ')[1]

        users_file_name = "login.txt"
    
        try:
            users_file = open(users_file_name, 'r', encoding= self.ENCODING)

        except FileNotFoundError:
            print(FileNotFoundError)
            
        users_data = users_file.readlines()

        
        for line in users_data:
            if username in line:
                data = line.split(' ')
                if username == data[0] and password == data[1]:
                    self.send(conn, "Logged In Successfully")
                    user_rights = data[2][0:len(data[2]) - 1] #\n at the end of data[2]
                    time.sleep(.1)
                    self.send(conn, user_rights) #User rights
                    return (username, user_rights)
                
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
    