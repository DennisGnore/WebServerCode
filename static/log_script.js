window.onload = function() {
    fetch('/logs/data')
        .then(response => response.json())
        .then(data => {
            const logBox = document.getElementById('logBox');
            logBox.innerHTML = ''; // Pulisci il contenitore

            data.forEach((entry) => {
                const logItem = document.createElement('div');
                logItem.className = 'logItem';
                logItem.textContent = entry;
                logBox.appendChild(logItem);
            });
        })
        .catch(error => console.error('Error fetching log data:', error));
};
