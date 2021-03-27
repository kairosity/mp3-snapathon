from flask import (
    flash, render_template,
    redirect, request, session, url_for,
    abort)
from flask_paginate import Pagination, get_page_args
import imghdr
import os
from datetime import datetime
from datetime import timedelta
import random
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Constant Variables
competitions = [
    {
        "category": "portraiture",
        "instructions": "Enter your portraits now! \
            These can be of animals or humans and can be \
                close up or full length.They should communicate\
                     something substantial about the subject."
    },
    {
        "category": "landscape",
        "instructions": "Enter your lanscapes now!\
             These should be primarily focused on the natural world.\
                  No city-scapes. Focus on delivering images with great\
                       lighting in interesting locations."
    },
    {
        "category": "architecture",
        "instructions": "Enter your architectural photos now!\
             Interesting angles and great composition is key here."
    },
    {
        "category": "wildlife",
        "instructions": "Enter your wildlife and nature photos now!\
             Flora OR fauna are acceptable. Capture amazing images of\
                  the natural world at its most spectacular."
    },
    {
        "category": "street",
        "instructions": "Enter your street photography now!\
             Encounters and imagery from urban jungles."
    },
    {
        "category": "monochrome",
        "instructions": "Enter your monochrome photography now.\
             Any subject, any place, black and white imagery only.\
                  PLEASE no sepia tones!"
    },
    {
        "category": "event",
        "instructions": "Enter your event photography now!\
             Weddings, baptisms, concerts, theatre etc.. If it\
                  has guests, it's an event!"
    }
]


# Development Testing Functions
# 1. clear_user_points(database_var)
# 2. clear_all_awards(database_var)
# 3. clear_all_photo_votes(database_var)
# 4. delete_collection()
def clear_user_points(database_var):
    '''
    * This function brings all the user points to 0.
    It is only used in development.

    \n Args:
    1. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.

    \n Returns:
    * Resets all the users' user_points fields to 0 in the db.
    '''
    all_users = list(database_var.db.users.find())
    for user in all_users:
        database_var.db.users.update_one(
            {"username": user["username"]},
            {'$set': {"user_points": 0}})


def clear_all_awards(database_var):
    '''
    * This function brings all the photo awards to null.
    It is only used in development for testing.

    \n Args:
    1. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.

    \n Returns:
    * Set all the photo documents as having "awards": null
    '''
    all_photos = list(database_var.db.photos.find())
    for photo in all_photos:
        database_var.db.photos.update_one(
            {"filename": photo["filename"]},
            {'$set': {"awards": None}})


def clear_all_photo_votes(database_var):
    '''
    * This removes all photo vote records from all photos in the db.

    \n Args:
    1. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.

    \n Returns:
    * Deletes all values in the photo_votes field on all photo docs in the db.
    '''
    all_photos = list(database_var.db.photos.find())
    for photo in all_photos:
        database_var.db.photos.update_one(
            {"filename": photo["filename"]},
            {'$set': {"photo_votes": 0}})


def delete_collection(database_var):
    '''
    * This function deletes the entire mongoDB collection.
      It is only used for testing in development.

    \n Args:
     1. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.
    \n Returns:
    * Deletes the entire db collection.
    '''
    database_var.db.fs.chunks.remove({})
    database_var.db.fs.files.remove({})
    database_var.db.photos.remove({})
    database_var.db.users.remove({})


# Scheduled/Timed Functions:
# 1. new_comp(database_var)


def new_comp(database_var):
    '''
    * This function allows all users to enter a new competition.
      It is run automatically using APScheduler at 0:00 Monday morning.

    \n Args:
    1. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.

    \n Returns:
    * Changes the 'can_enter' field to True for every user in the db.
    '''
    all_users = list(database_var.db.users.find())
    for user in all_users:
        database_var.db.users.update_one(
            {"username": user["username"]},
            {'$set': {"can_enter": True}})


# awards() Helper Functions:
# 1. get_this_weeks_comp_users(*args)
# 2. filter_users_and_exclude_non_voters(*args)
# 3. get_range_of_scores(*args)
# 4. awards_score_requirements(*args)
# 5. determine_winners(*args)
# 6. add_points_to_winning_users(*args)
# 7. add_points_to_users_who_voted_well(*args)


def get_this_weeks_comp_users(entries, database_var):
    '''
    * Creates a list of the users who entered a particular competition.

    \n Args:
    1. entries (arr): All the photo objects entered into this
       competition.
    2. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.

    \n Returns:
    * An array of users who entered this week's competition.
    '''
    this_weeks_usernames = []
    this_weeks_users = []

    for img in entries:
        this_weeks_usernames.append(img["created_by"])

    for username in this_weeks_usernames:
        this_weeks_users.append(
            database_var.db.users.find_one({"username": username}))

    return this_weeks_users


def filter_users_and_exclude_non_voters(
        array_of_users, database_var, comp_week_and_year):
    '''
    * This divides the arr of users who entered the competition into users
      who voted and users who did not vote. It then penalises users who entered
      the competition but failed to vote, by reducing their entry's points
      to 0.

    \n Args:
    1. array_of_users (arr): The users who entered the specific competition.
    2. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.
    3. comp_week_and_year (str): A datetime formatted string of type: "052021"
       representing the week & year the competition took place.

    \n Returns:
    * Alters the user db for those photos by users who failed to vote. Resets
      the photo's "photo_votes" to 0.
    * Returns an array of valid_users.
    '''
    valid_users = []
    non_voters = []

    for user in array_of_users:
        if user["votes_to_use"] > 0:
            non_voters.append(user)
        else:
            valid_users.append(user)

    for user in non_voters:
        database_var.db.photos.update_one(
            {"created_by": user["username"],
                "week_and_year": comp_week_and_year},
            {'$set': {"photo_votes": 0}})
        database_var.db.users.update_one(
            {"username": user["username"]},
            {'$set': {"votes_to_use": 0}})

    return valid_users


