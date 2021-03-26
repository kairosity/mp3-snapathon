
        

mongo.db.users.update_one({"username":username}, {'$set': {"username": form_username }})
mongo.db.photos.update_many({"created_by": username}, {'$set': {"created_by": form_username}})
session["user"] = form_username
mongo.db.users.update_one({"username":username}, {'$set': {"email": form_email }})


mongo.db.users.update_one({"username": username},{'$set', {"password": generate_password_hash(request.form.get("new_password"))}}) 


if check_password_hash(user["password"], request.form.get("current_password")):
    print(form_new_password)
    print(form_new_password_confirmation)
    if form_new_password == form_new_password_confirmation:
        mongo.db.users.update_one({"username": username},{'$set', {"password": generate_password_hash(request.form.get("new_password"))}}) 
    else:
        flash("Your new passwords do not match, please try again.")
        return redirect(url_for('edit_profile', username=username))

else: 
    flash("Sorry, but your current password was entered incorrectly. Please try again.")
    return redirect(url_for('edit_profile', user=user))


------------------------------



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


 # for entry in this_weeks_entries:
    #     if entry["photo_votes"] == first_place_vote_count:
    #         mongo.db.photos.update_one(
    #             {"filename": entry["filename"]},
    #             {'$set': {"awards": 1}})
    #         user = mongo.db.users.find_one(
    #             {"username": entry["created_by"]})

    #         if user not in first_place_users:
    #             first_place_users.append(user)
    #             photo = mongo.db.photos.find_one(
    #                 {"filename": entry["filename"]})

    #         if photo not in first_place_photos:
    #             first_place_photos.append(photo)

    #     elif entry["photo_votes"] == second_place_vote_count:
    #         mongo.db.photos.update_one(
    #             {"filename": entry["filename"]},
    #             {'$set': {"awards": 2}})
    #         user = mongo.db.users.find_one(
    #             {"username": entry["created_by"]})

    #         if user not in second_place_users:
    #             second_place_users.append(user)
    #             photo = mongo.db.photos.find_one(
    #                 {"filename": entry["filename"]})

    #         if photo not in second_place_photos:
    #             second_place_photos.append(photo)

    #     elif entry["photo_votes"] == third_place_vote_count:
    #         mongo.db.photos.update_one(
    #             {"filename": entry["filename"]},
    #             {'$set': {"awards": 3}})
    #         user = mongo.db.users.find_one(
    #             {"username": entry["created_by"]})

    #         if user not in third_place_users:
    #             third_place_users.append(user)
    #         photo = mongo.db.photos.find_one(
    #             {"filename": entry["filename"]})
    #         if photo not in third_place_photos:
    #             third_place_photos.append(photo)

    def test_function():
    mongo.db.users.update_one({"username": "apschedulertestuser"}, {'$inc': {"user_points": 1}})
    print("User points incremented")


Was a template called photos.html
    {% extends "base.html" %}
{% block content %}
    {% for photo in photos %}

        {{ photo.photo_title }}
    
    {% endfor %}

    {{ pic_to_show }}

{% endblock %}


<!-- Materialize Icons CDN -->
    <!-- <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"> -->