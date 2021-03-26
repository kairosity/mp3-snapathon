
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for,
    abort)
from flask_pymongo import PyMongo
from helpers import (
    get_this_weeks_comp_users,
    filter_users_and_exclude_non_voters,
    get_range_of_scores,
    awards_score_requirements,
    determine_winners,
    add_points_to_winning_users,
    add_points_to_users_who_voted_well,
    get_last_monday_and_images,
    first_second_third_place_compcat_users,
    get_images_by_week_and_year,
    paginated_and_pagination_args,
    filter_user_search,
    filter_admin_search,
    register_new_user,
    login_user,
    get_profile_page_photos,
    get_next_weekday,
    time_strings_for_template,
    get_time_remaining_string,
    get_competition,
    upload_comp_entry,
    edit_user_profile,
    delete_user_account,
    shuffle_array,
    edit_this_photo,
    delete_this_photo,
    vote_for_photo
    )
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail, Message
import os
from datetime import datetime
from datetime import timedelta
from flask_talisman import Talisman
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

# WTF-Forms CSRF Protection
csrf = CSRFProtect(app)

# Content Security Policy
csp = {
    'default-src': [
        '\'self\'',
        'cdnjs.cloudflare.com',
        'fonts.googleapis.com'
    ],
    'style-src': [
        '\'self\'',
        'cdnjs.cloudflare.com',
        'https://fonts.googleapis.com'
    ],
    'font-src': [
        '\'self\'',
        "https://fonts.gstatic.com",
        'cdnjs.cloudflare.com'
    ],
    'img-src': '*',
    'script-src': [
        'cdnjs.cloudflare.com',
        'code.jquery.com',
        '\'self\'',
    ]
}
# Flask Talisman Security Settings
talisman = Talisman(app,
                    force_https_permanent=True,
                    frame_options="DENY",
                    session_cookie_secure=True,
                    content_security_policy=csp,
                    content_security_policy_nonce_in=['script-src'])

# App Configuration Settings
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")
app.config['UPLOAD_EXTENSIONS'] = \
    ['.jpg', '.png', '.gif', '.svg', '.jpeg', '.heic']

# Email Settings
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