def get_range_of_scores(comp_week_and_year, database_var):
    '''
    * This calculates the range of scores or votes in the competition.

    \n Args:
    1. comp_week_and_year (str): A datetime formatted string of type: "052021"
       representing the week & year the competition took place.
    2. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.

    \n Returns:
    * An array of the range of votes / points from photos in the
      competition.

    '''
    this_weeks_entries_ordered = list(database_var.db.photos.find(
        {'$query': {"week_and_year": comp_week_and_year},
            '$orderby': {'photo_votes': -1}}))

    range_of_votes = []

    for photo in this_weeks_entries_ordered:
        if photo["photo_votes"] > 0:
            range_of_votes.append(photo["photo_votes"])

    return range_of_votes


def awards_score_requirements(array_of_scores):
    '''
    * This calculates the number of votes needed for a photo to receive a
      1st, 2nd & 3rd place award, given an array of scores.

    \n Args:
    1. array_of_scores (arr): Specifically an array of the numbers of total
       votes all photos have received in the competition.

    \n Returns:
    * 3 values: the votes needed for 1st place, 2nd place & 3rd place.
    '''
    second_place_vote_array = []
    third_place_vote_array = []
    first_place_vote_count = max(array_of_scores) if array_of_scores else None

    if first_place_vote_count:
        second_place_vote_array = \
            [n for n in array_of_scores if n != first_place_vote_count]

    second_place_vote_count = \
        max(second_place_vote_array) if second_place_vote_array else None
    if second_place_vote_count:
        third_place_vote_array = \
            [n for n in second_place_vote_array
                if n != second_place_vote_count]

    third_place_vote_count = \
        max(third_place_vote_array) if third_place_vote_array else None

    return first_place_vote_count, \
        second_place_vote_count, third_place_vote_count


def determine_winners(
        first_place_votes_needed, second_place_votes_needed,
        third_place_votes_needed, photo_arr, database_var):
    '''
    * This uses the score requirements for winning awards, to determine which
      photos and users won 1st, 2nd and 3rd place. It updates the "awards"
      field in the db for the winning images, and it returns 3 arrays of
      winning users.

    \n Args:
    1. first_place_votes_needed, second_place_votes_needed &
       third_place_votes_needed (int): The required number of votes a photo
       needs to place 1st, 2nd or 3rd.
    2. photo_arr (arr): The array of photo objs in this specific competition.
    3. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.

    \n Returns:
    * 3 arrays: Users winning 1st, 2nd & 3rd place for this competition.
      They are arrays because ties are possible.

    '''
    first_place_users = []
    second_place_users = []
    third_place_users = []

    for entry in photo_arr:
        if entry["photo_votes"] == \
                first_place_votes_needed and first_place_votes_needed > 0:
            database_var.db.photos.update_one(
                {"filename": entry["filename"]},
                {'$set': {"awards": 1}})
            user = database_var.db.users.find_one(
                {"username": entry["created_by"]})

            if user not in first_place_users:
                first_place_users.append(user)

        elif entry["photo_votes"] == \
                second_place_votes_needed and second_place_votes_needed > 0:
            database_var.db.photos.update_one(
                {"filename": entry["filename"]},
                {'$set': {"awards": 2}})
            user = database_var.db.users.find_one(
                {"username": entry["created_by"]})

            if user not in second_place_users:
                second_place_users.append(user)

        elif entry["photo_votes"] == \
                third_place_votes_needed and second_place_votes_needed > 0:
            database_var.db.photos.update_one(
                {"filename": entry["filename"]},
                {'$set': {"awards": 3}})
            user = database_var.db.users.find_one(
                {"username": entry["created_by"]})

            if user not in third_place_users:
                third_place_users.append(user)

    return first_place_users, second_place_users, third_place_users


def add_points_to_winning_users(
        first_place_user_arr, second_place_user_arr,
        third_place_user_arr, database_var):
    '''
    * Takes in arrays of winning users and increases their "user_points"
      fields in the db by their respective scores.

    \n Args:
    1. first_place_user_arr, second_place_user_arr, third_place_user_arr (arr):
       Arrays of users who have won 1st, 2nd & 3rd place.
    2. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.

    \n Returns:
    * Updates the db with the scores for 1st, 2nd & 3rd place (7, 5 & 3).
    '''

    for user in first_place_user_arr:
        database_var.db.users.update_one(
            {"username": user["username"]}, {'$inc': {"user_points": 7}})

    for user in second_place_user_arr:
        database_var.db.users.update_one(
            {"username": user["username"]}, {'$inc': {"user_points": 5}})

    for user in third_place_user_arr:
        database_var.db.users.update_one(
            {"username": user["username"]}, {'$inc': {"user_points": 3}})


def add_points_to_users_who_voted_well(
        user_arr, comp_week_and_year, database_var):
    '''
    * Adds points to users who voted for the 1st, 2nd & 3rd placed images.

    \n Args:
    1. user_arr (arr): An array of users who entered the competition.
    2. comp_week_and_year (str): A datetime formatted string of type: "052021"
       representing the week & year the competition took place.
    3. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.

    \n Returns:
    * Increments the users' "user_points" field in the db if they
      voted for the 1st, 2nd & 3rd placed images by 3, 2 & 1 points
      respectively.

    '''
    for user in user_arr:
        for photo in user["photos_voted_for"]:
            photo_as_obj = list(database_var.db.photos.find(
                {"_id": photo, "week_and_year": comp_week_and_year}))
            if photo_as_obj:
                photo_as_obj = photo_as_obj[0]
                if photo_as_obj["awards"] == 1:
                    database_var.db.users.update_one(
                        {"username": user["username"]},
                        {'$inc': {"user_points": 3}})
                if photo_as_obj["awards"] == 2:
                    database_var.db.users.update_one(
                        {"username": user["username"]},
                        {'$inc': {"user_points": 2}})
                if photo_as_obj["awards"] == 3:
                    database_var.db.users.update_one(
                        {"username": user["username"]},
                        {'$inc': {"user_points": 1}})


