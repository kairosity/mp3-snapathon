# Snapathon!
## Shoot, Compete, Rate, Repeat!
## Code Institute Milestone Project 3

Snapathon seeks to gamify photography. It is a photo-sharing application that enhances the user experience with competition. 

# Table of Contents

# UX
## User Stories

This application is targeted towards photography enthusiasts. Anyone who takes photographs for fun and loves to share them with others.
Other photo sharing platforms have indicated a massive opportunity for an application that successfully gamifies photography and this application aims to achieve that.
Snapathon aims to entice users to register and upload their images in weekly competitions pitting their best images against others'.

## First Time User Stories

### *As a first time user / prospective user I want to be able to...*

- Easily understand the purpose of this web application. 
- Quickly and easily understand how to navigate and use the application.
- Read the competition rules and how to enter and have these be clearly explained.
- View an application that is visually and creatively appealing and physically easy to look at. 
- Browse images entered by other people to get a sense of what the application does and how it runs. 
- Filter my browsing by keyword, or by selecting only images that have won awards.
- View the most recent winning images and see how many points they got and who they were created by.
- Register an account using my email and password. 
- Confirm my password when registering, to ensure that I don't enter a typo.
- Contact the application owner if I have any questions. 

## Returning User Stories
### *As a returning user I want to be able to...*

#### Login & Profile 
- Login to the application.
- View my profile.
- Upload an avatar. 
- Edit my account information - change my password, username or avatar.
#### Competition
- Enter an image for competition. 
- Edit the details of the image I entered for competition. 
- Delete the image I entered for competition.
- View all the images that have been entered into this week's competition.
- Use my vote to vote for the image I think is the best.
#### Profile View & Functionality
- See how many points I have won.
- See all the images I've entered into competition.
- View my award-winning images separately from the main collection. 
- View all the images I've voted for.
#### Other 
- View other user profiles to see their images, who they've voted for and how many points they've won.
- Browse all the images entered from all competitions.
- Filter my browsing by keyword, or by selecting only images that have won awards.
- View the most recent award-winning images and see how many points they got and who they were created by.

## Accessibility User Stories

- As a user who is colourblind, I want the colours and design elements used to employ sufficient contrast so that any visual cues are easily apparent.
- As a keyboard user, I want to be able to navigate the application using the keyboard. 
- As a user using screen reader technology, I want my screen reader to describe the page elements correctly.


### *As the application creator I want to be able to...*

- Create and maintain a user-friendly platform allowing photography enthusiasts to compete with each other and to inspire each other with excellent images. 
- Ensure that the application is as accessible as possible to include as wide a variety of users as possible.
- Create a competition application that is re-usable for other fields, if this one proves popular. 
- Eventually introduce a profit-earning aspect to the application, perhaps by monetizing awards for professional photographers. 
 
#### back to [contents](#table-of-contents) 

--- 
 # Strategy

## Project Goals
As already touched upon, the aim with this project is to create a usable photography competition application that enhances the quality of photography users display on the internet. 
As a professional photographer, I would love to use an application where the emphasis is less on sharing personal images and more on sharing images based on the quality of their photography.
High quality cameras on phones and mobile devices have made photography hugely accessible for everyone, however there has also been a marked drop in the quality of the photography people post online. 

The main goal for this application is to create an interface and an environment that encourage great quality images. That encourages looking for good light and interesting subjects.

My application goals summarized: 

- Create a workable photography competition application that is fun and intutive to use. 
- Gamify photography (both amateur & professional), and thus encourage high quality imagery as opposed to the current trend of low-quality personal images.
- Make the content publicly accessible / viewable, so as to encourage users to register and use the application. 
- Create a loyal community of users who regularly engage and compete against each other for points and bragging rights. 
- Allow users to easily register and then login and out of the application and have them be able to store and retrieve their data easily.
- Create an application that is easy to use and fully responsive on all major screen sizes and types.
- Create an application that might be monetized in the future once it develops a decent sized following of loyal users.

## Target users
The target users for this application are anyone who enjoys photography as a pasttime or professionally. There are no restrictions on tools or technology used to take photographs, a mobile phone camera is just as valid as a high-end dSLR or mirrorless. 
The importance is placed on the image itself, and how much that image speaks to its audience. The target market is also not limited by age or any other demographic, other than they will obviously be somewhat computer & technically literate.

## Research / Background to the application
I am a professional photographer, working in many different photographic fields for over a decade and I have a love/hate relationship with online photography competitions. Competitions based on the determination of a "panel of judges" 
can be overly subjective and these panels are usually comprised of the site owner who may or may not have any authority on the matter. I wanted to create a democratic competition where the competitors are also the judges and therefore the final awards are 
as meritocratic as possible. Especially since one of the more innovative aspects of this application is that users will be awarded points not only when their images win, but also if they vote for any of the top 3 placed images. In this way, users will be encouraged to actively vote for what they think are the best images, and not selectively based on strategizing. 

Ideally, there could also be a professional photographer offshoot to this application and such determinations would hold even more weight, the professional aspect could also be a sub-category worthy of future investigation. 


 
## Value to the user 