# Mongo database connection
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

    this_week_and_year_formatted = datetime.now().strftime("%V%G")
    this_weeks_entries = list(mongo.db.photos.find(
        {"week_and_year": this_week_and_year_formatted}))

    this_weeks_users = get_this_weeks_comp_users(
        this_weeks_entries, mongo)

    valid_users = filter_users_and_exclude_non_voters(
        this_weeks_users, mongo, this_week_and_year_formatted)

    range_of_votes = get_range_of_scores(
        this_week_and_year_formatted, mongo)

    first_place_vote_count,\
        second_place_vote_count,\
        third_place_vote_count = \
        awards_score_requirements(range_of_votes)

    first_place_users,\
        second_place_users,\
        third_place_users = \
        determine_winners(
            first_place_vote_count,
            second_place_vote_count,
            third_place_vote_count,
            this_weeks_entries, mongo)

    add_points_to_winning_users(
        first_place_users, second_place_users, third_place_users, mongo)

    add_points_to_users_who_voted_well(
        valid_users, this_week_and_year_formatted, mongo)


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
    * If user is logged in, email form is pre-filled with their
    email address.

    \n Args:
    1. User inputs (str): email and message from contact form.

    \n Returns:
    * Template displaying the homepage
    * POST method sends SNAPATHON an email from the user.
    '''
    if request.method == "POST":
        try:
            with app.app_context():
                msg = Message(subject="New Email From Contact Form")
                msg.sender = request.form.get("email_of_sender")
                msg.recipients = [os.environ.get('MAIL_USERNAME')]
                message = request.form.get("message")
                msg.body = f"Email From: {msg.sender} \nMessage: {message}"
                mail.send(msg)
                flash("Email Sent!")
                return redirect(url_for('home'))
        except Exception:
            flash("Apologies, but your email could not be sent. \
                  Please try again later.")
            abort(500)

    if 'user' in session:
        userToTarget = mongo.db.users.find_one({"username": session["user"]})
        user_email = userToTarget["email"]
    else:
        user_email = ""

    return render_template("index.html", user_email=user_email)


@app.route("/winners")
def winners():
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
        "There are currently no winners to display.\
            Check back here soon!"

    images_to_display, last_mon = \
        get_last_monday_and_images(mongo, get_images_by_week_and_year)

    week_starting = last_mon.strftime("%A, %d of %B")

    first_place, second_place, third_place, \
        list_of_users, competition_category = \
        first_second_third_place_compcat_users(
            images_to_display, mongo)

    return render_template("winners.html",
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

    all_photos = list(mongo.db.photos.find({"type": "entry"}))

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
                           source_url=source_url,
                           category=category,
                           query=query,
                           awards=awards)


@app.route('/admin-search')
def admin_search():
    '''
    * Takes the admin's inputed search query and filters back users that
      match the keyword criterion.

    \n Args:
    1. query (str): Admin input from the admin search form.

    \n Returns:
    * Renders an array of paginated and filtered photo objects that match
      the search criterion on the browse template.
    '''
    if session:
        if 'user' in session:
            if session["user"] == 'admin':
                source_url = request.referrer

                query = request.args.get("query")

                filtered_users = filter_admin_search(query, mongo)

                pagination, users_paginated = \
                    paginated_and_pagination_args(
                                    filtered_users, 10, "page", "per_page")

                if not filtered_users:
                    flash("I'm sorry, but your\
                         search did not return any images.")

                return render_template("admin.html",
                                       all_users=users_paginated,
                                       pagination=pagination,
                                       source_url=source_url,
                                       query=query)
            else:
                flash("You do not have permission to access this page!")
                abort(403)
        else:
            flash("You do not have permission to access this page!")
            abort(403)
    else:
        flash("You must be logged in to access this page!")
        abort(403)


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
    * If registration is unsuccessful the register template is
      reloaded with flash messages detailing why.
    '''

    if request.method == "POST":
        url = register_new_user(mongo, request, app)
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
    user_profile_photo, user_photos, \
        photos_voted_for_objs, award_winners,\
        user_entry_this_comp = \
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

    source_url = request.referrer

    return render_template("profile.html",
                           username=username,
                           user=user,
                           user_profile_photo=user_profile_photo,
                           user_photos=user_photos,
                           photos_voted_for=photos_voted_for_objs,
                           award_winners=award_winners,
                           user_entry_this_comp=user_entry_this_comp,
                           can_enter=can_enter,
                           votes_to_use=votes_to_use,
                           comp_closes=comp_closes,
                           voting_closes=voting_closes,
                           next_comp_starts=next_comp_starts,
                           source_url=source_url)


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
    if 'user' in session:
        if session["user"] == username or session["user"] == 'admin':

            user = mongo.db.users.find_one({"username": username})
            source_url = request.referrer

            if request.method == "POST":

                if 'user' in session:
                    if session["user"] == \
                            username or session["user"] == 'admin':

                        url = edit_user_profile(
                                    user, username, request, mongo, app)
                        return url
                    else:
                        flash("You cannot edit someone else's account!")
                        abort(403)
                else:
                    flash("You must be logged in to edit your\
                    account, and you are not allowed \
                    to edit someone else's account!")
                    abort(403)

            return render_template(
                'edit_profile.html', user=user, source_url=source_url)
        else:
            flash("You cannot edit another user's profile!")
            return redirect(url_for('login'))
    else:
        flash("You must be logged in to edit your profile!")
        return redirect(url_for('login'))


