from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for,
    abort)
from flask_pymongo import PyMongo, pymongo
from flask_paginate import Pagination, get_page_args
import os
from datetime import datetime
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash

if os.path.exists("env.py"):
    import env


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
    print("All user points zeroed")


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
    print("No photo has any awards now.")


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
    print("No photo has any votes now.")


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
    print("All users can now enter a new image in competition")


# awards() Helper Functions:
# 1. get_this_weeks_comp_users(*args)
# 2. filter_users_and_exclude_non_voters(*args)
# 3. awards_score_requirements(*args)
# 4. determine_winners(*args)
# 5. add_points_to_winning_users(*args)
# 6. add_points_to_users_who_voted_well(*args)
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
            print(f"This week's non-votes are:{non_voters}")
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

    print(f"Range of Votes:{range_of_votes}")

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


# Recent Winners Helper Functions
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


# Pagination Helper.
def paginated_and_pagination_args(
        photos_arr, PER_PAGE, page_param, per_page_param):
    '''
    * Uses the flask_paginate extension to return the specific
      pagination options for a particular template.

    \n Args:
    1. photos_arr (arr): The array of photos for the template to
       be paginated.
    2. PER_PAGE (int): The number of images to display per
       paginated page.
    3. page_param (str): The reference of a GET param that holds the
       page index. It displays in the URL.
    4. per_page_param (str): The reference to refer to 'per_page'.

    \n Returns:
    * pagination_args (obj): An instance of the Pagination object with
      all the inputed specs.
    * photos_to_display (arr): The array of photos that were passed in to
      the function split using the offset & PER_PAGE variables.
    '''
    page, _, _, = get_page_args(
            page_parameter=page_param, per_page_parameter=per_page_param)

    offset = page * PER_PAGE - PER_PAGE
    total = len(photos_arr)

    pagination_args = Pagination(page=page,
                                 per_page=PER_PAGE,
                                 total=total,
                                 page_parameter=page_param,
                                 per_page_parameter=per_page_param)

    photos_to_display = photos_arr[offset: offset + PER_PAGE]

    return pagination_args, photos_to_display


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
    * 1. All photos the user has entered into competition.
    * 2. All photos the user has voted for in competition.
    * 3. All the user's award-winning photos.
    '''
    user = database_var.db.users.find_one({"username": username})

    user_photos = list(
        database_var.db.photos.find({"created_by": user["username"]}))

    photos_voted_for_array = user["photos_voted_for"]
    photos_voted_for_objs = []

    if photos_voted_for_array != []:
        for img in photos_voted_for_array:
            photo_obj = list(database_var.db.photos.find({"_id": img}))
            for photo in photo_obj:
                if photo["week_and_year"] != \
                        datetime.now().strftime("%V%G"):
                    photos_voted_for_objs.append(photo)
    # else:
    #     # Maybe put a msg in the template to that effect?
        # print("This user has not voted for any images yet")
    award_winners = []
    for img in user_photos:
        if img["awards"] is not None:
            award_winners.append(img)

    return user_photos, photos_voted_for_objs, award_winners


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
    final_time_string = f"{days} days,{hours} hours and {minutes} minutes"
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


def edit_user_profile(user, username, form_username,
                      form_email, form_current_password, form_new_password,
                      form_new_password_confirmation, database_var):
    '''
    * When successful this updates the user information. When not successful
      it flashes a message to the user explaining why and redirects them, either
      to an error page, or it reloads the edit_profile template.

    \n Args:
    1. user (obj): The user object from the db
    2. username (str): The username that the user means to edit.
    3. form_username (str): The username inputed into the form.
    4. form_email (str): The email inputed into the form.
    5. form_current_password (str): The string inputed by the user
       to reference their current password.
    6. form_new_password (str): Inputed by the user - the string they
       want to change their password to.
    7. form_new_password_confirmation (str): The confirmation inputed
       by the user to confirm their password change.
    8. database_var (obj): A variable holding the PyMongo Object that
       accesses the MongoDB Server.

    \n Returns:
    * If successful, this updates the user information in the db and returns
      the user's profile page, with any new details updated.
    * If unsuccessful, this returns either an error page or the edit-profile
      template, both with flash messages detailing the issue.
    '''
    update_user = {}
    update_photos = {}

    # If the user has changed their username
    if form_username != user["username"]:
        existing_username = database_var.db.users.find_one(
                            {"username": form_username})
        if existing_username:
            flash("Username is already in use, please choose a different one.")
            url = redirect(url_for('edit_profile',
                           user=user, username=form_username))
            return url
        else:
            update_user["username"] = form_username
            update_photos["created_by"] = form_username

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
    
    if form_current_password:

        if check_password_hash(user["password"], form_current_password):
            if form_new_password:

                if form_new_password == form_new_password_confirmation:
                    update_user["password"] = generate_password_hash(form_new_password)

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

    if update_photos:
        database_var.db.photos.update_many(
            {"created_by": username}, {"$set": update_photos})

    if update_user:
        database_var.db.users.update_one(
                              {"username": username}, {'$set': update_user})
        session["user"] = form_username
        user = database_var.db.users.find_one(
                                     {"username": session["user"]})
        user_photos = list(database_var.db.photos.find(
                            {"created_by": session["user"]}))

    user = database_var.db.users.find_one({"username": session["user"]})
    username = session["user"]
    can_enter = user["can_enter"]
    votes_to_use = user["votes_to_use"]

    user_photos, photos_voted_for_objs, award_winners = \
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
                          user_photos=user_photos,
                          photos_voted_for=photos_voted_for_objs,
                          award_winners=award_winners,
                          can_enter=can_enter,
                          votes_to_use=votes_to_use,
                          comp_closes=comp_closes,
                          voting_closes=voting_closes,
                          next_comp_starts=next_comp_starts)
    return url
