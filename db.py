import sqlite3
import os
from common import createToken, isTokenValid, getTimeFrame
from constants import CAR_POOL_REQUEST_NOT_FOUND_ERROR_CODE, CAR_POOL_OFFER_MADE_TO_SELF_ERROR_CODE, CAR_POOL_OFFER_ALREADY_EXISTS_ERROR_CODE
from datetime import datetime

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
databaseLocation = os.path.join(THIS_FOLDER, 'database.db')

def createUser(name, emailId, profileImage, countryCode, phoneNo, userToken, tokenValidUntil):
    databaseConnection = sqlite3.connect(databaseLocation)
    databaseCursor = databaseConnection.cursor()
    databaseCursor.execute("INSERT INTO users(name, emailId, profileImage, countryCode, phoneNo, userToken, tokenValidUntil) VALUES(?,?,?,?,?,?,?)",(name, emailId, profileImage, countryCode, phoneNo, userToken, tokenValidUntil))
    databaseConnection.commit()
    databaseConnection.close()
    return
    
def getToken(emailId):
    databaseConnection = sqlite3.connect(databaseLocation)
    databaseCursor = databaseConnection.cursor()
    tokenData = databaseCursor.execute("SELECT userToken, tokenValidUntil FROM users WHERE emailId = ?",(emailId,)).fetchone()
    if tokenData is not None:
        if isTokenValid(tokenData[1]):
            databaseConnection.close()
            return tokenData[0]
        else:
            userToken, tokenValidUntil = createToken()
            databaseCursor.execute("UPDATE users SET userToken = ?, tokenValidUntil = ? WHERE emailId = ?",(userToken, tokenValidUntil, emailId))
            databaseConnection.commit()
            databaseConnection.close()
            return userToken
    else:
        databaseConnection.close()
        raise Exception("User does not exist with emailId: " + emailId)

def userTokenValid(emailId, token):
    databaseConnection = sqlite3.connect(databaseLocation)
    databaseCursor = databaseConnection.cursor()
    tokenData = databaseCursor.execute("SELECT userToken, tokenValidUntil FROM users WHERE emailId = ?", (emailId,)).fetchone()
    if tokenData is not None:
        if token == tokenData[0]:
            if isTokenValid(tokenData[1]):
                databaseConnection.close()
                return True
            else:
                databaseConnection.close()
                return False
        else:
            databaseConnection.close()
            return False
    else:
        databaseConnection.close()
        raise Exception("User does not exist with emailId: " + emailId)

def isProfileComplete(emailId):
    databaseConnection = sqlite3.connect(databaseLocation)
    databaseCursor = databaseConnection.cursor()
    userData = databaseCursor.execute("SELECT phoneNo, countryCode FROM users WHERE emailId = ?",(emailId,)).fetchone()
    if userData is not None:
        databaseConnection.close()
        if userData[0] and userData[1]:
            return True
        else:
            return False
    else:
        raise Exception("User does not exist with emailId: " + emailId)
    
def deleteAllUsersFromDb():
    databaseConnection = sqlite3.connect(databaseLocation)
    databaseCursor = databaseConnection.cursor()
    databaseCursor.execute("DELETE FROM users")
    databaseConnection.commit()
    databaseConnection.close()
    return

def updateUserProfileDetails(emailId,name,phoneNo,countryCode):
    databaseConnection = sqlite3.connect(databaseLocation)
    databaseCursor = databaseConnection.cursor()
    if name:
        databaseCursor.execute("UPDATE users SET name = ? WHERE emailId = ?",(name, emailId))
    if phoneNo:
        databaseCursor.execute("UPDATE users SET phoneNo = ? WHERE emailId = ?",(phoneNo, emailId))
    if countryCode:
        databaseCursor.execute("UPDATE users SET countryCode = ? WHERE emailId = ?",(countryCode, emailId))
    databaseConnection.commit()
    databaseConnection.close()
    return

def makeCarPoolRequest(emailId,date,time,noOfPassengers,noOfTrolleys,startLocation,endLocation, newRequest):
    time = (datetime.strptime(time, '%H:%M').time()).strftime('%H:%M')
    databaseConnection = sqlite3.connect(databaseLocation)
    databaseCursor = databaseConnection.cursor()
    if newRequest:
        databaseCursor.execute("INSERT INTO carPoolRequests(emailId,date,time,noOfPassengers,noOfTrolleys,startLocation,endLocation) VALUES(?,?,?,?,?,?,?)",(emailId,date,time,noOfPassengers,noOfTrolleys,startLocation,endLocation))
    else:
        databaseCursor.execute("UPDATE carPoolRequests SET date = ?, time = ?, noOfPassengers = ?, noOfTrolleys = ?, startLocation = ?, endLocation = ? WHERE emailId = ?",(date,time,noOfPassengers,noOfTrolleys,startLocation,endLocation,emailId))
    databaseConnection.commit()
    databaseConnection.close()
    return

def carPoolRequestExists(emailId):
    databaseConnection = sqlite3.connect(databaseLocation)
    databaseCursor = databaseConnection.cursor()
    userData = databaseCursor.execute("SELECT * FROM carPoolRequests WHERE emailId = ?",(emailId,)).fetchone()
    if userData is not None:
        databaseConnection.close()
        return True
    else:
        databaseConnection.close()
        return False
    
