from flask import Flask, render_template, request, jsonify
import requests
from RPLCD.i2c import CharLCD
import time
import threading
from gpiozero import Button, OutputDevice
import logging

logs = []
response_logs = []
console_logs = []

# Configurazione del server Flask
app = Flask(__name__)

# Configura il logging per vedere i dettagli degli errori
logging.basicConfig(level=logging.INFO)

# Pin GPIO per il tasto e per il controllo del MOSFET del display
DISPLAY_PIN = 17  # Usa GPIO17 per il controllo del MOSFET
BUTTON_PIN = 27  # Usa GPIO27 per il tasto

display_control = OutputDevice(DISPLAY_PIN)
button = Button(BUTTON_PIN, pull_up=True)  # Configura il tasto con pull-up interno

# Stato del display (acceso all'inizio)
display_on = True

# Accende il display all'inizio
display_control.on()  # Accende il display
time.sleep(1)  # Ritardo di 1 secondo per stabilizzare

# Configurazione del display LCD
i2c_expander = 'PCF8574'
lcd_address = 0x27  # Assicurati che questo sia l'indirizzo giusto
lcd_columns = 16
lcd_rows = 2

# Inizializza il display LCD
lcd = CharLCD(i2c_expander, lcd_address, port=1, cols=lcd_columns, rows=lcd_rows, backlight_enabled=True)

lcd.clear()
time.sleep(0.1)
lcd.write_string("Avvio in corso")
lcd.crlf()  # Vai alla seconda riga
lcd.write_string("Attendere.")
time.sleep(1)
lcd.clear()
time.sleep(0.1)
lcd.write_string("Avvio in corso")
lcd.crlf()  # Vai alla seconda riga
lcd.write_string("Attendere..")
time.sleep(1)
lcd.clear()
time.sleep(0.1)
lcd.write_string("Avvio in corso")
lcd.crlf()  # Vai alla seconda riga
lcd.write_string("Attendere...")
time.sleep(1)

# Variabili globali per mantenere lo stato dei dispositivi
stampante_status = "OFF"
deumidificatore_status = "OFF"

# Lock per garantire che solo un thread alla volta possa aggiornare il display
lcd_lock = threading.Lock()

def turn_on_display():
    global display_on
    display_control.on()  # Accendi il display
    display_on = True
    time.sleep(1)  # Ritardo per permettere al display di accendersi completamente

    # Re-inizializza il display LCD
    lcd.close(clear=True)  # Chiudi il display corrente per sicurezza
    time.sleep(0.1)
    lcd.__init__(i2c_expander, lcd_address, port=1, cols=lcd_columns, rows=lcd_rows, backlight_enabled=True)
    lcd.clear()

def turn_off_display():
    global display_on
    display_control.off()  # Spegni il display
    display_on = False

# Funzione per alternare lo stato del display quando si preme il tasto
def toggle_display():
    if display_on:
        turn_off_display()
    else:
        turn_on_display()  # Accendi il display
        time.sleep(2)  # Aumenta il ritardo per garantire che il display sia pronto
        update_lcd()  # Aggiorna il display con le scritte precedenti


# Collega il pulsante alla funzione di alternanza
button.when_pressed = toggle_display

# Funzione per aggiornare il display LCD
def update_lcd():
    with lcd_lock:  # Assicura che un solo thread acceda al display alla volta
        lcd.clear()
        time.sleep(0.1)  # Breve ritardo per garantire che il display sia pulito
        lcd.write_string(f"Stampante: {stampante_status[:8]}")  # Limita a 8 caratteri
        lcd.crlf()  # Vai alla seconda riga
        lcd.write_string(f"Deumidif: {deumidificatore_status[:8]}")  # Limita a 8 caratteri
        time.sleep(0.1)  # Breve ritardo per garantire che il testo sia scritto

# Funzione per ottenere lo stato reale dei dispositivi dall'ESP8266
def fetch_device_status():
    global stampante_status, deumidificatore_status

    try:
        esp8266_ip = 'http://192.168.178.164'
        response = requests.get(f"{esp8266_ip}/status")
        response.raise_for_status()  # Solleva un'eccezione per gli errori HTTP

        led_status = response.json()

        # Aggiorna lo stato dei dispositivi in base ai dati ricevuti
        stampante_status = "ON" if led_status.get('led1') == 'ON' else "OFF"
        deumidificatore_status = "ON" if led_status.get('led2') == 'ON' else "OFF"
    except requests.exceptions.RequestException as e:
        logging.error(f"Errore durante il recupero dello stato dei dispositivi: {e}")
        stampante_status = "OFF"
        deumidificatore_status = "OFF"

    # Aggiorna il display LCD con lo stato attuale
    update_lcd()