# Winners Helper Functions
# 1. get_images_by_week_and_year(*args)
# 2. get_last_monday_and_images(*args)
# 3. first_second_third_place_compcat_users(*args)


def get_images_by_week_and_year(w_a_y, database_var):
    '''
    * Returns a list of images entered into a competition in a
      particular week.

    \n Args:
    1. w_a_y (str): A datetime formatted string of type: "052021"
       representing the week & year the photo was entered into competition.
    2. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.

    \n Returns:
    * A list of photos that were entered into the competition that
      specific week.
    '''
    entries_that_week = list(
        database_var.db.photos.find({"week_and_year": w_a_y}))
    return entries_that_week


def get_last_monday_and_images(database_var, func_to_get_images):
    '''
    * This gets the datetime object of the 'last monday' i.e. the date of
      commencement of the 'last' referenced competition. It also gets the
      collection of entries for that particular competition.

    \n Args:
    1. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.
    2. func_to_get_images (func): A function that takes 2 args:
       1. The week & year in question.
       2. A database obj (as per #1 above)
       This func returns an array of images from a particular competition.

    \n Returns:
    * The datetime object of the 'last monday' - if we access this Mon-Sun
      before 22:00PM, this will reference the previous week's Monday. If we
      access this on Sunday after 22:00PM this will reference the current
      week's Monday.
    * An array of 'images_to_display'-i.e. competition entries from that
      particular week.
    '''
    today = datetime.now()
    day_of_week = today.weekday()
    hour_of_day = today.time().hour
    this_week_and_year = datetime.now().strftime("%V%G")

    week_before = today - timedelta(weeks=1)
    last_week_and_year = week_before.strftime("%V%G")

    if day_of_week in range(0, 6) or day_of_week == 6 and hour_of_day < 22:
        images_to_display = \
            func_to_get_images(last_week_and_year, database_var)
        last_mon = week_before
        while last_mon.weekday() != 0:
            last_mon = last_mon - timedelta(days=1)
    else:
        images_to_display = \
            func_to_get_images(this_week_and_year, database_var)
        last_mon = today
        while last_mon.weekday() != 0:
            last_mon = last_mon - timedelta(days=1)

    return images_to_display, last_mon


def first_second_third_place_compcat_users(photo_array, database_var):
    '''
    * This divides a given array of photos into 3 arrays, for 1st,
      2nd & 3rd placed award-winning photos. It also creates an arr
      of the users who have created those award-winning photos. Finally
      it returns the category of the competition in question.

    \n Args:
    1. photo_array (arr): An array of photo objects.
    2. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.

    \n Returns:
    * first_place, second_place, third_place (arrs): Arrays of competition
      winning photo objects.
    * list_of_users (arr): An array of the users who created those images.
    * competition_category (str): The theme of the competition in question.
    '''
    first_place = []
    second_place = []
    third_place = []

    list_of_users = []
    competition_category = None

    for img in photo_array:
        if img["awards"] == 1:
            first_place.append(img)
            list_of_users.append(database_var.db.users.find_one(
                                {"username": img["created_by"]}))
            competition_category = img["competition_category"]
        elif img["awards"] == 2:
            second_place.append(img)
            list_of_users.append(database_var.db.users.find_one(
                                {"username": img["created_by"]}))
            competition_category = img["competition_category"]
        elif img["awards"] == 3:
            third_place.append(img)
            list_of_users.append(database_var.db.users.find_one(
                                {"username": img["created_by"]}))
            competition_category = img["competition_category"]

    return first_place, second_place, \
        third_place, list_of_users, competition_category


def paginated_and_pagination_args(
        objs_arr, PER_PAGE, page_param, per_page_param):
    '''
    * Uses the flask_paginate extension to return the specific
      pagination options for a particular template.

    \n Args:
    1. objs_arr (arr): The array of photos for the template to
       be paginated.
    2. PER_PAGE (int): The number of images to display per
       paginated page.
    3. page_param (str): The reference of a GET param that holds the
       page index. It displays in the URL.
    4. per_page_param (str): The reference to refer to 'per_page'.

    \n Returns:
    * pagination_args (obj): An instance of the Pagination object with
      all the inputed specs.
    * objs_to_display (arr): The array of objects that were passed in to
      the function split using the offset & PER_PAGE variables.
    '''
    page, _, _, = get_page_args(
            page_parameter=page_param, per_page_parameter=per_page_param)

    offset = page * PER_PAGE - PER_PAGE
    total = len(objs_arr)

    pagination_args = Pagination(page=page,
                                 per_page=PER_PAGE,
                                 total=total,
                                 page_parameter=page_param,
                                 per_page_parameter=per_page_param,
                                 css_framework='materialize')

    objs_to_display = objs_arr[offset: offset + PER_PAGE]

    return pagination_args, objs_to_display


# Filter Search Functions
# 1. filter_user_search(*args)
# 2. filter_admin_search(*args)


def filter_user_search(
        select_search, keyword_search, checkbox_search, database_var):
    '''
    * Filters a user's search by their inputed criteria.

    \n Args:
    1. select_search (str): One of a finite number of pre-populated
       dropdown menu search categories.
    2. keyword_search (str): A user's text input search.
    3. checkbox_search (arr): An array of integers representing
       checkbox options on the search page.
    4. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.

    \n Returns:
    * An array of photo objects from the db filtered to match the search
      inputs.
    '''
    full_search = keyword_search
    full_query = {}

    if keyword_search:
        full_query["$text"] = {"$search": full_search}

    if checkbox_search:
        full_query["awards"] = {"$in": checkbox_search}

    if select_search:
        full_query["competition_category"] = select_search

    filtered_photos = list(database_var.db.photos.find(full_query))

    return filtered_photos


