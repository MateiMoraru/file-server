import socket, os, time
from typing import List

class Server:
    BUFFER_SIZE = 4096
    ENCODING = "UTF-8"
    REPO_RIGHTS_FILE_NAME = "repo_rights.txt"
    USERS_FILE_NAME = "login.txt"

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

            if command[0] == 'echo':
                self.handle_echo(command, path, user_name, user_rights, conn)
            elif command[0] == "create":
                self.handle_create(command, path, user_name, conn)
            elif command[0] == 'set':
                self.handle_set(command, user_name, user_rights, conn)
            elif command[0] == 'add-admin':
                self.handle_admin(command, user_rights, conn)
            elif command[0] == 'cat':
                self.handle_cat(command, path, user_name, user_rights, conn)
            elif command[0] == "kill" or command[0] == "k":
                self.send(conn, "Destroy Client")
                print(f"{user_rights} {user_name} Disconnected")
            else:
                self.send(conn, "Unknown Command")


    def handle_admin(self, command: List[str], user_rights: str, conn: socket.socket):
        if user_rights == 'admin':
            users_file = open(self.USERS_FILE_NAME, 'w+', encoding=self.ENCODING)
            if command[1] in users_file.readlines():
                self.send(conn, "An Account With The Same Username Already Exists-w")
                return
            
            new_user = f'{command[1]} NONE admin'
            users_file.write(new_user)
            self.send(conn, f"Admin created. When Opening The Client As {command[1]}, Sign Up As You Need To Specify Your Password-w")
        else:
            self.send(conn, "You Don't Have The Correct Rights To Create An Admin-w")


    def handle_cat(self, command: List[str], path: str, user_name: str, user_rights: str, conn: socket.socket):
        if os.path.exists(path + command[1]):
            fin = open(path + command[1], 'r', encoding=self.ENCODING).read()
            self.send(conn, fin + '-w')
        else:
            self.send(conn, "File Doesn't exist-w")

    def handle_echo(self, command: List[str], path: str, user_name: str, user_rights: str, conn: socket.socket):
        if command[-2] == '>>':
            file_name = command[-1]
            if '/' in file_name:
                file_dir = file_name.split('/')[0]
                access_dir = self.access_dir(file_dir, user_name, user_rights)
                print(access_dir)
            else:
                access_dir = (True)

            if access_dir[0]:
                if os.path.exists(path + file_name):
                    fout = open(path + file_name, 'a', encoding=self.ENCODING)
                    self.send(conn, f"Added To {file_name}-w")
                else:
                    fout = open(path + file_name, 'w', encoding=self.ENCODING)
                    self.send(conn, f"Created File {file_name}-w")

                fout.write(' '.join(command[1:len(command)-2]))
                fout.close()
        else:
            message = ' '.join(command[1:len(command)])
            print(f'{user_name}> {message}')
            self.send(conn, f'{user_name}> {message}-w')


    def handle_create(self, command: List[str], path: str, user_name: str, conn: socket.socket):
        if len(command) < 3:
            print("Wrong command usage")
            self.send(conn, "Wrong command usage-w")
            return
        
        file_name = command[2]
        if command[1] == "repo":
            if os.path.exists(path + file_name):
                self.send(conn, "Repository already exists-w")
            else:
                os.mkdir(path + file_name)
                repo_rights_out = open(self.REPO_RIGHTS_FILE_NAME, 'a', encoding=self.ENCODING)
                if '/' in file_name:
                    pass
                data = f"\n{file_name} collaborators {user_name} readers {user_name}"
                repo_rights_out.write(data)
                self.send(conn, f"Created repo {file_name}-w")
        elif command[1] == "file":
            open(path + file_name, 'w', encoding=self.ENCODING).close()
            self.send(conn, f"Created file {file_name}-w")
        else:
            self.send(conn, "Wrong Usage, run help-w")


    def handle_set(self, command: List[str], user_name, user_rights, conn: socket.socket):
        if len(command) < 4:
            print("Wrong command usage")
            self.send(conn, "Wrong command usage.\n Try running: set <repo_name> <collaborators|readers> <*|user_name>-w")
        rights = self.access_dir(command[1], user_name, user_rights)
        print(rights)
        if rights[0] and rights[1] != 'reader':
            if command[2] == 'collaborator':
                repo_rights_in = open(self.REPO_RIGHTS_FILE_NAME, 'r', encoding=self.ENCODING)
                data = repo_rights_in[rights[2]]
                t_data = data.split(' ')
                new_data = t_data[0] + ' ' + t_data[1] + ' ' + command[3] + ' ' + t_data[2] + ' ' + t_data[3]
                repo_rights_in[rights[2]] = new_data
                print(new_data)

                repo_rights_out = open(self.REPO_RIGHTS_FILE_NAME, 'w', encoding=self.ENCODING)
                repo_rights_out.write(repo_rights_in)
                repo_rights_in.close()
                repo_rights_out.close()
                self.send(conn, f"Successfully set the collaborators to: {command[3]}")


    def access_dir(self, path: str, user_name: str, user_rights: str): #TODO: split the path by "/" in order to check the correct directory 
        index = -1
        if user_rights == 'admin':
            return (True, 'admin', None)
        else:
            repo_rights_file = open(self.REPO_RIGHTS_FILE_NAME, 'r', encoding=self.ENCODING)
            repo_rights = repo_rights_file.readlines()
            repo_rights_file.close()
            print("aualeu")
            for line in repo_rights:
                index += 1
                print(line, user_name in line)
                if path in line: #Exista cazuri cu erori dar nu stau acm sa le repar
                    collaborators = line.split(' ')[2]
                    readers = line.split(' ')[4]
                    if user_name in collaborators or collaborators == '*':
                        return (True, 'collaborator', index)
                    elif user_name in readers or readers == '*':
                        return (True, 'reader', index)
        return (False, None, None)

        
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
            fin_password = line.split(' ')[1]
            if username == fin_username:
                self.send(conn, "Account Already Exists-w")
                self.signup(conn)
                return
        
        users_file = open(users_file_name, 'a', encoding = self.ENCODING)
        users_file.write(credentials + ' user\n')
        users_file.close()
        self.send(conn, "Account Created Successfully-w")


    def login(self, conn: socket.socket, count: int = 0):
        print("Login")
        credentials = self.recv(conn)
        username = credentials.split(' ')[0]
        password = credentials.split(' ')[1]

        try:
            users_file = open(self.USERS_FILE_NAME, 'r', encoding= self.ENCODING)

        except FileNotFoundError:
            print(FileNotFoundError)
            
        users_data = users_file.readlines()

        
        for line in users_data:
            if username in line:
                data = line.split(' ')
                if username == data[0] and password == data[1]:
                    self.send(conn, "Logged In Successfully-w")
                    user_rights = data[2][0:len(data[2]) - 1] #\n at the end of data[2]
                    time.sleep(.1)
                    self.send(conn, user_rights) #User rights
                    return (username, user_rights)
                
        if count <= 2:
            self.send(conn, "Wrong Credentials-w")

            self.login(conn, count + 1)
        else:
            self.send(conn, "Account Not Recognised-w")
            return False


    def send(self, conn: socket.socket, message: str):
        bytes_all = message.encode(self.ENCODING)
        bytes_sent = conn.send(bytes_all)

        if bytes_all != bytes_sent:
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
    