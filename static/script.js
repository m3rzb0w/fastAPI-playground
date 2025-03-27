function startProcess() {
    cleanList()
    fetch('/start', { method: 'POST' })
        .then(response => response.json())
        .then(() => openWebSocket());
}

function cleanList() {
    const factList = document.getElementById("response-list");
    if (factList) {
        factList.innerHTML = "";
    }
}

function openWebSocket() {
    let socket = new WebSocket("ws://localhost:8000/ws");

    socket.onmessage = function(event) {
        let data = JSON.parse(event.data);
        
        document.getElementById("progress-bar").style.width = data.progress + "%";

        let listItem = document.createElement("li");
        let requestNumber = Math.round((data.progress / 100) * 10);
        listItem.textContent = `Request ${requestNumber}: ${data.response}`;
        document.getElementById("response-list").appendChild(listItem);
    };

    socket.onclose = function() {
        console.log("WebSocket closed");
    };
}
