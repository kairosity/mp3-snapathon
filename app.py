
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for,
    abort)
from flask_pymongo import PyMongo
# from flask.ext.wtf import Form, TextField, TextAreaField, SubmitField
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail, Message
import os
from bson.objectid import ObjectId
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date, time
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
if os.path.exists("env.py"):
    import env 



app = Flask(__name__)

csrf = CSRFProtect(app)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")
app.config['MAX_CONTENT_LENGTH'] = 750 * 750
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif', '.svg', '.jpeg']

mail_settings = {
    "MAIL_SERVER": os.environ.get('MAIL_SERVER'),
    "MAIL_PORT": os.environ.get('MAIL_PORT'),
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": os.environ.get('MAIL_USE_SSL'),
    "MAIL_USERNAME": os.environ.get('MAIL_USERNAME'),
    "MAIL_PASSWORD": os.environ.get('MAIL_PASSWORD'),
    "SECURITY_EMAIL_SENDER": os.environ.get("SECURITY_EMAIL_SENDER")
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
    
    #4 Identify the non-voters' image entered & bring the image votes to 0. & then bring their votes to use to 0 as well. 
    #This is filtered further to only target this week's image.
    for user in non_voters:
        mongo.db.photos.update_one({"created_by": user["username"], "week_and_year": datetime.now().strftime("%V%G") }, {'$set': {"photo_votes": 0}})
        mongo.db.users.update_one({"username": user["username"]},{'$set': {"votes_to_use": 0}})  

    
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
            mongo.db.photos.update_one({"filename": entry["filename"]}, {'$set': {"awards": 1}})
            user = mongo.db.users.find_one({"username": entry["created_by"]})

            if user not in first_place_users:
                first_place_users.append(user)
            photo = mongo.db.photos.find_one({"filename": entry["filename"]})
            if photo not in first_place_photos:
                first_place_photos.append(photo)
        elif entry["photo_votes"] == second_place_vote_count:
            mongo.db.photos.update_one({"filename": entry["filename"]}, {'$set': {"awards": 2}})
            user = mongo.db.users.find_one({"username": entry["created_by"]})

            if user not in second_place_users:
                second_place_users.append(user)
            photo = mongo.db.photos.find_one({"filename": entry["filename"]})
            if photo not in second_place_photos:
                second_place_photos.append(photo) 
        elif entry["photo_votes"] == third_place_vote_count:
            mongo.db.photos.update_one({"filename": entry["filename"]}, {'$set': {"awards": 3}})
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
                if photo_as_obj["awards"] == 1:
                    mongo.db.users.update_one({"username": user["username"]}, {'$inc': {"user_points": 3}})
                if photo_as_obj["awards"] == 2: 
                    mongo.db.users.update_one({"username": user["username"]}, {'$inc': {"user_points": 2}})
                if photo_as_obj["awards"] == 3:
                    mongo.db.users.update_one({"username": user["username"]}, {'$inc': {"user_points": 1}})
        
    print("Awards & points have been calculated and awarded.")

def new_comp():
    all_users = list(mongo.db.users.find())
    for user in all_users:
        mongo.db.users.update_one({"username": user["username"]}, {'$set': {"can_enter": True}})
    print("All users can now enter a new image in competition")


scheduler = BackgroundScheduler()
scheduler.add_job(awards, 'cron', day_of_week='sun', hour=22, minute=00, second=0, start_date='2021-01-24 00:00:00')
scheduler.add_job(new_comp, 'cron', day_of_week='mon', hour=00, minute=00, second=0, start_date='2021-01-24 00:00:00')
scheduler.start()

def delete_collection():
    mongo.db.fs.chunks.remove({})
    mongo.db.fs.files.remove({})
    mongo.db.photos.remove({})
    mongo.db.users.remove({})


@app.context_processor
def inject_datetime():
    date_time = datetime.now()
    return dict(datetime=date_time)


inject_datetime()


@app.route("/")
@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        with app.app_context():
            msg = Message(subject="New Email From Contact Form")
            msg.sender = request.form.get("email_of_sender")
            msg.recipients = [os.environ.get('MAIL_USERNAME')]
            message = request.form.get("message")
            msg.body = f"Email From: {msg.sender} \nMessage: {message}"
            mail.send(msg)
            flash("Email Sent!")
            return redirect(url_for('home'))

    return render_template("index.html")


@app.route("/recent_winners")
def recent_winners():

    # Get date & time
    today = datetime.now()
    day_of_week = today.weekday()
    hour_of_day = today.time().hour
    week_and_year = datetime.now().strftime("%V%G")

    week_before = today - timedelta(weeks=1)
    last_week_and_year = week_before.strftime("%V%G")


    def get_winning_images_by_week_and_year(w_a_y):
        return list(mongo.db.photos.find({"week_and_year": w_a_y} ))
    

    # If dow is Mon-Sat  Sun BEFORE 22:00PM:
    if day_of_week in range(0,5) or day_of_week == 6 and hour_of_day < 22:
        images_to_display = get_winning_images_by_week_and_year(last_week_and_year)
        last_mon = week_before
        while last_mon.weekday() != 0:
            last_mon = last_mon - timedelta(days=1)
    # If dow is sun and it's after 22:00
    else:
        images_to_display = get_winning_images_by_week_and_year(week_and_year)
        last_mon = today
        while last_mon.weekday() !=0:
            last_mon = today - timedelta(days=1)
    
    first_place = []
    second_place = []
    third_place = []

    list_of_users = []
    week_starting = last_mon.strftime("%A, %d of %B")

    for img in images_to_display:
        if img["awards"] == 1:
            first_place.append(img)
            list_of_users.append(mongo.db.users.find_one({"username": img["created_by"] }))
            competition_category = img["competition_category"]
        elif img["awards"] == 2:
            second_place.append(img)
            list_of_users.append(mongo.db.users.find_one({"username": img["created_by"] }))
        elif img["awards"] == 3:
            third_place.append(img)
            list_of_users.append(mongo.db.users.find_one({"username": img["created_by"] }))

    return render_template("recent_winners.html", first_place=first_place,
                                                  second_place=second_place,
                                                  third_place=third_place,
                                                  users=list_of_users,
                                                  week_starting=week_starting,
                                                  competition_category=competition_category)


@app.route("/browse", methods=["GET", "POST"])
def browse():

    all_photos = list(mongo.db.photos.find())

    return render_template("browse_images.html", photos=all_photos)

@app.route('/search', methods=["GET", "POST"])
def search():

    if request.method == 'POST':
        category = request.form.get("category")
        query = request.form.get("query")
        awards = [int(n) for n in request.form.getlist("award")] 
        
        full_search = query
        full_query = {}

        if query:
            full_query["$text"]={"$search": full_search}

        if awards:
             full_query["awards"]={"$in": awards}
            
        if category:
            full_query["competition_category"] = category
        
        filtered_photos = list(mongo.db.photos.find(full_query))

        source_url = request.referrer
        
        return render_template("browse_images.html", 
                                photos=filtered_photos, source_url=source_url)

        

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
        
        #If it is Mon-Friday can_enter = True If it is Sat or Sun it's False? Does it need to be False? 

        register = {
            "username": request.form.get("username").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "user_points": 0,
            "photos_entered": [],
            "photos_voted_for": [],
            "votes_to_use": 0,
            "can_enter": True
        }
        mongo.db.users.insert_one(register)

        # puts the new user into a session
        session["user"] = request.form.get("username").lower()
        flash("Registration successful!")

        username = session["user"]

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

    if photos_voted_for_array != []:
        for img in photos_voted_for_array:
            photo_obj = list(mongo.db.photos.find({"_id": img}))
            photos_voted_for_objs.append(photo_obj[0])
    else:
        print("This user has not voted for any images yet")
    award_winners = []
    for img in user_photos:
        if img["awards"] != None:
            award_winners.append(img)
    
    can_enter = user["can_enter"]
    votes_to_use = user["votes_to_use"]

    today = datetime.now().strftime('%Y-%m-%d')

    # Code from Emmanuel's Stack Overflow answer (attributed in README.md)
    def get_next_weekday(startdate, weekday):
        """
        @startdate: given date, in format '2013-05-25'
        @weekday: week day as a integer, between 0 (Monday) to 6 (Sunday)
        """
        d = datetime.strptime(startdate, '%Y-%m-%d')
        t = timedelta((7 + weekday - d.weekday()) % 7)
        date = d + t
        return date
    
    competition_ends = get_next_weekday(today, 5)
    next_competition_starts = get_next_weekday(today, 1)
    voting_ends = get_next_weekday(today, 7) - timedelta(hours=2)

    now = datetime.now()
    time_til_comp_ends = competition_ends - now
    time_til_voting_ends = voting_ends - now
    time_til_next_comp_starts = next_competition_starts - now
 
    def get_time_remaining_string(timedelta):
        days = timedelta.days 
        timedelta_string = str(timedelta)
        time_array = timedelta_string.split(",").pop().split(":")
        hours = time_array[0]
        minutes = time_array[1]
        final_time_string = f"{days} days,{hours} hours and {minutes} minutes"
        return final_time_string

    comp_closes = get_time_remaining_string(time_til_comp_ends)
    voting_closes = get_time_remaining_string(time_til_voting_ends)
    next_comp_starts = get_time_remaining_string(time_til_next_comp_starts)

    return render_template("profile.html",
                           username=username, user_photos=user_photos,
                           user=user, photos_voted_for=photos_voted_for_objs,
                           award_winners=award_winners,
                           can_enter=can_enter,
                           votes_to_use=votes_to_use,
                           comp_closes=comp_closes,
                           voting_closes=voting_closes,
                           next_comp_starts=next_comp_starts)
    


''' 
1. This function checks if there is a user logged in. 
2. If so, is that user trying to edit her own profile page?
3. If so, it checks if the request method is POST. 
4. If it is POST, it takes all the form data and saves it in variables.
5. It creates 2 empty dicts to store the data.
6. It checks if the user has changed their username.
7. If they have it checks to make sure that username is not already in use, as usernames must be unique. 
8. If it's not already used, it pushes the new username into both new dicts, as the new username will need to be saved not only 
to the user doc, but also to every photo that user has uploaded in the created_by field. 
9. The function then runs the same logic for the user email, but this only needs to be changed on the user doc. 
10. Then it checks if the user has entered something into the current password field.
11. Then it checks if that password is correct.
12. If it is the right password, it checks if she has entered anything into the new password field.
13. If she has, it checks if that is equal to the new password confirmation field. 
14. If all three password fields have been entered correctly it pushes the new password to the update_user dict using the Werkzeug 
password hash. 
15. Then it checks if there is anything in either of the new dicts. If they contain data, the function updates the Mongo DB with that 
new data.
16. If the user data has been changed it also sets the session["user"] to be the new username.
17. Then it returns the profile page, which will reflect any updates immediately. 
'''

@app.route("/edit_profile/<username>", methods=['GET', 'POST'])
def edit_profile(username):

    if session:
        if session["user"] == username:
            user = mongo.db.users.find_one({"username": username})
            if request.method == "POST":

                # values from form
                form_username = request.form.get("username").lower()
                form_email = request.form.get("email").lower()
                form_current_password = request.form.get("current_password")
                form_new_password = request.form.get("new_password")
                form_new_password_confirmation = request.form.get("new_password_confirmation")

                update_user = {}
                update_photos = {}

                # If the user has changed their username
                if form_username != user["username"]:
                    existing_username = mongo.db.users.find_one({"username": form_username})
                    if existing_username:
                        flash("Username is already in use, please choose a different one.")
                        return redirect(url_for('edit_profile', user=user, username=username))      
                    else:
                        update_user["username"] = form_username
                        update_photos["created_by"] = form_username

                # If the user has changed their email address        
                if form_email != user["email"]:
                    # check if email address already exists in db
                    existing_email = mongo.db.users.find_one({"email": form_email})
                    if existing_email:
                        flash("That email is already in use, please choose a different one.")
                        return redirect(url_for('edit_profile', user=user, username=username))
                    else:
                        update_user["email"] = form_email
                
                if form_current_password:
                    if check_password_hash(user["password"], request.form.get("current_password")):
                        if form_new_password != None:
                            if form_new_password == form_new_password_confirmation:
                                update_user["password"] = generate_password_hash(form_new_password)
                            else:
                                flash("Your new passwords do not match, please try again.")
                                return redirect(url_for('edit_profile', username=username))
                        else:
                            flash("Your new password cannot be nothing. Please try again.")

                    else: 
                        flash("Sorry, but your current password was entered incorrectly. Please try again.")
                        return redirect(url_for('edit_profile', user=user, username=username))
                
                if update_photos:
                    mongo.db.photos.update_many({"created_by": username}, {"$set": update_photos})
                if update_user:
                    mongo.db.users.update_one({"username": username}, {'$set': update_user})
                    session["user"] = form_username

                user = mongo.db.users.find_one({"username": session["user"]})
                user_photos = list(mongo.db.photos.find({"created_by": session["user"]}))
                photos_voted_for_array = user["photos_voted_for"]
                photos_voted_for_objs = []

                if photos_voted_for_array != []:
                    for img in photos_voted_for_array:
                        photo_obj = list(mongo.db.photos.find({"_id": img}))
                        photos_voted_for_objs.append(photo_obj[0])
                flash("Profile updated successfully!")
                return render_template('profile.html', user=user, user_photos=user_photos, photos_voted_for=photos_voted_for_objs)

            source_url = request.referrer

            return render_template('edit_profile.html', user=user, source_url=source_url)

        else:
            flash("Sorry, but you cannot edit another user's profile.")
            return redirect(url_for('home'))

    else:
        return redirect(url_for('login'))
        flash("You must be logged in to edit your profile.")


@app.route("/compete", methods=['GET', 'POST'])
def compete():
    '''
    If the method is POST
    1. Grab the file that was uploaded & store it in a var called photo.
    2. Make sure that the uploaded file is an acceptable file type. Reject it if it's not. 
    3. Nullify any malicious filenames using werkzeug.
    4. Save that image to mongodb using gridfs at the same time store the file id
    into a var called file_id.
    5. Create a new_filename using the new file's '_id' attribute making the filename unique - add the original extension to that.
    6. Update the gridFS's filename attr to equal that new file id.
    7. Select the current user and save it into a var called current_user
    8. Create a new_entry dict with the data from the form and current_user & the file_id
    9. Add that dict entry into the photos collection.
    10. Get that photo object's id using the file_id. 
    11. Save that photo object's id into the current user object's photo's array.
    '''
    date_time = datetime.now()

    competitions = [
        {
            "category": "portraiture",
            "instructions": "Enter your portraits now! These can be of animals or humans and can be close up or full length. They should communicate something substantial about the subject."
        },
        {
            "category": "landscape",
            "instructions": "Enter your lanscapes now! These should be primarily focused on the natural world. No city-scapes. Focus on delivering images with great lighting in interesting locations."
        },
        {
            "category": "architecture",
            "instructions": "Enter your architectural photos now! Interesting angles and great composition is key here."
        }
        ]      

    def get_competition(week_number):
        if week_number % 3 == 1:
            return competitions[0]
        elif week_number % 3 == 2:
            return competitions[1]
        elif week_number % 3 == 0:
            return competitions[2]

    current_week_number = int(datetime.now().strftime("%V"))

    this_weeks_comp_category = get_competition(current_week_number)["category"]
    this_weeks_comp_instructions = get_competition(current_week_number)["instructions"]

    if request.method == 'POST':

        current_user = mongo.db.users.find_one(
                {"username": session["user"]})
        
        if current_user["can_enter"] == True:

            if 'photo' in request.files:
                photo = request.files['photo']

                # To make sure that the file type is one of the acceptable image file types
                file_extension = os.path.splitext(photo.filename)[1]
                if file_extension not in app.config['UPLOAD_EXTENSIONS']:
                    abort(400, "Sorry that file extension is not allowed. Please re-format your image to one of the following acceptable file types: jpg, svg, jpeg, png or gif")

                # A werkzeug util method for securing potentially malicious filenames - has to happen before the save.
                photo.filename = secure_filename(photo.filename)

                # Upload the photo to the gridfs mongo storage
                file_id = mongo.save_file(photo.filename, photo)

                # This makes the filename unique 
                new_filename = str(file_id) + file_extension

                # Update the gridFS "Filename" attribute to be equal to the file_id
                mongo.db.fs.files.update_one({"_id": file_id},
                                        { '$set': {"filename": new_filename}})


                new_entry = {
                "file_id": file_id,
                "filename": new_filename,
                "photo_title": request.form.get("title").lower(),
                "photo_story": request.form.get("story").lower(),
                "camera": request.form.get("camera").lower(),
                "lens": request.form.get("lens").lower(),
                "aperture": request.form.get("aperture").lower(),
                "shutter": request.form.get("shutter").lower(),
                "iso": request.form.get("iso").lower(),
                "created_by": session["user"],
                "date_entered": datetime.now(),
                "competition_category": this_weeks_comp_category,
                "week_and_year": datetime.now().strftime("%V%G"),
                "photo_votes": 0,
                "awards": None
                }
                mongo.db.photos.insert_one(new_entry)

                # Get the photo obj's id and put in a variable? 
                photo_to_add_to_user = mongo.db.photos.find_one({"file_id": file_id})
                photo_filename_to_add_to_user = photo_to_add_to_user["filename"]
                
                # Add the photo obj id into the user's photos array and give the user a vote.
                # Set can_enter to false
                mongo.db.users.update_one({"_id": current_user["_id"]},
                                            {'$push':{"photos": photo_filename_to_add_to_user},
                                            '$inc':{"votes_to_use": 1 },
                                            '$set':{"can_enter": False }})

                flash("Entry Received!")
        else:
            flash("I'm sorry, but you've already entered an image in this week's competition!")
    # Returns a list of all photos entered "this" week and this year based on the week_and_year attribute.
    this_weeks_entries = list(mongo.db.photos.find({"week_and_year": date_time.strftime("%V%G")}))


    return render_template("compete.html", this_weeks_entries=this_weeks_entries, datetime=date_time, category=this_weeks_comp_category, instructions=this_weeks_comp_instructions)

@app.route("/file/<filename>")
def file(filename):
    return mongo.send_file(filename)

@app.route("/photos/<filename>", methods=["GET", "POST"])
def get_photo(filename):

    source_url = request.referrer

    photo = mongo.db.photos.find_one({"filename": filename})
    user = mongo.db.users.find_one({"username": photo["created_by"]})
     
    username = user["username"]
    
    return render_template("get_photo.html", photo=photo, username=username, source_url=source_url)


@app.route("/edit_photo/<filename>", methods=["GET", "POST"])
def edit_photo(filename):

    # Add a rule that you have to be logged in to reach this page.

    photo = mongo.db.photos.find_one({"filename": filename})
    user = mongo.db.users.find_one({"username": photo["created_by"]})

    username = user["username"]

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
        return render_template("edit_photo.html", photo=photo)
    else:
        flash("You need to be logged in to edit photos.")
        return redirect(url_for("login"))


@app.route("/delete_photo/<filename>")
def delete_photo(filename):

    if session:
        photo_to_del = mongo.db.photos.find_one({"filename": filename})
        if session["user"] == photo_to_del["created_by"]:
            file_to_delete = mongo.db.fs.files.find_one({"filename": filename})
            chunks_to_delete = list(mongo.db.fs.chunks.find({"files_id": file_to_delete["_id"]}))
            
            # Remove the photo obj associated with this pic
            mongo.db.photos.delete_one({"filename": filename})
            # Remove the GridFS file associated with this filename
            mongo.db.fs.files.delete_one(file_to_delete)
            # Remove the GridFS chunk(s) associated with this filename
            for chunk in chunks_to_delete:
                mongo.db.fs.chunks.delete_one(chunk)
            # Remove this filename from the user photos array
            user = mongo.db.users.find_one({"username": session["user"]})
            user_photos = user["photos"]

            for photo in user_photos:
                if photo == filename:
                    mongo.db.users.update_one({"username": session["user"]}, {'$pull': {"photos": photo}})

            flash("Photograph deleted successfully!")
            return redirect(url_for('profile', username=session["user"]))
        else:
            flash("You may not delete another user's photo.")
            return redirect(url_for('home'))
    # Why is the below not working?
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
