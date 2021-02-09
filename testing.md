
## browse()

### Issue 1

When developing my search / filter method, I wanted to give users the option of filtering their searches by keywords, categories and awards. 
The default mongo db index $search method for $text indexes is an 'or' search, i.e. if a user types in "Mountain" and then chooses "Landscape" from
the category dropdown menu, the search would return all photos entered into landscape competitions AND all images with mountain as a keyword. 
What I wanted is an "and" search, so that the search would return all images entered into landscape competitions with "mountain" as a keyword.

### Fix 1

Unfortunately the mongoDB documentation was of no use here. It doesn't cover "and" searches, thankfully stack overflow had the answer. Separating 
the search terms with "" works as below: 

                { "$search": "\"mountain\" \"landscape\"" }


### Issue 2 

When integrating pagination with my search function, it worked fine for the regular browsing page, where all images are displayed. The full number of photos returned 
were correctly divided up and pagination laid out, however when the search was filtered, the pagination stopped working once a user clicked to go to page 2. The initial pagination
worked correctly, but then page 2 would just return all the images again, unfiltered. 

### Fix 2

This took a lot of re-shuffling and with help from [Ed Bradley](https://github.com/Edb83) & Kevin from Code Institute. 


## recent_winners()

### Issue 1
When testing this function and page over the course of a week, all was working well until suddenly I was getting a 504 Gateway Time-out error message. 
<p align="center">
  <img src="static/images/issues/recent_winners_timeout.png">
</p>

### Fix 1 
I used a number of print statements in the function and discovered that the issue was here:

       
        if day_of_week in range(0,5) or day_of_week == 6 and hour_of_day < 22:
            images_to_display = get_winning_images_by_week_and_year(last_week_and_year)
            last_mon = week_before
            while last_mon.weekday() != 0:
                last_mon = last_mon - timedelta(days=1)

I had mistakenly used range(0,5) thinking that would *include* 5 (or weekday() == saturday), but range is not inclusive of the outer number, so it was ignoring
Saturday, and thankfully I was testing it on a Saturday, otherwise it probably would have gone unnoticed. Changing range to ```range(0,6)``` solved the issue. 

## get_photo() 

### Issue 1

This is the photo detail page, and I wanted to dynamically set the "back to..." button to check what the source url was and then insert a link to go back to that particular page. 

This was coded using request.referrer in the get_photo() route and then that was passed into the template using a "source_url" variable, which was then reference conditionally for example:

            {% if "profile" in source_url %}

            <a href="{{url_for('profile', username=photo.created_by)}}"><i class="fas fa-long-arrow-alt-left"></i>Back to {{username|capitalize}}'s Profile</a>
            
            {% elif "compete" in source_url %}

And so on... However if the user is logged in and viewing her/his own photo, they have the option of editing that photo's details. They see an "edit photo" button which brings them to the edit_photo
view, they edit a form that is pre-filled with the photo's details and click save. This then brings them back to the photo detail view. With the source_url code in the template, the act of them saving
changes to their image was causing the following error: 

<p align="center">
  <img src="static/images/issues/edit-photo-error.png">
</p>

### Fix 1

Some investigation led me to the fact that "POST" methods do not have a "source_url" insofar as the request.referrer from a POST is None, which was throwing this error. As a fix, I added another IF statement
to the template, first checking IF there is a source_url, and if there is not, then it's most likely coming from the edit_photo view and does not require a "back to.." link as the user can just click on the "Edit photo
details" button again.


## compete() function

### Issue 1 & Fix 1

The difficulty here was in using gridfs to store the larger file type of a photograph. Mongo does not store images in their db directly, so I had to understand 
how the request object and gridfs work together to store files. 

        if 'photo' in request.files:
            photo = request.files['photo']

            file_id = mongo.save_file(photo.filename, photo)

The above code takes the file input with its name set to 'photo' from the request.files and sets that as a variable called photo. I then stored the result of saving that 
to mongo db in a variable called file_id which I was then able to add to the photo object as an attribute called file_id. Since this string is unique I could then reference it as below
in order to add that specific photo's _id to the user's photos array. Hence all three collections are connected: the photos, the users and the files.

            photo_to_add_to_user = mongo.db.photos.find_one({"file_id": file_id})
            photo_id_to_add_to_user = photo_to_add_to_user["_id"]


### Issue 2:

The method of retrieving and displaying files that gridfs uses made this functionality more complicated, as the send_file() function that it relies on, only uses the file's "filename"
to send the file. This was frustrating because it is quite possible that there be more than one photo with the same filename. 'photo.jpg' or the like. So as I had to rely on the filenames, 
instead of on the objectIds as I'd hoped, I needed a way to make every filename completely unique. 

### Fix 2:

I achieved this by creating a new filename, using the suffix (.png, .svg, .jpg) and then once the save_file() method had returned the file_id into my variable of the same name, I used a str() of 
this to create a filename for each image that is completely unique and identical to their file_id. I then updated the file in mongo to have this new filename. 

            filename_suffix = photo.filename[-4:]
            new_filename = str(file_id) + filename_suffix
             
            mongo.db.fs.files.update_one({"_id": file_id},
                                    { '$set': {"filename": new_filename}})



- used a @context_processor to inject datetime into all templates - so I don't need to keep passing it around.



## base.html template

### Issue 1 
I needed a way to reference datetime in my navigation html and because the navigation html code was written in the base.html template, there was no route leading to it that I could use to include the datetime 
variables. 

### Fix 1 

I discovered @app.context_processor functions which run before the templates are rendered and allow you to inject things into the entire application. I used a context_processor for datetime. 

## Integrating Email functionality

### Issue 1
I got the email working after collating many online tutorials, but the "sender" information that I was extracting from the form was not translating over to gmail where the emails could be read. So it looked like all 
the emails were being sent from the Snapathon gmail account, as below:

<p align="center">
  <img src="static/images/issues/email-issue2.png">
</p>


### Fix 1
I realised that this is expected behaviour, because it is the connected gmail account sending emails to itself. To pass on the sender information, I added the form sender into the message that gets delivered to the app's gmail, as below: 

            if request.method == "POST":
                with app.app_context():
                    msg = Message(subject="New Email From Contact Form")
                    msg.sender=request.form.get("email_of_sender")
                    msg.recipients=[os.environ.get('MAIL_USERNAME')]
                    message = request.form.get("message")
             -->    msg.body=f"Email From: {msg.sender} \nMessage: {message}"
                    mail.send(msg)
                    flash("Email Sent!")
                    return redirect(url_for('home'))

### Issue 2 
The email functionality was working fine in the local port, but when deployed to Heroku I was getting the following error: 

<p align="center">
  <img src="static/images/issues/email-error.png">
</p>

### Fix 2
I had not inputed my new mail configuration variables in the Heroku config vars input area. Once I did it connected perfectly.

## awards()

### Issue 1 

When the awards function was run, it was over awarding certain users. During testing I ran a number of simulations and found that 4 users in particular were being awarded
an illogical number of points. Everyone else was being awarded the correct number of user_points, and the awards were working correctly as far as the photos were concerned. 

### Fix 1 

I ran through the function line by line and using print() statements on every logical segment, I discovered that the users in question were being added twice to the valid_users
array. Eventually I realised that in testing the application I had uploaded more than the one allotted photo for each of those users and since the function is based on an assumption
of 1 entry per user per week, that fact was breaking the code. I deleted the offending extra images and it worked well again, but there is definitely room to refactor that code *if* 
I decide that the application could host more than a single competition per week, or if users are allowed upload more than one image per competition. 

## Error Messages

### Issue 1
413 Errors (request entity too large / Payload too large) were not passing to the error.html template to render correctly. In development I was getting a message 
saying the port was unresponsive. 

### Fix 1 
Using print() I was able to see that the error view was working correctly right up until the rendering of the template. If I switched from rendering a template to just 
returning the error message like this:

            @app.errorhandler(413)
            def payload_too_large(e):
                error = 413
                error_msg = "Sorry, but the file you're trying to upload is too large."
                return error_msg, 413

It worked fine, but I wanted my nicely styled error page to load, as with all other errors. Especially since this particular error would likely be thrown a lot as users try 
to upload large files. 

After some research I found the following note in the Flask documentation:

            Connection Reset Issue
            When using the local development server, you may get a connection reset error instead of a 413 response. 
            You will get the correct status response when running the app with a production WSGI server.

I checked it on the deployed version and it still wasn't working. (FINISH)

# Testing the Automated Processes

The awards() function runs automatically on a Sunday evening at 22:00 - obviously to test this, I had to change those settings and run it manually. 

Firstly I created a selection of dummy users and for each of them I entered 1 image into a dummy weekly competition. I then made each user vote for various images and recorded
who voted for which image. I created two spreadsheets: one recording what the user actions were and expected results, the other recording the photograph votes received and expected
awards. Basically a manual version of what automated tests would achieve. 

#|Photo Title | Votes Received | Photo Created By | Users Who Voted For Photo | Expected Awards | Actual Awards
---|------------ | -------------|--------------|----------------------|------------|--------
. | __*Test 1*__ 
1.| "Sunset of Fire"  | 7 | Eoghan | Anne1, Cathy, Frederick, Loretta, Monica, Orlaith, Derrick | 1st place | 1st place
2.| "Best Beach Ever"  | 3 | Frederick | Eoghan, Georgina, Horatio | 2nd place | 2nd place
3.|  "Lightening Attack"  | 3 | Ignacio | Barbara, Stephanie, Quentin | 2nd place | 2nd place
4.|  "Peace & Quiet"  | 2 | Derrick | Ignacio, Patricia | 3rd place | 3rd place
. | __*Test 2*__ 
1.| "Sunset of Fire"  | 7 | Eoghan | Anne1, Cathy, Frederick, Loretta, Monica, Orlaith, Derrick | 1st place | 1st place
2.| "Best Beach Ever"  | 3 | Frederick | Eoghan, Georgina, Horatio | 2nd place | 2nd place
3.|  "Lightening Attack"  | 3 | Ignacio | Barbara, Stephanie, Quentin | 2nd place | 2nd place
4.|  "Peace & Quiet"  | 2 | Derrick | Ignacio, Patricia | 3rd place | 3rd place

As you can see the awards and points logic functioned perfectly in both tests, but as below illustrates this manually testing strategy caught 
an inconsistency with the user_points. Once I solved it, test 2 ran correctly. 


#|User | User Photo | Photo User Voted For | Expected User Points From Awards | Expected User Points From Voting | Expected User Points Total | Actual User Points Total
---|------------ | -------------|--------------|----------------------|------------|--------|-----
. | __*Test 1*__ 
1.| Derrick | "Peace & Quiet" | "Sunset of Fire" | 3 | 3 | 6 | 6
2.| Eoghan | "Sunset of Fire" | "Best Beach Ever" | 7 | 2 | 9 | _*11*_
3.| Frederick | "Best Beach Ever" | "Sunset of Fire" | 5 | 3 | 8 | _*11*_
4.| Ignacio | "Lightening Attack" | "Peace & Quiet" | 5 | 1 | 6 | 6
. | __*Test 2*__ 
1.| Derrick | "Peace & Quiet" | "Sunset of Fire" | 3 | 3 | 6 | 6
2.| Eoghan | "Sunset of Fire" | "Best Beach Ever" | 7 | 2 | 9 | 9
3.| Frederick | "Best Beach Ever" | "Sunset of Fire" | 5 | 3 | 8 | 8
4.| Ignacio | "Lightening Attack" | "Peace & Quiet" | 5 | 1 | 6 | 6






I created two development functions clear_user_points() & clear_all_awards(), to quickly and easily clear the slate and re-test the awards() function as many times 
as needed. 

        def clear_user_points():
            all_users = list(mongo.db.users.find())
            for user in all_users:
                mongo.db.users.update_one({"username": user["username"]}, {'$set': {"user_points": 0}})
            print("All user points zeroed")


        def clear_all_awards():
            all_photos = list(mongo.db.photos.find())
            for photo in all_photos:
                mongo.db.photos.update_one({"filename": photo["filename"]}, {'$set': {"awards": None}})
            print("No photo has any awards now.")

This strategy helped me catch one issue that arose not because of the code logic, but because I had allowed 4 users to upload more than one image. 

# Input Validation

## Registration Form

Various validations were employed to ensure the registration form saved the correct inputs to the database. 

1. The 'required' attribute was added to *all* inputs to ensure that no blank fields are returned. 

2. For usernames the 'min-length' attribute was set to 5 and the 'max-length' to 25.

3. For passwords, the 'min-length' attribute was set to 6 and the 'max-length' to 25.

4. For the email input the 'pattern' attribute was employed to use regex to ensure only valid email formats are entered. 

        pattern="^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$"

    This is not a failsafe regex for email, however it will suffice for the first iteration of this application. 

5. On the backend side of things, both usernames and emails are checked against existing data in the database to ensure neither have already been registered. 

6. Also on the backend, the password & password confirmation fields are checked against each other, to ensure they match and to protect against typos. 

## Compete form for uploading user's photos into competition

- Validations:

### Limiting the maximum size of uploaded files

This was achieved using a config instruction: ```app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024``` This effectively stops any request body that is larger
than 1MB. Flask automatically halts any large requests and returns a 413 status code. This is a useful validation for two reasons: it stops overly massive images from being uploaded
that would slow the application down, and it stops a decent amount of potential security threats where hackers upload malicious programmes. 

### Limiting the type of files that can be uploaded 

This was achieved again by using a config instruction: ```app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif', '.svg', '.jpeg']``` Which was then referenced in 
the compete() method for uploading photos. When the file is received but before it is saved to the database, the compete() function checks if it is one of these acceptable 
file types and if not, it throws an error: 

        file_extension = os.path.splitext(photo.filename)[1]
            if file_extension not in app.config['UPLOAD_EXTENSIONS']:
                abort(400, "Sorry that file extension is not allowed. Please reformat your image to one of the following acceptable file types: jpg, svg, jpeg, png or gif")

This further limits the ability of users with malicious intent to upload damaging files to the database.

### Sanitizing the filenames for further security 

Another security validation incorporated is the werkzeug ```secure_filename``` util. This is applied to the uploaded photo filename before it is saved to the database, to ensure that any
dodgy filenames e.g. /paths/to/os/systems/etc.jpg are sanitized before they can do any damage. 




## Security Considerations

### WTF-forms & CSRF Protection