@app.route('/delete-account/<username>', methods=['GET', 'POST'])
def delete_account(username):
    '''
    * Deletes a user and all associated photos completely.

    \n Args:
    1. username (str): The username of the user to be deleted.

    \n Returns:
    * If successful, deletes all records of the user from the db.
    * If a user was deleting their own account they are redirected to
    the app homepage.
    * If an admin was deleting a user's account they are redirected to
    the admin user control page.
    * If unsuccessful users are redirected to the 'edit profile' page.
    * If unsuccessful admin are redirected to the user deletion page of
      the user they are trying to delete.
    '''
    if 'user' in session:
        if session["user"] == username or session["user"] == 'admin':
            if request.method == "POST":
                url = delete_user_account(username, mongo, request)
                return url

            if request.method == "GET":
                flash("To delete your account, please first login, then click the \
                    'edit profile button' & then select 'delete account'.")
                return redirect(url_for('profile', username=session["user"]))
        else:
            flash("You cannot delete another user's account!")
            abort(403)
    else:
        flash("You must be logged in to delete your account.")
        return redirect(url_for('login'))


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

    photo_user_voted_for = None

    if session:
        if 'user' in session:

            current_user = mongo.db.users.find_one(
                        {"username": session["user"]})

            this_weeks_entries = list(mongo.db.photos.find(
                                {"week_and_year": date_time.strftime("%V%G")}))

            # If the user has voted
            if current_user["votes_to_use"] == 0:
                for img in current_user["photos_voted_for"]:
                    for entry in this_weeks_entries:
                        if img == entry["_id"]:
                            photo_user_voted_for = img
            else:
                photo_user_voted_for = None

            current_week_number = int(datetime.now().strftime("%V"))
            this_weeks_comp_category = get_competition(
                                    current_week_number)["category"]
            this_weeks_comp_instructions = get_competition(
                                        current_week_number)["instructions"]

            if request.method == 'POST':

                if current_user["can_enter"] is True:

                    url = upload_comp_entry(request,
                                            mongo,
                                            app,
                                            this_weeks_comp_category,
                                            current_user)

                    flash("Entry Received!")
                    return redirect(url_for('compete'))

                else:
                    flash("I'm sorry, but you've already entered \
                        an image in this week's competition!")

            this_weeks_entries = list(mongo.db.photos.find(
                                {"week_and_year": date_time.strftime("%V%G")}))

            pagination, photos_paginated = \
                paginated_and_pagination_args(
                                this_weeks_entries, 50, "page", "per_page")

            photos_paginated_copy = photos_paginated.copy()

            photos_paginated_shuffled = shuffle_array(photos_paginated_copy)

            return render_template(
                "compete.html",
                this_weeks_entries=photos_paginated_shuffled,
                datetime=date_time,
                category=this_weeks_comp_category,
                instructions=this_weeks_comp_instructions,
                pagination=pagination,
                user=current_user,
                photo_user_voted_for=photo_user_voted_for)

        else:
            flash("You must be logged in to view the competition page.")
            return redirect(url_for("login"))
    else:
        flash("You must be logged in to view the competition page.")
        return redirect(url_for("login"))


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

    try:
        user = mongo.db.users.find_one({"username": photo["created_by"]})
    except TypeError:
        flash("I'm sorry but that photo could not be found.")
        abort(404)

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

    if request.method == "POST":
        photo = mongo.db.photos.find_one({"filename": filename})
        url = edit_this_photo(request, mongo, filename, photo)
        return url

    if session:
        if 'user' in session:
            photo = mongo.db.photos.find_one({"filename": filename})
            try:
                user = mongo.db.users.find_one(
                    {"username": photo["created_by"]})
            except TypeError:
                flash("Sorry, but that photo cannot be found.")
                abort(404)
            username = user["username"]
            if session["user"] == username:
                return render_template("edit_photo.html", photo=photo)
            else:
                flash("You cannot edit another user's photo.")
                return redirect(url_for("profile", username=session["user"]))
        else:
            flash("You need to be logged in to edit photos.")
            return redirect(url_for("login"))
    else:
        flash("You need to be logged in to edit photos.")
        return redirect(url_for("login"))


@app.route("/delete-photo/<filename>",  methods=["POST"])
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
    if request.method == 'POST':
        if 'user' in session:
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
    '''
    * Votes for a particular photo.

    \n Args:
    1. filename (str): The unique filename of the image voted for.

    \n Returns:
    * If successful, adds a vote to that image.
    * Reloads the page.
    '''

    photo = mongo.db.photos.find_one({"filename": filename})

    if not session:
        flash("You must be logged in to vote.")
        return redirect(url_for("login"))

    if request.method == "POST":
        url = vote_for_photo(mongo, photo)
        return url


