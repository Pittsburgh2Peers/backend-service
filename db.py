import sqlite3
import os
from common import createToken, isTokenValid

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