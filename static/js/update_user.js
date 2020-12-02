
$(function () {
    //Modificar Usuario
    $('#btn-modificar').click(function () {
        let num_id = localStorage.getItem("var_compartida");
        id_mod = Number(num_id);

        nombre = $('#mod-nombre').val();
        contrasenia = $('#mod-contrasenia').val();

        $.ajax({
            url: '/update_user', //URL a la cual se enviará la peticion
            type: 'POST', //Petiición POST al servidor
            dataType: "json", //Se esperan datos Json del servidor
            contentType: "application/json",
            data: JSON.stringify({
                id: id_mod,
                nom: nombre,
                con: contrasenia,
            }),
            success: function (data) {
                alert(data.status);
            },
            error: function (error) { //Si se obtiene algun error
                console.log(error);
            }
        });
    });
})