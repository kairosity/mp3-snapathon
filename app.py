
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for,
    abort, jsonify)
from flask_pymongo import PyMongo, pymongo
from helpers import *
from flask_paginate import Pagination, get_page_args
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
    '''
    * This function automatically calculates photo awards and user points from
      the votes the competition entries have received.
      It is run automatically using AP Scheduler on Sunday Evening at 22:00PM.

    \n Args:
       None.

    \n Returns (updates db):
    * Resets the photo_points for invalid entries to 0.
    * Calculates & assigns points to each user who won a 1st, 2nd or 3rd
      placement.
    * Updates the db photo objs for photos that won 1st, 2nd or 3rd.
    * Calculates & assigns points to each user who voted for a photo that
      came 1st, 2nd or 3rd.
    '''
    #This needs to change to # datetime.now().strftime("%V%G")
    this_week_and_year_formatted = "052021"
    this_weeks_entries = list(mongo.db.photos.find(
        {"week_and_year": this_week_and_year_formatted}))

    this_weeks_users = get_this_weeks_comp_users(this_weeks_entries, mongo)

    valid_users = filter_users_and_exclude_non_voters(this_weeks_users, mongo, this_week_and_year_formatted)

    range_of_votes = get_range_of_scores(this_week_and_year_formatted, mongo)
 
    first_place_vote_count, second_place_vote_count, third_place_vote_count = awards_score_requirements(range_of_votes)

    first_place_users, second_place_users, third_place_users = determine_winners(first_place_vote_count, second_place_vote_count, third_place_vote_count, this_weeks_entries, mongo)
    
    add_points_to_winning_users(first_place_users, second_place_users, third_place_users, mongo)
    
    add_points_to_users_who_voted_well(valid_users, this_week_and_year_formatted, mongo)
    
    print("Awards & points have been calculated and awarded.")

# awards()

# Development Testing Functions
# clear_user_points(mongo)
# clear_all_awards(mongo)
# clear_all_photo_votes(mongo)


'''
These are the scheduled functions:
1. awards() runs automatically on Sunday at 22:00PM
2. new_comp() runs automatically on Monday at 0:00AM
'''
scheduler = BackgroundScheduler()
scheduler.add_job(awards, 'cron', day_of_week='sun',
                  hour=22, minute=00, second=0,
                  start_date='2021-01-24 00:00:00')
scheduler.add_job(new_comp, 'cron', [mongo], day_of_week='wed',
                  hour=00, minute=00, second=0,
                  start_date='2021-01-24 00:00:00')
scheduler.start()


@app.context_processor
def inject_datetime():
    '''
    This context processor function allows all templates to access the current
    datetime.now() using the var datetime.
    '''
    date_time = datetime.now()
    return dict(datetime=date_time)


inject_datetime()


@app.route("/")
@app.route("/home", methods=["GET", "POST"])
def home():
    '''
    * Displays homepage template & allows user to send email.

    \n Args:
    1. User inputs (str): email and message from contact form.

    \n Returns:
    * Template displaying the homepage
    * POST method sends SNAPATHON an email from the user.
    '''
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


@app.route("/recent-winners")
def recent_winners():
    '''
    * This gets a list of the most recent competition award-winning images
      and passes them to the 'winners' template, alongside information about
      when the last competition was held and what the theme was.

    \n Args: None.

    \n Returns:
    * Template displaying the most recent award-winning photographs and info
      about when that competition was held and what its' theme was.
    '''

    competition_category = \
        "There was no competition last week, \
            and therefore there are no recent winners."

    images_to_display, last_mon = \
        get_last_monday_and_images(mongo, get_images_by_week_and_year)

    week_starting = last_mon.strftime("%A, %d of %B")

    first_place, second_place, third_place, \
        list_of_users, competition_category = \
        first_second_third_place_compcat_users(
            images_to_display, mongo)

    return render_template("recent_winners.html",
                           first_place=first_place,
                           second_place=second_place,
                           third_place=third_place,
                           users=list_of_users,
                           week_starting=week_starting,
                           competition_category=competition_category)


