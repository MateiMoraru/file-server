import socket
import getpass
import time
import os

class Client:
    ENCODING = "UTF-8"
    BUFFER_SIZE = 4096
    END_OF_FILE = "!END!OF!FILE!"
    END_OF_STREAM = "!END!OF!STREAM!"

    def __init__(self, ip: str = "127.0.0.1", port: int = 8181):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        self.server_addr = (ip, port)

        self.user_name = "None"
        self.user_rights = "None"
        self.path = ""

    
    def connect(self):
        self.socket.connect(self.server_addr)

        signup = input("Do You Want To Create An Account? yes/no\n")
        self.send(signup)
        if signup == "yes":
            self.signup()
            self.login()
        else:
            self.login()

        self.run()


    def run(self):
        if self.user_rights != "None":
            while True:
                command = input(f"{self.path}> ")
                argvs = command.split(' ')
                self.send(command)
                if argvs[0] == 'send-file':
                    self.send_file(argvs)  
                elif argvs[0] == 'get-file':
                    self.get_file()

                response = self.recv()
                self.process_recv(response)

                if argvs[0] == 'cd' and 'You' not in response:
                    self.path = response
                
                if response == "Destroy Client":
                    self.socket.close()
                    return
                elif response == "Destroy Server":
                    self.socket.close()
                    return
        else:
            print("Failed To Log In")

    
    def send_file(self, command):
        file_name = command[1:len(command)]
        for file in file_name:
            self.send(file)
            data = open(file, 'r').readlines()
            data = self.split_file_into_chunks(data)

            for chunk in data:
                self.send(chunk)
                time.sleep(.1)
            self.send(self.END_OF_FILE)
            time.sleep(.1)
        self.send(self.END_OF_STREAM)

    
    def split_file_into_chunks(self, data):
        if len(data) > self.BUFFER_SIZE:
            new_data = []
            last_i = 0
            for i in range(0, len(data), self.BUFFER_SIZE):
                new_data.append(data[last_i:i])
                last_i = i
            return new_data
        else:
            return data

    
    def get_file(self):
        data = self.recv()
        print(data)
        while self.END_OF_STREAM not in data:
            file_name = data
            file = ""
            data = self.recv()
            print(data)
            while self.END_OF_FILE not in data:
                file += data
                data = self.recv()
            print(data)

            os.mkdir("Downloads")
            fout = open("Downloads/" + file_name, 'w')
            fout.write(file)
            fout.close()
            if self.END_OF_STREAM not in data:
                break
        print('Your Files Are Saved In "Downloads/"')


    def signup(self):
        username = input("Username: ")
        password = getpass.getpass(prompt="Password: ")
        credentials = username + ' ' + password

        self.send(credentials)

        confirmation = self.recv()

        if "No Password Provided" in confirmation:
            print(confirmation)
            self.signup()
        elif "Account Already Exists" in confirmation:
            print(f"{confirmation}, Try Again")
            self.signup()

        else:
            print(confirmation)

        print("Please Login Again\n")

        
    def login(self):
        username = input("Username: ")
        password = getpass.getpass(prompt="Password: ")
        credentials = username + ' ' + password
        print()

        self.send(credentials)
        confirmation = self.recv()
        if "No Password Provided" in confirmation:
            print(confirmation)
            self.login()
        elif "Welcome" in confirmation:
            confirmation = self.recv()
            self.process_recv(confirmation)
        elif "Logged In Successfully" in confirmation:
            self.user_rights = self.recv()
            self.user_name = username
            print(f"Logged In Successfully, With {self.user_rights} Rights.\n")
        elif confirmation == "Wrong Credentials":
            print("The Credentials You Entered Weren't Found In Our Database.\n Try Again.\n")
            self.login()

        elif confirmation == "Account Not Recognised":
            print("\n Your Account Was Not Found In Our Database.\n Try Creating One.\n")

    
    def send(self, message: str):
        bytes_all = message.encode(self.ENCODING)
        bytes_sent = self.socket.send(bytes_all)

        if bytes_all != bytes_sent:
            return False
        
        return True
    

    def process_recv(self, response):
        if '-w' in response:
            response = response[0:len(response) - 2]
            print(response)


    def recv(self):
        try:
            message = self.socket.recv(self.BUFFER_SIZE).decode(self.ENCODING)
            return message
        except TimeoutError as e:
            print(e)

if __name__ == "__main__":
    client = Client("127.0.0.1", 8181)
    client.connect()