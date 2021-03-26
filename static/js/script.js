$(document).ready(function(){

// Initialises all Materialize JS components
    $('.sidenav').sidenav();
    $('.tabs').tabs();
    $('.collapsible').collapsible();
    $('.tooltipped').tooltip();
    $('select').formSelect();
    $('.modal').modal();
    $('input#title, textarea#story, input#camera, input#lens, input#aperture, input#shutter, input#iso, textarea#message').characterCounter();
        
// Adds the "active" class to the nav-link currently active.
        $(function(){
        $(".nav-link").each(function(){
                if ($(this).attr("href") == window.location.pathname){
                        $(this).parent().addClass("active");
                }
        });
    });
    
/* This function sets the keyboard focus styles for the images in 
the Browse section so that the :hover overlay styles apply to 
keyboard users.
*/
    $('.overlay-link').focus(function(){
        $(this).parent().css({'bottom':'0', "height":"100%"});
        });
    $('.overlay-link').blur(function(){
        $(this).parent().css({'bottom':"", "height":""});
        });
});
    
document.addEventListener('DOMContentLoaded', function() {
     
/**
 * This function checks to see if an image on the winners page is horizontal or vertical
 * and if horizontal it adds some styles to format it correctly.
 */
    function verticalOrHorizontalAwardImage(){
        let photos = document.querySelectorAll('.award-photo');
        photos.forEach(photo => {
            if (photo.width > photo.height){
                photo.classList.add('award-photo-horizontal');
                let awardBadge = photo.nextElementSibling.children[0];
                awardBadge.classList.add('award-horizontal');
            }
        });
    }
    
    verticalOrHorizontalAwardImage();
});
    
/**
 * This function checks to see if the edit profile page is loaded and if so, it waits until it's fully loaded.
 * Then it checks to see if the profile image field has a custom profile photo and if it does, 
 * it adds an event listener to the delete profile icon so the user can choose to delete their custom image 
 * and revert to the default. 
 * To do this it creates a new hidden input to POST with the form to the Flask view.
 */
if (document.URL.includes('edit-profile')){
    document.addEventListener('DOMContentLoaded', function(event) {
        function deleteCustomProfilePic(){
        let profilePicInput = document.querySelector('.profile-pic-input');
        if (profilePicInput.value !== ''){
            profilePicInput.value = ''; 
            elementToAppendTo = document.getElementById('mainProfilePhotoInputField');

            let delProfilePicInput = document.createElement("input");

            let delProfilePicInputType = document.createAttribute('type');
            delProfilePicInputType.value = 'text';
            delProfilePicInput.setAttributeNode(delProfilePicInputType);

            let delProfilePicInputName = document.createAttribute('name');
            delProfilePicInputName.value = 'del-profile-pic';
            delProfilePicInput.setAttributeNode(delProfilePicInputName);

            let delProfilePicInputClass = document.createAttribute('class');
            delProfilePicInputClass.value = 'del-profile-pic-hidden';
            delProfilePicInput.setAttributeNode(delProfilePicInputClass);

            let delProfilePicInputValue = document.createAttribute('value');
            delProfilePicInput.setAttributeNode(delProfilePicInputValue);

            elementToAppendTo.appendChild(delProfilePicInput);
        }   
    }
    delProfilePicIcon = document.querySelector('.del-profile-pic');
    if (delProfilePicIcon){
        delProfilePicIcon.addEventListener('click', deleteCustomProfilePic);
    }
});
}
    
/**
 * This function checks to see if the search page is loaded and if so, it waits until it's fully loaded.
 * Then it checks if there are any photo results & if there are it makes sure to scroll the window to them, so the 
 * user is able to immediately view the images.
 * Then it uses the hidden elements (hidden-category & hidden-awards) on the search results page to pass those variables 
 * from the Flask view to this JS file and then checks which variables are passed and alters the select options and 
 * checkboxes to match them.
 */
if (document.URL.includes('search')){
    document.addEventListener('DOMContentLoaded', function(event) {

        let photos = document.getElementsByTagName('img');

        if (photos.length > 0){
            window.location.hash="entries";
        }

        let selectOptions = document.getElementsByTagName('option');
        let awardCheckBoxes = document.querySelectorAll('.checkbox-yellow');

        let category;
        if(document.querySelector('.hidden-category')){
            category = document.querySelector('.hidden-category');
        }
        
        let awards;
        if (document.querySelector('.hidden-awards')){
            awards = document.querySelector('.hidden-awards').innerHTML;
        }
        
        let check1 = document.createAttribute('checked');
        let check2 = document.createAttribute('checked');
        let check3 = document.createAttribute('checked');

        for (let i=0; i<awardCheckBoxes.length; i++){
            if (awards){
                if (awards.includes("1") && awardCheckBoxes[i].value == 1){
                    awardCheckBoxes[i].setAttributeNode(check1);
                } 
                if (awards.includes("2") && awardCheckBoxes[i].value == 2){
                    awardCheckBoxes[i].setAttributeNode(check2);
                } 
                if (awards.includes("3") && awardCheckBoxes[i].value == 3){
                    awardCheckBoxes[i].setAttributeNode(check3);
                }
            }
        }
        if (category){
            for (let i = 0; i < selectOptions.length; i++) {
            if (category.innerHTML == selectOptions[i].value ){
                let sel = document.createAttribute('selected');
                selectOptions[i].setAttributeNode(sel);
                }
            }
        }
        
    });
}
    