
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

    #Send the search queries back to the form to populate the inputs?

    return render_template("browse_images.html",
                           photos=photos_paginated,
                           pagination=pagination,
                           source_url=source_url,
                           category=category,
                           query=query,
                           awards=awards)


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
        url = register_new_user(mongo, request)
        return url
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
    * GET renders the edit-profile template if the user is logged in &
      requesting their own page. Otherwise it renders an error page with
      a flash message outlining the issue.
    * POST: If the form is submitted successfully and user details changed,
      this updates the db with the new user data and then renders the user's
      profile with the updated details. If unsuccessful, this

    '''
    user = mongo.db.users.find_one({"username": username})
    source_url = request.referrer
    if request.method == "POST":

        if session:
            if session["user"] == username:

                url = edit_user_profile(
                            user, username, request, mongo)
                return url
            else:
                flash("You cannot edit someone else's account...obvz!")
                abort(403)
        else:
            flash("You must be logged in to edit your\
            account, and obviously, you are not allowed \
            to edit someone else's account!")
            abort(403)

    return render_template(
        'edit_profile.html', user=user, source_url=source_url)


@app.route('/delete-account/<username>', methods=['GET', 'POST'])
def delete_account(username):

    if request.method == "POST":
        url = delete_user_account(username, mongo, request)
        return url


@app.route("/compete", methods=['GET', 'POST'])
def compete():
    '''
    * If method is GET this renders the compete template which
      outlines the competition rules, upload guidelines and entry form.
      If the method is POST this uploads the new entry and its data
      to the db and confirms the upload with a flash message. If the POST
      is unsuccessful a flash message is displayed detailing the issue.

    \n Args:
    1. user input from form(str & file): title, story, camera, lens, aperture,
       shutter, iso & photo file.

    \n Return:
    * Saves the data to the db & reloads the compete page whether successful
      or not, uses flash messages to inform the user of which.
    '''
    date_time = datetime.now()

    current_week_number = int(datetime.now().strftime("%V"))
    this_weeks_comp_category = get_competition(
                               current_week_number)["category"]
    this_weeks_comp_instructions = get_competition(
                                   current_week_number)["instructions"]

    if request.method == 'POST':

        current_user = mongo.db.users.find_one(
                {"username": session["user"]})

        if current_user["can_enter"] is True:

            upload_comp_entry(request,
                              mongo,
                              app,
                              this_weeks_comp_category,
                              current_user)
 
        else:
            flash("I'm sorry, but you've already entered \
                   an image in this week's competition!")

    this_weeks_entries = list(mongo.db.photos.find(
                        {"week_and_year": date_time.strftime("%V%G")}))

    pagination, photos_paginated = paginated_and_pagination_args(
                                   this_weeks_entries, 10, "page", "per_page")

    return render_template("compete.html",
                           this_weeks_entries=photos_paginated,
                           datetime=date_time,
                           category=this_weeks_comp_category,
                           instructions=this_weeks_comp_instructions,
                           pagination=pagination)

@app.route("/file/<filename>")
def file(filename):
    '''
    * This is the GridFS file url response from MongoDB. It is
      used as the source url for displaying the photos in the app.

    \n Args:
    1. filename (str): The unique photo filename.

    \n Returns:
    * The unique file url for a particular photo.
    '''
    return mongo.send_file(filename)


@app.route("/photos/<filename>", methods=["GET", "POST"])
def get_photo(filename):
    '''
    * This displays a photo complete with all its attendant
      details.

    \n Args:
    1. filename (str): The photo's filename which is unique.

    \n Returns:
    * The template for that photo's detailed view.
    '''
    source_url = request.referrer

    photo = mongo.db.photos.find_one({"filename": filename})
    user = mongo.db.users.find_one({"username": photo["created_by"]})

    username = user["username"]

    return render_template("get_photo.html",
                           photo=photo,
                           username=username,
                           source_url=source_url)


@app.route("/edit-photo/<filename>", methods=["GET", "POST"])
def edit_photo(filename):
    '''
    * This edits a user's photo's details when successful,
      updating them in the db.

    \n Args:
    1. filename (str): The unique filename of the photo object
       to be edited.
    2. The form user inputs for any of: photo title, photo story,
       camera, lens, aperture, shutter & iso.

    \n Returns:
    * If successful, updates the mongo db and renders the get_photo
      template for the photo that was edited.
    '''

    photo = mongo.db.photos.find_one({"filename": filename})
    user = mongo.db.users.find_one({"username": photo["created_by"]})

    username = user["username"]

    if request.method == "POST":
        url = edit_this_photo(request, mongo, filename, photo)
        return url

    if session:
        if session["user"] == username:
            return render_template("edit_photo.html", photo=photo)
        else:
            flash("You cannot edit another user's photo. Edit your own!")
            return redirect(url_for("profile", username=session["user"]))
    else:
        flash("You need to be logged in to edit photos.")
        return redirect(url_for("login"))


@app.route("/delete-photo/<filename>")
def delete_photo(filename):
    '''
    * Deletes every record of a photo from the db and application.

    \n Args:
    1. filename (str): The unique filename of the image to be deleted.

    \n Returns:
    * If successful, deletes all records of the image from the db, and if
      the user accrued points due to the image winning an award, those
      points are removed. Redirects to the user's profile page.
    * If unsuccessful shows the user a flash message detailing the issue
      and redirects to home, or login.
    '''
    if session:
        photo_to_del = mongo.db.photos.find_one({"filename": filename})
        if session["user"] == photo_to_del["created_by"]:

            delete_this_photo(mongo, photo_to_del, filename)

            flash("Photograph deleted successfully!")
            return redirect(url_for('profile', username=session["user"]))
        else:
            flash("You may not delete another user's photo.")
            return redirect(url_for('home'))
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
        url = vote_for_photo(mongo, photo)
        return url

@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You've been logged out")
    print(session.values())
    session.pop("user", None)
    session.clear()

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
