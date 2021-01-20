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

