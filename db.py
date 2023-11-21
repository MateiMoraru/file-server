import pymongo

class Mongo:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.users = self.client["File-server"]["users"]

    def search_name(self, name: str):
        return self.users.find({"name": name})
    
    def search_name_pwd(self, name: str, pwd: str):
        return self.users.find({'name': name, 'password': pwd})
    
    def is_admin(self, name: str):
        is_admin = self.users.find({"name": name, "rights": "admin"})
        #print(self.users["rights"].)
        return is_admin

    def add_user(self, name: str, password: str, rights: str):
        data = {"name": name, "password": password, "rights": rights}
        self.users.insertOne(data)
