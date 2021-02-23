$(document).ready(function(){
    
    $('.sidenav').sidenav();
    $('.tabs').tabs();
    $('.collapsible').collapsible();
    $('.tooltipped').tooltip();
    $('select').formSelect();
    $('.modal').modal();

    /* 
    Rafał Cz.'s code from Stack Overflow - attributed in README.md
    For each a link on the page - if the href is the current location, 
    it adds an .active class. 
    */
    $(function(){
       $("a").each(function(){
               if ($(this).attr("href") == window.location.pathname){
                       $(this).parent().addClass("active");
               }
       });
    });

    // $(function(){

    //    let paginationLi = $(".pagination li")
    //    let activeLi = $(".pagination").find('li.active');
    //    activeLi.removeClass('active')

    // //    Add the active class to number of the page it starts on. 
    //     let currentPage = window.location.href;
    //     console.log(currentPage)

    //    paginationLi.click(function(){   
    //         $(this).addClass('active')
    //         console.log(this)
    //    })
    // });

     $(function(){
       $("a").each(function(){
               if ($(this).attr("href") == window.location.pathname){
                       $(this).parent().addClass("active");
               }
       });
    });

 
});

document.addEventListener('DOMContentLoaded', function(event) {
 
    /**
     * This function checks to see if an image on the winners page is horizontal or vertical
     * and if horizontal it adds some styles to format it correctly.
     */
    
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

    verticalOrHorizontalAwardImage()

})

/**
     * This function checks to see if the edit profile page is loaded and if so, it waits until it's fully loaded
     * Then it checks to see if the profile image field has a custom profile photo and if it does, 
     * it adds an event listener to the delete profile image so the user can choose to delete their custom image 
     * and revert to the default. 
     */

if (document.URL.includes('edit-profile')){
    document.addEventListener('DOMContentLoaded', function(event) {
        function deleteCustomProfilePic(){
        let profilePicInput = document.querySelector('.profile-pic-input');
        if (profilePicInput.value !== ''){
            profilePicInput.value = ''; 
            elementToAppendTo = document.getElementById('mainProfilePhotoInputField')

            let delProfilePicInput = document.createElement("input")

            let delProfilePicInputType = document.createAttribute('type')
            delProfilePicInputType.value = 'text'
            delProfilePicInput.setAttributeNode(delProfilePicInputType)

            let delProfilePicInputName = document.createAttribute('name')
            delProfilePicInputName.value = 'del-profile-pic'
            delProfilePicInput.setAttributeNode(delProfilePicInputName)

            let delProfilePicInputClass = document.createAttribute('class')
            delProfilePicInputClass.value = 'del-profile-pic-hidden'
            delProfilePicInput.setAttributeNode(delProfilePicInputClass)

            let delProfilePicInputValue = document.createAttribute('value')
            delProfilePicInputValue.value = "del-uploaded-profile-pic"
            delProfilePicInput.setAttributeNode(delProfilePicInputValue)

            elementToAppendTo.appendChild(delProfilePicInput)
        }   
    }
    delProfilePicIcon = document.querySelector('.del-profile-pic')
    if (delProfilePicIcon){
        delProfilePicIcon.addEventListener('click', deleteCustomProfilePic)
    }
})
}

