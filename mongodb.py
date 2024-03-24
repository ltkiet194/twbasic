from pymongo import MongoClient

class GameStoreDatabase:
    def __init__(self, url, db_name):
        self.client = MongoClient(url)
        self.db = self.client[db_name]
        self.col_game = self.db['GameData']
        self.col_users = self.db['Users']
        self.col_game_review = self.db['GameReview']
        self.col_game_comment = self.db['GameComment']
        self.col_static = self.db['Static']
        

    def insert_data(self, collection_name, data):
        collection = self.db[collection_name]
        result = collection.insert_one(data)
        return result.inserted_id
    def find_one(self, collection_name, query):
        collection = self.db[collection_name]
        result = collection.find_one(query)
        return list(result)

    def find(self, collection_name, query):
        collection = self.db[collection_name]
        result = collection.find(query)
        return list(result)
    def find_sort(self, collection_name, query , limit):
        collection = self.db[collection_name]
        result = collection.find().sort(query).limit(limit)
        return list(result)

    def update_data(self, collection_name, query, new_data):
        collection = self.db[collection_name]
        result = collection.update_one(query, {'$set': new_data})
        return result.modified_count

    def delete_data(self, collection_name, query):
        collection = self.db[collection_name]
        result = collection.delete_one(query)
        return result.deleted_count

# Example usage:
url = 'mongodb://localhost:27017'
db_name = 'GameStore'
game_db = GameStoreDatabase(url, db_name)


