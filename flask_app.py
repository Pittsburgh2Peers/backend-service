from flask import Flask
from flask_cors import CORS

from routes.admin import adminRoutes
from routes.user import userRoutes
from routes.carPool import carPoolRoutes
from routes.uHaul import uHaulRoutes

app = Flask(__name__)

CORS(app)

userRoutes(app)
carPoolRoutes(app)
adminRoutes(app)
uHaulRoutes(app)

if __name__ == "__main__":
    app.run(debug=True)