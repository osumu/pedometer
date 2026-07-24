from bottle import Bottle, run, static_file, response
import serial
import threading
import time
import json
import webbrowser
import subprocess

def upload_sketch(path, port='COM3'):
    compile_result = subprocess.run([
        'arduino-cli', 'compile',
        '--fqbn', 'arduino:avr:mega:cpu=atmega2560',
        path
    ], shell=True, capture_output=True)

    if compile_result.returncode != 0:
        print("\033[31mCompilation failed \033[0m", compile_result.stderr)
        return

    upload_result = subprocess.run([
        'arduino-cli', 'upload',
        '--port', port,
        '--fqbn', 'arduino:avr:mega:cpu=atmega2560',
        path
    ], encoding='utf-8', shell=True, capture_output=True, text=True)

    if upload_result.returncode == 0:
        print("\033[32mSketch writing successful!\033[0m")
    else:
        print("\033[33mWrite failed:\033[0m", upload_result.stderr)

upload_sketch(r"3dsquare\3dsquare.ino")

app = Bottle()

try:
    ser = serial.Serial('COM3', 9600, timeout=1)
except Exception as e:
    Exception("\033[31mThe COM port could not be opened due to {} ".format(type(e).__name__), e, "\033[0m")
    ser = None

latest_pitch = 0
latest_roll = 0
latest_yaw = 0
latest_temp = 0.0

def read_serial():
    global latest_pitch, latest_roll, latest_yaw, latest_temp
    if not ser:
        return
    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if not line or 'nan' in line:
                continue
            pitch, roll, yaw, temp = map(float, line.split(','))
            latest_pitch = pitch
            latest_roll = roll
            latest_yaw = yaw
            latest_temp = temp
        except:
            continue

threading.Thread(target=read_serial, daemon=True).start()


@app.route('/')
def index():
    return static_file('index.html', root='.')

@app.route('/data')
def data():
    response.content_type = 'application/json'
    return json.dumps({
        'pitch': latest_pitch,
        'roll': latest_roll,
        'yaw': latest_yaw,
        'temp': latest_temp
    })

# bottle.WSGIRefServer()
server_thread = threading.Thread(
    target=lambda: run(
        app, server='wsgiref', 
        host='localhost', port=8080, 
        debug=True
    )
)

server_thread.start()

time.sleep(1)
webbrowser.open('http://localhost:8080/')

try:
    server_thread.join()
except KeyboardInterrupt:
    print("\033[34mServer stopped\033[0m")
