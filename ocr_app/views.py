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

from ocr_app.db import connect_db, save_request, find_id, getById, updateStatus
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
                
    except ValueError as e:
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
        data = getById(db, transactionId)
        responseDict={}
        jsonObject={}
        print(data)
        if data['pan_data']:
            print("getById: pan_data",data['pan_data'])
            responseDict['status'] = str(data['status'])
            #responseDict['transactionId'] = str(rqstDict['transactionId'])
            responseDict['transactionId'] = str(transactionId)
            responseDict['data'] = (data['pan_data'])
            print("responseDict",responseDict)
            jsonObject = json.loads(json.dumps(responseDict, indent=4))
            #jsonObject = responseDict #json.dumps(responseDict)
            #print("jsonObject type:",type(jsonObject))
        else:
            print("getById: returned no data")
            responseDict['status'] = 'Returned data is under process or error'
            jsonObject = json.loads(json.dumps(responseDict, indent=4))
            #jsonStr = json.dumps(responseDict, sort_keys=True)
            #jsonObject = json.loads(jsonStr)

        return JsonResponse(jsonObject,safe=False)

    except ValueError as e:
        return Response(e.args[0],status.HTTP_400_BAD_REQUEST)

