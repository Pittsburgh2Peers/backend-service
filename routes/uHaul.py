from flask import request

import logging

from routes.common.constants import TOKEN_INVALID_ERROR_CODE, TOKEN_INVALID_ERROR_MESSAGE, \
    U_HAUL_REQUEST_NOT_FOUND_ERROR_CODE, U_HAUL_REQUEST_NOT_FOUND_ERROR_MESSAGE
from routes.common.utils import formatResponse
from routes.db.dbInteraction import uHaulRequestExists, userTokenValid, makeUHaulRequest, fetchAllUHaulRequests, \
    fetchMyUHaulOffers

logger = logging.getLogger(__name__)


def uHaulRoutes(app):
    @app.route("/uHaulRequest", methods=["POST", "PUT"])
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
                    makeUHaulRequest(emailId, date, time, canDrive, startLocation, endLocation, True)
                    return formatResponse(True)
                else:
                    makeUHaulRequest(emailId, date, time, canDrive, startLocation, endLocation, False)
                    return formatResponse(True)
            else:
                return formatResponse(True, errorCode=TOKEN_INVALID_ERROR_CODE,
                                      errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
        except Exception as e:
            logger.error("Exception ==>" + str(e))
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
                dayRange = 2 if not dayRangeStr else int(dayRangeStr)
                uHaulRequests = fetchAllUHaulRequests(dayRange, date, emailId)
                return formatResponse(True, {"data": uHaulRequests})
            else:
                return formatResponse(True, errorCode=TOKEN_INVALID_ERROR_CODE,
                                      errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
        except Exception as e:
            logger.error("Exception ==>" + str(e))
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
                    return formatResponse(True, {"offers": uHaulOffers, "pendingRequestDetails": pendingRequestDetails})
                else:
                    return formatResponse(True, errorCode=U_HAUL_REQUEST_NOT_FOUND_ERROR_CODE,
                                          errorMessage=U_HAUL_REQUEST_NOT_FOUND_ERROR_MESSAGE)
            else:
                return formatResponse(True, errorCode=TOKEN_INVALID_ERROR_CODE,
                                      errorMessage=TOKEN_INVALID_ERROR_MESSAGE)
        except Exception as e:
            logger.error("Exception ==>" + str(e))
            return formatResponse(False, errorMessage=e)
