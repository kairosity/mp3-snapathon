
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
# from flask.ext.wtf import Form, TextField, TextAreaField, SubmitField
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail, Message
import os
from bson.objectid import ObjectId
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env 



app = Flask(__name__)

csrf = CSRFProtect(app)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mail_settings = {
    "MAIL_SERVER": os.environ.get('MAIL_SERVER'),
    "MAIL_PORT": os.environ.get('MAIL_PORT'),
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": os.environ.get('MAIL_USE_SSL'),
    "MAIL_USERNAME": os.environ.get('MAIL_USERNAME'),
    "MAIL_DEFAULT_SENDER": os.environ.get("MAIL_DEFAULT_SENDER"),
    "MAIL_PASSWORD": os.environ.get('MAIL_PASSWORD')
}

app.config.update(mail_settings)
mail = Mail(app)
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
    #This is filtered further to only target this week's image.
    for user in non_voters:
        mongo.db.photos.update_one({"created_by": user["username"], "week_and_year": datetime.now().strftime("%V%G") }, {'$set': {"photo_votes": 0}})

    
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
    first_place_users =[]
    second_place_users = []
    third_place_users = []
    first_place_photos = []
    second_place_photos = []
    third_place_photos = []

    for entry in this_weeks_entries:
        if entry["photo_votes"] == first_place_vote_count:
            mongo.db.photos.update_one({"filename": entry["filename"]}, {'$set': {"awards": "first"}})
            user = mongo.db.users.find_one({"username": entry["created_by"]})

            if user not in first_place_users:
                first_place_users.append(user)
            photo = mongo.db.photos.find_one({"filename": entry["filename"]})
            if photo not in first_place_photos:
                first_place_photos.append(photo)
        elif entry["photo_votes"] == second_place_vote_count:
            mongo.db.photos.update_one({"filename": entry["filename"]}, {'$set': {"awards": "second"}})
            user = mongo.db.users.find_one({"username": entry["created_by"]})

            if user not in second_place_users:
                second_place_users.append(user)
            photo = mongo.db.photos.find_one({"filename": entry["filename"]})
            if photo not in second_place_photos:
                second_place_photos.append(photo) 
        elif entry["photo_votes"] == third_place_vote_count:
            mongo.db.photos.update_one({"filename": entry["filename"]}, {'$set': {"awards": "third"}})
            user = mongo.db.users.find_one({"username":entry["created_by"]})

            if user not in third_place_users:
                third_place_users.append(user)
            photo = mongo.db.photos.find_one({"filename": entry["filename"]})
            if photo not in third_place_photos:
                third_place_photos.append(photo)
        

    #7. Give the creator of the images the correct number of points.   
    for user in first_place_users:
        mongo.db.users.update_one({"username": user["username"]}, {'$inc': {"user_points": 7}})
    
    for user in second_place_users:
        mongo.db.users.update_one({"username": user["username"]}, {'$inc': {"user_points": 5}})
    
    for user in third_place_users:
        mongo.db.users.update_one({"username": user["username"]}, {'$inc': {"user_points": 3}})

    #8 Assign points to users for voting for 1st, 2nd & 3rd images. 

    for user in valid_users:
        for photo in user["photos_voted_for"]:
            #translate that photo id to a photo object. 
            photo_as_obj = list(mongo.db.photos.find({"_id": photo})) 
            if photo_as_obj:
                photo_as_obj = photo_as_obj[0]
                if photo_as_obj["awards"] == "first":
                    mongo.db.users.update_one({"username": user["username"]}, {'$inc': {"user_points": 3}})
                if photo_as_obj["awards"] == "second": 
                    mongo.db.users.update_one({"username": user["username"]}, {'$inc': {"user_points": 2}})
                if photo_as_obj["awards"] == "third":
                    mongo.db.users.update_one({"username": user["username"]}, {'$inc': {"user_points": 1}})
        
    print("This was run with APSheduler!")

   
scheduler = BackgroundScheduler()
scheduler.add_job(awards, 'cron', day_of_week='sun', hour=22, minute=00, second=0, start_date='2021-01-24 00:00:00')
scheduler.start()

def delete_collection():
    mongo.db.fs.chunks.remove({})


@app.context_processor
def inject_datetime():
    date_time = datetime.now()
    return dict(datetime=date_time)

@app.route("/")
@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "POST":
            with app.app_context():
                msg = Message(subject="New Email From Contact Form")
                msg.sender=request.form.get("email_of_sender")
                msg.recipients=[os.environ.get('MAIL_USERNAME')]
                message = request.form.get("message")
                msg.body=f"Sender: {msg.sender} \n Message: {message}"
                print(msg)
                mail.send(msg)
                flash("Email Sent!")
                return redirect(url_for('home'))

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
            "user_points": 0,
            "photos_entered": [],
            "photos_voted_for": [],
            "votes_to_use": 0
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

    print(photos_voted_for_array)
    if photos_voted_for_array != []:
        for img in photos_voted_for_array:
            photo_obj = list(mongo.db.photos.find({"_id": img}))
            photos_voted_for_objs.append(photo_obj[0])
    else:
        print("This user has not voted for any images yet")

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

    source_url = request.referrer
    print(source_url)

    photo = mongo.db.photos.find_one({"filename": filename})
    user = mongo.db.users.find_one({"username": photo["created_by"]})
    
    return render_template("get_photo.html", photo=photo, user=user, source_url=source_url)


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
            flash("Sorry, but you don't have any votes to use. You've either already voted, or you did not enter this week's competition.")
            return redirect(url_for("compete"))

         # Check that the photo does not belong to the user. If it does send the user a message that they cannot vote for their own photo.
        elif user_voting["username"] == photo["created_by"]:
            flash(" Sorry, but you cannot vote for your own photo... obviously.")
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
