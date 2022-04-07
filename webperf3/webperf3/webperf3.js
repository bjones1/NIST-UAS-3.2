// ********************************************************
// |docname| - Client-side scripts for the webperf3 web app
// ********************************************************
"use strict";

// Misc
// ====
// Convert a date in seconds to a string.
let formatDate = (datesecs) =>
    datesecs === undefined
        ? ""
        : new Date(datesecs * 1000).toLocaleTimeString();
//
// Websocket
// =========
// A function to update the connection status of the webpage.
let setIsConnected = (text, backgroundColor) => {
    let ic = document.getElementById("is_connected");
    ic.textContent = text;
    ic.style.backgroundColor = backgroundColor;
};

// Create a websocket to communicate with the CodeChat Server.
let ws = new ReconnectingWebSocket(`ws://${window.location.hostname}:8765`);

// When connected, update the webpage's connection status.
ws.onopen = () => {
    console.log("webperf3 client: websocket to webperf3 server open.");
    setIsConnected("online", "white");
};

// Provide logging to help track down errors.
ws.onerror = (event) => {
    console.error(`webperf3 client: websocket error ${event}.`);
};

// When disconnected, update the webpage's connection status.
ws.onclose = (event) => {
    console.log(`webperf3 client: websocket closed by event ${event}.`);
    setIsConnected("offline", "salmon");
};

// Handle messages.
ws.onmessage = (event) => {
    if (event.data === "new data") {
        location.reload();
    } else {
        console.error(
            `webperf3 client: websocket received unknown message ${event.data}`
        );
    }
};
