from flask import Flask, render_template, request, session, redirect, urlfor
import utils

app = Flask(__name__)

@app.route("/", methods = ["GET", "POST"])
@app.route("/home", methods = ["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("home.html")
    else if request.form["submit"] == "login":
        username = request.form["username"]
        password = request.form["password"]
        if ( utils.check_login_info(username, password) ):
            return render_template("home.html") #Successful Login
        else:
            return render_template("home.html") #Failed Login
    
    else if request.form["submit"] == "create":
        username = request.form["username"]
        password = request.form["password"]
        confirm_passwd = request.form["confirm_password"]
        email = request.form["email"]
        error = utils.register_new_user(username, password, confirm_password, email)
        if (error = None):
            return render_template("home.html") #Successful Account Creation
        else:
            return render_template("home.html") #Failed Account Creation

@app.route("/blog/<postid>")
def blog(postid=0):
    if postid <= 0:
        #404 Error
    else:
        #Find the post and its comments

@app.route("/user/<userid>", methods = ["GET", "POST"])
def user(userid=0):
    if userid <= 0:
        #404 Error
    else if request.method == "GET":
        #Find the user's information
    else if request.method == "POST":
        #Process Form
