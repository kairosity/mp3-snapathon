
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


# datetime.now().strftime("%V%G")

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



def delete_collection():
    '''
    This function deletes the entire mongoDB collection.
    It is only used for testing.
    '''
    mongo.db.fs.chunks.remove({})
    mongo.db.fs.files.remove({})
    mongo.db.photos.remove({})
    mongo.db.users.remove({})



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
    - Renders landing page

    - "POST" takes message from email form &
    - Creates a new Message object populated with that data.
    - Sends that message to Snapathon's email (set in MAIL_SETTINGS dict).
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


@app.route("/recent_winners")
def recent_winners():
    '''
    - Gets current date, time, weekday & hour & gets current week_and_year.
    - Calculates what the  week_and_year was last week.
    - Function defined to find all images by their week_and_year field.
    - Conditional: If it is Mon-Sat OR Sun before 22:00, then the above
      function is run using LAST week - to get the last competition's
      images & to get the date of LAST Monday (when that competition started).
    - If it is Sunday after 22:00 then the current week_and_year is used and
      last monday refers to the Monday just passed.
    - Once the correct week_and_year is established those images that won
      awards are placed in award-specific arrays to be passed to the "recent
      winners" template alongside the competition category.
    '''
    # Get date & time
    today = datetime.now()
    day_of_week = today.weekday()
    hour_of_day = today.time().hour
    week_and_year = datetime.now().strftime("%V%G")

    week_before = today - timedelta(weeks=1)
    last_week_and_year = week_before.strftime("%V%G")

    competition_category = "There was no competition last week, and therefore there are no recent winners."

    def get_images_by_week_and_year(w_a_y):
        winning_images = list(mongo.db.photos.find({"week_and_year": w_a_y}))
        return winning_images

    if day_of_week in range(0, 6) or day_of_week == 6 and hour_of_day < 22:
        images_to_display = get_images_by_week_and_year(last_week_and_year)
        last_mon = week_before
        while last_mon.weekday() != 0:
            last_mon = last_mon - timedelta(days=1)
    else:
        images_to_display = get_images_by_week_and_year(week_and_year)
        last_mon = today
        while last_mon.weekday() != 0:
            last_mon = last_mon - timedelta(days=1)

    first_place = []
    second_place = []
    third_place = []

    list_of_users = []
    week_starting = last_mon.strftime("%A, %d of %B")

    for img in images_to_display:
        if img["awards"] == 1:
            first_place.append(img)
            list_of_users.append(mongo.db.users.find_one(
                                {"username": img["created_by"]}))
            competition_category = img["competition_category"]
        elif img["awards"] == 2:
            second_place.append(img)
            list_of_users.append(mongo.db.users.find_one(
                                {"username": img["created_by"]}))
            competition_category = img["competition_category"]
        elif img["awards"] == 3:
            third_place.append(img)
            list_of_users.append(mongo.db.users.find_one(
                                {"username": img["created_by"]}))
            competition_category = img["competition_category"]

    return render_template("recent_winners.html",
                           first_place=first_place,
                           second_place=second_place,
                           third_place=third_place,
                           users=list_of_users,
                           week_starting=week_starting,
                           competition_category=competition_category)


def paginated_and_pagination_args(
        photos_arr, PER_PAGE, page_param, per_page_param):

    '''
    - Unpacks the get_page_args into "page" & 2 unused vars.
    - Sets offset manually using per_page & page.
    - Sets total to be the length of the photos array.
    - Creates a Pagination object with all the required args
      & stores in "pagination_args".
    - Creates a var that takes the array of photos given to the func
      as an arg and splits it into the correct sized chunk using
      offset & PER_PAGE.
    - Returns the two latter vars.
    '''

    page, _, _, = get_page_args(page_parameter=page_param, per_page_parameter=per_page_param)

    offset = page * PER_PAGE - PER_PAGE
    total = len(photos_arr)

    pagination_args = Pagination(page=page,
                                 per_page=PER_PAGE,
                                 total=total,
                                 page_parameter=page_param,
                                 per_page_parameter=per_page_param)

    photos_to_display = photos_arr[offset: offset + PER_PAGE]

    return pagination_args, photos_to_display