def filter_admin_search(
        keyword_search, database_var):
    '''
    * Filters an admin's search for a user by their keyword search.

    \n Args:
    1. keyword_search (str): An admin's text input search.
    2. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.

    \n Returns:
    * An array of user objects from the db filtered to match the search
      inputs.
    '''
    full_search = keyword_search
    full_query = {}

    if keyword_search:
        full_query["$text"] = {"$search": full_search}

    filtered_users = list(database_var.db.users.find(full_query))

    return filtered_users


# Upload Image Functions
# 1. validate_image_type(arg)
# 2. check_file_size(*args)
# 3. save_photo(*args)


def validate_image_type(stream):
    '''
    * This checks what type of file is being uploaded.

    \n Args:
    1. stream(data): A particular stream of data.

    \n Returns:
    * If the data read matches one of a selection of image file types
    then the function returns the file extension.
    * If the data does not match a selection of image file types then
    the function returns None.
    '''
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')


def check_file_size(file, size_limit_in_bytes):
    '''
    * This checks the size of the uploaded file against a set limit.

    \n Args:
    1. file (obj): A file of some form of data.
    2. size_limit_in_bytes (int): The maximum fize size limit in bytes.

    \n Returns:
    * If the file size is greater than the limit set, this function returns
    a 413 error: "Payload too large".
    * If the file size is under the limit this function returns True.
    '''
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0, 0)

    if file_length > size_limit_in_bytes:
        return abort(413)
    else:
        return True


def save_photo(request, database_var, name_of_image_from_form, app):
    '''
    * This saves an image from a form to the mongo DB.

    \n Args:
    1. request (obj): The POST request object send via the form
       by the user to the server.
    2. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.
    3. name_of_image_from_form (str): The string assigned to form's file
       upload "name" field.
    4. app (obj): The WSGI application as an object of the Flask class.
    '''
    photo = request.files[name_of_image_from_form]

    file_extension = os.path.splitext(photo.filename)[1]

    if file_extension not in app.config['UPLOAD_EXTENSIONS'] or \
            file_extension != validate_image_type(photo.stream):
        abort(415)

    check_file_size(photo, 560000)

    photo.filename = secure_filename(photo.filename)

    file_id = database_var.save_file(photo.filename, photo)

    # This makes the filename unique
    new_filename = str(file_id) + file_extension

    # Update the gridFS "Filename" attribute to be equal to the file_id
    database_var.db.fs.files.update_one(
                                {"_id": file_id},
                                {'$set': {"filename": new_filename}})
    return file_id, new_filename


def register_new_user(database_var, request, app):
    '''
    * This registers a new user and saves their data to the db.

    \n Args:
    1. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.
    2. request (obj): The request object the user POSTs to the server
       containing the data from the register form: username, email &
       password.

    \n Returns:
    * If successful this will save the new user's data to the db and
      render the new user's profile page.
    * It also logs the user in and  starts a new session with that
      user's username as the session variable's value.
    * If unsuccessful this will flash a message detailing the issue and
      reload the register template.
    '''
    existing_email = database_var.db.users.find_one(
                    {"email": request.form.get("email").lower()})
    existing_username = database_var.db.users.find_one(
                        {"username": request.form.get("username").lower()})

    if existing_email:
        flash("Email is already registered.")
        url = redirect(url_for('register'))
        return url

    if existing_username:
        flash("Username is already in use, please choose a different one.")
        url = redirect(url_for('register'))
        return url

    password1 = request.form.get("password")
    password2 = request.form.get("password-confirmation")

    if password1 != password2:
        flash("Passwords do not match, please try again.")
        url = redirect(url_for('register'))
        return url

    photo_filename_to_add_to_user = None

    if request.files['profile-pic']:
        file_id, new_filename = save_photo(
                request, database_var, "profile-pic", app)

        new_entry = {
            "file_id": file_id,
            "filename": new_filename,
            "type": "profile-pic",
            "user": request.form.get("username").lower()
        }

        database_var.db.photos.insert_one(new_entry)

        photo_to_add_to_user = database_var.db.photos.find_one(
                                {"file_id": file_id})

        photo_filename_to_add_to_user = photo_to_add_to_user["filename"]

    register_user = {
        "username": request.form.get("username").lower(),
        "email": request.form.get("email").lower(),
        "profile_photo": photo_filename_to_add_to_user
        if photo_filename_to_add_to_user else None,
        "password": generate_password_hash(request.form.get("password")),
        "user_points": 0,
        "photos": [],
        "photos_voted_for": [],
        "votes_to_use": 0,
        "can_enter": True
    }
    database_var.db.users.insert_one(register_user)

    session["user"] = request.form.get("username").lower()
    flash("Registration successful!")
    username = session["user"]
    url = redirect(url_for("profile", username=username))
    return url


def login_user(email, password, database_var):
    '''
    * This logs the user in, or tells them why their login
      attempt was unsuccessful.

    \n Args:
    1. email (str): user input from login form of their email.
       Must be unique and match the password they input.
    2. password (str): user input from login form, must match
       hashed password in db connected to user email from arg 1.
    3. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.

    \n Returns:
    * A url variable that holds the template to redirect to. For a
      successful login, this will be the user's profile page. Otherwise
      it will reload the login page with a flash message telling the user
      why their login attempt failed.
    '''
    existing_user = database_var.db.users.find_one(
        {"email": email})

    if existing_user:
        if check_password_hash(
                existing_user["password"], password):
            username = existing_user["username"]
            session["user"] = username
            flash(f"Welcome, {username}!")
            if existing_user["username"] == "admin":
                url = redirect(url_for("admin"))
            else:
                url = redirect(url_for("profile", username=username))
            return url
        else:
            flash("Incorrect username and/or password!")
            url = redirect(url_for("login"))
            return url
    else:
        flash("Incorrect username and/or password!")
        url = redirect(url_for("login"))
        return url


