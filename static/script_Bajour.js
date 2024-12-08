const onButton = document.getElementById('on-button');
const offButton = document.getElementById('off-button');
const rainbowButton = document.getElementById('rainbow-button');
const strobeButton = document.getElementById('strobe-button');
const colorButtons = document.querySelectorAll('.color-button');
const brightnessButtons = document.querySelectorAll('.brightness-button');
const speedButtons = document.querySelectorAll('.speed-button');
const logDiv = document.getElementById('log');

// Gestione eventi pulsanti di accensione/spegnimento
onButton.addEventListener('click', () => {
    sendCommand('ON');
});

offButton.addEventListener('click', () => {
    sendCommand('OFF');
});

// Gestione eventi pulsanti per effetti
rainbowButton.addEventListener('click', () => {
    sendCommand('RAINBOW');
});

strobeButton.addEventListener('click', () => {
    sendCommand('STROBE');
});

// Gestione eventi pulsanti colori
colorButtons.forEach(button => {
    button.addEventListener('click', () => {
        const colorValue = button.getAttribute('data-color');
        sendCommand(`COLOR${colorValue}`);
    });
});

// Gestione eventi pulsanti luminosità
brightnessButtons.forEach(button => {
    button.addEventListener('click', () => {
        const brightnessValue = button.getAttribute('data-value');
        sendCommand(`BRIGHTNESS:${brightnessValue}`);
    });
});

// Gestione eventi pulsanti velocità
speedButtons.forEach(button => {
    button.addEventListener('click', () => {
        const speedValue = button.getAttribute('data-value');
        sendCommand(`SPEED:${speedValue}`);
    });
});

// Funzione per inviare comandi
let debounceTimeout;
function sendCommand(cmd) {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(() => {
        fetch(`/command_Bajour?cmd=${cmd}`)
            .then(response => response.text())
            .then(data => {
                logDiv.innerHTML += `<p>Comando inviato: ${cmd} - Risposta: ${data}</p>`;
            })
            .catch(error => {
                logDiv.innerHTML += `<p>Errore: ${error}</p>`;
            });
    }, 300); // Imposta il tempo di debounce a 300ms
}