@app.route("/browse")
def browse():

    '''
    - Finds all photos in the DB
    - Runs the pagination func and saves the return values into 2 vars.
    - Passes those vars to the browse template to paginate the results.
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
    Takes the user inputted search query and finds images that
      match the criterion.
    - Sets a request referrer var.
    - Sets 3 vars to take in the user's search query.
    - Sets vars (full_search & full_query) to use to optionally chain
      the other filters.
    - Sets 3 conditionals to build a full search query with.
    - Returns the filtered_photos using the results of the constructed
      query.
    - Runs the pagination func and saves the return values into 2 vars.
    - If the filtered search returns no images - displays a msg to the user.
    - Renders the results of the search query to the browse template. Passing
      through the paginated & filtered photos, the pagination args & the source
      url.
    '''
    source_url = request.referrer

    category = request.args.get("category")
    query = request.args.get("query")
    awards = [int(n) for n in request.args.getlist("award")]

    full_search = query
    full_query = {}

    if query:
        full_query["$text"] = {"$search": full_search}

    if awards:
        full_query["awards"] = {"$in": awards}

    if category:
        full_query["competition_category"] = category

    filtered_photos = list(mongo.db.photos.find(full_query))

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
    The GET request returns the registration page.
    The POST request registers a new user.
    - Checks if the email already exists in the db.
    - Checks if the username already exists in the db.
    - If they exist returns a msg to user.
    - Checks if passwords match, if they do...
    - Creates the register dict with required user fields.
    - Inserts the register var into the db.
    - Creates a new session for the user based on username.
    - Redirects the new user to their new profile page.
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

        session["user"] = request.form.get("username").lower()
        flash("Registration successful!")
        username = session["user"]

        return redirect(url_for("profile", username=username))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    '''
    GET returns login page.
    POST logs the user in.
    - Checks to see if the username entered exists.
    - If it does, checks to see if the (hashed) password is the
      same as the password just entered in the form.
    - If it is correct, creates a session for that user and
      redirects them to their profile page with user access.
    - If the password is incorrect or the username doesn't exist
      it reloads the login page.
    '''
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                username = existing_user["username"]
                session["user"] = username
                flash(f"Welcome, {username}!")
                return redirect(url_for("profile", username=username))
            else:
                flash("Incorrect username and/or password!")
                return redirect(url_for("login"))
        else:
            flash("Incorrect username and/or password!")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):

    '''
    Returns a user's profile page, with extra access if it belongs
    to the user herself.
    - Finds the user based on the username passed to the url.
    - Finds a list of photos created by that user.
    - Finds a list of photo ids that this user has voted on.
    - For each id it looks in the photo db and finds the image itself.
    - If that image was NOT entered this week (i.e. the current competition):
    - Then it puts that image in an array to return to the template.
    - It creates an array of all the images created by this user that have
      won awards.
    - Function defined that takes a date and returns the next of a specific
      weekday (mon, tues etc..).
    - Three vars are declared that use this func:
      1. The next Friday (when the competition ends).
      2. The next Monday (when the next competition starts).
      3. Then next Sunday at 22:00PM (when voting ends).
    - Three more variables are then used to determine the timedeltas
      between "now" and when those other vars occur.
    - Another function is declared to take in these timedeltas as args
      and it returns a final time string stating when these events will occur
      in terms of how many days, hours etc.. are left.
    - These strings are then saved into 3 more vars which are passed
      to the template alongside the other important vars to display the profile.
    '''
    user = mongo.db.users.find_one({"username": username})
    user_photos = list(mongo.db.photos.find({"created_by": user["username"]}))

    photos_voted_for_array = user["photos_voted_for"]
    photos_voted_for_objs = []

    if photos_voted_for_array != []:
        for img in photos_voted_for_array:
            photo_obj = list(mongo.db.photos.find({"_id": img}))
            for photo in photo_obj:
                if photo["week_and_year"] != datetime.now().strftime("%V%G"):
                    photos_voted_for_objs.append(photo)
    else:
        # Maybe put a msg in the template to that effect?
        print("This user has not voted for any images yet")
    award_winners = []
    for img in user_photos:
        if img["awards"] is not None:
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
        final_date = d + t
        return final_date

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


@app.route("/edit_profile/<username>", methods=['GET', 'POST'])
def edit_profile(username):
    '''
    GET renders the edit_profile template form.
    - Checks to see if there is a session and if the session user is the
      same as the user being edited.
    - If so, allows the edit_profile form to be viewed.
    POST allows a user to edit their profile and save the changes, with an
    option to completely delete their account.
    - Stores form data into vars & creates 2 empty dicts.
    - Checks to see if the user is trying to change their username.
    - If they are, it checks to make sure that username is not already
      in use as usernames must be unique.
    - If it's not already used, it pushes the new username into both new dicts
      as the new username will need to be saved not only to the user doc,
      but also to every photo that user has uploaded in the created_by field.
    - Same logic is then applied for the user email, but this only needs to be
      changed in the user document.
    - Checks if the user has entered something into the current password field.
    - Checks if that password is correct.
    - If it is the right password, it checks if the user has entered anything
      into the new password field.
    - If she has, checks if that is == to the new password confirmation field.
    - If all 3 password fields have been entered correctly it pushes the new
      password to the update_user dict using the Werkzeug password hash.
    - Checks if there is anything in either of the new dicts. If they contain
      data, the DB is updated with the new data.
    16. If the user data has been changed it also sets the session["user"] to be the new username.
    17. Then it returns the profile page, which will reflect any updates immediately. 
    '''
    if session:
        if session["user"] == username:
            user = mongo.db.users.find_one({"username": username})
            if request.method == "POST":
                form_username = request.form.get("username").lower()
                form_email = request.form.get("email").lower()
                form_current_password = request.form.get("current_password")
                form_new_password = request.form.get("new_password")
                form_new_password_confirmation = request.form.get("new_password_confirmation")

                update_user = {}
                update_photos = {}

                # If the user has changed their username
                if form_username != user["username"]:
                    existing_username = mongo.db.users.find_one(
                                        {"username": form_username})
                    if existing_username:
                        flash("Username is already in use, please choose a different one.")
                        return redirect(url_for(
                               'edit_profile', user=user, username=username))
                    else:
                        update_user["username"] = form_username
                        update_photos["created_by"] = form_username

                if form_email != user["email"]:
                    existing_email = mongo.db.users.find_one(
                                    {"email": form_email})
                    if existing_email:
                        flash("That email is already in use, please choose a different one.")
                        return redirect(url_for(
                               'edit_profile', user=user, username=username))
                    else:
                        update_user["email"] = form_email

                if form_current_password:
                    if check_password_hash(user["password"],
                                           request.form.get(
                                               "current_password")):
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
            flash("You cannot edit someone else's account...obvz!")
            abort(403)

    else:
        flash("You must be logged in to edit your account, and obviously, you are not allowed to edit someone else's account!")
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
