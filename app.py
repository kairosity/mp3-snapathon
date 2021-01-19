import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env 


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if email address already exists in db
        existing_email = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})
        existing_username = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_email:
            flash("Email is already registered.")
            return redirect(url_for('register'))
        
        if existing_username:
            flash("Username is already in use, please choose a different one.")
            return redirect(url_for('register'))
        
        # check if password fields match
        password1 = request.form.get("password")
        password2 = request.form.get("password-confirmation")

        if password1 != password2:
            flash("Passwords do not match, please try again.")
            return redirect(url_for('register'))

        register = {
            "username": request.form.get("username").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # puts the new user into a session
        session["user"] = request.form.get("email").lower()
        flash("Registration successful!")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # does username exist?
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            # ensure that the hashed password matches this input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("email").lower()
                flash("Welcome, {}!".format(existing_user["username"]))
            else:
                #invalid password hash
                flash("Incorrect username and/or password!")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect username and/or password!")
            return redirect(url_for("login"))

    return render_template("login.html")


# @app.route("/get_photos")
# def get_photos():
#     photos = mongo.db.photos.find()
#     return render_template("photos.html", photos=photos)

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
