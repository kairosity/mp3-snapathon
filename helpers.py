from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for,
    abort)
from flask_pymongo import PyMongo, pymongo
from flask_paginate import Pagination, get_page_args
import os
from datetime import datetime
from datetime import timedelta

if os.path.exists("env.py"):
    import env


# Development Testing Functions
# 1. clear_user_points(database_var)
# 2. clear_all_awards(database_var)
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
    all_photos = list(database_var.db.photos.find())
    for photo in all_photos:
        database_var.db.photos.update_one(
            {"filename": photo["filename"]},
            {'$set': {"photo_votes": 0}})
    print("No photo has any votes now.")

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


def filter_users_and_exclude_non_voters(array_of_users, database_var, comp_week_and_year):
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
        second_place_vote_array = [n for n in array_of_scores if n != first_place_vote_count]

    second_place_vote_count = max(second_place_vote_array) if second_place_vote_array else None
    if second_place_vote_count:
        third_place_vote_array = [n for n in second_place_vote_array if n != second_place_vote_count]

    third_place_vote_count = max(third_place_vote_array) if third_place_vote_array else None

    return first_place_vote_count, second_place_vote_count, third_place_vote_count


def determine_winners(first_place_votes_needed, second_place_votes_needed, third_place_votes_needed, photo_arr, database_var):
    '''
    * This uses the score requirements for winning awards, to determine which
      photos and users won 1st, 2nd and 3rd place. It updates the "awards"
      field in the db for the winning images, and it returns 3 arrays of winning
      users.
    
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
        if entry["photo_votes"] == first_place_votes_needed and first_place_votes_needed > 0:
            database_var.db.photos.update_one(
                {"filename": entry["filename"]},
                {'$set': {"awards": 1}})
            user = database_var.db.users.find_one(
                {"username": entry["created_by"]})

            if user not in first_place_users:
                first_place_users.append(user)

        elif entry["photo_votes"] == second_place_votes_needed and second_place_votes_needed > 0:
            database_var.db.photos.update_one(
                {"filename": entry["filename"]},
                {'$set': {"awards": 2}})
            user = database_var.db.users.find_one(
                {"username": entry["created_by"]})

            if user not in second_place_users:
                second_place_users.append(user)

        elif entry["photo_votes"] == third_place_votes_needed and second_place_votes_needed > 0:
            database_var.db.photos.update_one(
                {"filename": entry["filename"]},
                {'$set': {"awards": 3}})
            user = database_var.db.users.find_one(
                {"username": entry["created_by"]})

            if user not in third_place_users:
                third_place_users.append(user)

    return first_place_users, second_place_users, third_place_users

def add_points_to_winning_users(first_place_user_arr, second_place_user_arr, third_place_user_arr, database_var):
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

def add_points_to_users_who_voted_well(user_arr, comp_week_and_year, database_var):
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

