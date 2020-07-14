from pymongo import MongoClient
from bson.objectid import ObjectId


def connect_db():
    client = MongoClient()
#    client = MongoClient('mongodb://localhost:27017')
    client = MongoClient("mongodb+srv://dev-user:indifi123@cluster0-jfb0t.mongodb.net/?retryWrites=true&w=majority")

    db = client["pan_ocr_database"]
    return db
    
    
def save_request(db, rqst):
#    posts = db.posts
    post_data = {
        'fileUrl':rqst['fileUrl'],
        'type':rqst['type'],
        'callbackUrl':rqst['callbackUrl'],
        'pan_data':{},
        'status':'initiated',
        'process_time':'null',
        'start_time':'null',
        'created at':'null'
    }
    return db.pan_records.insert_one(post_data).inserted_id
    
    
def save_pan_data(db, _id, data):
#    return db.pan_records.find_one_and_update({"_id": ObjectId(_id)}, {"$set": {'pan_data':'data'}})
    return db.pan_records.update_one({"_id": ObjectId(_id)}, {"$set": {'pan_data':data}})
    
def find_id(db, url):
    return db.pan_records.find_one({"url": url})
    
def getById(db, _id):
    return db.pan_records.find_one({"_id": ObjectId(_id)})

def getData(db):
    for x in db.pan_records.find():
        print(x)
        
def updateStatus(db, _id, status):
    return db.pan_records.update_one({"_id": ObjectId(_id)}, {"$set": {'status':status}})

def updateProcessTime(db, _id, processTime, startTime, Date):
    return db.pan_records.update({"_id": ObjectId(_id)}, {"$set": {'process_time':processTime,'start_time':startTime,'created at':Date}})
