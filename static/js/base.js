$(document).ready(function() {
 let clicked = false;
$("#form").hide();
$("#info").css("visibility","hidden");
$("#header").hide();
$(".oct").on("click", function(){
    if(clicked === false){
    $("#hidupd").click();
    clicked = true;
    $("#hidupd").change(function(){
        if ($("#hidupd").val()){
        $("#octopus").hide();
        $("#octohov").hide();
        $("#octoth").css("visibility","visible");
        $("#info").css("visibility","visible");
        $("#hidsbm").click();}
        });
        }
    })

});