@app.route("/browse")
def browse():
    '''
    * Fetches all the photos entered into the competition from all time
      and paginates them for quicker loading times.

    \n Args: None

    \n Returns:
    * Template displaying all the images to the user, paginated.
    '''

    all_photos = list(mongo.db.photos.find())

    pagination, photos_paginated = paginated_and_pagination_args(
                                   all_photos, 10, "page", "per_page")

    return render_template("browse_images.html",
                           photos=photos_paginated,
                           pagination=pagination)


@app.route('/search')
def search():
    '''
    * Takes the user inputed search query and filters back images that
      match the criterion.
    
    \n Args:
    1. query (str): User input from the search form.

    \n Returns:
    * Renders an array of paginated and filtered photo objects that match
      the search criterion on the browse template.
    '''
    source_url = request.referrer

    category = request.args.get("category")
    query = request.args.get("query")
    awards = [int(n) for n in request.args.getlist("award")]

    filtered_photos = filter_user_search(category, query, awards, mongo)

    pagination, photos_paginated = paginated_and_pagination_args(
                                   filtered_photos, 10, "page", "per_page")

    if not filtered_photos:
        flash("I'm sorry, but your search did not return any images.")

    return render_template("browse_images.html",
                           photos=photos_paginated,
                           pagination=pagination,
                           source_url=source_url)


@app.route("/register", methods=["GET", "POST"])
def register():
    '''
    * GET request displays the registration page for new users.
      POST request registers a new user using data received
      from a registration form.

    \n Args:
    1. user inputs (str): email, username, password taken in from
       the registration form.

    \n Returns:
    * If GET: Renders the registration template.
    * If POST registration is successful, it inserts a new user into the db.
    * Logs the new user in and creates a new session for that
      user.
    * Redirects that user to their new profile page template.
    * If registration is unsuccessfuly the register template is
      reloaded with flash messages detailing why.
    '''

    if request.method == "POST":
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

        password1 = request.form.get("password")
        password2 = request.form.get("password-confirmation")

        if password1 != password2:
            flash("Passwords do not match, please try again.")
            return redirect(url_for('register'))

        register_user = {
            "username": request.form.get("username").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "user_points": 0,
            "photos_entered": [],
            "photos_voted_for": [],
            "votes_to_use": 0,
            "can_enter": True
        }
        mongo.db.users.insert_one(register_user)

        session["user"] = request.form.get("username").lower()
        flash("Registration successful!")
        username = session["user"]

        return redirect(url_for("profile", username=username))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    '''
    * GET request returns the login page.
      POST request logs the user in if inputed credentials match
      db records.

    \n Args:
    1. user inputs (str): email & password taken in from
       the login form.

    \n Returns:
    * If GET: Renders the login template.
    * If POST: succesful, then logs the user in, creates a new
      session and redirects the user to their profile page.
    * IF POST: unsuccessful, then displays a flash message to the
      user to tell them why, and reloads the login template.
    '''
    if request.method == "POST":
        email = request.form.get("email").lower()
        password = request.form.get("password")
        url = login_user(email, password, mongo)
        return url

    return render_template("login.html")

@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    '''
    * Displays a user's profile page, with extra features if it belongs
      to the user themself.

    \n Args:
    1. username (str): The specific username registered to a user in
       the db.

    \n Returns:
    * The user's profile template, complete with all their competition entries,
      all the photos that user has voted for and all that user's award-
      winning photos, displayed in three different sections.
    * If the user is logged in and viewing their own profile page, they
      will see an 'edit profile' button, as well as information about the next
      stage of the competition and links to bring them to the compete or
      vote templates.
    '''
    user_photos, photos_voted_for_objs, award_winners = \
        get_profile_page_photos(username, mongo)

    user = mongo.db.users.find_one({"username": username})
    can_enter = user["can_enter"]
    votes_to_use = user["votes_to_use"]

    today = datetime.now().strftime('%Y-%m-%d')

    competition_ends = get_next_weekday(today, 5)
    next_competition_starts = get_next_weekday(today, 1)
    voting_ends = get_next_weekday(today, 7) - timedelta(hours=2)

    comp_closes, voting_closes, next_comp_starts = \
        time_strings_for_template(
                competition_ends, next_competition_starts,
                voting_ends, get_time_remaining_string)

    return render_template("profile.html",
                           username=username,
                           user=user,
                           user_photos=user_photos,
                           photos_voted_for=photos_voted_for_objs,
                           award_winners=award_winners,
                           can_enter=can_enter,
                           votes_to_use=votes_to_use,
                           comp_closes=comp_closes,
                           voting_closes=voting_closes,
                           next_comp_starts=next_comp_starts)


