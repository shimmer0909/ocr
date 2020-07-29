from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.core import serializers
from django.conf import settings
import json
from django.http import HttpResponse

from ocr_app.db import connect_db, save_request, find_id, getById, updateStatus, updateError, connect_db_conf
from ocr_app.publish import publish

db_settings = getattr(settings, "MONGO", None)
if db_settings is None:
    raise ValueError("No settings found")

@api_view(["POST"])

def ocr(panimg):
    try:
        img = ""
        rqst=json.loads(panimg.body)
        if ('file_url' in rqst):
            file_url = rqst['file_url']
        if ('type' in rqst):
            type = rqst['type']
        if ('callback_url' in rqst):
            callback_url = rqst['callback_url']
        
        db = connect_db_conf(db_settings.get('USER'), db_settings.get('HOST'), db_settings.get('PASSWORD'), db_settings.get('DBNAME'))
    
                
        id = save_request(db, rqst)
        publish(str(id))
        response = {}
        response['transactionId'] = str(id)
        
        json_object = json.loads(json.dumps(response, indent=4))
        return JsonResponse(json_object,safe=False)
                
    except Exception as e:
        print("e : ", e)
        error = updateError(db,str(id),str(e))
        return Response(e.args[0],status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def getProcessedDoc(rqst):
    print("rqst",rqst)
    try:
        transactionId = rqst.GET.get('transactionId', '')
        print("getProcessedDoc for transaction id:", transactionId)
        
        db = connect_db_conf(db_settings.get('USER'), db_settings.get('HOST'), db_settings.get('PASSWORD'), db_settings.get('DBNAME'))
    
        data = None
        responseDict={}
        jsonObject={}
        try:
            data = getById(db, transactionId)
        except:
            print("No data could be fetched using given id: ",e)
            error = updateError(db,transactionId,"No data could be fetched using given id")
        if data is not None:
            if data['pan_data']:
                responseDict['status'] = str(data['status'])
                responseDict['errmsg'] = str(data['error'])
                responseDict['transactionId'] = str(transactionId)
                responseDict['data'] = (data['pan_data'])
                print("responseDict",responseDict)
                jsonObject = json.loads(json.dumps(responseDict, indent=4))
            else:
                print("getById: returned no data")
                responseDict['status'] = str(data['status'])
                responseDict['errmsg'] = str(data['error'])
                responseDict['transactionId'] = str(transactionId)
                jsonObject = json.loads(json.dumps(responseDict, indent=4))
        else:
            error = updateError(db,transactionId,"Invalid transaction id")
            responseDict['errmsg'] = 'Invalid transaction id'
            jsonObject = json.loads(json.dumps(responseDict, indent=4))

        return JsonResponse(jsonObject,safe=False)

    except ValueError as e:
        print("e : ", e)
        error = updateError(db,transactionId,str(e))
        return Response(e.args[0],status.HTTP_400_BAD_REQUEST)