def get_profile_page_photos(username, database_var):
    '''
    * This gets the three categories of photos to show on
      a user's profile page, based on the username passed in.

    \n Args:
    1. username (str): A user's username to find in the db.
    2. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.

    \n Returns:
    * Three arrays of photo objects associated with the username passed
      in:
    * 1. The user's profile photo if there is one.
    * 2. All photos the user has entered into competition.
    * 3. All photos the user has voted for in competition.
    * 4. All the user's award-winning photos.
    '''
    user = database_var.db.users.find_one({"username": username})

    user_profile_photo = None

    user_profile_photo = database_var.db.photos.find_one({"user": username})

    try:
        user_photos = list(
            database_var.db.photos.find({"created_by": user["username"]}))
    except TypeError:
        flash("I'm sorry but that user could not be found.")
        abort(404)

    user_entry_this_comp = database_var.db.photos.find_one(
                            {"created_by": user["username"],
                             "week_and_year": datetime.now().strftime("%V%G")})

    photos_voted_for_array = user["photos_voted_for"]
    photos_voted_for_objs = []

    if photos_voted_for_array != []:
        for img in photos_voted_for_array:
            photo_obj = list(database_var.db.photos.find({"_id": img}))
            for photo in photo_obj:
                if photo["week_and_year"] != \
                        datetime.now().strftime("%V%G"):
                    photos_voted_for_objs.append(photo)

    award_winners = []
    for img in user_photos:
        if img["awards"] is not None:
            award_winners.append(img)

    return user_profile_photo, user_photos,\
        photos_voted_for_objs,\
        award_winners, user_entry_this_comp


# Code from Emmanuel's Stack Overflow answer (attributed in README.md)
def get_next_weekday(startdate, weekday):
    """
    * This calculates the next occuring weekday of any passed in day
    of the week.

    \n Args:
    1. startdate (str): given date, in format '2013-05-25'
    2. weekday (int): week day between 0 (Monday) to 6 (Sunday)

    \n Returns:
    * A datetime object representing the date of the next day of the
      week passed into the function. I.e. The date of next Monday.
    """
    date = datetime.strptime(startdate, '%Y-%m-%d')
    time = timedelta((7 + weekday - date.weekday()) % 7)
    final_date = date + time
    return final_date


def get_time_remaining_string(timedelta):
    '''
    * This returns a string describing an amount of time in days,
      hours and minutes.

    \n Args:
    1. timedelta (datetime.timedelta): Describes an amount of time.

    \n Returns:
    * A string in English made from the timedelta describing the
      time in the format: 'x' days, 'y' hours and 'z' minutes.
    '''
    days = timedelta.days
    timedelta_string = str(timedelta)
    time_array = timedelta_string.split(",").pop().split(":")
    hours = time_array[0]
    minutes = time_array[1]
    days_plural = "days,"
    days_singular = "day,"
    hours_singular = 'hour'
    hours_plural = 'hours'
    minutes_singular = 'minute'
    minutes_plural = 'minutes'
    final_time_string = f"{days} {days_singular if int(days)==1 else days_plural} {hours} {hours_singular if int(hours)==1 else hours_plural} and {minutes} {minutes_singular if int(minutes)==1 else minutes_plural}"
    return final_time_string


def time_strings_for_template(
        comp_end_date, next_comp_start_date, vote_end_date, get_time_func):
    '''
    * This forms human readable strings referring to how much time
      is left until certain events occur.

    \n Args:
    1. comp_end_date (datetime): When the current competition ends.
    2. next_comp_start_date (datetime): When the next competition starts.
    3. vote_end_date (datetime): When the next voting period begins.
    4. get_time_func (function): A func to calculate the initial time
       string that this function creates.

    \n Returns:
    * Three time strings that refer to when: 1. The competition closes,
      2. Voting Closes, 3. The next competition starts. To pass to the
      profile template.
    '''
    now = datetime.now()
    time_til_comp_ends = comp_end_date - now
    time_til_voting_ends = vote_end_date - now
    time_til_next_comp_starts = next_comp_start_date - now

    comp_closes = get_time_func(time_til_comp_ends)
    voting_closes = get_time_func(time_til_voting_ends)
    next_comp_starts = get_time_func(time_til_next_comp_starts)

    return comp_closes, voting_closes, next_comp_starts


