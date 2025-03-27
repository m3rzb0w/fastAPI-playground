function cleanList() {
    const factList = document.getElementById("response-list");
    if (factList) {
        factList.innerHTML = "";
    }
    const progressBar = document.getElementById("progress-bar");
    if (progressBar) {
        progressBar.style.width = "0%";
    }
}

function generateClientId() {
    return Math.random().toString(36).slice(2, 11);
}

let clientId = generateClientId();
let socket = null;

function startProcess() {
    cleanList();
    document.getElementById("start-btn").disabled = true;
    console.log(`Starting process for client_id: ${clientId}`);

    fetch(`/start?client_id=${clientId}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log("Start process response:", data);
            openWebSocket();
        })
        .catch(error => {
            console.error("Error in starting process:", error);
            document.getElementById("start-btn").disabled = false;
        });
}

function openWebSocket() {
    if (socket) {
        console.log("Closing existing WebSocket connection");
        socket.close();
        socket = null;
    }

    socket = new WebSocket(`ws://localhost:8000/ws/${clientId}`);
    console.log(`WebSocket opening for client_id: ${clientId}`);

    socket.onopen = function() {
        console.log("WebSocket connection opened");
    };

    socket.onmessage = function(event) {
        console.log("WebSocket message received:", event.data);
        let data = JSON.parse(event.data);
        const progressBar = document.getElementById("progress-bar");
        if (progressBar) {
            progressBar.style.width = data.progress + "%";
        }
        let listItem = document.createElement("li");
        listItem.textContent = `Request ${Math.round((data.progress / 100) * 10)}: ${data.response}`;
        const responseList = document.getElementById("response-list");
        if (responseList) {
            responseList.appendChild(listItem);
        }
    };

    socket.onerror = function(error) {
        console.error("WebSocket error:", error);
        document.getElementById("start-btn").disabled = false;
        socket = null;
    };

    socket.onclose = function() {
        console.log("WebSocket closed");
        document.getElementById("start-btn").disabled = false;
        socket = null;
    };
}

document.addEventListener('DOMContentLoaded', function() {
    const startButton = document.getElementById("start-btn");
    if (startButton) {
        startButton.addEventListener('click', startProcess);
    } else {
        console.error("Start button not found in the HTML.");
    }
});