from pymongo import MongoClient
from bson.objectid import ObjectId
from django.conf import settings


def connect_db():
    client = MongoClient()
#    client = MongoClient('mongodb://localhost:27017')
#    client = MongoClient("mongodb+srv://dev-user:indifi123@cluster0-jfb0t.mongodb.net/?retryWrites=true&w=majority")
    client = MongoClient("mongodb+srv://" + settings.MONGO["USER"] + ":" + settings.MONGO["PASSWORD"] + "@" + settings.MONGO["HOST"] + "/?retryWrites=true&w=majority")
    
    
#    db = client["pan_ocr_database"]
    db = client[settings.MONGO["DBNAME"]]
    return db

def connect_db_conf(user, host, password, dbname):
    client = MongoClient()
    client = MongoClient("mongodb+srv://" + user + ":" + password + "@" + host + "/?retryWrites=true&w=majority")

    db = client[dbname]
    return db
    
def save_request(db, rqst):
#    posts = db.posts
    
    post_data = {
        'file_url':rqst['file_url'],
        'type':rqst['type'],
        'pan_data':{},
        'status':'initiated',
        'error':'None',
        'process_time':'null',
        'start_time':'null',
        'created_at':'null'
    }
    if ('callback_url' in rqst):
        post_data['callback_url'] = rqst['callback_url']
    return db.pan_records.insert_one(post_data).inserted_id
    
    
def save_pan_data(db, _id, data):
#    return db.pan_records.find_one_and_update({"_id": ObjectId(_id)}, {"$set": {'pan_data':'data'}})
    return db.pan_records.update_one({"_id": ObjectId(_id)}, {"$set": {'pan_data':data}})
    
def find_id(db, url):
    return db.pan_records.find_one({"url": url})
    
def getById(db, _id):
    return db.pan_records.find_one({"_id": ObjectId(_id)})
        
def updateStatus(db, _id, status):
    return db.pan_records.update_one({"_id": ObjectId(_id)}, {"$set": {'status':status}})

def updateError(db, _id, error):
    return db.pan_records.update_one({"_id": ObjectId(_id)}, {"$set": {'error':error}})

def updateProcessTime(db, _id, processTime, startTime, Date):
    return db.pan_records.update({"_id": ObjectId(_id)}, {"$set": {'process_time':processTime,'start_time':startTime,'created_at':Date}})