@app.route("/admin", methods=["GET", "POST"])
def admin():
    '''
    * Displays the admin user control page that lists
      all non-admin users.

    \n Args: None

    \n Returns:
    * Displays the admin page.
    '''
    all_users = list(mongo.db.users.find())
    if session:
        if 'user' in session:
            if session["user"] == "admin":

                pagination, users_paginated = paginated_and_pagination_args(
                                   all_users, 30, "page", "per_page")
                return render_template(
                    'admin.html',
                    all_users=users_paginated, pagination=pagination)

            else:
                flash("You do not have permission to access this page!")
                abort(403)
        else:
            flash("You do not have permission to access this page!")
            abort(403)
    else:
        flash("You must be logged in to access this page!")
        abort(403)


@app.route("/admin-delete-user-account/<username>")
def admin_delete_user_account(username):
    '''
    * Displays the page that allows an admin to delete
    a user's account.

    \n Args:
    1. username (str): The specific username registered to a user in
       the db.

    \n Returns:
    * Displays the delete user account template for admins.
    '''
    if session:
        if 'user' in session:
            if session["user"] == "admin":
                source_url = request.referrer
                user = mongo.db.users.find_one({"username": username})
                if user is not None:
                    return render_template(
                        'admin-delete-user-account.html',
                        user=user, username=username, source_url=source_url)
                else:
                    flash("Sorry, but that user was not found on the system.")
                    abort(404)
            else:
                flash("You do not have permission to access this page!")
                abort(403)
        else:
            flash("You do not have permission to access this page!")
            abort(403)
    else:
        flash("You must be logged in to access this page!")
        abort(403)


@app.route("/logout")
def logout():
    '''
    * Logs a user out.

    \n Args:
    1. None

    \n Returns:
    * Logs a user out of their session and revokes their
      access to protected pages.
    '''
    if session:
        if 'user' in session:
            session.pop("user", None)
            flash("You've been logged out")
            return redirect(url_for("login"))
        else:
            flash("You're not logged in.")
            return redirect(url_for("login"))
    else:
        flash("You're not logged in.")
        return redirect(url_for("login"))


@app.errorhandler(403)
def forbidden_error(e):
    error = 403
    error_msg = "I actually can't believe you tried to do that.\
    Totally Forbidden, sorry."
    return render_template('error.html', error=error, error_msg=error_msg), 403


@app.errorhandler(404)
def page_not_found(e):
    error = 404
    error_msg = "I'm sorry, we've searched everywhere, \
    but the page you are looking for does not exist."
    return render_template('error.html', error=error, error_msg=error_msg), 404


@app.errorhandler(408)
def request_timeout(e):
    error = 408
    error_msg = "Sorry, but the server timed out waiting for the request.\
    You might try again."
    return render_template('error.html', error=error, error_msg=error_msg), 408


@app.errorhandler(413)
def payload_too_large(e):
    error = 413
    error_msg = "Sorry, but the file you're trying to upload is too large.\
    If you are entering the competition, please have a look at the file size\
    guidelines in the rules section. If you are uploading a profile pic,\
    or a competition entry, please resize your image so that it is under\
    560KB. Thanks!"
    return render_template('error.html', error=error, error_msg=error_msg), 413


@app.errorhandler(415)
def unsupported_media_type(e):
    error = 415
    error_msg = "Sorry, but the file you're trying to upload is an unsupported\
    file type. We only accept .jpg, .jpeg, .gif, .svg or .png files. Thanks!"
    return render_template('error.html', error=error, error_msg=error_msg), 415


@app.errorhandler(500)
def internal_server_error(e):
    error = 500
    error_msg = "We're so sorry! There's been an internal server error.\
    It's not you, it's definitely us, but maybe try again later?"
    return render_template('error.html', error=error, error_msg=error_msg), 500


@app.errorhandler(Exception)
def all_other_exceptions(e):
    error_msg = "I'm sorry but the above error has occured."
    return render_template('error.html', error=e, error_msg=error_msg)


# SET DEBUG TO FALSE BEFORE DEPLOYMENT
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
