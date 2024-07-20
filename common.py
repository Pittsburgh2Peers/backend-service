from flask import jsonify
from uuid import uuid4
from datetime import timedelta, date, datetime

errorResponse = {
  "errorCode": "1",
  "errorMessage": "Something went wrong",
}
successResponse = {
    "errorCode": "0",
    "errorMessage": "OK",
}

def formatResponse(status, responseKeys={}, errorCode=None, errorMessage=None):
    if status:
        responseKeys.update(successResponse)
        if errorCode:
            responseKeys["errorCode"] = errorCode
        if errorMessage:
            responseKeys["errorMessage"] = errorMessage
        response = jsonify(responseKeys)
        response.headers.add('Access-Control-Allow-Methods','*')
        response.headers.add('Access-Control-Expose-Headers',"*")
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Content-Type', '*')
        return response
    else:
        response = jsonify(errorResponse)
        response.headers.add('Access-Control-Allow-Methods','*')
        response.headers.add('Access-Control-Expose-Headers',"*")
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Content-Type', '*')
        return response

def createToken():
    return str(uuid4()), (date.today() + timedelta(days=10)).strftime("%d-%m-%Y")

def isTokenValid(tokenValidUntil):
    return datetime.strptime(date.today().strftime("%d-%m-%Y"),"%d-%m-%Y") <= datetime.strptime(tokenValidUntil, "%d-%m-%Y")