The main value is in providing an interesting photography application that does not exist in this form yet. It is an innovative platform that
promotes quality photography. Furthermore the idea does not have to be limited to photography, it could be widened to include other art forms, or indeed any arena that could 
feasibly accommodate an online competition. Essentially its value could expand to encompass an ever-widening user base.

#### back to [contents](#table-of-contents) 
---

 # Scope
 ## Core Theme

The keystone idea for this application is to create a **_democratic online photography competition that runs once a week._**

Some of the features developed with this aim in mind are listed below: 

 ## Feature Ideas Table

 #|Opportunity/Potential Feature | Importance | Viability | Score
---|------------ | -------------|--------------|------------------
. | __*USER REGISTRATION FUNCTIONALITY & FEATURES*__ 
1.| Register as a new user  | 10 | 10 | 20
2.| Register using an email address | 4 | 6 | 10
3.| When registering be able to confirm password | 5 | 6 | 11
4.| Register a username as separate from login email | 6 | 9 | 15
5.| Receive an email link to confirm a genuine email address |3 | 3 | 6
. | __*USER LOGIN FUNCTIONALITY & FEATURES*__ 
1.| User logs in with email and password |10 | 9 | 19
2.| When a user logs in they are brought to their profile page |6 | 10 | 16
3.| A session is started and the user's login status is remembered as they use the application |9 | 9 | 18
4.| When a user is logged in they can enter competitions and vote.  |10 | 9 | 19
5.| A user has to be logged in, in order to enter the competition or vote. |10 | 9 | 19
. | __*USER PROFILE FUNCTIONALITY & FEATURES*__ 
1.| A user's profile page shows all photos they have entered into competition. |4 | 4 | 8
2.| The profile page shows all the photos that user has voted for. |7 | 7 | 14
3.| The profile page displays the user's total points. |9 | 8 | 17
4.| The profile page displays badges the user has won by engaging with the application in various ways. |4 | 5 | 9
5.| A user can change their username, email address & password |7 | 8 | 15
6.| Other users can comment on individual photos on the profile page.  |2 | 2 | 4
7.| Other users can like photos on the profile page |1 | 2 | 3
8.| A user's total points score is displayed next to their username. |8 | 7 | 15
. | __*COMPETITION FUNCTIONALITY & FEATURES*__ 
1.| Users can upload images to competitions. |10 | 10 | 20
2.| Users can edit their uploaded image details. |8 | 9 | 17
3.| Users can delete their uploaded images. |8 | 8 | 16
4.| Users can easily view images they've uploaded for competition |8 | 9 | 17
5.| Users may upload entries for competition between Monday & Friday |7 | 8 | 15
6.| Voting days and time are on Saturday & Sunday until 22:00PM  |7 | 8 | 15
7.| Users vote by clicking a vote icon under their choice of image. |7|7|14
8.| Awards and points are automatically awarded and announced on Sunday at 22:00PM |7 | 8 | 15
9.| There is a page where the most recent winning images are displayed along with the points they've received. |8 | 8 | 16
10.| Points are awarded to users both if they win and if they vote for a winning image. |7 | 7 | 14
11.| Different categories of competitions could run simultaneously, allowing users to enter more than one competition per week. |3 |5 | 8
12.| Competitions could be sponsored by specific brands of camera, or lenses or gear. |2 | 4 | 6
. | __*OTHER FUNCTIONALITY & FEATURES*__ 
1.| Users can follow other users |3 | 2 | 5
2.| Images can be browsed by registered and unregistered users. |9|9|18
3.| Browsed images can be filtered by keyword or by awards. |7|7|14
4.| If an image is clicked on, a larger version of that image is shown including all its uploaded details and technical specs. |5|5|10

 ## List of Final Features for 1st Iteration of the Application

In order to create a working online competition the minimal viability feature list does not allow for too much compromise. There are certain features that must 
be implemented if the application is to work at a fundamental level. Those are the features I decided to run with, the MVP features:

1. The ability of a user to register an account using an email address and a password.  
2. When registering to be able to confirm the new password to avoid typos.
3. To register a unique username as separate from the registered email.
4. The ability to login using their email and password. 
5. When a user logs in they are brought directly to their profile page.
6. They can enter competitions and vote when they are logged in, and only registered and logged in users can compete or vote.
7. A user's profile page shows their uploaded photograph entries, other user's photographs they have voted for and any photographs of theirs that have won awards.
8. A user's profile page also shows their total number of points. 
9. A user can change their username, email address & password.
9. A user can upload images to the weekly competitions, and they can edit or delete those images at any point. 
10. If a user uploads an image they get a single vote which they can use to vote for any image that is not theirs. Voting takes place on Saturday & Sunday until 22:00PM.
11. Users can vote by clicking the "Vote" button under their photo of choice.
12. Points & awards are calculated automatically on Sunday evening.
13. The Browse page allows registered and unregistered users to look through the entire collection of uploaded images and filter them by awards or keywords.
14. Anywhere an image is displayed, it can be clicked on and the user will be brought to that photograph's view page which displays more detailed information about the image as well as a larger version of the photo.

