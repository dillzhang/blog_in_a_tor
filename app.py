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
            return render_template("home.html",username=username,loggedIn=True, status="Login Successful") #Successful Login
        else:
            return render_template("home.html", status="Login Failed") #Failed Login
    
    elif request.form["Submit"] == "create":
        username = request.form["username"]
        password = request.form["password"]
        confirm_passwd = request.form["confirm_password"]
        email = request.form["email"]
        error = utils.register_new_user(username, password, confirm_passwd, email)
        if (error == None):
            return render_template("home.html", status="Account Creation Successful") #Successful Account Creation
        else:
            return render_template("home.html", status="Account Creation Failed: " + error) #Failed Account Creation

        
@app.route("/blog/<postid>")
def blog(postid=0):
    if postid <= 0:
        return "<h1> 404 Error </h1>"
    else:
        return render_template("blog.html")

    
@app.route("/user/<username>", methods=["GET", "POST"])
def user(username=""):
    if username == "":
        return "<h1> 404 Error </h1>"
    elif request.method == "GET":
        prevposts = utils.get_user_posts(username)
        return render_template("user.html", username=username, posts=prevposts)
    elif request.method == "POST":
        return render_template("user.html")

    
if __name__ == "__main__":
    app.debug = True
    app.secret_key = utils.secret_key
    app.run(host="0.0.0.0", port=8000)
