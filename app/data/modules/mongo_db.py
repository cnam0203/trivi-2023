
from pymongo import MongoClient

class MongoDB:
    def __init__(self, 
                 MONGO_HOST,
                 MONGO_PORT,
                 MONGO_USERNAME, 
                 MONGO_PASSWORD, 
                 MONGO_DB):
        self.client = MongoClient('mongodb://%s:%s@%s:%s/?authMechanism=DEFAULT' % (MONGO_USERNAME, MONGO_PASSWORD, MONGO_HOST, MONGO_PORT))
        self.db = self.client[MONGO_DB]
        
    def insert(self, collection_name, data):
        self.collection = self.db[collection_name]
        data = self.collection.insert_one(data)
        return data
        
    def find(self, collection_name, query):
        self.collection = self.db[collection_name]
        return self.collection.find(query)
    
    def find_one(self, collection_name, query):
        self.collection = self.db[collection_name]
        return self.collection.find_one(query)
    
    def update(self, collection_name, query, data):
        self.collection = self.db[collection_name]
        self.collection.update_one(query, {"$set": data})
        
    def delete(self, collection_name, query):
        self.collection = self.db[collection_name]
        self.collection.delete_one(query)