These are what I determined are the very basic level features to make the competition work, photo "likes", the ability of users to comment on images, the ability to follow other users, 
these are all features that are expected at some level, because most social media platforms follow such a similar formula, however because they are not essential to the working of this application, 
they can be implemented in future updates. The "long wow".

## Content requirements

As this application is heavily dependent on images, there are content-specific considerations to be addressed. The structure of the database is a top priority. MongoDB allows for scalability and because it is non-relational, there is considerable scope for 
trying things out to see what works best. The GridFS componenent of MongoDB is perfect for the first model of an image based application because it is so self-contained and relatively easy to use. Other options would have been to incorporate a third-party solution like S3 
or Cloudinary, and these remain viable options for future releases should the application grow, but I like the simplicity of having MongoDB take care of all the user data.

#### back to [contents](#table-of-contents) 
---

 # Structure

The structure is somewhat non-linear as there are multiple views and the views a user can see are determined by whether or not they are registered and logged in. 

## Consistency & Predictability

### Navigation
The application has been designed with predictable and known interaction features. Navigation is simplified with a fixed navbar along the top of the view at all times when on desktop, and a hamburger icon on mobile and smaller screens. 
The back button is never relied on. Design features, buttons, forms, switches, filters and search bars are all laid out and work in a consistent, predictable fashion. 

### Design
All content, typography and method of interacting with the application has been designed to ensure consistency across the board, there are no surprises in store for the user. 

All important content is visible on the page and when the user might need to scroll down this is made obvious for them. 

### Feedback
The application ensures that users get feedback after most important interactions. 

#### Flash Messages.
The application makes good use of the Flash methods to deliver messages to the user. They are used to tell the users when they have done something wrong, or why something won't work, as well as delivering positive feedback when the user 
correctly does what they were expected to do correctly.
Here are all the flash message used in the application for great user feedback and assurance:

- 
- 
- 

#### Form validation messages
Alongside the Flash messages, the Materialize library has some great in built form validation messages that are delivered to the user to tell them what is expected of them when filling out the various forms on the site. 

#### 404 error pages 

Custom 404 pages .....


## Information Architecture

This application combines both linear and non-linear narratives. For first time users there is an obvious progression, they are encouraged to register but before they do so they can explore the application to a limited degree. 

Once they've registered they can enter an image into a competition, or they can browse other images, or they can view their own profiles or the profiles and photographs of other users. 
There is no set linearity to these options, but as the options are limited to a few main pathways, the application doesn't get overly confusing and it remains straightforward and intuitive. 

When a user selects an image to view its details, a hub and spoke structure is employed insofar as a "back to ... " link is added in addition to the omnipresent navbar option for the user. 

This "back to ..." is coded to be conditional and will refer to the user's source url page. So if the user arrived at the photo detail page from clicking on an image in "Recent Winners", it will read "Back to Recent Winners", likewise if they 
came to the photo detail page from a user profile, it will read "Back to username's profile". This adds a level of intelligence to the application that will further assure the user. 


## Users Not Logged In / Guest Users 

### Landing Page: 

1. Application landing page. - the first thing a user sees are two options: login / register. 
2. If they choose to scroll down the page to learn more, the application purpose and rules of competition are clearly outlined. 
3. Further scrolling on that page brings them to the contact form.

The first view is designed in this manner to encourage information-seeking behaviour and provide answers within the first interaction. If the user arrives at the page and is immediately enticed to sign up, perfect, 
otherwise they can scroll down and understand a little more about what the application does. 

Ideally, users will choose to register at this juncture, however should they choose to continue browsing, the navigation options at this level are as follows:

### Navigation (not logged in): 

1. Home - The landing page where the rules of the competition are outlined. 
2. Recent Winners - This is where the top 3 images from the last competition are displayed.
3. Browse - All current and past entries can be viewed and filtered using keywords or award status. 
4. Login - Registered users can navigate here to login. 
5. Register - Unregistered users can navigate here to register. 
6. Contact Us - This directs the user back to the bottom of the landing page, where the contact form is located. 

For our target users who have yet to register, I have divided their user flows into two categories: 1. The Direct Route 2. The Exploratory Route. These are illustrated below:

<p align="center">
  <img src="static/images/user-flow/direct-registration-user-flow.png">
</p>

<p align="center">
    <img src="static/images/user-flow/exploratory-user-flow.png">
</p>

Whichever route the user takes, the end goal is registration. I have included guest (non-registered) access to "Recent Winners" and "Browse" specifically to cater for users who want to 
feel the product before they commit. The online version of consumers picking things and turning them over in shops. For tactile, more suspicious consumers, these exploratory routes to the business 
goal are important to assure them the product is sound. 

### Navigation (logged in):

1. Home - Landing page, available if the user wants to re-read the competition rules. 
2. My Profile - When a user logs in they are redirected to this page where all their entries, votes and winning images are viewable.
3. Compete / Vote - This link will read "Compete" between Monday & Friday and "Vote" between Saturday & Sunday. The compete page will show the current week's entries as well as a button to enter an image, and another link to review the rules. 
4. Vote - This view will display all of the current week's entries all of which have "Vote" icons, clicking on any of the images will bring the user to the photo details view, where they can view a larger version of the image as well as all the photo details. 
5. Recent Winners - This is where the top 3 placed images from the last competition are displayed, along with the votes they received.
6. Browse - All current and past entries can be viewed and filtered using keywords or award status. 
7. Logout - Users can logout by clicking this link. 
8. Contact Us - This directs the user back to the bottom of the landing page, where the contact form is located. 

