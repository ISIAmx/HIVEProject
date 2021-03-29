
$(function () {
    $('#btn-login').click(function () {
        username = $('#username').val();
        userhash = $('#password').val();
        localStorage.setItem('username', username);
        localStorage.setItem('userhash', userhash);

        $.ajax({
            url: '/login', //URL a la cual se enviará la peticion
            type: 'POST', //Petiición POST al servidor
            dataType: "json", //Se esperan datos Json del servidor
            contentType: "application/json",
            data: JSON.stringify({
                username: username,
                userhash: userhash
            }),
            success: function (data) {
                if (data.status == 1) {
                    window.location.href = "profile";
                } else {
                    $('#message').append('Datos Incorrectos o Usuario no Existe');
                }

            },
            error: function (error) { //Si se obtiene algun error
                console.log(error);
            }
        });
    });
});

