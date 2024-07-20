from flask import jsonify
from uuid import uuid4
from datetime import timedelta, date, datetime

errorMessage = {
  "errorCode": "1",
  "message": "Something went wrong",
}
successMessage = {
    "errorCode": "0",
    "errorMessage": "OK",
}

def formatResponse(status, responseKeys):
    if status:
        responseKeys.update(successMessage)
        response = jsonify(responseKeys)
        response.headers.add('Access-Control-Allow-Methods','*')
        response.headers.add('Access-Control-Expose-Headers',"*")
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Content-Type', '*')
        return response
    else:
        response = jsonify(errorMessage)
        response.headers.add('Access-Control-Allow-Methods','*')
        response.headers.add('Access-Control-Expose-Headers',"*")
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Origin', 'https://eximplify-develop.vercel.app')
        response.headers.add('Content-Type', '*')
        return response

def createToken():
    return str(uuid4()), (date.today() + timedelta(days=10)).strftime("%d-%m-%Y")

def isTokenValid(tokenValidUntil):
    return datetime.strptime(date.today().strftime("%d-%m-%Y"),"%d-%m-%Y") <= datetime.strptime(tokenValidUntil, "%d-%m-%Y")
