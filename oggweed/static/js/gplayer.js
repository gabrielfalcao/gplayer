$(function(){
    $(".play").on("click", function(e){
        $(this).toggle("active");
        var player = document.getElementById("player");
        player.play();
        return e.preventDefault();
    });
});
