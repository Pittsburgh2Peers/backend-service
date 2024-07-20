from flask import Flask, request
from flask_cors import CORS
from uuid import uuid4
from datetime import timedelta, date
from db import createUser, getToken
from common import formatResponse, createToken

app = Flask(__name__)

CORS(app)

@app.route("/registrationSuccess", methods=["POST"])
def registrationSuccess():
    try:
        requestBody = request.get_json()
        name = requestBody["name"]
        emailId = requestBody["email"]
        profileImage = requestBody["profileImage"]
        countryCode = requestBody["countryCode"]
        phoneNo = requestBody["phoneNo"]
        userToken, tokenValidUntil = createToken()
        data = { "token": userToken }
        createUser(name, emailId, profileImage, countryCode, phoneNo, userToken, tokenValidUntil)
        return formatResponse(True, data)
    except Exception as e:
        print("Exception ==>", e)
        return formatResponse(False, None)
    
@app.route("/generateToken", methods=["POST"])
def generateToken():
    try:
        requestBody = request.get_json()
        emailId = requestBody["email"]
        token = getToken(emailId)
        data = { "token": token }
        return formatResponse(True, data)
    except Exception as e:
        print("Exception ==>", e)
        return formatResponse(False, None)

if __name__ == "__main__":
    app.run(debug=True)