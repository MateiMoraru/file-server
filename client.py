import socket

class Client:
    ENCODING = "UTF-8"
    BUFFER_SIZE = 4096

    def __init__(self, ip: str, addr: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_addr = (ip, addr)

    
    def connect(self):
        self.socket.connect(self.server_addr)

        signup = input("Do You Want To Create An Account? yes/no")
        self.send(signup)

        if signup == "yes":
            self.signup()
        else:
            self.login()


    def login(self):
        username = input("Username: ")
        password = input("Password: ") #Use GetPass to hide password
        credentials = username + ' ' + password

        self.send(credentials)

        confirmation = self.recv()
        
        if confirmation == "Logged In Successfully":
            self.user_rights = self.recv()
            print(f"Logged In Successfully, With {self.user_rights} Rights.")

        elif confirmation == "Wrong Credentials":
            print("The Credentials You Entered Weren't Found In Our Database.\n Try Again.\n")
            self.login()

        elif confirmation == "Account Not Recognised":
            print("\n Your Account Was Not Found In Our Database.\n Try Creating One.")

    
    def signup(self):
        username = input("Username: ")
        password = input("Password: ") #Use GetPass to hide password
        credentials = username + ' ' + password

        self.send(credentials)

        confirmation = self.recv()

        if confirmation == "Account Already Exists":
            print(f"{confirmation}, Try Again")
            self.signup()

        else:
            print(confirmation)

        print("Please Login Now")

        self.login()
        

    def send(self, message: str):
        bytes = message.encode(self.ENCODING)
        bytes_sent = self.socket.send(bytes)

        if len(bytes) != len(bytes_sent):
            return False
        
        return True
    

    def recv(self):
        try:
            message = self.socket.recv(self.BUFFER_SIZE).decode(self.ENCODING)
            return message
        except TimeoutError as e:
            print(e)