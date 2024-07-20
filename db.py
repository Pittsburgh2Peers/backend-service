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
        tokenValid = isTokenValid(tokenData[1])
        if tokenValid:
            databaseConnection.close()
            return tokenData[0]
        else:
            userToken, tokenValidUntil = createToken()
            databaseCursor.execute("UPDATE users SET userToken = ?, tokenValidUntil = ? WHERE emailId = ?",(userToken, tokenValidUntil, emailId,))
            databaseConnection.commit()
            databaseConnection.close()
            return userToken
    else:
        raise Exception("User does not exist with emailId: " + emailId)
        
        