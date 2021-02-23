
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

I eventually changed and refactored the flask-paginate functionality into my function paginated_and_pagination_args() which worked for all pages. 
Thanks to [Ed Bradley](https://github.com/Edb83) & Kevin from Code Institute for some initial pointers on how to go about doing this.

### Issue 2 
In order to set the values of the search form to the values searched for by the user, I needed to pass the template variables from the pages to the javascript file.
```category``` & ```awards``` held the values of the user's search and because they represent one of multiple choices, I could not refer directly to the value in the form
field as with ```query```. 

An easy option would be to write inline JavaScript that used the template variables, however my CSP would not allow for that, without voiding the protection afforded by it.

### Fix 2
I created two hidden elements that printed the values of ```category``` and ```awards``` to the template, and then I was able to target those elements with JavaScript in my 
external script file, without altering my CSP.

## winners()

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

### Issue 2
As some photos are vertical and some are horizontal, the placement of the awards badge on the overlay was too far away and missing the image completely on vertical
images. I needed a way to set the left: position of the award depending on whether the image was vertical or horizontal. Another related issue was the width 
attribute of the winning images. For landscape images I needed the width to be the full 100%, but for vertical images I needed it to be maximum 100%, as the 
max-height was set at 600px and by forcing the image to take up 100% of the space, much of the image would be hidden. 

### Fix 2
I used the following function to conditionally set extra classes for the horizontal images, this was vertical images were the default and I could change the max-width: 100%
to width:100%, and I set the particular left: position for the horizontal awards as well. 

                function verticalOrHorizontalAwardImage(){
                    let photos = document.querySelectorAll('.award-photo')
                    photos.forEach(photo => {
                        if (photo.width > photo.height){
                            photo.classList.add('award-photo-horizontal')
                            let awardBadge = photo.nextElementSibling.children[0]
                            awardBadge.classList.add('award-horizontal')
                        }
                    })
                }

### Issue 3
The above worked, except sometimes the styles didn't seem to apply, and only on multiple page reloads would they work.

### Fix 3

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

## edit_profile()

### Issue 1 
As part of the edit profile functionality I wanted to give users the option to delete any custom profile picture they had uploaded that they no longer wanted, but without
having to upload a replacement image. I wanted to include an X button on the update profile form which would allow them to just delete their current profile pic and
to revert to the default. 

This functionality proved a lot harder than imagined because unlike other input fields the "file" field could not automatically and easily link to the file object stored in the 
database, and there was no obvious way of determining how to display the delete button. 

### Fix 1
To solve this, I did a number of things: 

1. First in the edit_profile template, I checked whether the user had a custom profile photo uploaded and for users that did, I pre-filled the value field of the file input
with the unique filename of that image. 
2. Then I added a delete profile pic icon with a tooltip on hover to further explain its' purpose.
3. Then I devised a JavaScript function that listened for clicks on that icon and when clicked would create a hidden input field with a value to POST to my flask view.
This allowed me to write logic based on the specific situation whereby a user has a profile image and wants to just delete that image. 

I found that without this hidden field there were no attributes present and readable in the "file" input field that I could use to write conditional logic. 

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

### Issue 3
I wanted to implement a shuffle function for the vote page so that no one's images are given undue physical priority. For example if one image is always the first 
listed, and there are 50 images in the competition, which are paginated 10 per page, all images one page 1 are more than likely going to get more votes. 

### Fix 3
This proved harder than imagined to fix, first I created a shuffle function that took an array and return a random shuffle of that array, which I then passed to the paginate
function. The problem with this is that it shuffled each time a new page was loaded, so a photo might appear on page 1, but appear again on page 4. So this implementation
was useless. 

My next thought was to shuffle the images at source, so as they emerge from Mongo DB, that way, they would not be shuffled each time the page is loaded. But that resulted in 
the exact same issue, just with the shuffle happening at an earlier stage.

I realised that there is a logical inconsistency with merging a random shuffle with pagination that is difficult to overcome. If the shuffle is truly random then we are left with
the initial problem that once a page is "turned" a photo can be on two pages at once, and some images may not display at all. 

As a compromise, I decided to increase the number of images per page to 50 for the vote and compete pages, and although this might increase the page loading time, at lease the shuffle
will be consistent and all images will display, I also changed the location of when the shuffle function is called. 

                this_weeks_entries = list(mongo.db.photos.find(
                        {"week_and_year": date_time.strftime("%V%G")}))

                pagination, photos_paginated = paginated_and_pagination_args(
                                            this_weeks_entries, 50, "page", "per_page")

                photos_paginated_copy = photos_paginated.copy()

                photos_paginated_shuffled = shuffle_array(photos_paginated_copy)

                return render_template("compete.html",
                                    this_weeks_entries=photos_paginated_shuffled,

As you can see from the above code, first I paginated the image array and then I shuffled them, this way even if there are more than 50 images and some are unlucky enough to
be pushed to page 2 or further, at least within those pages the order is randomised on each page load. 

This functionality will do for the first iteration of the application, but there is definitely room for improvement. 

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

### Issue 2 

During testing for edge-cases, I found 3 different but related scenarios that were breaking the application:
1. If no one voted for any of the entries during the week and the awards() function ran on schedule on Sunday night, it was throwing an error. 
2. If one photo got all the votes - error. 
3. If one photo got say 6 votes, one photo got 4 photos and no other photos got votes, the application was awarding 1st & 2nd place logically, but then awarding 3rd 
place to every other entry.

### Fix 2

When refactoring the code to account for these edge-cases, I firstly included ternary operators in my definition of all the vote_count variables. Checking to see if 
the arrays that they rely on had any data in them, i.e. were not 0. If they were 0, I made the count equal null. Then in defining each subsequent array, I first checked 
to make sure the count they relied on was not null/None.

            first_place_vote_count = max(array_of_scores) if array_of_scores else None

            if first_place_vote_count:
                second_place_vote_array = [n for n in array_of_scores if n != first_place_vote_count]

            second_place_vote_count = max(second_place_vote_array) if second_place_vote_array else None
            if second_place_vote_count:
                third_place_vote_array = [n for n in second_place_vote_array if n != second_place_vote_count]

            third_place_vote_count = max(third_place_vote_array) if third_place_vote_array else None

            return first_place_vote_count, second_place_vote_count, third_place_vote_count

In the next part of the awards logic, I then added an extra check ```and first_place_votes_needed > 0:``` to each level to ensure that the votes needed 
to receive an award were greater than 0, and only if they were does the code assign awards to those images, and thus down the line, points to those users. 

            for entry in photo_arr:
                if entry["photo_votes"] == first_place_votes_needed and first_place_votes_needed > 0:
                    database_var.db.photos.update_one(
                        {"filename": entry["filename"]},
                        {'$set': {"awards": 1}})
                    user = database_var.db.users.find_one(
                        {"username": entry["created_by"]})

                    if user not in first_place_users:
                        first_place_users.append(user)

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

### Testing the "user must vote" rule contained in the awards() function. 

The rules of the competition state that if you enter the competition, you must vote for an image other than you own before 22:00PM on Sunday. Users who enter 
and who do not vote, will have their entry's points reduced to 0. This happens automatically as votes are counted. To test this, I created a dummy user called "Franny"
who entered an image of some leaves, and whose image got 100 votes between Friday night and Sunday at 22:00. Franny did not vote for any image. I then ran the awards()
function and made sure that her image's points were reduced to 0. 

#### Franny's user document before awards() is run:
<p align="left">
  <img src="static/images/testing/franny_before_awards().png">
</p>

#### Franny's photo document before awards() is run:
<p align="left">
  <img src="static/images/testing/franny-photo-before-awards().png">
</p>

#### Franny's user document after awards() is run:
<p align="left">
  <img src="static/images/testing/franny_after_awards().png">
</p>

#### Franny's photo document after awards() is run:
<p align="left">
  <img src="static/images/testing/franny-photo-after-awards().png">
</p>

As you can see the ```awards()``` function correctly reduced Franny's ```votes_to_use``` from 1 to 0, 
as well as reducing her photo "leaves"'s ```photo_votes``` from 100 to 0.
Leaves received more votes than any other photo in that competition, but did not win any awards, 
evidenced by its ```awards``` field remaining ```null```

## Testing the Vote logic

### Issue 1

An issue with the functionality of the application arose when I realise that during the voting period ( Friday at midnight until Sunday at 22:00 ) users could see
the points on the images by clicking into the photo details, or by looking at the profile "Votes" section of different users. Admittedly it would take some amount of independent 
focused research on behalf of the contestants, however if they did it, it would make it easy for a user to score points by voting for the image doing the best just before voting ends. 

### Fix 1 

I looked at the locations in the application that display points and I changed the code to make the points display only occur for photos whose week_and_year field was not equal 
to the current week_and_year. For the photo details page this line was added to the template itself: 

            {% if datetime.strftime("%V%G") != photo.week_and_year %}
                <h3 class="photo-points col s10 offset-s1 center-align">{{photo.photo_votes}} points</h3>
            {% endif %}


For the user profile page, I confined the logic to the view rather than the template:


        if photos_voted_for_array != []:
        for img in photos_voted_for_array:
            photo_obj = list(mongo.db.photos.find({"_id": img}))
            for photo in photo_obj:
                if photo["week_and_year"] != datetime.now().strftime("%V%G"):
                    photos_voted_for_objs.append(photo)  

Where ```photos_voted_for_objs``` was the array passed to the template.  

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

### Flask-Talisman 

#### Issue 1

I installed flask-talisman to protect against a variety of common security threats and when I reloaded my application, it had changed it somewhat:

<p align="left">
  <img src="static/images/issues/talisman1.png">
</p>
<p align="left">
  <img src="static/images/issues/talisman2.png">
</p>

#### Fix 1

I gleaned that Talisman was not allowing the Materialize framework to do its job and it 
transpired that it was blocking a number of domains from sending data to the site, which of course
is what it does. To allow in the sources of: Google Fonts, Materialize and jQuery, as well as my own 
JavaScript files, I had to explicity tell Talisman that those sources were ok. I did so as below with a 
little help from Stack Overflow (attributed in README.md)

        csp = {
            'default-src': [
                '\'self\'',
                'cdnjs.cloudflare.com',
                'fonts.googleapis.com'
            ],
            'style-src': [
                "\'self\'",
                'cdnjs.cloudflare.com',
                'https://fonts.googleapis.com'
            ],
            'font-src': [
                "\'self\'",
                "https://fonts.gstatic.com"
            ],
            'img-src': '*',
            'script-src': [
                'cdnjs.cloudflare.com',
                'code.jquery.com',
                '\'self\'',
            ]
        }

        talisman = Talisman(app, content_security_policy=csp)

This code adds an extra layer of security as it allows in images from all sources, within the parameters of the 
security measures I have already set up for images, but it does not allow any other media files. 