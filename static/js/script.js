$(document).ready(function(){
    
    
    $('.sidenav').sidenav();
    $('.tabs').tabs();
    $('.collapsible').collapsible();
    $('.tooltipped').tooltip();
    $('select').formSelect();

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


});