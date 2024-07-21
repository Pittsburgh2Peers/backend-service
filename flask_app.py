from flask import Flask, request
from flask_cors import CORS
from uuid import uuid4
from datetime import timedelta, date
from db import createUser, getToken, isProfileComplete, userTokenValid, deleteAllUsersFromDb, updateUserProfileDetails, makeCarPoolRequest, carPoolRequestExists, fetchAllCarPoolRequests, offerCarPoolRequest
from common import formatResponse, createToken
from constants import TOKEN_INVALID_ERROR_CODE, TOKEN_INVALID_ERROR_MESSAGE, CAR_POOL_REQUEST_EXISTS_ERROR_CODE, CAR_POOL_REQUEST_EXISTS_ERROR_MESSAGE, CAR_POOL_OFFER_MADE_TO_SELF_ERROR_CODE, CAR_POOL_OFFER_MADE_TO_SELF_ERROR_MESSAGE, CAR_POOL_REQUEST_NOT_FOUND_ERROR_CODE, CAR_POOL_REQUEST_NOT_FOUND_ERROR_MESSAGE, CAR_POOL_OFFER_ALREADY_EXISTS_ERROR_CODE, CAR_POOL_OFFER_ALREADY_EXISTS_ERROR_MESSAGE

app = Flask(__name__)

CORS(app)

@app.route("/registrationSuccess", methods=["POST", "PUT"])
def registrationSuccess():
    try:
        requestBody = request.get_json()
        name = requestBody.get("name")
        emailId = requestBody.get("email")
        profileImage = requestBody.get("profileImage")
        countryCode = requestBody.get("countryCode")
        phoneNo = requestBody.get("phoneNo")
        userToken, tokenValidUntil = createToken()
        data = { "token": userToken }
        createUser(name, emailId, profileImage, countryCode, phoneNo, userToken, tokenValidUntil)
        return formatResponse(True, data)
    except Exception as e:
        print("Exception ==>", e)
        return formatResponse(False, errorMessage=e)
    
@app.route("/generateToken", methods=["POST"])
def generateToken():
    try:
        requestBody = request.get_json()
        emailId = requestBody.get("email")
        token = getToken(emailId)
        data = { "token": token }
        return formatResponse(True, data)
    except Exception as e:
        print("Exception ==>", e)
        return formatResponse(True, errorMessage=str(e))
    
