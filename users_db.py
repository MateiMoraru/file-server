import pymongo

class Mongo:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:8181/")
    
    def add_branch(self, name):
        
