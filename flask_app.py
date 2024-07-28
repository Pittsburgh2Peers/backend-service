from flask import Flask, request, render_template
from flask_cors import CORS
from uuid import uuid4
from datetime import timedelta, date
from db import createUser, getToken, isProfileComplete, userTokenValid, deleteAllUsersFromDb, updateUserProfileDetails, makeCarPoolRequest, carPoolRequestExists, fetchAllCarPoolRequests, offerCarPoolRequest, fetchMyCarPoolOffers, fetchUserDetails, getAllUsers, getCarPoolRequests, fetchUserFlags, uHaulRequestExists, makeUHaulRequest, fetchAllUHaulRequests, fetchMyUHaulOffers
from common import formatResponse, createToken
from constants import TOKEN_INVALID_ERROR_CODE, TOKEN_INVALID_ERROR_MESSAGE, CAR_POOL_REQUEST_EXISTS_ERROR_CODE, CAR_POOL_REQUEST_EXISTS_ERROR_MESSAGE, CAR_POOL_OFFER_MADE_TO_SELF_ERROR_CODE, CAR_POOL_OFFER_MADE_TO_SELF_ERROR_MESSAGE, CAR_POOL_REQUEST_NOT_FOUND_ERROR_CODE, CAR_POOL_REQUEST_NOT_FOUND_ERROR_MESSAGE, CAR_POOL_OFFER_ALREADY_EXISTS_ERROR_CODE, CAR_POOL_OFFER_ALREADY_EXISTS_ERROR_MESSAGE, USER_NOT_FOUND_ERROR_CODE, USER_NOT_FOUND_ERROR_MESSAGE, U_HAUL_REQUEST_NOT_FOUND_ERROR_CODE, U_HAUL_REQUEST_NOT_FOUND_ERROR_MESSAGE
import re
import logging
app = Flask(__name__)

logger = logging.getLogger(__name__)

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
        logger.error("Exception ==>"+ str(e))
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
        logger.error("Exception ==>"+ str(e))
        return formatResponse(False, errorMessage=str(e))
    
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
        logger.error("Exception ==>"+ str(e))
        return formatResponse(False, errorMessage=e)
    
@app.route("/deleteAllUsers")
def deleteAllUsers():
    try:
        deleteAllUsersFromDb()
        return formatResponse(True)
    except Exception as e:
        logger.error("Exception ==>"+ str(e))
        return formatResponse(False, errorMessage=e)
    
