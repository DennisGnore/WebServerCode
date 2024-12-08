const responses = [];
const logs = [];
const consoleLogs = [];

function showResponse(message) {
    if (responses.length >= 6) {
        responses.shift();
    }
    responses.push(message);

    const responseBox = document.getElementById('responseBox');
    if (responseBox) {
        responseBox.innerHTML = '';
        responses.forEach((response) => {
            const responseItem = document.createElement('div');
            responseItem.className = 'responseItem';
            responseItem.textContent = response;
            responseBox.appendChild(responseItem);
        });
    }
}

function logMessage(message) {
    if (logs.length >= 6) {
        logs.shift();
    }
    logs.push(message);

    const logBox = document.getElementById('logBox');
    if (logBox) {
        logBox.innerHTML = '';
        logs.forEach((log) => {
            const logItem = document.createElement('div');
            logItem.className = 'logItem';
            logItem.textContent = log;
            logBox.appendChild(logItem);
        });
    }
}

function consoleLogMessage(message) {
    if (consoleLogs.length >= 6) {
        consoleLogs.shift();
    }
    consoleLogs.push(message);

    const consoleBox = document.getElementById('consoleBox');
    if (consoleBox) {
        consoleBox.innerHTML = '';
        consoleLogs.forEach((log) => {
            const logItem = document.createElement('div');
            logItem.className = 'logItem';
            logItem.textContent = log;
            consoleBox.appendChild(logItem);
        });
    }
}

function sendCommand(command) {
    const url = `/command?cmd=${command}`;

    console.log(`Sending command to ${url}`);
    logMessage(`Sending command: ${command}`);
    consoleLogMessage(`Sending command to ${url}`);

    fetch(url, { mode: 'cors' })
        .then(response => response.text())
        .then(data => {
            console.log(`Response: ${data}`);
            showResponse(command);
            consoleLogMessage(`Response: ${data}`);
            if (data !== `Command received: ${command}`) {
                logMessage(`Response received: ${data}`);
            }
            updateLED(command, data);
        })
        .catch(error => {
            console.error('Error:', error);
            showResponse(`Error: ${error}`);
            logMessage(`Error: ${error}`);
            consoleLogMessage(`Error: ${error}`);
        });
}

function sendCommandWithTimer(onCommand, offCommand, timerId) {
    const timerElement = document.getElementById(timerId);
    const timeInSeconds = Number(timerElement.value);
    if (isNaN(timeInSeconds)) {
        console.error('Il tempo inserito non è valido');
        return;
    }
    console.log(`Invio del comando ${onCommand}`);
    sendCommand(onCommand);
    console.log(`Impostazione del timer per ${timeInSeconds} secondi`);
    setTimeout(() => {
        console.log(`Invio del comando ${offCommand} dopo ${timeInSeconds} secondi`);
        sendCommand(offCommand);
    }, timeInSeconds * 1000);
}

function updateLED(command, response) {
    const ledId = `led${command.charAt(command.length - 1)}`;
    const ledElement = document.getElementById(ledId);
    if (ledElement) {
        if (response.includes('ON')) {
            ledElement.style.backgroundColor = 'blue';
        } else if (response.includes('OFF')) {
            ledElement.style.backgroundColor = 'grey';
        }
    }
}

function getLEDStatus() {
    const url = `/status?t=${Date.now()}`;

    fetch(url, { mode: 'cors' })
        .then(response => response.json())
        .then(data => {
            updateLED('ON1', data.led1);
            updateLED('ON2', data.led2);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

window.onload = getLEDStatus;

const originalConsoleLog = console.log;
console.log = function(message) {
    originalConsoleLog(message);
    consoleLogMessage(message);
};

const originalConsoleError = console.error;
console.error = function(message) {
    originalConsoleError(message);
    consoleLogMessage(message);
};