@app.route("/edit-profile/<username>", methods=['GET', 'POST'])
def edit_profile(username):
    '''
    * GET renders the edit-profile template form if the username passed
      to the request matches the user currently logged in. If it doesn't,
      the user is shown a flash message explaining the issue. POST allows
      a user to edit their profile and save the changes, with a link to an
      option to completely delete their account.

    \n Args:
    1. username (str): The specific username registered to a user in
       the db.
    2. user inputs (str): Username, email, current password & new password
       taken in via the edit-profile form.

    \n Returns:
    * GET renders the edit-profile template if the user is logged in & requesting
      their own page. Otherwise it renders an error page with a flash message
      outlining the issue.
    * POST: If the form is submitted successfully and user details changed, this 
      updates the db with the new user data and then renders the user's profile 
      with the updated details. If unsuccessful, this

    '''
    if session:
        if session["user"] == username:
            user = mongo.db.users.find_one({"username": username})
            if request.method == "POST":

                form_username = request.form.get("username").lower()
                form_email = request.form.get("email").lower()
                form_current_password = request.form.get("current_password")
                form_new_password = request.form.get("new_password")
                form_new_password_confirmation = \
                    request.form.get("new_password_confirmation")

                url = edit_user_profile(
                    user, username, form_username, form_email,
                    form_current_password, form_new_password,
                    form_new_password_confirmation, mongo)

                return url

            source_url = request.referrer

            return render_template(
                'edit_profile.html', user=user, source_url=source_url)

        else:
            flash("You cannot edit someone else's account...obvz!")
            abort(403)

    else:
        flash("You must be logged in to edit your\
             account, and obviously, you are not allowed \
             to edit someone else's account!")
        abort(403)


