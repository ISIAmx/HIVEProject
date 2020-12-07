
$(function () {
	$('#btn-register').click(function () {
		user = $('#username').val();
		pwd = $('#password').val();

		if (user == '' || pwd == '') {
			alert("No ha llenado todos los campos!");
		} else {
			$.ajax({
				url: '/register', //URL a la cual se enviará la peticion
				type: 'POST', //Petiición POST al servidor
				dataType: "json", //Se esperan datos Json del servidor
				contentType: "application/json", //Contenido enviado: json
				data: JSON.stringify({
					username: user,
					password: pwd,
				}),//Envia datos en formato json

				success: function (data) {
					alert(data.status);
				},
				error: function (error) { //Si se obtiene algun error
					console.log(error);
				}
			});

		}
	});
});
