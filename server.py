import socket, os, time
from typing import List
from db import Mongo
import threading

class Server:
    BUFFER_SIZE = 4096
    ENCODING = "UTF-8"
    END_OF_FILE = "!END!OF!FILE!"
    END_OF_STREAM = "!END!OF!STREAM!"
    WRONG_ARGUMENTS_EXCEPTION = "Wrong Command Arguments, Try Running help"
    NAVIGATION_NO_RIGHTS_EXCEPTION = "You Aren't Allowed To Navigate Here-w"

    def __init__(self, ip: str = "127.0.0.1", port: int = 8080):        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = (ip, port)
        self.database = Mongo()
        self.listening = True
        self.connections = []
        

    def run(self):
        self.socket.bind(self.addr)
        self.socket.listen()
        print(f"Server Listening For Connections on {self.addr}.")
        
        while self.listening:
            conn, addr = self.socket.accept()
            print(f"Client Connected From {addr}")
            self.connections.append(conn)
            try:    
                client = threading.Thread(target=self.handle_conn, args=[conn])
                client.start()
            except Exception as e:
                print(e)
                print("Client Disconnected")


    def handle_conn(self, conn: socket.socket):
        user_name = "None"
        user_rights = "None"
        path = 'server/'
        current_repo = ''

        signup = self.recv(conn)
        
        if signup == 'yes':
            self.signup(conn)
            user_name, user_rights = self.login(conn)
        else:
            user_name, user_rights = self.login(conn)

        while True:
            current_repo = path.replace('server/', '')
            command = self.recv(conn).split(' ')
            print(command)

            if command[0] == 'echo':
                self.handle_echo(command, path, user_name, user_rights, conn)
            elif command[0] == 'create':
                self.handle_create(command, path, user_name, conn)
            elif command[0] == 'set':
                self.handle_set(command, user_name, user_rights, conn)
            elif command[0] == 'add-admin':
                self.handle_admin(command, user_rights, conn)
            elif command[0] == 'log-out':
                user_name = 'Guest'
                user_rights = 'user'
            elif command[0] == 'cat':
                self.handle_cat(command, path, current_repo, user_name, user_rights, conn)
            elif command[0] == 'cat-database':
                self.handle_cat_database(user_rights, conn)
            elif command[0] == 'cd':
                current_repo = self.handle_change_dir(current_repo, command, user_name, user_rights, conn)
                if current_repo != None:
                    path += current_repo
            elif command[0] == 'ls':
                self.handle_list(path, current_repo, conn)
            elif command[0] == 'send-file':
                self.handle_get_file(conn, path)
            elif command[0] == 'get-file':
                self.handle_send_file(command, conn)
            elif command[0] == 'help':
                self.handle_help()
            elif command[0] == 'kill' or command[0] == 'k':
                self.send(conn, "Destroy Client")
                print(f"{user_rights} {user_name} Disconnected")
            elif command[0] == 'kill-server' or command[0] == 'shutdown':
                self.shutdown(conn)
            else:
                self.send(conn, "Unknown Command")

    
    def handle_change_dir(self, path:str, command: List[str], user_name:str, user_rights: str, conn: socket.socket):
        if len(command) < 2:
            print(self.WRONG_ARGUMENTS_EXCEPTION + '-w')
            self.send(self.WRONG_ARGUMENTS_EXCEPTION + '-w')
            return
        
        if len(path) > 1: 
            path += command[1] + '/'
            self.send(conn, f"{path}")
            return path
        else:
            access_dir = self.access_dir(command[1], user_name, user_rights)
            if access_dir[0] and access_dir[1] != None:
                path += command[1] + '/'
                self.send(conn, f"{path}")
                return path
            else:
                self.send(conn, self.NAVIGATION_NO_RIGHTS_EXCEPTION)
                return path
            

    def handle_list(self, path: str, current_repo: str, conn: socket.socket):
        directories = os.listdir(path)
        dirs = ""
        files = ""
        for data in directories:
            if os.path.isfile(path + data):
                files += data
            else:
                dirs += data

        self.send(conn, f"Dirs: {dirs} \nFiles: {files}-w")
        

    def handle_add_admin(self, command: List[str], user_rights: str, conn: socket.socket):
        if len(command) < 2:
            print(self.WRONG_ARGUMENTS_EXCEPTION + '-w')
            self.send(self.WRONG_ARGUMENTS_EXCEPTION + '-w')
            return
        if user_rights == 'admin':
            if self.database.search_name(command[1]):
                self.send(conn, "An Account With The Same Username Already Exists-w")
                return
            
            self.database.add_empty_user(command[1], "admin")
            self.send(conn, f"Admin created. When Opening The Client As {command[1]}, Log In, Specifying Your Password, As You Need To Specify Your Password-w")
        else:
            self.send(conn, "You Don't Have The Correct Rights To Create An Admin Account-w")


    def handle_cat(self, command: List[str], path: str, current_repo: str, user_name: str, user_rights: str, conn: socket.socket):
        if len(command) < 2:
            print(self.WRONG_ARGUMENTS_EXCEPTION + '-w')
            self.send(self.WRONG_ARGUMENTS_EXCEPTION + '-w')
            return
        
        if os.path.exists(path + command[1]):
            if len(current_repo) > 1 and '/' not in command[1]:
                access_dir = self.access_dir(current_repo, user_name, user_rights)
                if access_dir[0] and access_dir[1] != None:
                    fin = open(path + command[1], 'r', encoding=self.ENCODING).read()
                    self.send(conn, fin + '-w')
                else:
                    self.send(conn, self.NAVIGATION_NO_RIGHTS_EXCEPTION + '-w')
            else:
                self.send(conn, "You Must Navigate To The Head Repo Using 'cd' Firstly-w")
        else:
            self.send(conn, "File Doesn't exist-w")


    def handle_echo(self, command: List[str], path: str, user_name: str, user_rights: str, conn: socket.socket):
        if len(command) < 2:
            print(self.WRONG_ARGUMENTS_EXCEPTION + '-w')
            self.send(self.WRONG_ARGUMENTS_EXCEPTION + '-w')
            return
        
        if command[-2] == '>>':
            file_name = command[-1]
            if '/' in file_name:
                file_dir = file_name.split('/')[0]
                access_dir = self.access_dir(file_dir, user_name, user_rights)
                print(access_dir)
            elif path == 'server/':
                access_dir = (True)

            if access_dir[0] and access_dir[1] == "collaborator":
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
            for user in self.connections:
                self.send(user, f'{user_name}> {message}-w')
            #self.socket.sendall(f'{user_name}> {message}-w'.encode(self.ENCODING))


    def handle_create(self, command: List[str], path: str, user_name: str, conn: socket.socket):
        if len(command) < 3:
            print(self.WRONG_ARGUMENTS_EXCEPTION + '-w')
            self.send(self.WRONG_ARGUMENTS_EXCEPTION + '-w')
            return
        
        file_name = command[2]
        if command[1] == "repo":
            if os.path.exists(path + file_name):
                self.send(conn, "Repository already exists-w")
            else:
                os.mkdir(path + file_name)
                if '/' in file_name:
                    pass
                self.database.create_repo(file_name, user_name)
                self.send(conn, f"Created repo {file_name}-w")
        elif command[1] == "file":
            open(path + file_name, 'w', encoding=self.ENCODING).close()
            self.send(conn, f"Created file {file_name}-w")
        else:
            self.send(conn, "Wrong Usage, run help-w")


    def handle_set(self, command: List[str], user_name: str, user_rights: str, conn: socket.socket):
        if len(command) < 4:
            print(self.WRONG_ARGUMENTS_EXCEPTION + '-w')
            self.send(self.WRONG_ARGUMENTS_EXCEPTION + '-w')
            return
               
        repo = command[1]
        rights = self.access_dir(repo, user_name, user_rights)
        if rights[0] and rights[1] != 'reader':
            if command[2] == 'collaborators':
                collaborators = []
                if len(command) > 3:
                    for i in range(3, len(command)):
                        collaborators.append(command[i])
                self.database.set_collaborators(repo, collaborators)
                self.send(conn, f"{collaborators} Are Now Collaborators-w")
            if command[2] == 'readers':
                readers = []
                if len(command) > 3:
                    for i in range(3, len(command)):
                        readers.append(command[i])
                self.database.set_readers(repo, readers)
                self.send(conn, f"{readers} Are Now Readers-w")

    
    def handle_cat_database(self, user_rights: str, conn: socket.socket):
        if user_rights == 'user':
            self.send(conn, "You Don't Have The Correct Rights In Order To Run This Command-w")
        else:
            database = ""
            database += "USERS:\n\n"
            for document in self.database.users.find():
                print(document)
                database += str(document) + '\n'
            database += "FILE-SYSTEM:\n\n"
            for document in self.database.file_system.find():
                print(document)
                database += str(document) + '\n'
            database += '-w'
            self.send(conn, database)

    
    def handle_get_file(self, conn: socket.socket, path: str):
        data = self.recv(conn)
        while self.END_OF_STREAM not in data:
            file_name = data
            file = ""
            data = self.recv(conn)
            while self.END_OF_FILE not in data:
                file += data
                data = self.recv(conn)
        
            fout = open(path + file_name, 'w')
            fout.write(file)
            fout.close()
            if self.END_OF_STREAM not in data:
                break
        self.send(conn, "Finished transferring file/s-w")

    def handle_send_file(self, command: List[str], conn: socket.socket):
        if len(command) < 2:
            print(self.WRONG_ARGUMENTS_EXCEPTION + '-w')
            self.send(self.WRONG_ARGUMENTS_EXCEPTION + '-w')
            return
        file_name = command[1:len(command)]
        for file in file_name:
            self.send(conn, file)
            data = open(file, 'r').readlines()
            data = self.split_file_into_chunks(data)

            for chunk in data:
                self.send(conn, chunk)
                time.sleep(.1)
            self.send(conn, self.END_OF_FILE)
            time.sleep(.1)
        self.send(conn, self.END_OF_STREAM)
        self.send(conn, "Finished Transferring Files-w")

    
    def split_file_into_chunks(self, data: str):
        if len(data) > self.BUFFER_SIZE:
            new_data = []
            last_i = 0
            for i in range(0, len(data), self.BUFFER_SIZE):
                new_data.append(data[last_i:i])
                last_i = i
            return new_data
        else:
            return data


    def access_dir(self, repo: str, user_name: str, user_rights: str):
        if user_rights == 'admin':
            return (True, 'collaborator') #(can-access, rights)
        else:
            collaborators = self.database.get_collaborators(repo)
            if user_name in collaborators:
                return (True, 'collaborator')
            readers = self.database.get_readers(repo)
            if user_name in readers:
                return (True, 'reader')
        return (False, None)


    def handle_help(self):
        commands = ['',
                    'echo <message> - send a message to all the users that are connected',
                    'echo <message> >> <file_name> - send a message to the server and save it in a file',
                    'create <repo|file> <name>',
                    'set <repo> <collaborators|readers> <name|*>',
                    'add-admin <user_name>',
                    'cat <file_name>',
                    'log-out - log out of the current account',
                    'kill - Quit the program',
                    '']
        
        print('-' * 50)
        for command in commands:
            print(command)
        print('-' * 50)

        
    def signup(self, conn: socket.socket):
        credentials = self.recv(conn)
        username = credentials.split(' ')[0]
        password = credentials.split(' ')[1]
        if len(password) < 1:
            print("No Password Provided")
            self.send("No Password Provided-w")
            self.signup(conn)

        if self.database.search_name(username):
            self.send(conn, "Account Already Exists-w")
            self.signup(conn)
        else:
            self.database.add_user(username, password, "user")
            self.send(conn, "Account Created Successfully-w")


    def login(self, conn: socket.socket, count: int = 0):
        print("Login")
        credentials = self.recv(conn)
        username = credentials.split(' ')[0]
        password = credentials.split(' ')[1]
        if len(password) < 1:
            print("No Password Provided")
            self.send(conn, "No Password Provided")
            self.login(conn)
        
        resp = self.database.search_name_pwd(username, password)

        if self.database.search_name(username) and self.database.is_empty(username):
            self.database.set_password(username, password)
            self.send(conn, f"Welcome {username}, Your Account Has Successfully Been Created-w")
            time.sleep(.1)
            self.send(conn, "Logged In Successfully")
            user_rights = self.database.is_admin(username)
            time.sleep(.1)
            self.send(conn, user_rights)
            return (username, user_rights)
        if resp:
            self.send(conn, "Logged In Successfully-w")
            user_rights = self.database.is_admin(username)
            time.sleep(.1)
            self.send(conn, str(user_rights))
            return (username, user_rights)
        if count <= 2:
            self.send(conn, "Wrong Credentials-w")

            self.login(conn, count + 1)
        else:
            self.send(conn, "Account Not Recognised-w")
            return False
        
    
    def shutdown(self, conn: socket.socket):
        self.send(conn, "Destroy Server")
        print(f"Shutting Down Server")
        self.listening = False
        self.socket.close()


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
    