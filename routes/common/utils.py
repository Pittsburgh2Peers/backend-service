from flask import jsonify
from uuid import uuid4
from datetime import timedelta, date, datetime
import logging

logger = logging.getLogger(__name__)

errorResponse = {
  "errorCode": "1",
  "errorMessage": "Something went wrong",
}
successResponse = {
    "errorCode": "0",
    "errorMessage": "OK",
}

def addHeaders(response):
    response.headers.add('Access-Control-Allow-Methods','*')
    response.headers.add('Access-Control-Expose-Headers','*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Origin', 'https://pittsburgh2peers.vercel.app')
    response.headers.add('Content-Type', '*')
    return response

def formatResponse(status, responseKeys={}, errorCode=None, errorMessage=None):
    if status:
        responseKeys.update(successResponse)
        if errorCode:
            responseKeys["errorCode"] = errorCode
        if errorMessage:
            responseKeys["errorMessage"] = errorMessage
        response = jsonify(responseKeys)
        return addHeaders(response)
    else:
        response = jsonify(errorResponse)
        return addHeaders(response)

def createToken():
    return str(uuid4()), (date.today() + timedelta(days=10)).strftime("%d-%m-%Y")

def isTokenValid(tokenValidUntil):
    return datetime.strptime(date.today().strftime("%d-%m-%Y"),"%d-%m-%Y") <= datetime.strptime(tokenValidUntil, "%d-%m-%Y")

def getTimeFrame(time, timeRange):
    try:
        behindTime = datetime.combine(date.today(), datetime.strptime(time, '%H:%M').time()) - timedelta(hours=timeRange)
        aheadTime = datetime.combine(date.today(), datetime.strptime(time, '%H:%M').time()) + timedelta(hours=timeRange)
        today = datetime.today()
        lowerLimitTime = "00:00" if behindTime.date() < today.date() else behindTime.strftime('%H:%M')
        upperLimitTime = "23:59" if aheadTime.date() > today.date() else aheadTime.strftime('%H:%M')
        return lowerLimitTime, upperLimitTime
    except Exception as e:
        logger.error("Exception ==>"+ str(e))
        return "00:00", "23:59"

def getDayFrame(date, dayRange):
    try:
        behindDate = datetime.strptime(date, "%d-%m-%Y") - timedelta(days=dayRange)
        aheadDate = datetime.strptime(date, "%d-%m-%Y") + timedelta(days=dayRange)
        lowerLimitDate = behindDate.strftime('%Y-%m-%d')
        upperLimitDate = aheadDate.strftime('%Y-%m-%d')
        return lowerLimitDate, upperLimitDate
    except Exception as e:
        logger.error("Exception ==>"+ str(e))
        return "1900-01-01", "2100-01-01"