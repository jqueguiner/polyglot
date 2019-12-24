$(function() {
   $(".experiment").click(function() {
      // remove classes from all
      $(".experiment").removeClass("active");
      // add class to the one we clicked
      $(this).addClass("active");
   });
});

$('a.experiment').click(function(e){
     e.preventDefault();
});