def fetchAllCarPoolRequests(startLocation, endLocation, time, timeRange, date, emailId):
    databaseConnection = sqlite3.connect(databaseLocation)
    databaseCursor = databaseConnection.cursor()
    lowerLimitTime = "00:00"
    upperLimitTime = "23:59"
    if time is not None:
        lowerLimitTime, upperLimitTime = getTimeFrame(time, timeRange)
    if endLocation is not None:
        requestData = databaseCursor.execute("SELECT * FROM carPoolRequests WHERE emailId != ? AND date = ? AND startLocation = ? AND endLocation = ? AND time BETWEEN ? AND ? ",(emailId, date, startLocation, endLocation, lowerLimitTime, upperLimitTime)).fetchall()
    else:
        requestData = databaseCursor.execute("SELECT * FROM carPoolRequests WHERE emailId != ? AND date = ? AND startLocation = ? AND time BETWEEN ? AND ?",(emailId, date, startLocation, lowerLimitTime, upperLimitTime)).fetchall()
    allCarPoolRequests = []
    for request in requestData:
        userDetails = databaseCursor.execute("SELECT countryCode,phoneNo,name FROM users WHERE emailId = ?", (request[1],)).fetchone()
        requestDict = {
            "requestId": str(request[0]),
            "date": request[2],
            "time": request[3],
            "noOfPassengers": request[4],
            "noOfTrolleys": request[5],
            "startLocation": request[6],
            "endLocation": request[7],
            "phoneNo": userDetails[0] + userDetails[1],
            "name" : userDetails[2]
        }
        allCarPoolRequests.append(requestDict)
    databaseConnection.close()
    return allCarPoolRequests
    
def offerCarPoolRequest(emailId, carPoolId, carType):
    databaseConnection = sqlite3.connect(databaseLocation)
    databaseCursor = databaseConnection.cursor()
    carPoolData = databaseCursor.execute("SELECT * FROM carPoolRequests WHERE requestId = ?",(carPoolId,)).fetchone()
    if carPoolData is not None:
        if carPoolData[1] == emailId:
            databaseConnection.close()
            return CAR_POOL_OFFER_MADE_TO_SELF_ERROR_CODE
        else:
            offerAlreadyExistsData = databaseCursor.execute("SELECT * FROM carPoolOffers WHERE requestId = ? AND emailId = ?",(carPoolId, emailId)).fetchone()
            if offerAlreadyExistsData is not None:
                databaseConnection.close()
                return CAR_POOL_OFFER_ALREADY_EXISTS_ERROR_CODE
            databaseCursor.execute("INSERT INTO carPoolOffers(emailId,carType, requestId) VALUES(?,?,?)",(emailId, carType, carPoolId))
            carPoolOfferId = databaseCursor.execute("SELECT seq FROM sqlite_sequence WHERE name = 'carPoolOffers'").fetchone()[0]
            existingCarPoolOfferIds = databaseCursor.execute("SELECT offerIds FROM carPoolRequests WHERE requestId = ?",(carPoolId,)).fetchone()
            if existingCarPoolOfferIds is not None and existingCarPoolOfferIds[0] is not None and existingCarPoolOfferIds[0] != "":
                offerIds = existingCarPoolOfferIds[0]
                offerIds = offerIds + "," + str(carPoolOfferId)
                databaseCursor.execute("UPDATE carPoolRequests SET offerIds = ? WHERE requestId = ?", (offerIds, carPoolId))
                databaseConnection.commit()
            else:
                databaseCursor.execute("UPDATE carPoolRequests SET offerIds = ? WHERE requestId = ?", (str(carPoolOfferId), carPoolId))
                databaseConnection.commit()
            databaseConnection.close()
            return True
    else:
        databaseConnection.close()
        return CAR_POOL_REQUEST_NOT_FOUND_ERROR_CODE
    
def fetchMyCarPoolOffers(emailId):
    databaseConnection = sqlite3.connect(databaseLocation)
    databaseCursor = databaseConnection.cursor()
    carPoolRequestDetails = databaseCursor.execute("SELECT * FROM carPoolRequests WHERE emailId = ?", (emailId,)).fetchone()
    if carPoolRequestDetails is None:
        databaseConnection.close()
        return False, None, None
    else:
        carPoolOffers = databaseCursor.execute("SELECT * FROM carPoolOffers WHERE requestId = ?",(str(carPoolRequestDetails[0]),)).fetchall()
        offers = []
        for offer in carPoolOffers:
            offerDict = {
                "offerId": str(offer[0]),
                "nameOfPerson": databaseCursor.execute("SELECT name FROM users WHERE emailId = ?", (offer[1],)).fetchone()[0],
                "carType": offer[2]
            }
            offers.append(offerDict)
        databaseConnection.close()
        pendingRequestDetails = {
            "requestId": str(carPoolRequestDetails[0]),
            "date": carPoolRequestDetails[2],
            "time": carPoolRequestDetails[3],
            "noOfPassengers": carPoolRequestDetails[4],
            "noOfTrolleys": carPoolRequestDetails[5],
            "startLocation": carPoolRequestDetails[6],
            "endLocation": carPoolRequestDetails[7]
        }
        return True, offers, pendingRequestDetails
    
def fetchUserDetails(emailId):
    databaseConnection = sqlite3.connect(databaseLocation)
    databaseCursor = databaseConnection.cursor()
    userDetails = databaseCursor.execute("SELECT name,profileImage,verified,accessProvided,phoneNo,countryCode FROM users WHERE emailId = ?", (emailId,)).fetchone()
    if userDetails is None:
        databaseConnection.close()
        return None
    else:
        databaseConnection.close()
        return {
            "name": userDetails[0],
            "profileImage": userDetails[1],
            "verified": True if userDetails[2] == "Y" else False,
            "accessProvided": True if userDetails[3] == "Y" else False,
            "phoneNo": userDetails[4],
            "countryCode": userDetails[5]
        }
        
def getAllUsers():
    databaseConnection = sqlite3.connect(databaseLocation)
    databaseCursor = databaseConnection.cursor()
    users = databaseCursor.execute("SELECT name FROM users").fetchall()
    print(users)
    databaseConnection.close()
    return users 