@app.route("/updateUserProfile", methods=["POST", "PUT"])
def updateUserProfile():
    try:
        requestBody = request.get_json()
        emailId = requestBody.get("email")
        token = requestBody.get("token")
        if userTokenValid(emailId, token):
            name = requestBody.get("name")
            phoneNo = requestBody.get("phoneNo")
            if phoneNo:
                # remove all spaces
                phoneNo = re.sub(" ", "", phoneNo)
            countryCode = requestBody.get("countryCode")
            updateUserProfileDetails(emailId,name,phoneNo,countryCode)
            return formatResponse(True)
        else:
            return formatResponse(True,errorCode=TOKEN_INVALID_ERROR_CODE, errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
    except Exception as e:
        logger.error("Exception ==>"+ str(e))
        return formatResponse(False, errorMessage=e)

@app.route("/carPoolRequest", methods=["POST", "PUT"])
def carPoolRequest():
    try:
        requestBody = request.get_json()
        emailId = requestBody.get("email")
        token = requestBody.get("token")
        if userTokenValid(emailId, token):
            date = requestBody.get("date")
            time = requestBody.get("time")
            noOfPassengers = requestBody.get("noOfPassengers")
            noOfTrolleys = requestBody.get("noOfTrolleys")
            startLocation = requestBody.get("startLocation")
            endLocation = requestBody.get("endLocation")
            if not carPoolRequestExists(emailId):
                makeCarPoolRequest(emailId,date,time,noOfPassengers,noOfTrolleys,startLocation,endLocation, True)
                return formatResponse(True)
            else:
                makeCarPoolRequest(emailId,date,time,noOfPassengers,noOfTrolleys,startLocation,endLocation, False)
                return formatResponse(True)
        else:
            return formatResponse(True,errorCode=TOKEN_INVALID_ERROR_CODE, errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
    except Exception as e:
        logger.error("Exception ==>"+ str(e))
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
        logger.error("Exception ==>"+ str(e))
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
        logger.error("Exception ==>"+ str(e))
        return formatResponse(False, errorMessage=e)

@app.route("/getMyCarPoolOffers", methods=["POST"])
def getMyCarPoolOffers():
    try:
        requestBody = request.get_json()
        emailId = requestBody.get("email")
        token = requestBody.get("token")
        if userTokenValid(emailId, token):
            carPoolRequestFound, carPoolOffers, pendingRequestDetails = fetchMyCarPoolOffers(emailId)
            if carPoolRequestFound:
                return formatResponse(True, {"offers": carPoolOffers, "pendingRequestDetails": pendingRequestDetails })
            else:
                return formatResponse(True,errorCode=CAR_POOL_REQUEST_NOT_FOUND_ERROR_CODE, errorMessage=CAR_POOL_REQUEST_NOT_FOUND_ERROR_MESSAGE)
        else:
            return formatResponse(True,errorCode=TOKEN_INVALID_ERROR_CODE, errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
    except Exception as e:
        logger.error("Exception ==>"+ str(e))
        return formatResponse(False, errorMessage=e)

@app.route("/")
def home():
    return "<h1 style='margin-top: 20px; text-align: center;'>Pittsburgh 2 Peers is releasing soon!</h1><h4 style='text-align: center;'>The waitlist registration has closed</h4>"

@app.route("/getUserProfileDetails", methods=["POST"])
def getUserProfileDetails():
    try:
        requestBody = request.get_json()
        emailId = requestBody.get("email")
        token = requestBody.get("token")
        if userTokenValid(emailId, token):
            user = fetchUserDetails(emailId)
            if user:
                return formatResponse(True, {"userDetails": user})
            else:
                return formatResponse(True,errorCode=USER_NOT_FOUND_ERROR_CODE, errorMessage=USER_NOT_FOUND_ERROR_MESSAGE)
        else:
            return formatResponse(True,errorCode=TOKEN_INVALID_ERROR_CODE, errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
    except Exception as e:
        logger.error("Exception ==>"+ str(e))
        return formatResponse(False, errorMessage=e)
    
@app.route("/adminDashboard")
def adminDashboard():
    # get all users and count
    userData = getAllUsers()
    carPoolData = getCarPoolRequests()
    return render_template("adminDashboard.html", userData=userData, userCount = len(userData), carPoolData = carPoolData, carPoolCount = len(carPoolData))

@app.route("/getFlags", methods=["POST"])
def getFlags():
    try:
        requestBody = request.get_json()
        emailId = requestBody.get("email")
        token = requestBody.get("token")
        if userTokenValid(emailId, token):
            userFlags = fetchUserFlags(emailId)
            return formatResponse(True, userFlags)
        else:
            return formatResponse(True,errorCode=TOKEN_INVALID_ERROR_CODE, errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
    except Exception as e:
        logger.error("Exception ==>"+ str(e))
        return formatResponse(False, errorMessage=e)

@app.route("/uHaulRequest", methods=["POST"])
def uHaulRequest():
    try:
        requestBody = request.get_json()
        emailId = requestBody.get("email")
        token = requestBody.get("token")
        if userTokenValid(emailId, token):
            date = requestBody.get("date")
            time = requestBody.get("time")
            canDrive = requestBody.get("canDrive")
            startLocation = requestBody.get("startLocation")
            endLocation = requestBody.get("endLocation")
            if not uHaulRequestExists(emailId):
                makeUHaulRequest(emailId,date,time,canDrive,startLocation,endLocation, True)
                return formatResponse(True)
            else:
                makeUHaulRequest(emailId,date,time,canDrive,startLocation,endLocation, False)
                return formatResponse(True)
        else:
            return formatResponse(True,errorCode=TOKEN_INVALID_ERROR_CODE, errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
    except Exception as e:
        logger.error("Exception ==>"+ str(e))
        return formatResponse(False, errorMessage=e)

@app.route("/getAllUHaulRequests", methods=["POST"])
def getAllUHaulRequests():
    try:
        requestBody = request.get_json()
        emailId = requestBody.get("email")
        token = requestBody.get("token")
        if userTokenValid(emailId, token):
            date = requestBody.get("date")
            dayRangeStr = requestBody.get("dayRange")
            timeRange = 2 if not dayRangeStr else int(dayRangeStr)
            uHaulRequests = fetchAllUHaulRequests(dayRange, date, emailId)
            return formatResponse(True, {"data": uHaulRequests})
        else:
            return formatResponse(True,errorCode=TOKEN_INVALID_ERROR_CODE, errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
    except Exception as e:
        logger.error("Exception ==>"+ str(e))
        return formatResponse(False, errorMessage=e)
    
@app.route("/getMyUHaulOffers", methods=["POST"])
def getMyUHaulOffers():
    try:
        requestBody = request.get_json()
        emailId = requestBody.get("email")
        token = requestBody.get("token")
        if userTokenValid(emailId, token):
            uHaulRequestFound, uHaulOffers, pendingRequestDetails = fetchMyUHaulOffers(emailId)
            if uHaulRequestFound:
                return formatResponse(True, {"offers": uHaulOffers, "pendingRequestDetails": pendingRequestDetails })
            else:
                return formatResponse(True,errorCode=U_HAUL_REQUEST_NOT_FOUND_ERROR_CODE, errorMessage=U_HAUL_REQUEST_NOT_FOUND_ERROR_MESSAGE) 
        else:
            return formatResponse(True,errorCode=TOKEN_INVALID_ERROR_CODE, errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
    except Exception as e:
        logger.error("Exception ==>"+ str(e))
        return formatResponse(False, errorMessage=e)

if __name__ == "__main__":
    app.run(debug=True)