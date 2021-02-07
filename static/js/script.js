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


});