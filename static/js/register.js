
document.getElementById('btn-register').onclick = function () {
	let regUser = getValueById('registerUsername');
	let regKey = getValueById('registerPostingKey');

	if (!steem.auth.isWif(regKey)) {
		regKey = steem.auth.toWif(regUser, regKey, 'posting');
	}

	let pub = steem.auth.wifToPublic(regKey);

	steem.api.setOptions({ url: 'https://api.pharesim.me' });
	steem.api.getAccounts([regUser], function (err, result) {

		if (result.length != 0) {
			let keys = result[0]['posting']['key_auths'];

			for (var i = 0; i < keys.length; i++) {
				if (keys[i][0] == pub) {
					username = result[0]['name'];
					usercode = regKey;
					register();
				} else {
					errorMessage();
				}
			}
		}
		else {
			errorMessage();
		}
	});
}

const errorMessage = () => {
	document.getElementById('message').innerText = '';
	document.getElementById('message').innerText = 'Datos Incorrectos'
}


function register() {
	//$('#btn-register').click(function () {
	user = username;
	pwd = usercode;

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

	usercode = '';
}


function getValueById(id) {
	return document.getElementById(id).value;
}