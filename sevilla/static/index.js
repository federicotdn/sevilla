"use strict";

const SEND_INTERVAL_MS = 1 * 1000;
const RETRY_INTERVAL_MS = 4 * 1000;
const STORAGE_KEY = "unsent_note";

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
    }
});

function noteModified() {
    elem("indicator").className = "indicatorLoading";
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
    var timestamp = Date.now();
    var params = new URLSearchParams({ "timestamp": timestamp });
    var request = new XMLHttpRequest();
    var url = elem("noteEndpoint").dataset.url + "?" + params.toString();

    request.open("PUT", url);
    request.setRequestHeader("Content-Type", "text/plain");

    request.onloadend = () => {
        if (request.status !== 200) {
            elem("indicator").className = "indicatorError";
            scheduleUploadNote(RETRY_INTERVAL_MS);
            return;
        }

        var data = JSON.parse(request.response);
        var receivedTimestamp = data.timestamp;

        if (lastTimestamp === receivedTimestamp) {
            elem("indicator").className = "indicatorOk";
            lastTimestamp = null;
            localStorage.removeItem(STORAGE_KEY);
        }
    };

    lastTimestamp = timestamp;
    request.send(elem("noteText").value);
}
