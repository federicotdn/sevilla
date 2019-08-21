"use strict";

window.addEventListener("DOMContentLoaded", () => {
});

function getDate(timestamp) {
    var d = new Date(timestamp);
    var now = new Date();
    var date = null;

    if (d.getDate() === now.getDate() &&
	d.getMonth() === now.getMonth() &&
	d.getFullYear() === now.getFullYear()) {
	date = "Today";
    } else {
	date = d.toDateString();
    }

    var h = d.getHours().toString().padStart(2, "0");
    var m = d.getMinutes().toString().padStart(2, "0");
    return date + ", " + h + ":" + m;
}

function onHidePressed(id) {
    return function(event) {
	event.preventDefault();
	var request = new XMLHttpRequest();
	request.open("POST", "hide?id=" + id);
	request.onload = () => {
	     location.reload();
	};

	request.send();
    };
}
