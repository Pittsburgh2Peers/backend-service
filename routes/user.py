import re

from flask import request

import logging

from routes.common.constants import TOKEN_INVALID_ERROR_CODE, TOKEN_INVALID_ERROR_MESSAGE, USER_NOT_FOUND_ERROR_CODE, \
    USER_NOT_FOUND_ERROR_MESSAGE
from routes.common.utils import createToken, formatResponse
from routes.db.dbInteraction import getToken, userTokenValid, isProfileComplete, updateUserProfileDetails, \
    fetchUserDetails, fetchUserFlags, createUser

logger = logging.getLogger(__name__)

def userRoutes(app):
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
            data = {"token": userToken}
            createUser(name, emailId, profileImage, countryCode, phoneNo, userToken, tokenValidUntil)
            return formatResponse(True, data)
        except Exception as e:
            logger.error("Exception ==>" + str(e))
            return formatResponse(False, errorMessage=e)

    @app.route("/generateToken", methods=["POST"])
    def generateToken():
        try:
            requestBody = request.get_json()
            emailId = requestBody.get("email")
            token = getToken(emailId)
            data = {"token": token}
            return formatResponse(True, data)
        except Exception as e:
            logger.error("Exception ==>" + str(e))
            return formatResponse(False, errorMessage=str(e))

    @app.route("/userProfileComplete", methods=["POST"])
    def userProfileComplete():
        try:
            requestBody = request.get_json()
            emailId = requestBody.get("email")
            token = requestBody.get("token")
            if userTokenValid(emailId, token):
                profileComplete = isProfileComplete(emailId)
                data = {"eligible": profileComplete}
                return formatResponse(True, data)
            else:
                return formatResponse(True, errorCode=TOKEN_INVALID_ERROR_CODE,
                                      errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
        except Exception as e:
            logger.error("Exception ==>" + str(e))
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
                updateUserProfileDetails(emailId, name, phoneNo, countryCode)
                return formatResponse(True)
            else:
                return formatResponse(True, errorCode=TOKEN_INVALID_ERROR_CODE,
                                      errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
        except Exception as e:
            logger.error("Exception ==>" + str(e))
            return formatResponse(False, errorMessage=e)

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
                    return formatResponse(True, errorCode=USER_NOT_FOUND_ERROR_CODE,
                                          errorMessage=USER_NOT_FOUND_ERROR_MESSAGE)
            else:
                return formatResponse(True, errorCode=TOKEN_INVALID_ERROR_CODE,
                                      errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
        except Exception as e:
            logger.error("Exception ==>" + str(e))
            return formatResponse(False, errorMessage=e)

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
                return formatResponse(True, errorCode=TOKEN_INVALID_ERROR_CODE,
                                      errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
        except Exception as e:
            logger.error("Exception ==>" + str(e))
            return formatResponse(False, errorMessage=e)
