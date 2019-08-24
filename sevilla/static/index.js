"use strict";

const OK_COLOR = "#28A745";
const LOAD_COLOR = "#A0A0A0";
const ERR_COLOR = "#CC3232";
const SEND_INTERVAL_MS = 1 * 1000;
const RETRY_INTERVAL_MS = 4 * 1000;
const NOTE_ID_BITS = 128;

var indicatorOk = true;
var noteId = null;
var noteElem = null;
var lastTimeout = null;
var lastTimestamp = null;
var indicatorElem = null;

window.addEventListener("DOMContentLoaded", () => {
    noteId = generateID();

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
	document.title = "Sevilla";
    } else {
	document.title = "*Sevilla";
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
    if (noteElem.value.length === 0) {
	// The user erased the entire contents of the note.  Instead
	// of overwriting the old one, start a new note.  This is
	// useful in iOS Web Applications where the state of the page
	// is sometimes cached and when the app opens the previous
	// note is still there.  It gives the user an oportunity to
	// start a new note without having to refresh.
	noteId = generateID();
	return;
    }

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

function generateID() {
    var array = new Uint8Array(NOTE_ID_BITS / 8);
    window.crypto.getRandomValues(array);
    var id = Array.from(array).map(n => n.toString(16).padStart(2, "0")).join("");

    if (id.length !== NOTE_ID_BITS / 4) {
	return null;
    }

    return id;
}

function uploadNote() {
    if (noteElem.value.length === 0) {
	// Do not send out an empty note - cancel send.
	setIndicatorColor(OK_COLOR);
	lastTimestamp = null;
	return;
    }

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
