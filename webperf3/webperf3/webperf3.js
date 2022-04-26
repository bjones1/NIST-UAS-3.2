// ********************************************************
// |docname| - Client-side scripts for the webperf3 web app
// ********************************************************
"use strict";

// Misc
// ====
// Convert a date in seconds to a string.
const formatDate = (datesecs) =>
    datesecs ? new Date(datesecs * 1000).toLocaleTimeString() : "";

const formatRate = (bps) =>
    bps ? Number(Math.round(bps)).toLocaleString() : "";

// Given text, escape it so it formats correctly as HTML. Taken from https://stackoverflow.com/a/48054293. Note that this also transforms newlines into ``<br>`` -- see https://developer.mozilla.org/en-US/docs/Web/API/Node/textContent.
const escapeHTML = (unsafeText) => {
    const div = document.createElement("div");
    div.textContent = unsafeText;
    return div.innerHTML;
};

// Compare two arrays with scalar contents from `SO <https://stackoverflow.com/a/19746771/16038919>`__. Insert snarky comment about JavaScript as a programming language here.
const scalar_array_equals = (array1, array2) =>
    array1.length === array2.length &&
    array1.every((value, index) => value === array2[index]);

// Update the performance table
// ============================
// Fetch an updated table from the server.
const update_table = () => {
    fetch("/table")
        .then((response) => {
            if (!response.ok) {
                throw new Error("Network response was not OK");
            }
            return response.json();
        })
        .then((iperf3_data) => {
            // Create the new table.
            let old_iperf3_data;
            try {
                old_iperf3_data = JSON.parse(
                    window.localStorage.getItem("iperf3-data")
                );
            } catch (e) {}
            // The try/catch will succeed if there's nothing in local storage, but end up with a value of null. Replace this with an empty array.
            old_iperf3_data = old_iperf3_data || [];
            let html = `
<tr>
    <th>Port</th>
    <th style="width: 15rem">Name</th>
    <th style="width: 10rem">Timestamp</th>
    <th style="width: 10rem">Send rate (bps)</th>
    <th style="width: 10rem">Receive rate (bps)</th>
</tr>`;
            iperf3_data.forEach((row, index) => {
                html += `
<tr ${
                    scalar_array_equals(old_iperf3_data[index] || [], row)
                        ? ""
                        : "style='background-color:lightcoral;'"
                }>
    <td>${index + 5201}</td>
    <td>${escapeHTML(row[3])}</td>
    <td>${formatDate(row[0])}</td>
    <td>${formatRate(row[1])}</td>
    <td>${formatRate(row[2])}</td>
</tr>`;
            });
            window.localStorage.setItem(
                "iperf3-data",
                JSON.stringify(iperf3_data)
            );

            // Update the resulting HTML.
            document.getElementById("perf-table").innerHTML = html;
            document.getElementById("last-update").innerHTML =
                new Date().toLocaleTimeString();
        })
        .catch((error) =>
            console.error(
                "There has been a problem with your fetch operation:",
                error
            )
        );
};

// Websocket
// =========
// A function to update the connection status of the webpage.
const setIsConnected = (text, backgroundColor) => {
    const ic = document.getElementById("is_connected");
    ic.textContent = text;
    ic.style.backgroundColor = backgroundColor;
};

// Create a websocket to communicate with the CodeChat Server.
const ws = new ReconnectingWebSocket(`ws://${window.location.hostname}:8765`);

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

// Handle messages, which is always new contents for the perf table.
ws.onmessage = (event) => {
    if (event.data === "new data") {
        update_table();
    } else {
        console.error(
            `webperf3 client: websocket received unknown message ${event.data}`
        );
    }
};
