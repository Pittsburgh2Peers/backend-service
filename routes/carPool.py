from flask import request

import logging

from routes.common.constants import TOKEN_INVALID_ERROR_CODE, TOKEN_INVALID_ERROR_MESSAGE, \
    CAR_POOL_REQUEST_NOT_FOUND_ERROR_CODE, CAR_POOL_REQUEST_NOT_FOUND_ERROR_MESSAGE, \
    CAR_POOL_OFFER_MADE_TO_SELF_ERROR_CODE, CAR_POOL_OFFER_ALREADY_EXISTS_ERROR_CODE, \
    CAR_POOL_OFFER_ALREADY_EXISTS_ERROR_MESSAGE, CAR_POOL_OFFER_MADE_TO_SELF_ERROR_MESSAGE
from routes.common.utils import formatResponse
from routes.db.dbInteraction import userTokenValid, makeCarPoolRequest, fetchAllCarPoolRequests, offerCarPoolRequest, \
    carPoolRequestExists, fetchMyCarPoolOffers

logger = logging.getLogger(__name__)


def carPoolRoutes(app):
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
                    makeCarPoolRequest(emailId, date, time, noOfPassengers, noOfTrolleys, startLocation, endLocation,
                                       True)
                    return formatResponse(True)
                else:
                    makeCarPoolRequest(emailId, date, time, noOfPassengers, noOfTrolleys, startLocation, endLocation,
                                       False)
                    return formatResponse(True)
            else:
                return formatResponse(True, errorCode=TOKEN_INVALID_ERROR_CODE,
                                      errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
        except Exception as e:
            logger.error("Exception ==>" + str(e))
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
                timeRange = 3 if timeRangeStr == None else int(timeRangeStr)
                date = requestBody.get("date")
                carPoolRequests = fetchAllCarPoolRequests(startLocation, endLocation, time, timeRange, date, emailId)
                return formatResponse(True, {"data": carPoolRequests})
            else:
                return formatResponse(True, errorCode=TOKEN_INVALID_ERROR_CODE,
                                      errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
        except Exception as e:
            logger.error("Exception ==>" + str(e))
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
                        return formatResponse(True, errorCode=CAR_POOL_REQUEST_NOT_FOUND_ERROR_CODE,
                                              errorMessage=CAR_POOL_REQUEST_NOT_FOUND_ERROR_MESSAGE)
                    elif requestRaised == CAR_POOL_OFFER_MADE_TO_SELF_ERROR_CODE:
                        return formatResponse(True, errorCode=CAR_POOL_OFFER_MADE_TO_SELF_ERROR_CODE,
                                              errorMessage=CAR_POOL_OFFER_MADE_TO_SELF_ERROR_MESSAGE)
                    elif requestRaised == CAR_POOL_OFFER_ALREADY_EXISTS_ERROR_CODE:
                        return formatResponse(True, errorCode=CAR_POOL_OFFER_ALREADY_EXISTS_ERROR_CODE,
                                              errorMessage=CAR_POOL_OFFER_ALREADY_EXISTS_ERROR_MESSAGE)
                    else:
                        return formatResponse(False, errorMessage="Something Went Wrong")
            else:
                return formatResponse(True, errorCode=TOKEN_INVALID_ERROR_CODE,
                                      errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
        except Exception as e:
            logger.error("Exception ==>" + str(e))
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
                    return formatResponse(True,
                                          {"offers": carPoolOffers, "pendingRequestDetails": pendingRequestDetails})
                else:
                    return formatResponse(True, errorCode=CAR_POOL_REQUEST_NOT_FOUND_ERROR_CODE,
                                          errorMessage=CAR_POOL_REQUEST_NOT_FOUND_ERROR_MESSAGE)
            else:
                return formatResponse(True, errorCode=TOKEN_INVALID_ERROR_CODE,
                                      errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
        except Exception as e:
            logger.error("Exception ==>" + str(e))
            return formatResponse(False, errorMessage=e)
