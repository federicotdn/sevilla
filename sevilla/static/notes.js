"use strict";

window.addEventListener("DOMContentLoaded", () => {
    var timestamps = document.getElementsByClassName("noteTimestamp");
    for (var i = 0; i < timestamps.length; i++) {
	var timestamp = parseInt(timestamps[i].innerText);
	timestamps[i].innerText = naturalDate(timestamp);
    }
});

function naturalDate(timestamp) {
    // UTC timestamp to local date
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
