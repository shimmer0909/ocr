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

from ocr_app.db import connect_db, save_request, find_id, getById, updateStatus, updateError
from ocr_app.publish import publish


@api_view(["POST"])

def ocr(panimg):
    try:
        img = ""
        rqst=json.loads(panimg.body)
        if ('fileUrl' in rqst):
            fileUrl = rqst['fileUrl']
        if ('type' in rqst):
            type = rqst['type']
        if ('callbackUrl' in rqst):
            callbackUrl = rqst['callbackUrl']
        
        db = connect_db()
                
        id = save_request(db, rqst)
        publish(str(id))
        response = {}
        response['transactionId'] = str(id)
        
        json_object = json.loads(json.dumps(response, indent=4))
        return JsonResponse(json_object,safe=False)
                
    except Exception as e:
        error = updateError(db,str(id),e)
        return Response(e.args[0],status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def getProcessedDoc(rqst):
    print("rqst",rqst)
    try:
        transactionId = rqst.GET.get('transactionId', '')
        #rqstDict=json.loads(rqst.body)
        #print("rqstDict: ",rqstDict)
        #transactionId = rqstDict['transactionId']
        print("getProcessedDoc for transaction id:", transactionId)
        
        db = connect_db()
        data = None
        responseDict={}
        jsonObject={}
        try:
            data = getById(db, transactionId)
        except:
            error = updateError(db,transactionId,"No data could be fetched using given id")
            print("No data could be fetched using given id")
#        print("data: ",data)
        if data is not None:
#            print(data)
            if data['pan_data']:
                print("getById: pan_data",data['pan_data'])
                responseDict['status'] = str(data['status'])
                responseDict['errmsg'] = str(data['error'])
                #responseDict['transactionId'] = str(rqstDict['transactionId'])
                responseDict['transactionId'] = str(transactionId)
                responseDict['data'] = (data['pan_data'])
                print("responseDict",responseDict)
                jsonObject = json.loads(json.dumps(responseDict, indent=4))
                #jsonObject = responseDict #json.dumps(responseDict)
                #print("jsonObject type:",type(jsonObject))
            else:
                print("getById: returned no data")
#                status = updateStatus(db,transactionId,'error')
#                responseDict['status'] = 'error'
                responseDict['status'] = str(data['status'])
                responseDict['errmsg'] = str(data['error'])
                responseDict['transactionId'] = str(transactionId)
#                responseDict['errmsg'] = 'Unable to process image'
                jsonObject = json.loads(json.dumps(responseDict, indent=4))
                #jsonStr = json.dumps(responseDict, sort_keys=True)
                #jsonObject = json.loads(jsonStr)
        else:
            error = updateError(db,transactionId,"Invalid transaction id")
            responseDict['errmsg'] = 'Invalid transaction id'
            jsonObject = json.loads(json.dumps(responseDict, indent=4))

        return JsonResponse(jsonObject,safe=False)

    except ValueError as e:
        error = updateError(db,transactionId,e)
        return Response(e.args[0],status.HTTP_400_BAD_REQUEST)

#errmsg:invalid transaction id
#status = error