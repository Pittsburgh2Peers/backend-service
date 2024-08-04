from flask import render_template

from routes.db.dbInteraction import getAllUsers, getCarPoolRequests, getUHaulRequests

def adminRoutes(app):
    @app.route("/adminDashboard")
    def adminDashboard():
        userData = getAllUsers()
        carPoolData = getCarPoolRequests()
        uHaulData = getUHaulRequests()
        return render_template("adminDashboard.html", userCount=len(userData), carPoolCount=len(carPoolData),
                               uHaulCount=len(uHaulData))