def edit_user_profile(user, username, request, database_var, app):
    '''
    * When successful this updates the user information. When not successful
      it flashes a message to the user explaining why and redirects them,\
      either to an error page, or it reloads the edit_profile template.

    \n Args:
    1. user (obj): The user object from the db
    2. username (str): The username that the user means to edit.
    3. request (obj): The POST request object send via the form
       by the user to the server.
    4. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.
    5. app (obj): The WSGI application as an object of the Flask class.

    \n Returns:
    * If successful, this updates the user information in the db and returns
      the user's profile page, with any new details updated.
    * If unsuccessful, this returns either an error page or the edit-profile
      template, both with flash messages detailing the issue.
    '''
    update_user = {}
    update_photos = {}
    update_profile_photo_ref = {}

    form_username = request.form.get("username").lower()
    form_email = request.form.get("email").lower()
    form_profile_pic = request.files["profile-pic"]
    form_del_profile_pic = request.form.get("del-profile-pic")
    form_current_password = request.form.get("current_password")
    form_new_password = request.form.get("new_password")
    form_new_password_confirmation = \
        request.form.get("new_password_confirmation")

    # If the user has changed their username
    if form_username != user["username"]:
        existing_username = database_var.db.users.find_one(
                            {"username": form_username})
        if existing_username:
            flash("That username is already taken, please choose a\
                 different one.")
            url = redirect(url_for('edit_profile',
                           user=user, username=username))
            return url
        else:
            update_user["username"] = form_username
            update_photos["created_by"] = form_username
            update_profile_photo_ref["user"] = form_username

    if form_email != user["email"]:
        existing_email = database_var.db.users.find_one(
                        {"email": form_email})
        if existing_email:
            flash("That email is already in use, \
                   please choose a different one.")
            url = redirect(url_for(
                  'edit_profile', user=user, username=form_username))
            return url
        else:
            update_user["email"] = form_email

    existing_profile_pic = user["profile_photo"]

    # 1. If the delete hidden field is activated && no new file is uploaded.
    if form_del_profile_pic == "del-uploaded-profile-pic" and\
            form_profile_pic.filename == "":

        # delete user's profile pic.
        if existing_profile_pic is not None:
            print("profile pic is here to be deleted without a new upload")

            file_to_delete = database_var.db.fs.files.find_one(
                {"filename": existing_profile_pic})
            print(file_to_delete)

            chunks_to_delete = list(database_var.db.fs.chunks.find({
                                    "files_id": file_to_delete["_id"]}))

            database_var.db.photos.delete_one(
                {"filename": existing_profile_pic})

            database_var.db.fs.files.delete_one(file_to_delete)

            for chunk in chunks_to_delete:
                database_var.db.fs.chunks.delete_one(chunk)

            database_var.db.users.update_one(
                                    {"username": username},
                                    {'$set': {"profile_photo": None}})

    # If there is a file to upload and a current profile pic.
    elif form_profile_pic.filename != "" and existing_profile_pic is not None:

        # Upload new Photo
        file_id, new_filename = save_photo(
            request, database_var, "profile-pic", app)

        new_entry = {
            "file_id": file_id,
            "filename": new_filename,
            "type": "profile-pic",
            "user": user["username"]
        }

        database_var.db.photos.insert_one(new_entry)

        photo_to_add_to_user = database_var.db.photos.find_one(
                            {"file_id": file_id})

        photo_filename_to_add_to_user = photo_to_add_to_user["filename"]

        update_user["profile_photo"] = photo_filename_to_add_to_user

        # Delete the current Profile Photo.
        file_to_delete = database_var.db.fs.files.find_one(
            {"filename": existing_profile_pic})

        chunks_to_delete = list(database_var.db.fs.chunks.find({
                                "files_id": file_to_delete["_id"]}))

        database_var.db.photos.delete_one(
            {"filename": existing_profile_pic})

        database_var.db.fs.files.delete_one(file_to_delete)

        for chunk in chunks_to_delete:
            database_var.db.fs.chunks.delete_one(chunk)

    # If there is no existing profile photo but there...
    # ...IS a new photo to be uploaded.
    elif existing_profile_pic is None and form_profile_pic.filename != "":

        file_id, new_filename = save_photo(
            request, database_var, "profile-pic", app)

        new_entry = {
            "file_id": file_id,
            "filename": new_filename,
            "type": "profile-pic",
            "user": user["username"]
        }

        database_var.db.photos.insert_one(new_entry)

        photo_to_add_to_user = database_var.db.photos.find_one(
                            {"file_id": file_id})

        photo_filename_to_add_to_user = photo_to_add_to_user["filename"]

        update_user["profile_photo"] = photo_filename_to_add_to_user

    if form_current_password:
        if check_password_hash(user["password"], form_current_password):
            if form_new_password:

                if form_new_password == form_new_password_confirmation:
                    update_user["password"] = \
                        generate_password_hash(form_new_password)

                else:
                    flash("Your new passwords do not match, please try again.")
                    url = redirect(url_for(
                            'edit_profile', username=form_username))
                    return url
            else:
                flash("Your new password cannot be nothing. If you were not\
                       trying to change your password, there is no need to\
                       enter your current password.")
                url = redirect(url_for(
                           'edit_profile', user=user, username=form_username))
                return url

        else:
            flash("Sorry, but your current password was entered \
                  incorrectly. Please try again.")
            url = redirect(url_for(
                           'edit_profile', user=user, username=form_username))
            return url

    if (form_new_password and not form_current_password) or \
            (form_new_password_confirmation and not form_current_password):
        flash("You must enter your current password to change your password.\
            Please try again.")
        url = redirect(url_for(
                        'edit_profile', user=user, username=form_username))
        return url

    # updating all the images to being created by new username
    if update_photos:
        database_var.db.photos.update_many(
            {"created_by": username}, {"$set": update_photos})

    # Updating profile pic to being created by new username
    if update_profile_photo_ref:
        database_var.db.photos.update_many(
            {"user": username}, {"$set": update_profile_photo_ref})

    if update_user:
        database_var.db.users.update_one(
                              {"username": username}, {'$set': update_user})

        if session["user"] != 'admin':
            session["user"] = form_username

        if "username" in update_user:
            username_to_query = update_user["username"]
        else:
            username_to_query = user["username"]

        user = database_var.db.users.find_one(
                                     {"username": username_to_query})
        user_photos = list(database_var.db.photos.find(
                            {"created_by": username_to_query}))

        user_photos = list(database_var.db.photos.find(
                            {"user": username_to_query}))

        user = database_var.db.users.find_one({"username": username_to_query})

    username = user["username"]
    can_enter = user["can_enter"]
    votes_to_use = user["votes_to_use"]

    user_profile_photo, user_photos, \
        photos_voted_for_objs, award_winners, _ = \
        get_profile_page_photos(username, database_var)

    today = datetime.now().strftime('%Y-%m-%d')

    competition_ends = get_next_weekday(today, 5)
    next_competition_starts = get_next_weekday(today, 1)
    voting_ends = get_next_weekday(today, 7) - timedelta(hours=2)

    comp_closes, voting_closes, next_comp_starts = \
        time_strings_for_template(
                competition_ends, next_competition_starts,
                voting_ends, get_time_remaining_string)

    flash("Profile updated successfully!")

    url = render_template('profile.html',
                          user=user,
                          username=username,
                          user_profile_photo=user_profile_photo,
                          user_photos=user_photos,
                          photos_voted_for=photos_voted_for_objs,
                          award_winners=award_winners,
                          can_enter=can_enter,
                          votes_to_use=votes_to_use,
                          comp_closes=comp_closes,
                          voting_closes=voting_closes,
                          next_comp_starts=next_comp_starts)
    return url


