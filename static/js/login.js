
$(function () {
    $('#btn-login').click(function () {
        user = $('#username').val();
        pwd = $('#password').val();

        $.ajax({
            url: '/login', //URL a la cual se enviará la peticion
            type: 'POST', //Petiición POST al servidor
            dataType: "json", //Se esperan datos Json del servidor
            contentType: "application/json",
            data: JSON.stringify({
                username: user,
                password: pwd
            }),
            success: function (data) {
                alert(data.status); 
            },
            error: function (error) { //Si se obtiene algun error
                console.log(error);
            }
        });
    });
});