### Recent Winners 

This is a simple page where the photographs coming in 1st, 2nd & 3rd from the last competition will be displayed alongside their creator's username and the number of votes they won. 
Clicking on any of the images will open the image view page where further details of the photograph can be seen. 

### Browse

This is the full collection of images uploaded to the application. They are displayed as medium-sized thumbnails and users can click on any of them to bring them to the image view page, where further details about the photograph can be viewed. 
Users can also choose to filter the images displayed by using a search bar, where they can search by keywords. They can also choose to view only images that have won awards. 

### Login 

This is where users who have registered can login to the application. They can login using their email address.

### Register

This is where first time users can register to become members. They fill in a username, email address and password. They are asked to type in their password twice. 




## Interaction Design 



#### back to [contents](#table-of-contents) 
---

# Skeleton


#### back to [contents](#table-of-contents) 
---

# Surface



#### back to [contents](#table-of-contents) 
---

# Features

## Browse Images

- When a user searches for a particular sub-section of images, the returning page scrolls down automatically to feature the images rather than the search box. 

## Register as a new user. 

When users sign up they must enter a username that must be unique, an email that must also be unique and a password. 

They are asked to confirm their password, which is an important feature to prevent a user from accidentally misspelling a password and then not being able to sign in.

Other validations/features present on the registration form are:
- The username must be at least 5 characters long. 
- The email address must be of valid email format. (Regex based so not foolproof)
- The password must be at least 6 characters long.
- Both password fields must be identical and the passwords are case sensitive. 
- If the username or email address has already been registered, the registration will not go ahead and the user will be instructed as to the reason. 

## Login Functionality & Features 

When users login, I chose to ask for their email address rather than their username, because although both are unique, I think that users more easily forget their 
usernames, as they usually differ from application to application. 

Users enter their login email address and their password and are immediately brought to their profile page, where a welcome message is displayed referencing their username.

User passwords are hashed and then read by the Werkzeug 

### Profile Pages

A user's profile page is their calling card on the application.
Anyone whether logged in or not, can visit a user's profile page, either by entering the url: /profile/username 
Or by clicking in via an image on the site.

Features:

1. When a user is logged in, they see "My Profile" in the navigation.
2. Their profile page displays their username, their total competition points, their entries into competition, other user's photos that they've voted for and any of their images that have won
awards. 
3. When logged in and on their own profile page, a user will see an "edit profile" button which they can use to change any of their profile details including their password.





## Compete/Vote Page

The competition entry page and the vote page, share the same HTML real estate and they are conditionally programmed to appear and disappear depending what day of the 
week it is. 

The "Compete" Page is displayed (both the page and the link in the navbar) from Monday to Friday until 22:00PM. 

The "Compete" Page allows users to upload one image per competition, it asks for various image detail information.

At 22:00 every Friday, the compete html page is replaced by the Vote HTML page, and "Compete" becomes "Vote" in the navbar. 

Every Sunday at 22:00 the votes are automatically tallied and points assigned to images and users. Both pages' functionality ceases and the "Vote" page shows a message linking to 
the "Recent Winners" page where the winning images are displayed. It also contains a message giving users information about the next competition that will start at midnight on Monday morning. 



## Contact Form 

At the very bottom of the homepage is a contact form for getting in touch with the application creator. Direct lines of communication are important with an application such as this where
creative work is displayed. If users have any questions about functionality or copyright issues or questions, they need an easy way to get in touch. 

The contact form was built as a regular HTML form and the emails are sent to a Snapathon gmail account using flask-mail. I've also integrated the flask-wtf-csrf extension to protect against csrf attacks, by using a hidden
input field holding the csrf token. 

Users arrive at the Contact Form either by finding it organically by scrolling down the homepage, or by clicking on the link that is always in the navbar. 

The form fields are limited to an email: field and the message field as the kind of application this is, does not necessitate a long complicated email form. 

# Attribution

