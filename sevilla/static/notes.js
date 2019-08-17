"use strict";

const API_URL = location.origin + "/notes";

var notesTable = null;
var noteRow = null;

var previousPageButton = null;
var nextPageButton = null;

var currentPage = null;

window.addEventListener("DOMContentLoaded", () => {
    notesTable = document.getElementById("notesTable");
    noteRow = document.getElementById("noteRow");
    previousPageButton = document.getElementById("paginationButtonPrevious");
    nextPageButton = document.getElementById("paginationButtonNext");

    previousPageButton.onclick = onPreviousClicked;
    nextPageButton.onclick = onNextClicked;

    document.getElementById("backButton").onclick = () => {
	window.location.href = window.location.protocol + "//" + window.location.host + "/";
    };

    var urlParams = new URLSearchParams(window.location.search);
    currentPage = parseInt(urlParams.get("page") || "0");

    if (currentPage > 0) {
	previousPageButton.disabled = false;
    }

    var params = new URLSearchParams({
	"page": currentPage
    });

    var request = new XMLHttpRequest();
    request.open("GET", API_URL + "?" + params.toString());
    request.onload = notesReceived;
    request.onerror = notesReceivedError;
    request.send();
});

function onPreviousClicked(event) {
    event.preventDefault();

    var queryString = "";
    if (currentPage > 1) {
	queryString = "?page=" + (currentPage - 1).toString();
    }

    window.location.href = window.location.protocol +
	"//" +
	window.location.host +
	window.location.pathname +
	queryString;
}

function onNextClicked(event) {
    event.preventDefault();

    window.location.href = window.location.protocol +
	"//" +
	window.location.host +
	window.location.pathname +
	"?page=" + (currentPage + 1).toString();
}

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

function notesReceived() {
    /* jshint validthis: true */
    document.getElementById("loadingHeader").style.display = "none";

    if (this.status !== 200) {
	notesReceivedError();
	return;
    }

    var data = JSON.parse(this.response);
    var totalCount = data.totalCount;
    var notes = data.notes;
    var paginationSize = data.paginationSize;

    if (notes.length > paginationSize) {
	notesReceivedError();
	return;
    }

    notes.forEach((n) => {
	var clone = document.importNode(noteRow.content, true);
	var td = clone.querySelectorAll("td");

	td[0].textContent = getDate(n.timestamp);
	td[1].firstChild.setAttribute("href", "read?id=" + n.id);
	td[1].firstChild.textContent = n.preview;
	td[2].onclick = onHidePressed(n.id);

	notesTable.appendChild(clone);
    });

    if (currentPage * paginationSize + notes.length < totalCount) {
	nextPageButton.disabled = false;
    }
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

function notesReceivedError() {
    document.getElementById("notesError").style.display = "block";
    document.getElementById("notesTableHeader").style.display = "none";
    nextPageButton.style.display = "none";
    previousPageButton.style.display = "none";
}
