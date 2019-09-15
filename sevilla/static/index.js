"use strict";

const OK_COLOR = "#28A745";
const LOAD_COLOR = "#A0A0A0";
const ERR_COLOR = "#CC3232";
const SEND_INTERVAL_MS = 1 * 1000;
const RETRY_INTERVAL_MS = 4 * 1000;

var indicatorOk = true;
var noteId = null;
var noteElem = null;
var lastTimeout = null;
var lastTimestamp = null;
var indicatorElem = null;
var initialTitle = null;

window.addEventListener("DOMContentLoaded", () => {
    initialTitle = document.title;
    noteId = document.getElementById("noteId").innerText;

    noteElem = document.getElementById("noteText");
    noteElem.value = "";
    noteElem.oninput = noteModified;

    indicatorElem = document.getElementById("indicator");
    indicatorElem.onclick = indicatorClicked;

    // Note is blank - and it doesn't exist on the server yet, so
    // technically we're synced
    setIndicatorColor(OK_COLOR);
});

function setIndicatorColor(color) {
    indicatorElem.style.backgroundColor = color;
    indicatorOk = (color === OK_COLOR);

    if (color !== LOAD_COLOR) {
	document.title = initialTitle;
    } else {
	document.title = "*" + initialTitle;
    }

    indicatorElem.style.cursor = indicatorOk ? "pointer" : "default";
}

function indicatorClicked() {
    if (!indicatorOk) {
	return;
    }

    window.location.pathname = "notes";
}

function noteModified() {
    setIndicatorColor(LOAD_COLOR);
    scheduleUploadNote(SEND_INTERVAL_MS);
}

function scheduleUploadNote(interval) {
    if (lastTimeout) {
	clearTimeout(lastTimeout);
	lastTimeout = null;
    }

    // Schedule a new send
    lastTimeout = setTimeout(() => {
	lastTimeout = null;
	uploadNote();
    }, interval);
}

function uploadNote() {
    var timestamp = Date.now();
    var params = new URLSearchParams({
	"timestamp": timestamp
    });

    var request = new XMLHttpRequest();
    request.open('POST', "/notes/" + noteId + "?" + params.toString());
    request.setRequestHeader("Content-Type", "text/plain");

    request.onload = noteUploaded;
    request.onerror = noteUploadedError;

    lastTimestamp = timestamp;
    request.send(noteElem.value);
}

function noteUploaded() {
    /* jshint validthis: true */

    if (this.status !== 200) {
	if (this.status === 401) {
	    // The user supposedly got to the current page by logging
	    // in, but after trying to submit a note, got an
	    // authentication error.  I've only seen this happen with
	    // iOS Web Applications, where sometimes index.html is
	    // cached and the login is skipped. Refresh the page to
	    // get a new login.
	    location.reload();
	}
	noteUploadedError();
	return;
    }

    var data = JSON.parse(this.response);
    var receivedTimestamp = data.timestamp;

    if (lastTimestamp === receivedTimestamp) {
	setIndicatorColor(OK_COLOR);
	lastTimestamp = null;
    }
}

function noteUploadedError() {
    setIndicatorColor(ERR_COLOR);
    scheduleUploadNote(RETRY_INTERVAL_MS);
}
