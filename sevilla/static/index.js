"use strict";

const SEND_INTERVAL_MS = 1 * 1000;
const RETRY_INTERVAL_MS = 4 * 1000;
const STORAGE_KEY = "unsent_note";

var Colors = Object.freeze({
    ok: "#28A745",
    loading: "#A0A0A0",
    error: "#CC3232"
});

var lastTimeout = null;
var lastTimestamp = null;

function elem(id) { return document.getElementById(id); }

window.addEventListener("DOMContentLoaded", () => {
    elem("noteText").oninput = noteModified;

    var unsentNote = localStorage.getItem(STORAGE_KEY);
    if (unsentNote) {
        // Restore unsent note and try to send it
        elem("noteText").value = unsentNote;
        noteModified();
    } else {
	elem("indicator").style.backgroundColor = Colors.ok;
    }
});

function noteModified() {
    elem("indicator").style.backgroundColor = Colors.loading;
    scheduleUploadNote(SEND_INTERVAL_MS);
}

function scheduleUploadNote(interval) {
    if (lastTimeout) {
        clearTimeout(lastTimeout);
        lastTimeout = null;
    }

    localStorage.setItem(STORAGE_KEY, elem("noteText").value);

    // Schedule a new send
    lastTimeout = setTimeout(() => {
        lastTimeout = null;
        uploadNote();
    }, interval);
}

function uploadNote() {
    lastTimestamp = Date.now();

    const url = "/notes/" + elem("noteId").innerText + "?" + "timestamp=" + lastTimestamp.toString();

    function status(response) {
        if (response.status === 200) {
            return Promise.resolve(response);
        }
        return Promise.reject(new Error("Unable to upload note."));
    }

    function json(response) {
        return response.json();
    }

    fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-type": "text/plain" },
        body: elem("noteText").value
    }).then(status).then(json).then((data) => {
        var receivedTimestamp = data.timestamp;

        if (lastTimestamp === receivedTimestamp) {
            elem("indicator").style.backgroundColor = Colors.ok;
            lastTimestamp = null;
            localStorage.removeItem(STORAGE_KEY);
        }
    }).catch(() => {
        elem("indicator").style.backgroundColor = Colors.error;
	scheduleUploadNote(RETRY_INTERVAL_MS);
    });
}
