$(document).ready(function(){
    $("#btnActualizar").click(function(){
        console.log("ola")
        CarModal("../templates/adminModal.html");
    });
});
function CarModal(ruta){
    $("#MTareas").load(ruta, function(){
        $("#MTareas").modal("show")
    })
}