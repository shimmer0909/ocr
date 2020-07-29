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

from ocr_app.db import MongoDb
Mongo = MongoDb()

from ocr_app.publish import RabbitMQ
RabbitMqClient = RabbitMQ()

@api_view(["POST"])
def ocr(request):
    try:
        rqst = json.loads(request.body)
        if ('fileUrl' in rqst):
            rqst['file_url'] = rqst['fileUrl']
        else:
            print('URL not found')
            return Response('Missing URL', status.HTTP_400_BAD_REQUEST)

        if not ('type' in rqst):
            rqst['type'] = 'pan'

        id = Mongo.save_request(rqst)
        RabbitMqClient.publish(id)
        response = {}
        response['transactionId'] = str(id)
        
        json_object = json.loads(json.dumps(response, indent=4))
        return JsonResponse(json_object, safe=False)

    except Exception as e:
        print("error : ", e)
        error = Mongo.updateError(str(id), str(e))
        return Response(e.args[0],status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def getProcessedDoc(rqst):
    try:
        transactionId = rqst.GET.get('transactionId', '')
        print("getProcessedDoc for transaction id:", transactionId)

        data = None
        responseDict={}
        jsonObject={}
        try:
            data = Mongo.getById(transactionId)
        except:
            print("No data could be fetched using given id: ",e)
            error = Mongo.updateError(transactionId, "No data could be fetched using given id")
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
            error = Mongo.updateError(transactionId, "Invalid transaction id")
            responseDict['errmsg'] = 'Invalid transaction id'
            jsonObject = json.loads(json.dumps(responseDict, indent=4))

        return JsonResponse(jsonObject,safe=False)

    except ValueError as e:
        print("error : ", e)
        error = Mongo.updateError(transactionId, str(e))
        return Response(e.args[0],status.HTTP_400_BAD_REQUEST)

