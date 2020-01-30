import pymongo


class MongoDBSaver:
    def __init__(self, host='localhost', port=27017, db_name='database', collection_name='collection'):
        self.client = pymongo.MongoClient(host=host, port=port)
        self.db = self.client.get_database(db_name)
        if collection_name in self.db.collection_names():
            self.collection = self.db.get_collection(collection_name)
        else:
            self.collection = self.db.create_collection(collection_name)

    def __getattr__(self, item):
        return self.collection.__getattribute__(item)

    def insert(self, list_or_dict):
        save_target = None
        if isinstance(list_or_dict, dict):
            save_target = [list_or_dict]
        elif isinstance(list_or_dict, list):
            save_target = list_or_dict

        if save_target is None:
            raise TypeError("list_or_dict must be a list or dict")
        return self.collection.insert_many(save_target)

    def find_dumps_safe(self, cond={}, show_filter={}):
        return self.collection.find(cond, dict(show_filter, _id=0))

    def flush(self, collection=None):
        if collection is None:
            collection = self.collection
        try:
            self.db.drop_collection(collection)
            return True
        except Exception:
            return False
