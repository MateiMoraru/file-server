import pymongo

class Mongo:
    def __init__(self, addr:str="mongodb://localhost:27017/"):
        self.client = pymongo.MongoClient(addr)
        self.users = self.client["File-server"]["users"]

    def search_name(self, name:str):
        return self.users.find_one({"name": name}) != None
    
    def search_name_pwd(self, name:str, pwd:str):
        return self.users.find({'name': name, 'password': pwd}) != None
    
    def is_admin(self, name:str):
        return str(self.users.find_one({"name": name})["rights"])
    
    def is_empty(self, name:str):
        return self.users.find_one({"name": name})["password"] == "NotInitialised"
    
    def set_password(self, name:str, password:str):
        self.users.find_one({"name": name}).update({"$set": {"password": password}})
    
    def add_empty_user(self, name:str, rights:str="user"):
        data = {"name": name, "password": "NotInitialised", "rights": rights}
        self.users.insert_one(data)

    def add_user(self, name:str, password:str, rights:str):
        data = {"name": name, "password": password, "rights": rights}
        self.users.insert_one(data)
