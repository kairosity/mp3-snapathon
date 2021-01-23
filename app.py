import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env 


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


def awards():
    #1. Identify all the photos entered into this week's competition.

    this_weeks_entries = list(mongo.db.photos.find({"week_and_year": datetime.now().strftime("%V%G") }) )
    
    #2. Identify all the user's who entered photos into this week's competition.
    this_weeks_usernames = []
    for img in this_weeks_entries:
        this_weeks_usernames.append(img["created_by"])

    this_weeks_users = []
    for username in this_weeks_usernames:
        this_weeks_users.append(mongo.db.users.find_one({"username": username}))

    #3. Make sure that those users actually voted. I.e. votes_to_use must be 0. 
    valid_users = []
    non_voters = []

    for user in this_weeks_users:
        if user["votes_to_use"] > 0:
            non_voters.append(user)
        else:
            valid_users.append(user)
    
    #4 Identify the non-voters' image entered & bring the image votes to 0. 

    for user in non_voters:
        mongo.db.photos.update_one({"created_by": user["username"]}, {'$set': {"photo_votes": 0}})

   
    #5. When all the valid entries are in an array - determine the 3 highest points scorers. 
    this_weeks_entries = list(mongo.db.photos.find( { '$query': {"week_and_year": datetime.now().strftime("%V%G")}, '$orderby': { 'photo_votes' : -1 } } ))

    list_of_votes = []

    for photo in this_weeks_entries:
        list_of_votes.append(photo["photo_votes"])

    # Determine the votes needed for 1st, 2nd & 3rd place. 
    first_place_vote_count = max(list_of_votes)
    second_place_vote_array = [n for n in list_of_votes if n!= first_place_vote_count]
    second_place_vote_count = max(second_place_vote_array)
    third_place_vote_array = [n for n in second_place_vote_array if n!= second_place_vote_count]
    third_place_vote_count = max(third_place_vote_array)

    #Determine which photos in this week's entries have those particular vote numbers and assign them awards. 

    for entry in this_weeks_entries:
        if entry["photo_votes"] == first_place_vote_count:
            mongo.db.photos.update_one({"filename": entry["filename"]}, {'$set': {"awards": "first"}})
        elif entry["photo_votes"] == second_place_vote_count:
            mongo.db.photos.update_one({"filename": entry["filename"]}, {'$set': {"awards": "second"}})
        elif entry["photo_votes"] == third_place_vote_count:
            mongo.db.photos.update_one({"filename": entry["filename"]}, {'$set': {"awards": "third"}})
            
awards()



    #7. Give the creator of the images the correct number of points. 

    #8. Take that images _id and give any user who has it in their photos_voted_for array the correct number of points. 

   
# scheduler = BackgroundScheduler()
# scheduler.add_job(scheduler_test, 'interval', minutes=1)
# scheduler.start()

def delete_collection():
    mongo.db.fs.chunks.remove({})


@app.context_processor
def inject_datetime():
    date_time = datetime.now()
    return dict(datetime=date_time)

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
            "password": generate_password_hash(request.form.get("password")),
            "votes": 0,
            "user_points": 0,
            "photos_entered": [],
            "photos_voted_for": []
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

    # grab the array of all the photo_ids this user has under their name 
    user = mongo.db.users.find_one({"username": username})
    user_photos = list(mongo.db.photos.find({"created_by": user["username"]}))

    '''
    Grabs the list of photo ids that this user has voted on & then 
    for each id it looks in the photos db for the image that matches 
    it and appends it to an array that we pass to the profile template.
    '''
    photos_voted_for_array = user["photos_voted_for"]
    photos_voted_for_objs = []

    for img in photos_voted_for_array:
        photo_obj = list(mongo.db.photos.find({"_id": img}))
        photos_voted_for_objs.append(photo_obj[0])

    return render_template("profile.html", username=username, user_photos=user_photos, user=user, photos_voted_for=photos_voted_for_objs)
    

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
    date_time = datetime.now()
   

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
            "created_by": session["user"],
            "date_entered": datetime.now(),
            "week_and_year": datetime.now().strftime("%V%G"),
            "file_id": file_id,
            "filename": new_filename,
            "photo_votes": 0
            }
            mongo.db.photos.insert_one(new_entry)

            # Get the photo obj's id and put in a variable? 
            photo_to_add_to_user = mongo.db.photos.find_one({"file_id": file_id})
            photo_id_to_add_to_user = photo_to_add_to_user["_id"]
          
            # Add the photo obj id into the user's photos array and give the user a vote.
            mongo.db.users.update_one({"_id": current_user["_id"]},
                                      {'$push':{"photos": photo_id_to_add_to_user},
                                       '$inc':{"votes_to_use": 1 }})
   
            flash("Entry Received!")
        
    # Returns a list of all photos entered "this" week and this year based on the week_and_year attribute.
    this_weeks_entries = list(mongo.db.photos.find({"week_and_year": date_time.strftime("%V%G")}))

    print(date_time.strftime("%H"))

    return render_template("compete.html", this_weeks_entries=this_weeks_entries, datetime=date_time)

@app.route("/file/<filename>")
def file(filename):
    return mongo.send_file(filename)

@app.route("/photos/<filename>", methods=["GET", "POST"])
def get_photo(filename):

    photo = mongo.db.photos.find_one({"filename": filename})
    user = mongo.db.users.find_one({"username": photo["created_by"]})
    
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
            "iso": request.form.get("iso").lower()
            }
        
        mongo.db.photos.update({"_id": photo["_id"]}, {"$set": edited_entry})
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


@app.route("/vote/<filename>", methods=["POST"])
def vote(filename):

    photo = mongo.db.photos.find_one({"filename": filename})

    if not session:
        flash("You must be logged in to vote.")
        return redirect(url_for("login"))

    if request.method == "POST":
        
        user_voting = mongo.db.users.find_one({"username": session["user"]})

        if user_voting["votes_to_use"] < 1:
            flash("Sorry, but you've already voted, you only have 1 vote.")
            return redirect(url_for("compete"))

         # Check that the photo does not belong to the user. If it does send the user a message that they cannot vote for their own photo.
        elif user_voting["username"] == photo["created_by"]:
            flash("You cannot vote for your own photos...obviously.")
            return redirect(url_for("compete"))

        else:
            # If it is not their photo:
            #1. Remove the user's vote 
            # #2. Place that image in the user's photos_voted_for array.
            mongo.db.users.update({"username": session["user"]},
                                    {'$inc':{"votes_to_use": -1}})

            mongo.db.users.update({"username": session["user"]},
                                    {'$push': {"photos_voted_for": photo["_id"]}})

            #3. Add a point to that photo's votes field. 
            mongo.db.photos.update_one({"_id": photo["_id"]},
                                      {'$inc': {"photo_votes": 1} })

            
            flash("Thank you for voting!")
            return redirect(url_for('compete', username=session['user']))
        

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