@app.route('/delete-account/<username>', methods=['GET', 'POST'])
def delete_account(username):

    if request.method == "POST":
       
        #This mucks up a bit because the session cookie lingers. Consider removing this and just leaving if session["user"] == username? 
        # Same issue above with edit_profile. 
        if session:
            if session["user"] == username:
                user = mongo.db.users.find_one({"username": username})
                all_photos = list(mongo.db.photos.find())

                #form vars
                form_password = request.form.get("password")
                form_password_confirmation = request.form.get("password_confirmation")

                # Security check first - user must enter her password twice in order to delete account. (Modal window with two password fields and a confirm button)
                if form_password:
                    if check_password_hash(user["password"], form_password):
                        if form_password == form_password_confirmation:
                            #1.Delete all this user's photos (files & chunks) from the mongo DB

                            if len(user["photos"]) > 0:
                                for photo in user["photos"]:
                                    # Remove the photo obj associated with this pic
                                    mongo.db.photos.delete_one({"filename": photo})
                                    # Target the GridFS file associated with this filename
                                    file_to_delete = mongo.db.fs.files.find_one({"filename": photo})
                                    # Target the Chunks associated with this files_id
                                    chunks_to_delete = list(mongo.db.fs.chunks.find({"files_id": file_to_delete["_id"]}))
                                    # Delete the file
                                    mongo.db.fs.files.delete_one(file_to_delete)

                                    if len(chunks_to_delete) > 0:
                                        # Delete the GridFS chunk(s) associated with this filename
                                        for chunk in chunks_to_delete:
                                            mongo.db.fs.chunks.delete_one(chunk)

                            
                            #3. Delete the user from the DB.
                            mongo.db.users.delete_one({"username": user["username"]})

                            #2. Pop the session. (There is still a session - why?)
                            session.pop("user", None)

                            flash("Account & photos deleted successfully, we're sorry to see you go. Come back to us any time!")
                            return redirect(url_for('home'))

                        else:
                            flash("Incorrect password. Please try again.")
                            return redirect(url_for('edit_profile', username=username))
                    else:
                        flash("Incorrect password. Please try again.")
                        return redirect(url_for('edit_profile', username=username))
                else:
                    flash("You must enter your password in order to delete your account. This is a security measure.")
                    return redirect(url_for('edit_profile', username=username))
    else:
        flash("You must be logged in to delete your account, and obviously, you are not allowed to delete someone else's account!")
        abort(403)



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
        },
        {
            "category": "wildlife",
            "instructions": "Enter your wildlife and nature photos now. Flora OR fauna are acceptable. Capture amazing images of the natural world at its most spectacular."
        },
        {
            "category": "street",
            "instructions": "Enter your street photography now. Encounters and imagery from urban jungles."
        },
        {
            "category": "monochrome",
            "instructions": "Enter your monochrome photography now. Any subject, any place, black and white imagery only. PLEASE no sepia tones!"
        },
        {
            "category": "event",
            "instructions": "Enter your event photography now. Weddings, baptisms, concerts, theatre etc.. If it has guests, it's an event!"
        }
        ]      

    def get_competition(week_number):
        if week_number % 7 == 0:
            return competitions[0]
        elif week_number % 7 == 1:
            return competitions[5]
        elif week_number % 7 == 2:
            return competitions[2]
        elif week_number % 7 == 3:
            return competitions[3]
        elif week_number % 7 == 4:
            return competitions[4]
        elif week_number % 7 == 5:
            return competitions[1]
        elif week_number % 7 == 6:
            return competitions[6]
    
    

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
                    abort(415)

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

    pagination, photos_paginated = paginated_and_pagination_args(this_weeks_entries, 10, "page", "per_page")



    return render_template("compete.html", this_weeks_entries=photos_paginated, 
                                           datetime=date_time, 
                                           category=this_weeks_comp_category, 
                                           instructions=this_weeks_comp_instructions,
                                           pagination=pagination)

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

            # If the photo to delete has won the user points, we need to remove those points when that image is deleted.
            if photo_to_del["awards"] == 1:
                mongo.db.users.update_one({"username": session["user"]}, {'$inc': {"user_points": -7}})
            elif photo_to_del["awards"] == 2:
                mongo.db.users.update_one({"username": session["user"]}, {'$inc': {"user_points": -5}})
            elif photo_to_del["awards"] == 3:
                mongo.db.users.update_one({"username": session["user"]}, {'$inc': {"user_points": -3}})
            
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
    session.pop("user", None)
    
    return redirect(url_for("login"))


@app.errorhandler(404)
def page_not_found(e):
    print(e)
    error = 404
    error_msg = "I'm sorry, we've searched everywhere, but the page you are looking for does not exist."
    return render_template('error.html', error=error, error_msg=error_msg), 404


@app.errorhandler(500)
def internal_server_error(e):
    error = 500
    error_msg = "We're so sorry! There's been an internal server error. It's not you, it's definitely us, but maybe try again later?"
    return render_template('error.html', error=error, error_msg=error_msg), 500


@app.errorhandler(403)
def forbidden_error(e):
    error = 403
    error_msg = "I actually can't believe you tried to do that. Totally Forbidden, sorry."
    return render_template('error.html', error=error, error_msg=error_msg), 403

#The print statement is working, but the template is not rendering? Not sure why. 

@app.errorhandler(413)
def payload_too_large(e):
    print(f"This specific error is: {e}")
    error = 413
    error_msg = "Sorry, but the file you're trying to upload is too large. If you are entering the competition, please have a look at the file size guidelines in the rules section. Thanks!"
    print(error_msg)
    return render_template('error.html', error=error, error_msg=error_msg), 413


@app.errorhandler(415)
def unsupported_media_type(e):
    print(f"Error:{e}")
    error = 415
    error_msg = "Sorry, but the file you're trying to upload is an unsupported file type. We only accept .jpg, .jpeg, .gif, .svg or .png files. Thanks!"
    return render_template('error.html', error=error, error_msg=error_msg), 415


@app.errorhandler(408)
def request_timeout(e):
    print(e)
    error = 408
    error_msg = "Sorry, but the server timed out waiting for the request. You might try again."
    return render_template('error.html', error=error, error_msg=error_msg), 408


#Check this works. This works - it just looks really boring. 
# @app.errorhandler(Exception)
# def all_other_exceptions(e):
#     return f"Something went wrong! Specifically: {e}"


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
