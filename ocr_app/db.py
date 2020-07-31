from pymongo import MongoClient
from bson.objectid import ObjectId
from django.conf import settings
from datetime import datetime


class MongoDb:
    """
    This class connects to db and fetch/update data based on query passed
    """
    def __init__(self, db_name=settings.MONGO["DBNAME"]):
        print(settings)
        self.client = MongoClient("mongodb+srv://" + settings.MONGO["USER"] + ":" + settings.MONGO["PASSWORD"] + "@" + settings.MONGO["HOST"] + "/?retryWrites=true&w=majority")
        self.db = self.client[db_name]
        print('connected to db')
        
    def save_request(self, rqst):    
        post_data = {
            'file_url': rqst['file_url'],
            'type': rqst['type'],
            'pan_data': {},
            'status': 'initiated',
            'error': 'None',
            'process_time': 'null',
            'start_time': 'null',
            'created_at': datetime.now()
        }
        if ('callback_url' in rqst):
            post_data['callback_url'] = rqst['callback_url']
        return self.db.pan_records.insert_one(post_data).inserted_id
        
        
    def save_pan_data(self, _id, data):
        return self.db.pan_records.update_one({"_id": ObjectId(_id)}, {"$set": {'pan_data':data}})
        
    def find_id(self, url):
        return self.db.pan_records.find_one({"url": url})
        
    def getById(self, _id):
        return self.db.pan_records.find_one({"_id": ObjectId(_id)})
            
    def updateStatus(self, _id, status):
        return self.db.pan_records.update_one({"_id": ObjectId(_id)}, {"$set": {'status':status}})

    def updateError(self, _id, error):
        return self.db.pan_records.update_one({"_id": ObjectId(_id)}, {"$set": {'error':error}})

    def updateProcessTime(self, _id, processTime, startTime, completedOn):
        return self.db.pan_records.update({"_id": ObjectId(_id)}, {"$set": {'process_time': processTime, 'start_time': startTime, 'completedOn': completedOn}})