def del_user_account2(password, password_confirmation,
                      user_deleting, user_to_delete, database_var):

    if password:
        if check_password_hash(user_deleting["password"], password):
            if password == password_confirmation:

                photos_to_delete = []

                if user_to_delete["profile_photo"]:
                    photos_to_delete.append(user_to_delete["profile_photo"])

                if len(user_to_delete["photos"]) > 0:
                    for photo in user_to_delete["photos"]:
                        photos_to_delete.append(photo)

                for photo in photos_to_delete:
                    # Remove the photo obj
                    database_var.db.photos.delete_one(
                        {"filename": photo})

                    file_to_delete = \
                        database_var.db.fs.files.find_one(
                            {"filename": photo})
                    # Target the Chunks for this files_id
                    chunks_to_delete = list(
                        database_var.db.fs.chunks.find(
                            {"files_id": file_to_delete["_id"]}))
                    # Delete the file
                    database_var.db.fs.files.delete_one(
                            file_to_delete)

                    if len(chunks_to_delete) > 0:
                        for chunk in chunks_to_delete:
                            database_var.db.fs.chunks.delete_one(
                                chunk)

                database_var.db.users.delete_one(
                    {"username": user_to_delete["username"]})

                if user_deleting["username"] == 'admin':
                    user_deleted_username = user_to_delete["username"]
                    message = f"{user_deleted_username}'s account &\
                         photos have been deleted successfully!"
                    url = redirect(url_for('admin'))
                else:
                    # 2. Pop the session.
                    session.pop("user", None)
                    message = "Your account & photos have \
                        been deleted successfully!"
                    url = redirect(url_for('home'))

                return message, url

            elif user_deleting["username"] == 'admin':
                message = "You must enter your admin password correctly twice in \
                    order to delete an account. This is a security measure."
                url = redirect(url_for(
                    'admin_user_details', username=user_to_delete["username"]))

            else:
                message = "You must enter your password correctly twice in order to delete your\
                      account. This is a security measure."
                url = redirect(url_for(
                    'edit_profile', username=user_deleting["username"]))

            return message, url

        elif user_deleting["username"] == 'admin':
            message = "Incorrect admin password, please\
                 try again. This is a security measure."
            url = redirect(url_for(
                'admin_user_details', username=user_to_delete["username"]))

        else:
            message = "Incorrect password. Please try again."
            url = redirect(url_for(
                'edit_profile', username=user_deleting["username"]))

        return message, url

    elif user_deleting["username"] == 'admin':
        message = "You must enter your admin password to delete an account."
        url = redirect(url_for(
            'admin_user_details', username=user_to_delete["username"]))
    else:
        message = "You must enter your password to delete your account."
        url = redirect(url_for(
                'edit_profile', username=user_deleting["username"]))

    return message, url


def delete_user_account(username, database_var, request):
    '''
    * This deletes all traces of a user's account including
    the user details and all their images, both entries & profile photo.

    \n Args:
    1. username (str): The username of the account to be deleted.
    2. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.
    3. request (obj): The POST request object send via the form
       by the user to the server.

    \n Returns:
    * If successful: first deletes all photos associated with that user
      from the db.
    * Then deletes the user from the db.
    * Then ends the user's session and redirects to the homepage with a flash
      messaging confirming that the account was deleted.
    * If unsuccessful, it redirects to the edit profile page with a flash
      message detailing the reason.
    * Unless the user is not logged in and trying to delete another user's
      account, in this case it will throw a 403 error with a message.
    '''
    if session:
        form_password = request.form.get("password")
        form_password_confirmation = request.form.get(
            "password_confirmation")
        user = database_var.db.users.find_one({"username": username})

        if session["user"] == username:

            message, url = del_user_account2(
                form_password, form_password_confirmation,
                user, user, database_var)

            flash(message)
            return url

        elif session["user"] == 'admin':

            admin_user = database_var.db.users.find_one({"username": "admin"})
            message, url = del_user_account2(
                form_password, form_password_confirmation,
                admin_user, user, database_var)

            flash(message)
            return url


# compete() Helper Functions
# 1. get_competition(*args)
# 2. upload_comp_entry(*args)


def get_competition(week_number):
    '''
    * Uses the week number to rotate the competition themes.

    \n Args:
    1. week_number (int): datetime week number 0-52/53

    \n Returns:
    * A competition category from the competitions array.
    '''
    if week_number % 7 == 0:
        return competitions[0]
    elif week_number % 7 == 1:
        return competitions[1]
    elif week_number % 7 == 2:
        return competitions[2]
    elif week_number % 7 == 3:
        return competitions[3]
    elif week_number % 7 == 4:
        return competitions[4]
    elif week_number % 7 == 5:
        return competitions[5]
    elif week_number % 7 == 6:
        return competitions[6]


def upload_comp_entry(request_obj,
                      database_var,
                      app,
                      this_weeks_comp_category,
                      current_user):
    '''
    * This uploads a new entry into the competition and saves the necessary
      photo and user data to the db. It also ensures the uploaded photo is
      safe, that it has one of the approved file extensions and it renames
      it so that its filename is unique.

    \n Args:
    1. request_obj (obj): The request object sent by the user when they POST
       the compete form.
    2. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.
    3. app (obj): The WSGI application as an object of the Flask class.
    4. this_weeks_comp_category (str): The competition theme for the current
       competition. This gets attached to the photo object in the db.
    5. current_user (obj): The logged in user who is trying to enter the
       competition.

    \n Returns:
    * Saves the new photo object to the db and enters it into the currently
      running competition. If successful reloads the compete template with
      a flash message telling the user their entry was received.
    '''
    if 'photo' in request.files:

        file_id, new_filename = save_photo(request, database_var, 'photo', app)

        new_entry = {
            "file_id": file_id,
            "filename": new_filename,
            "type": "entry",
            "photo_title": request.form.get("title").lower(),
            "photo_story": request.form.get("story"),
            "camera": request.form.get("camera"),
            "lens": request.form.get("lens"),
            "aperture": request.form.get("aperture"),
            "shutter": request.form.get("shutter"),
            "iso": request.form.get("iso"),
            "created_by": session["user"],
            "date_entered": datetime.now(),
            "competition_category": this_weeks_comp_category,
            "week_and_year": datetime.now().strftime("%V%G"),
            "photo_votes": 0,
            "awards": None
        }
        database_var.db.photos.insert_one(new_entry)

        photo_to_add_to_user = database_var.db.photos.find_one(
                              {"file_id": file_id})
        photo_filename_to_add_to_user = photo_to_add_to_user["filename"]

        database_var.db.users.update_one({"_id": current_user["_id"]},
                                         {'$push': {"photos":
                                          photo_filename_to_add_to_user},
                                          '$inc': {"votes_to_use": 1},
                                          '$set': {"can_enter": False}})