- [Adding class to li after page is loaded](https://stackoverflow.com/questions/40506710/adding-class-to-li-after-page-is-loaded/40506822#40506822)

    I used Rafal Cz.'s solution to this stack overflow question to change the active class on my navbar on desktop and mobile. 

- [CSS based responsive timeline](https://codepen.io/krishnab/pen/OPwqbW/)

    I used Krishna Babu's responsive CSS Timeline on my homepage to outline the competition schedule. 

- [Finding the date of the next Saturday](https://stackoverflow.com/questions/16769902/finding-the-date-of-the-next-saturday)

    I used Emmanuel's answer to this question to write user specific messages on my user's profile pages, when they login. 

## Unsplash Images Used in the Application

- <span>Photo by <a href="https://unsplash.com/@cdx2?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">C D-X</a> on <a href="https://unsplash.com/s/photos/yellow?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@ronaldcuyan?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Ronald Cuyan</a> on <a href="https://unsplash.com/s/photos/yellow?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@spencerdavis?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Spencer Davis</a> on <a href="https://unsplash.com/t/nature?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@stangad?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Davide Stanga</a> on <a href="https://unsplash.com/t/nature?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@sajad_sqs9966b?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Sajad Nori</a> on <a href="https://unsplash.com/t/nature?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@sickle?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Sergey Pesterev</a> on <a href="https://unsplash.com/t/travel?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@maxwhtd?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Max Whitehead</a> on <a href="https://unsplash.com/t/travel?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@etiennegirardet?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Etienne Girardet</a> on <a href="https://unsplash.com/s/photos/yellow?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@alken?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Alfred Kenneally</a> on <a href="https://unsplash.com/t/nature?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@brentstorm?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Brent Storm</a> on <a href="https://unsplash.com/t/nature?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@storybyphil?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Phil Desforges</a> on <a href="https://unsplash.com/t/nature?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@p_kuzovkova?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Polina Kuzovkova</a> on <a href="https://unsplash.com/t/nature?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@samferrara?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Samuel Ferrara</a> on <a href="https://unsplash.com/t/nature?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@mischievous_penguins?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Casey Horner</a> on <a href="https://unsplash.com/t/nature?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@jannerboy62?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Nick Fewings</a> on <a href="https://unsplash.com/t/nature?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@maxsaeling?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Max Saeling</a> on <a href="https://unsplash.com/t/nature?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@philipgraves97?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Philip Graves</a> on <a href="https://unsplash.com/t/nature?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@maxwhtd?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Max Whitehead</a> on <a href="https://unsplash.com/t/architecture?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@thanospal?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Thanos Pal</a> on <a href="https://unsplash.com/t/architecture?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@lobostudiohamburg?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">LoboStudio Hamburg</a> on <a href="https://unsplash.com/t/architecture?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@mattiabar?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">mattia barbotti</a> on <a href="https://unsplash.com/t/architecture?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@laup?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Paul Volkmer</a> on <a href="https://unsplash.com/t/architecture?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@cobblepot?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Kit Suman</a> on <a href="https://unsplash.com/t/architecture?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@runninghead?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Denny Ryanto</a> on <a href="https://unsplash.com/t/architecture?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@sushioutlaw?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Brian McGowan</a> on <a href="https://unsplash.com/t/architecture?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@thevantagepoint718?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Lerone Pieters</a> on <a href="https://unsplash.com/t/street-photography?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@rafael_ishkhanyan?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Rafael Ishkhanyan</a> on <a href="https://unsplash.com/t/street-photography?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@milltownphotography?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Sam Barber</a> on <a href="https://unsplash.com/t/street-photography?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@vardarious?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Volkan Vardar</a> on <a href="https://unsplash.com/t/street-photography?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@charlesetoroma?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Charles Etoroma</a> on <a href="https://unsplash.com/t/street-photography?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@like_that_mike?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Mike Kienle</a> on <a href="https://unsplash.com/t/street-photography?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@shotbybrandon?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">brandon patrisso</a> on <a href="https://unsplash.com/t/street-photography?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@dubhe?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Dubhe Zhang</a> on <a href="https://unsplash.com/t/street-photography?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@wexor?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Wexor Tmg</a> on <a href="https://unsplash.com/s/photos/animal?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@r3dmax?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Jonatan Pie</a> on <a href="https://unsplash.com/s/photos/animal?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@fridooh?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Frida Bredesen</a> on <a href="https://unsplash.com/s/photos/animal?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@kevinmueller?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Kevin Mueller</a> on <a href="https://unsplash.com/s/photos/animal?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@rayhennessy?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Ray Hennessy</a> on <a href="https://unsplash.com/s/photos/animal?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@licole?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Chris Charles</a> on <a href="https://unsplash.com/s/photos/animal?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@charlesdeluvio?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Charles Deluvio</a> on <a href="https://unsplash.com/s/photos/animal?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@danist07?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">贝莉儿 DANIST</a> on <a href="https://unsplash.com/s/photos/animal?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@rayhennessy?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Ray Hennessy</a> on <a href="https://unsplash.com/s/photos/animal?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@ninjason?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Jason Leung</a> on <a href="https://unsplash.com/s/photos/animal?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@wilsanphotography?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">wilsan u</a> on <a href="https://unsplash.com/s/photos/animal?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@mtths_psd?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">matthias iordache</a> on <a href="https://unsplash.com/s/photos/animal?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@elenadesotophoto?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Elena de Soto</a> on <a href="https://unsplash.com/s/photos/event?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@chuttersnap?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">CHUTTERSNAP</a> on <a href="https://unsplash.com/s/photos/event?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@alelmes?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Alasdair Elmes</a> on <a href="https://unsplash.com/s/photos/event?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@adam_whitlock?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Adam Whitlock</a> on <a href="https://unsplash.com/s/photos/event?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@kristinaco?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Kristina Evstifeeva</a> on <a href="https://unsplash.com/s/photos/event?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@karinacarvalho?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Karina Carvalho</a> on <a href="https://unsplash.com/s/photos/event?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@marcusneto?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Marcus Neto</a> on <a href="https://unsplash.com/s/photos/event?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@maximebhm?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Maxime Bhm</a> on <a href="https://unsplash.com/s/photos/event?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@brunocervera?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">BRUNO EMMANUELLE</a> on <a href="https://unsplash.com/s/photos/event?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@_ryan_?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Ryan</a> on <a href="https://unsplash.com/s/photos/event?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@robwingate?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Rob Wingate</a> on <a href="https://unsplash.com/s/photos/event?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@kunjparekh?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Kunj Parekh</a> on <a href="https://unsplash.com/s/photos/monochrome?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@8moments?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Simon Berger</a> on <a href="https://unsplash.com/s/photos/monochrome?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@fabster74?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Fabian Fauth</a> on <a href="https://unsplash.com/s/photos/monochrome?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@kevinbessat?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Kevin Bessat</a> on <a href="https://unsplash.com/s/photos/monochrome?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@pliessnig?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">HARALD PLIESSNIG</a> on <a href="https://unsplash.com/s/photos/monochrome?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@patrol?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Manouchehr Hejazi</a> on <a href="https://unsplash.com/s/photos/monochrome?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@fabster74?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Fabian Fauth</a> on <a href="https://unsplash.com/s/photos/monochrome?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@mattartz?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Matt Artz</a> on <a href="https://unsplash.com/s/photos/monochrome?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@sjois71?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">joyce huis</a> on <a href="https://unsplash.com/s/photos/monochrome?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@vincentvanzalinge?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Vincent van Zalinge</a> on <a href="https://unsplash.com/s/photos/monochrome?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@curranrob?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Rob Curran</a> on <a href="https://unsplash.com/s/photos/monochrome?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@samburriss?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Sam Burriss</a> on <a href="https://unsplash.com/s/photos/portrait?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@alexiby?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Alex Iby</a> on <a href="https://unsplash.com/s/photos/portrait?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@drew_hays?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Drew Hays</a> on <a href="https://unsplash.com/s/photos/portrait?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@cristian_newman?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Cristian Newman</a> on <a href="https://unsplash.com/s/photos/portrait?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@pixelatelier?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Christian Holzinger</a> on <a href="https://unsplash.com/s/photos/portrait?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@kfred?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Karl Fredrickson</a> on <a href="https://unsplash.com/s/photos/portrait?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@lephotographe_?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Arthur Chauvineau</a> on <a href="https://unsplash.com/s/photos/portrait?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@lanju_fotografie?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Lanju Fotografie</a> on <a href="https://unsplash.com/s/photos/torch?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@ralphkayden?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Ralph (Ravi) Kayden</a> on <a href="https://unsplash.com/s/photos/wires?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@jg2021?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Jarosław Głogowski</a> on <a href="https://unsplash.com/s/photos/sheep?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@lensinkmitchel?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Mitchel Lensink</a> on <a href="https://unsplash.com/s/photos/green?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@aaronburden?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Aaron Burden</a> on <a href="https://unsplash.com/images/nature?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@sadswim?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">ian dooley</a> on <a href="https://unsplash.com/images/travel?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@hectorfalcon?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Hector Falcon</a> on <a href="https://unsplash.com/t/experimental?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>
- <span>Photo by <a href="https://unsplash.com/@portuguesegravity?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Portuguese Gravity</a> on <a href="https://unsplash.com/s/photos/pool-sun?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText">Unsplash</a></span>

# Deployment

## Connecting the Application to MongoDB

1. Logged into my MongoDB account. 
2. With the "Clusters" tab selected, I clicked on "Connect" 
<p align="left">
  <img src="static/images/mongodb-connection-1.png">
</p>
3. Selected "Connect your application"
<p align="left">
  <img src="static/images/mongodb-connection-3.png">
</p>
4. Selected "Python" as the "Driver" and "Version" "3.6 or later". 
<p align="left">
  <img src="static/images/mongodb-connection-2.png">
</p>
5. Copied the connection string and pasted it in my env.py file editing it to include my dbname and my user password.

6.Created an instance of PyMongo and passed the application to that instance as below:


        mongo = PyMongo(app)

## Heroku Deployment

Before following the steps listed below, a requirements.txt file and a Procfile were created and pushed to GitHub using the following commands: 

        pip3 freeze --local > requirements.txt
        echo web: python app.py > Procfile

### The application was deployed via Heroku using this process: 

 1. Navigated to [Heroku](https://www.heroku.com/)
 2. Signed into my Heroku account. 
 3. Selected "New" on the dashboard and then "Create new application" option as below: 
 <p align="left">
  <img src="static/images/deployment-process-1.png">
</p>

 4. Selected a name for my application, selected "Europe" as the region and clicked "Create app". 
 <p align="left">
  <img src="static/images/deployment-process-2.png">
</p>
 5. With the "Deploy" tab selected, "GitHub - Connect to GitHub" was chosen as the deployment method.
<p align="left">
  <img src="static/images/deployment-process-3.png">
</p>
 6. Making sure my GitHub profile was displayed, I clicked "connect" next to the GitHub repository for this project.

<p align="left">
    <img src="static/images/deployment-process-4.png">
</p>
<p align="left">
    <img src="static/images/deployment-process-5.png">
</p>
<p align="left">
    <img src="static/images/deployment-process-6.png">
</p>
 7. Then I navigated to the "Settings" tab and clicked on "Reveal Convig Vars".
 <p align="left">
    <img src="static/images/deployment-process-7.png">
</p>

 8. Added in my configuration variables to Heroku.
 9. Navigated back to the "Deploy" tab and selected "Enable Automatic Deploys" with the master branch selected from the dropdown box.
 <p align="left">
    <img src="static/images/deployment-process-9.png">
</p>
<p align="left">
    <img src="static/images/deployment-process-10.png">
</p>
 10. Then clicked on "Deploy Branch" also with master selected. 
 <p align="left">
    <img src="static/images/deployment-process-11.png">
</p>
 11. Site is deployed and any changes are automatically deployed each time they are updated and pushed to GitHub during development.
<p align="left">
    <img src="static/images/deployment-process-12.png">
</p>

 # Tools and Other Resources Used 

## 1. Design

- ## [Font Awesome](https://fontawesome.com/)

    The icons used in this application were sourced from Font Awesome. 

- ## [Unsplash](https://unsplash.com/)

    Used throughout the application for images.

## HTML/CSS 

- ## [Regex use vs. Regex abuse](https://blog.codinghorror.com/regex-use-vs-regex-abuse/)

    Super article outlining the use of regular expressions. 

- ## [Form Input Validation Using Only HTML5 and Regex](https://code.tutsplus.com/tutorials/form-input-validation-using-only-html5-and-regex--cms-33095)

    Useful blog post on form validation. 

- ## [Keeping your footer at the bottom of the page](https://www.freecodecamp.org/news/how-to-keep-your-footer-where-it-belongs-59c6aa05c59c/)

    This is always a useful article.

- ## [Change color of underline input and label in Materialize.css framework](https://stackoverflow.com/questions/37127123/change-color-of-underline-input-and-label-in-materialize-css-framework)

    This Stack Overflow question was useful when customizing form elements. 

- ## [Change color of checkbox in Materialize framework](https://stackoverflow.com/questions/35261021/change-color-of-checkbox-in-materialize-framework)

    Stack Overflow article enabled me to override the Materialize checkbox colour styles. 

- ## [Beautiful CSS box-shadow examples](https://getcssscan.com/css-box-shadow-examples)

    A great collection of box-shadows

## JavaScript 

- ## [W3 Schools - Location hash Property](https://www.w3schools.com/jsref/prop_loc_hash.asp)

    Used on the browse page to scroll down to the images when a user searches.

## Python 

- ## [W3Schools Python Datetime Information](https://www.w3schools.com/python/python_datetime.asp)

    Used to help me write the datetime aspects of my code. 

- ## [Python | os.path.splitext() method](https://www.geeksforgeeks.org/python-os-path-splitext-method/)

    Very useful Python method for splitting files into roots & extensions. Used in this application to rename all incoming images.

- ## [How to add leading zeros to a number in Python](https://www.kite.com/python/answers/how-to-add-leading-zeros-to-a-number-in-python#:~:text=Use%20str.,0%20to%20the%20specified%20width%20.)

    Used briefly for a function that has since been removed. Good to know though.

- ## [Python List Comprehension](https://www.programiz.com/python-programming/list-comprehension)

    List comprehension used in a number of places throughout the application. A much more efficient and nicer way to loop through arrays. 

- ## [Write a long string into multiple lines of code in Python](https://note.nkmk.me/en/python-long-string/)
    
    How to format long strings while remaining PEP8 compliant. 

- ## [Using ternary operators in Python](https://book.pythontips.com/en/latest/ternary_operators.html)

    Nice short way to write conditionals.

- ## [Passing a function to another function in Python](https://medium.com/@lynzt/python-pass-a-function-to-another-function-and-run-it-with-args-b24141312bd7)

    Useful information for refactoring.

## Flask

- ## [Flask templates information](https://flask.palletsprojects.com/en/1.1.x/templating/#context-processors)

    Used to integrate a context processor for datetime into my application. 

- ## [Getting Referring URL for Flask Request](https://stackoverflow.com/questions/28593235/get-referring-url-for-flask-request)

    Used to change the back link on the photo details page, depending on what the source url (request.referrer) was.

- ## [How to enable CSRF protection in the Python / Flask app?](https://dev.to/dev0928/how-to-enable-csrf-protection-in-the-python-flask-app-5age)

    Decent introduction to using Flask-WTF extension to protect against CRSF attacks.

- ## [Handling File Uploads With Flask](https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask) 

    Wonderful walkthrough for explaining how to do various file upload validations. 

- ## [How to actually upload a file using Flask WTF FileField](https://stackoverflow.com/questions/14589393/how-to-actually-upload-a-file-using-flask-wtf-filefield?rq=1)

    Good information on using WTF File Field.

- ## [Get Form Checkbox Data in Flask with .getlist](https://www.youtube.com/watch?v=_sgVt16Q4O4)

    Quick tutorial on how to get and use the form checkbox data in Flask.

- ## [Simple Flask Pagination](https://medium.com/better-programming/simple-flask-pagination-example-4190b12c2e2e)

## Flask Paginate

- ## [How to use Flask Paginate](https://gist.github.com/mozillazg/69fb40067ae6d80386e10e105e6803c9)

    Used to help me integrate flask paginate. Especially useful was the comment by "hephzibahponcellat" on how to change the number of resuts per page. 

- ## [Flask Paginate __init__.py File](https://github.com/lixxu/flask-paginate/blob/master/flask_paginate/__init__.py)

    Used to get a better understanding of this extension in order to customise it to use 3 times on my profile page. 

## Flask-Mail

- ## [Configure Flask-Mail to use GMail](https://stackoverflow.com/questions/37058567/configure-flask-mail-to-use-gmail)

    Stack overflow article I found useful when figuring out how to connect Flask-Mail to gmail correctly.

- ## [Send Email programmatically with Gmail, Python, and Flask](https://www.twilio.com/blog/2018/03/send-email-programmatically-with-gmail-python-and-flask.html)

    Great blog article about sending email via Flask-Mail. 

- ## [Send Email with Gmail, Python, and Flask](https://medium.com/analytics-vidhya/send-email-with-gmail-python-and-flask-1810c25cf5f5)

    Useful blog post about Flask-Mail

- ## [The Flask Mega-Tutorial Part X: Email Support](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-x-email-support)

    This tutorial is useful for all aspects of Flask, but this bit was very useful when configuring Flask-Mail.

- ## [Python Flask e-mail form example](https://stackoverflow.com/questions/43728500/python-flask-e-mail-form-example)

    Another useful Stack Overflow question re: Flask-Mail.

## MongoDB 

- ## [GridFS Documentation](https://docs.mongodb.com/manual/core/gridfs/)

- ## [Save and Retrieve Files In a MongoDB with Flask-Pymongo](https://www.youtube.com/watch?v=DsgAuceHha4)

    Wonderfully concise tutorial that perfectly demonstrates how to save & retrieve images with GridFS & Flask. 

- ## [GridFS & MongoDB: Pros & Cons](https://www.compose.com/articles/gridfs-and-mongodb-pros-and-cons/)

    Article about whether to use GridFS or just store smaller files (<16MB> as binary data in a mongo collection.)

- ## [How to update a document in MongoDB instead of overwriting the exisiting one](https://stackoverflow.com/questions/49343649/how-to-update-a-document-without-overwriting-the-existing-one)

    Solved an issue I was having with this exact query.  

- ## [MongoDB: how to filter by multiple fields](https://developerslogblog.wordpress.com/2019/10/15/mongodb-how-to-filter-by-multiple-fields/)
    
    Good article on Mongo Filtering.

- ## [Text Indexes](https://docs.mongodb.com/manual/core/index-text/)

    Official documentation on building text indexes with Mongo DB.

- ## [How to AND and NOT in MongoDB $text search](https://stackoverflow.com/questions/23985464/how-to-and-and-not-in-mongodb-text-search)

    Useful stack overflow question, as the information is missing from the Mongo DB docs.

## Jinja

- ## [Jinja Documentation](https://jinja.palletsprojects.com/en/2.11.x/)

- ## [Get lengths of a list in a jinja2 template](https://stackoverflow.com/questions/1465249/get-lengths-of-a-list-in-a-jinja2-template)

    Used on the recent winners page to determine whether or not there was a tie. 

## APScheduler

- ## [Python timing task APScheduler](https://www.programmersought.com/article/6695232439/)

    Decent article explaining the basics of using APScheduler with Flask.

- ## [Passing Parameters to APScheduler](https://stackoverflow.com/questions/12412708/passing-parameters-to-apscheduler-handler-function)

    Used to work out how pass in db as a parameter, as the format is not intuitive.

## General/Misc

 - ## [RandomKeygen](https://randomkeygen.com/)

    A random key generator to create super secure keys & passwords. 

- ## [Bytes to bits to MBs to KBs to GBs converter](http://www.beesky.com/newsite/bit_byte.htm)

    Super useful for setting file size limits on uploads.

- ## [MDN Web Docs: Request.referrer](https://developer.mozilla.org/en-US/docs/Web/API/Request/referrer)

    Information on using request.referrer.

# Libraries

## [APScheduler](https://apscheduler.readthedocs.io/en/stable/#) 

Advanced Python Scheduler is a Python library that allows developers to schedule Python code to be executed at different times or intervals. 
Used in this application to schedule the awards & points process that happens each week on a Sunday at 22:00. 

## [Werkzeug](https://werkzeug.palletsprojects.com/en/1.0.x/)

A WSGI web application library used in this application for hashing and reading user passwords securely. 

## [Flask-Mail](https://pythonhosted.org/Flask-Mail/)

A Flask extension that allows users to send emails via the application. 

## [Flask Paginate](https://pythonhosted.org/Flask-paginate/)

A Flask extension to paginate. Says it's for use with bootstrap, but integrated fine with Materialize.

