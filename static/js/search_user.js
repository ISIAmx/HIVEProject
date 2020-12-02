function opciones(event, id_seccion) {

    num_secciones = document.getElementsByClassName("seccion");
    //Oculta campos no seleccionados
    for (let i = 0; i < num_secciones.length; i++) {
        num_secciones[i].style.display = "none";
    }
    //Activa campo seleccionado
    document.getElementById(id_seccion).style.display = "block";
}

//Se activa si se selecciona Modificar
function activar_contenedor(event, cont) {
    let modificar_seccion = document.getElementById(cont).style;

    if (modificar_seccion.display == "block") {
        modificar_seccion.display = "none";
    } else {
        modificar_seccion.display = "block";
    }
}

$(function () {
    //Buscar por nombre
    $('#btn1').click(function () {
        nombre = $('#nom').val();

        $.ajax({
            url: '/search_user', //URL a la cual se enviará la peticion
            type: 'POST', //Petiición POST al servidor
            dataType: "json", //Se esperan datos Json del servidor
            contentType: "application/json",
            data: JSON.stringify({
                nom: nombre,
                op: "1",
            }),
            success: function (data) {
                data = JSON.stringify(data);//Convierte lista json en string json
                data = $.parseJSON(data);//Convierte string json en objetos js
                //Imprime en los campos los datos del usuario buscado
                $(data).each(function (index, data) {
                    $("#resultado").text(data.nombre);
                    $("#mod-nombre").val(data.nombre);
                    $("#mod-contrasenia").val(data.contrasenia);
                    id_borrar = data.id; //guarda id de usuario obtenido para borrarlo si es necesario                   
                    localStorage.setItem("var_compartida", id_borrar);

                });
            },
            error: function (error) { //Si se obtiene algun error
                console.log(error);
            }
        });
    });

    //Borra usuario de la base de datos
    $('#borrar-usuario').click(function () {
        let conf = confirm("Está seguro que quiere eliminar a usuario?");

        if (conf == true) {
            $.ajax({
                url: '/delete_user', //URL a la cual se enviará la peticion
                type: 'POST', //Petiición POST al servidor
                dataType: "json", //Se esperan datos Json del servidor
                contentType: "application/json",
                data: JSON.stringify({
                    id: id_borrar, //Envía id del usuario a borrar

                }),
                success: function (data) {
                    alert(data.status) //Muestra mensaje del servidor
                },
                error: function (error) { //Si se obtiene algun error
                    console.log(error);
                }
            });
        }


    });
});