# Inizializzazione del display
def initialize_display():
    with lcd_lock:
        # Assicurati che il display sia correttamente re-inizializzato all'avvio
        lcd.__init__(i2c_expander, lcd_address, port=1, cols=lcd_columns, rows=lcd_rows, backlight_enabled=True)
        lcd.clear()
        lcd.cursor_pos = (0, 0)
        lcd.write_string("WebServer Pi")
        lcd.cursor_pos = (1, 13)
        lcd.write_string("IoT")
        time.sleep(3)
        lcd.clear()
        lcd.cursor_pos = (0, 5)
        lcd.write_string("Avvio")
        lcd.cursor_pos = (1, 3)
        lcd.write_string("WebServer")
        time.sleep(2)
    fetch_device_status()

@app.route('/')
def index():
    # Aggiorna il display con lo stato corrente all'apertura della pagina
    update_lcd()
    return render_template('index.html')

@app.route('/status', methods=['GET'])
def status():
    global stampante_status, deumidificatore_status

    try:
        esp8266_ip = 'http://192.168.178.164'
        response = requests.get(f"{esp8266_ip}/status")
        response.raise_for_status()

        led_status = response.json()

        # Aggiorna lo stato dei dispositivi in base ai dati ricevuti
        stampante_status = "ON" if led_status.get('led1') == 'ON' else "OFF"
        deumidificatore_status = "ON" if led_status.get('led2') == 'ON' else "OFF"
        update_lcd()

    except requests.exceptions.RequestException as e:
        logging.error(f"Errore durante il recupero dello stato: {e}")
        led_status = {'led1': 'OFF', 'led2': 'OFF'}
    return jsonify(led_status)

@app.route('/command', methods=['GET'])
def command():
    cmd = request.args.get('cmd')
    if cmd:
        try:
            esp8266_ip = 'http://192.168.178.164'
            response = requests.get(f"{esp8266_ip}/command?cmd={cmd}")
            response_text = response.text
            # Aggiungi ai log
            logs.append(f"Inviato comando: {cmd}")
            response_logs.append(f"Risposta ESP8266: {response_text}")
            
            # Solo se il comando ÃƒÂ¨ stato inviato con successo, aggiorniamo il display
            if response.status_code == 200:
                fetch_device_status()  # Aggiorna le variabili globali e aggiorna il display LCD

            return response_text
        except requests.exceptions.RequestException as e:
            error_message = f"Error: {e}"
            console_logs.append(error_message)
            return error_message
    return "No command received"

@app.route('/lamp')
def lamp_control():
    # Aggiorna il display con lo stato della lampada all'apertura della pagina
    return render_template('lamp.html')

# Route per inviare comandi alla lampada (ESP32)
@app.route('/command_lamp', methods=['GET'])
def command_lamp():
    cmd = request.args.get('cmd')
    if cmd:
        try:
            esp32_ip = 'http://192.168.178.180'  # Indirizzo IP corretto dell'ESP32
            response = requests.get(f"{esp32_ip}/command?cmd={cmd}")
            response_text = response.text
            logs.append(f"Inviato comando alla lampada: {cmd}")
            response_logs.append(f"Risposta ESP32: {response_text}")
            return response_text
        except requests.exceptions.RequestException as e:
            error_message = f"Error: {e}"
            console_logs.append(error_message)
            return error_message
    return "No command received"

@app.route('/Bajour')
def Bajour_control():
    # Aggiorna il display con lo stato della lampada all'apertura della pagina
    return render_template('Bajour.html')

# Route per inviare comandi alla lampada (ESP32)
@app.route('/command_Bajour', methods=['GET'])
def command_Bajour():
    cmd = request.args.get('cmd')
    if cmd:
        try:
            esp32_ip = 'http://192.168.178.160'  # Indirizzo IP corretto dell'ESP32
            response = requests.get(f"{esp32_ip}/command?cmd={cmd}")
            response_text = response.text
            logs.append(f"Inviato comando alla lampada: {cmd}")
            response_logs.append(f"Risposta ESP32: {response_text}")
            return response_text
        except requests.exceptions.RequestException as e:
            error_message = f"Error: {e}"
            console_logs.append(error_message)
            return error_message
    return "No command received"
    
    from flask import Flask, render_template
    
@app.route('/logs')
def logs_page():
    return render_template('logs.html', logs=logs, response_logs=response_logs)

app = Flask(__name__)

if __name__ == "__main__":
    initialize_display()
    app.run(host='0.0.0.0', port=443, ssl_context=('/home/Giovanni/Desktop/WebServerFiles/cert.pem', '/home/Giovanni/Desktop/WebServerFiles/key.key'))
