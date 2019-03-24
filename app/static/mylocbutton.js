
 	var btn = document.getElementById("location");
 	var post = document.getElementById("post");
 	btn.addEventListener("click", getMyLocation);
 	btn.addEventListener("click", displayLocation);
function getMyLocation () { //собственно наша функция для определения местоположения
	if (navigator.geolocation) { //для начала надо проверить, доступна ли геолокация, а то еще у некоторых браузеры то древние. Там о таком и не слышали.
		navigator.geolocation.getCurrentPosition(displayLocation); //если все ок, то вызываем метод getCurrentPosition и передаем ей нашу функцию displayLocation, реализую ее ниже.
	}
	else {
		alert("Функция геолокации не поддкрживается вашим браузером"); //выведем сообщение для старых браузеров.
	}
}
 
function displayLocation(position) { //передаем в нашу функцию объект position - этот объект содержит ширину и долготу и еще массу всяких вещей.

	var	latitude = position.coords.latitude; // излвекаем широту
	var	longitude = position.coords.longitude; // извлекаем долготу
	var a = document.createElement('a');
	var linkText = document.createTextNode("Моё меcтоположение");
	a.appendChild(linkText);
	a.title = "Моё местоположение";
	a.href = "https://maps.yandex.ru/?text="+latitude+","+longitude;
	test.post = "https://maps.yandex.ru/?text="+latitude+","+longitude;
}
