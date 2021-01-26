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
    - Photos need to be no larger than a certain size
    - Files uploaded need to be photos - (limit to .jpg or .png)?
    - Photos need to be a min resolution? 

## Security Considerations

### WTF-forms & CSRF Protection

