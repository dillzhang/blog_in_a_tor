from flask import Flask, render_template, request, session, redirect, url_for
import utils

app = Flask(__name__)

@app.route("/", methods = ["GET", "POST"])
@app.route("/home", methods = ["GET", "POST"])
def home():
    if request.method == "GET":
        uname = None
        if "username" in session:
            uname = session["username"]
        return render_template("home.html")
    elif request.form["Submit"] == "login":
        username = request.form["username"]
        password = request.form["password"]
        if ( utils.check_login_info(username, password) ):
            session["username"] = username
            return render_template("home.html",username=uname,loggedIn=True) #Successful Login
        else:
            return render_template("home.html") #Failed Login
    
    elif request.form["Submit"] == "create":
        username = request.form["username"]
        password = request.form["password"]
        confirm_passwd = request.form["confirm_password"]
        email = request.form["email"]
        error = utils.register_new_user(username, password, confirm_passwd, email)
        if (error == None):
            return render_template("home.html") #Successful Account Creation
        else:
            return render_template("home.html") #Failed Account Creation
"""
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
    elif request.method == "GET":
        #Find the user's information
    elif request.method == "POST":
        #Process Form
"""
if __name__ == "__main__":
       app.debug = True
       app.secret_key = utils.secret_key
       app.run(host="0.0.0.0", port=8000)
