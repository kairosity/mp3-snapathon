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
        session["user"] = request.form.get("username").lower()
        flash("Registration successful!")

        username = session["user"]
        print(username)

        return redirect(url_for("profile", username=username))
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
                    username = existing_user["username"]
                    session["user"] = username
                    flash(f"Welcome, {username}!")
                    return redirect(url_for("profile", username=username))
            else:
                # invalid password hash
                flash("Incorrect username and/or password!")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect username and/or password!")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    '''
    The session variable stores the email address because that's
    what the user logs in with. This uses that to return the
    username which we will use to return the profile page.
    '''

    # grab the array of all the photo_ids this user has under their name 
    current_user = mongo.db.users.find_one({"username": username})
    user_photos = list(mongo.db.photos.find({"created_by": current_user["_id"]}))
    return render_template("profile.html", username=username, user_photos=user_photos)
    

@app.route("/compete", methods=['GET', 'POST'])
def compete():
    '''
    If the method is POST
    1. Grab the file that was uploaded & store it in a var called photo.
    2. Save that image to mongodb using gridfs at the same time store the file id
    into a var called file_id.
    3. Select the current user and save it into a var called current_user
    4. Create a new_entry dict with the data from the form and current_user & the file_id
    5. Add that dict entry into the photos collection.
    6. Get that photo object's id using the file_id. 
    7. Save that photo object's id into the current user object's photo's array.
    '''
    if request.method == 'POST':
        if 'photo' in request.files:
            photo = request.files['photo']

            # Upload the photo to the gridfs mongo storage
            file_id = mongo.save_file(photo.filename, photo)

            filename_suffix = photo.filename[-4:]
            new_filename = str(file_id) + filename_suffix

             # Update the gridFS "Filename" attribute to be equal to the file_id
            mongo.db.fs.files.update_one({"_id": file_id},
                                    { '$set': {"filename": new_filename}})

            current_user = mongo.db.users.find_one(
                {"username": session["user"]})

            new_entry = {
            "photo_title": request.form.get("title").lower(),
            "photo_story": request.form.get("story").lower(),
            "camera": request.form.get("camera").lower(),
            "lens": request.form.get("lens").lower(),
            "aperture": request.form.get("aperture").lower(),
            "shutter": request.form.get("shutter").lower(),
            "iso": request.form.get("iso").lower(),
            "created_by": current_user["_id"],
            "file_id": file_id,
            "filename": new_filename
            }
            mongo.db.photos.insert_one(new_entry)

            # Get the photo obj's id and put in a variable? 
            photo_to_add_to_user = mongo.db.photos.find_one({"file_id": file_id})
            photo_id_to_add_to_user = photo_to_add_to_user["_id"]
          
            # Add the photo obj id into the user's photos array
            mongo.db.users.update_one({"_id": current_user["_id"]},
                                  { '$push':{"photos": photo_id_to_add_to_user}})
   
            flash("Entry Received!")

    return render_template("compete.html")

@app.route("/file/<filename>")
def file(filename):
    return mongo.send_file(filename)

@app.route("/photos/<filename>", methods=["GET", "POST"])
def get_photo(filename):

    photo = mongo.db.photos.find_one({"filename": filename})
    user = mongo.db.users.find_one({"_id": photo["created_by"]})
    
    return render_template("get_photo.html", photo=photo, user=user)


@app.route("/edit_photo/<filename>", methods=["GET", "POST"])
def edit_photo(filename):

    # Add a rule that you have to be logged in to reach this page.

    photo = mongo.db.photos.find_one({"filename": filename})
    user = mongo.db.users.find_one({"_id": photo["created_by"]})

    if request.method == "POST":

        edited_entry = {
            "photo_title": request.form.get("title").lower(),
            "photo_story": request.form.get("story").lower(),
            "camera": request.form.get("camera").lower(),
            "lens": request.form.get("lens").lower(),
            "aperture": request.form.get("aperture").lower(),
            "shutter": request.form.get("shutter").lower(),
            "iso": request.form.get("iso").lower(),
            "created_by": user["_id"],
            "file_id": photo["file_id"],
            "filename": filename
            }
        
        mongo.db.photos.update({"_id": photo["_id"]}, edited_entry)
        flash("Photo details edited successfully!")
        return redirect(url_for("get_photo", filename=filename))

    if session:
        return render_template("edit_photo.html", photo=photo, user=user)
    else:
        flash("You need to be logged in to edit photos.")
        return redirect(url_for("login"))


@app.route("/delete_photo/<filename>")
def delete_photo(filename):

    if session: 
        file_to_delete = mongo.db.fs.files.find_one({"filename": filename})
        chunk_to_delete = mongo.db.fs.chunks.find_one({"files_id": file_to_delete["_id"]})
        
        # Remove the photo obj associated with this pic
        mongo.db.photos.delete_one({"filename": filename})
        # Remove the GridFS file associated with this filename
        mongo.db.fs.files.delete_one(file_to_delete)
        # Remove the GridFS chunk(s) associated with this filename
        mongo.db.fs.chunks.delete_one(chunk_to_delete)
       
        flash("Photograph deleted successfully!")
        return redirect(url_for('profile', username=session["user"]))
    else:
        flash("Sorry, you must be logged in to delete a photograph.")
        return redirect(url_for('login'))

@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You've been logged out")
    session.pop("user")
    
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
