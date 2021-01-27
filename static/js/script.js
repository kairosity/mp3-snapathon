$(document).ready(function(){
    
    
    $('.sidenav').sidenav();
    $('.tabs').tabs();
    $('.collapsible').collapsible();


    // not working yet
     $('ul.right li').on('click', function(){
                if($(this).hasClass('active')){
                    $(this).removeClass('active');
                }
                $(this).addClass('active');
            });

});