@app.route("/userProfileComplete", methods=["POST"])
def userProfileComplete():
    try:
        requestBody = request.get_json()
        emailId = requestBody.get("email")
        token = requestBody.get("token")
        if userTokenValid(emailId, token):
            profileComplete = isProfileComplete(emailId)
            data = { "eligible": profileComplete }
            return formatResponse(True, data)
        else:
            return formatResponse(True,errorCode=TOKEN_INVALID_ERROR_CODE, errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
    except Exception as e:
        print("Exception ==>", e)
        return formatResponse(False, errorMessage=e)
    
@app.route("/deleteAllUsers")
def deleteAllUsers():
    try:
        deleteAllUsersFromDb()
        return formatResponse(True)
    except Exception as e:
        print("Exception ==>", e)
        return formatResponse(False, errorMessage=e)
    
@app.route("/updateUserProfile", methods=["POST, PUT"])
def updateUserProfile():
    try:
        requestBody = request.get_json()
        emailId = requestBody.get("email")
        token = requestBody.get("token")
        if userTokenValid(emailId, token):
            name = requestBody.get("name")
            phoneNo = requestBody.get("phoneNo")
            countryCode = requestBody.get("countryCode")
            updateUserProfileDetails(emailId,name,phoneNo,countryCode)
            return formatResponse(True)
        else:
            return formatResponse(True,errorCode=TOKEN_INVALID_ERROR_CODE, errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
    except Exception as e:
        print("Exception ==>", e)
        return formatResponse(False, errorMessage=e)

@app.route("/carPoolRequest", methods=["POST", "PUT"])
def carPoolRequest():
    try:
        requestBody = request.get_json()
        emailId = requestBody.get("email")
        token = requestBody.get("token")
        if userTokenValid(emailId, token):
            if not carPoolRequestExists(emailId):
                date = requestBody.get("date")
                time = requestBody.get("time")
                noOfPassengers = requestBody.get("noOfPassengers")
                noOfTrolleys = requestBody.get("noOfTrolleys")
                startLocation = requestBody.get("startLocation")
                endLocation = requestBody.get("endLocation")
                makeCarPoolRequest(emailId,date,time,noOfPassengers,noOfTrolleys,startLocation,endLocation)
                return formatResponse(True)
            else:
                return formatResponse(True,errorCode=CAR_POOL_REQUEST_EXISTS_ERROR_CODE, errorMessage=CAR_POOL_REQUEST_EXISTS_ERROR_MESSAGE)
        else:
            return formatResponse(True,errorCode=TOKEN_INVALID_ERROR_CODE, errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
    except Exception as e:
        print("Exception ==>", e)
        return formatResponse(False, errorMessage=e)
            
@app.route("/getAllCarPoolRequests", methods=["POST"])
def getAllCarPoolRequests():
    try:
        requestBody = request.get_json()
        emailId = requestBody.get("email")
        token = requestBody.get("token")
        if userTokenValid(emailId, token):
            startLocation = requestBody.get("startLocation")
            endLocation = requestBody.get("endLocation")
            time = requestBody.get("time")
            timeRangeStr = requestBody.get("timeRange")
            timeRange = 1 if not timeRangeStr else int(timeRangeStr)
            date = requestBody.get("date")
            carPoolRequests = fetchAllCarPoolRequests(startLocation,endLocation,time, timeRange, date, emailId)
            return formatResponse(True, {"data": carPoolRequests})
        else:
            return formatResponse(True,errorCode=TOKEN_INVALID_ERROR_CODE, errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
    except Exception as e:
        print("Exception ==>", e)
        return formatResponse(False, errorMessage=e)

@app.route("/offerCarPool", methods=["POST"])
def offerCarPool():
    try:
        requestBody = request.get_json()
        emailId = requestBody.get("email")
        token = requestBody.get("token")
        if userTokenValid(emailId, token):
            carPoolId = requestBody.get("id")
            carType = requestBody.get("carType")
            requestRaised = offerCarPoolRequest(emailId, carPoolId, carType)
            if requestRaised == True:
                return formatResponse(True)
            else:
                if requestRaised == CAR_POOL_REQUEST_NOT_FOUND_ERROR_CODE:
                    return formatResponse(True,errorCode=CAR_POOL_REQUEST_NOT_FOUND_ERROR_CODE, errorMessage=CAR_POOL_REQUEST_NOT_FOUND_ERROR_MESSAGE)
                elif requestRaised == CAR_POOL_OFFER_MADE_TO_SELF_ERROR_CODE:
                    return formatResponse(True,errorCode=CAR_POOL_OFFER_MADE_TO_SELF_ERROR_CODE, errorMessage=CAR_POOL_OFFER_MADE_TO_SELF_ERROR_MESSAGE)
                elif requestRaised == CAR_POOL_OFFER_ALREADY_EXISTS_ERROR_CODE:
                    return formatResponse(True,errorCode=CAR_POOL_OFFER_ALREADY_EXISTS_ERROR_CODE, errorMessage=CAR_POOL_OFFER_ALREADY_EXISTS_ERROR_MESSAGE)
                else:
                    return formatResponse(False, errorMessage="Something Went Wrong")
        else:
            return formatResponse(True,errorCode=TOKEN_INVALID_ERROR_CODE, errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
    except Exception as e:
        print("Exception ==>", e)
        return formatResponse(False, errorMessage=e)


@app.route("/")
def home():
    return "<h1 style='margin-top: 20px; text-align: center;'>Pittsburgh 2 Peers is releasing soon!</h1><h4 style='text-align: center;'>The waitlist registration has closed</h4>"

if __name__ == "__main__":
    app.run(debug=True)