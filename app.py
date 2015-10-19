from flask import Flask, render_template, request, session, redirect, url_for
import utils

app = Flask(__name__)


@app.route("/", methods = ["GET", "POST"])
@app.route("/home", methods = ["GET", "POST"])
def home():
    if request.method == "GET":
        if "username" in session and session["username"] != "":
            return render_template("home.html", username=session["username"], loggedIn=True)
        else:
            return render_template("home.html")
        
    elif request.form["Submit"] == "login":
        username = request.form["username"]
        password = request.form["password"]
        if ( utils.check_login_info(username, password) ):
            session["username"] = username
            return render_template("blog.html",username=username,loggedIn=True, status="Login Successful") #Successful Login
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

    elif session["username"] == "":
        return render_template("home.html", loggedIn = False, logout = True)

    
        
@app.route("/logout")
def logout():
    if "username" in session:
        session["username"] = ""
    return redirect(url_for("home"))

@app.route("/blog/<postid>", methods=["GET", "POST"])
def blog(postid):
    if postid <= 0:
        return "<h1> 404 Error </h1>"
    elif request.method == "GET":
        return render_template("blog.html", post=utils.get_post(postid), comments=utils.get_comments(postid))
    elif request.form["Submit"] == "Comment":
        utils.new_post(session["username"], comment)
        return redirect("/blog/" + postid)
)
    
@app.route("/editpost/<postid>", methods=["GET", "POST"])
def editpost(postid=-1):
    if postid < 0:
        return "<h1> 404 Error </h1>"
    elif request.method == "GET":
        return render_template("editpost.html", post=utils.get_post(postid))
    elif request.form["Submit"] == "Update":
        status = utils.modify_post(postid, request.form["post"])
        return redirect("/blog/"+postid)
    elif request.fomr["Submit"] == "Delete":
        utils.remove_post(postid)
        return redirect(url_for("home"))

    
@app.route("/editcomment/<commentid>", methods=["GET", "POST"])
def editcomment(commentid=-1):
    if commentid < 0:
        return "<h1> 404 Error </h1>"
    elif request.method == "GET":
        return render_template("editcomment.html", post=utils.get_comment(commentid))
    elif request.form["Submit"] == "Update":
        status = utils.modify_comment(commentid, request.form["comment"])
        return redirect(url_for("home"))
    elif request.form["Submit"] == "Delete":
        utils.remove_comment(commentid)
        return redirect(url_for("home"))

    
@app.route("/user/<username>", methods=["GET", "POST"])
def user(username=""):
    if username == "":
        return "<h1> 404 Error </h1>"
    elif request.method == "GET":
        prevposts = utils.get_user_posts(username)
        return render_template("user.html", username=username, posts=prevposts)
    elif request.form["Submit"] == "Change Password":
        status = utils.modify_password(username, request.form["password"], request.form["newpassowrd"], request.form["confirm_passwd"])
        if status != None:
            return render_template("user.html", status=status)
    elif request.form["Submit"] == "Change Email":
        status = utils.modify_email(username, request.form["password"], request.form["email"])
        if status != None:
            return render_template("user.html", status=status)
    elif request.form["Submit"] == "Post":
        utils.new_post(username, request.form["post"], request.form["heading"])
        return render_template("user.html")
    return render_template("user.html")

    
if __name__ == "__main__":
    app.debug = True
    app.secret_key = utils.secret_key
    app.run(host="0.0.0.0", port=8000)