def edit_this_photo(request, database_var, photo_filename, photo_obj):
    '''
    * This takes user input and updates the photo details in
      the mongo db with that input.

    \n Args:
    1. request (obj): The request object from the POST of the
       the edit photo form.
    2. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.
    3. photo_filename (str): The unique filename of the photo obj
       to be edited.
    4. photo_obj (obj): The photo object to delete.

    \n Returns:
    * Updates the db with the new photo details inputed by the user
      and returns a flash confirmation message and renders the
      get_photo template for the photo that was edited.

    '''
    edited_entry = {
        "photo_title": request.form.get("title"),
        "photo_story": request.form.get("story"),
        "camera": request.form.get("camera"),
        "lens": request.form.get("lens"),
        "aperture": request.form.get("aperture"),
        "shutter": request.form.get("shutter"),
        "iso": request.form.get("iso")
        }

    database_var.db.photos.update(
        {"_id": photo_obj["_id"]}, {"$set": edited_entry})
    flash("Photo details edited successfully!")
    url = redirect(url_for("get_photo", filename=photo_filename))
    return url


def delete_this_photo(database_var, photo_to_del, filename):
    '''
    * This deletes a photo from the user object, the photo collection,
      the GridFS files collection & the chunks collection in the
      Mongo DB database. It also removes any points accrued because
      of this photo by the user, from the user's user_points field.

    \n Args:
    1. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.
    2. photo_to_del (obj): The specific photo obj to delete.
    3. filename (str): The specific photo's filename.

    \n Returns:
    * Deletes all db records of the photo and adjusts the user's points
      accordingly if they won points due to this image.
    '''
    if photo_to_del["awards"] == 1:
        database_var.db.users.update_one(
            {"username": session["user"]}, {'$inc': {"user_points": -7}})
    elif photo_to_del["awards"] == 2:
        database_var.db.users.update_one(
            {"username": session["user"]}, {'$inc': {"user_points": -5}})
    elif photo_to_del["awards"] == 3:
        database_var.db.users.update_one(
            {"username": session["user"]}, {'$inc': {"user_points": -3}})

    file_to_delete = database_var.db.fs.files.find_one({"filename": filename})
    chunks_to_delete = list(database_var.db.fs.chunks.find({
                            "files_id": file_to_delete["_id"]}))

    database_var.db.photos.delete_one({"filename": filename})

    database_var.db.fs.files.delete_one(file_to_delete)

    for chunk in chunks_to_delete:
        database_var.db.fs.chunks.delete_one(chunk)

    user = database_var.db.users.find_one({"username": session["user"]})
    user_photos = user["photos"]

    for photo in user_photos:
        if photo == filename:
            database_var.db.users.update_one(
                {"username": session["user"]}, {'$pull': {"photos": photo}})

    date_now = (datetime.now().strftime("%w"))

    if (photo_to_del["week_and_year"] ==
            datetime.now().strftime("%V%G")) and \
            (int(date_now) in range(1, 6)):
        database_var.db.users.update_one(
                {"username": session["user"]},
                {'$set': {'can_enter': True}})

        if user["votes_to_use"] > 1:
            database_var.db.users.update_one(
                {"username": session["user"]}, {'$set': {'votes_to_use': 0}})


def vote_for_photo(database_var, photo_to_vote_for):
    '''
    * This records a user's vote for a photo in the competition.

    \n Args:
    1. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.
    2. photo_to_vote_for (obj): The photo object the user decides to vote
       for.

    \n Returns:
    * If successful it alters both the user record, adding that photo
      into their "photos_voted_for" array field, and that specific photo's
      record, adding a vote to its "photo_votes" field. Which in turn is
      used to calculate winners. It flashes a message to the user and
      reloads the compete template.
    * If unsuccessful, it flashes a message to the user detailing the issue
      and reloads the compete template.
    '''

    user_voting = database_var.db.users.find_one(
                    {"username": session["user"]})

    if user_voting["votes_to_use"] < 1:
        flash("Sorry, but you don't have any votes to use. \
                You've either already voted, or you did not enter \
                    this week's competition.")

        url = redirect(url_for("compete"))
        return url

    elif user_voting["username"] == photo_to_vote_for["created_by"]:
        flash("Sorry, but you cannot vote for your own photo... obviously.")
        url = redirect(url_for("compete"))
        return url

    else:
        database_var.db.users.update({"username": session["user"]},
                                     {'$inc': {"votes_to_use": -1}})

        database_var.db.users.update(
                {"username": session["user"]},
                {"$push":
                    {"photos_voted_for": photo_to_vote_for["_id"]}})

        database_var.db.photos.update_one(
                {"_id": photo_to_vote_for["_id"]},
                {'$inc': {"photo_votes": 1}})

        flash("Thank you for voting!")
        url = redirect(url_for('compete', username=session['user']))
        return url


def shuffle_array(arr):
    random.shuffle(arr)
    return arr
