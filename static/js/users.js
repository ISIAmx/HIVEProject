$(function () {
    $('#visualizar').click(function () {

        $.ajax({
            url: '/users', //URL a la cual se enviará la peticion
            type: 'POST', //Petiición POST al servidor
            dataType: "json", //Se esperan datos Json del servidor
            contentType: "application/json",
            data: JSON.stringify({ click: "true" }),
            success: function (data) {
                data = JSON.stringify(data);//Convierte lista json en string json
                data = $.parseJSON(data);//Convierte string json en objetos js

                $("#lista_usuarios").append("<table><tr><th>Nombre</th><th>");
                $(data).each(function (index, data) {
                    $("#lista_usuarios").append("<tr><td> " + data.user+ " </td><tr>");
                });
                $("#lista_usuarios").append("</table>");

            },
            error: function (error) { //Si se obtiene algun error
                console.log(error);
            }
        });
    });
});
