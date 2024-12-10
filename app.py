# .venv\Scripts\activate
# pip install Flask-SQLAlchemy
# pip install -U flask-cors
# pip install flask-socketio
from flask import Flask, jsonify , render_template
from flask_socketio import SocketIO, emit
import serial
import serial.tools.list_ports
import threading
from flask_sqlalchemy import SQLAlchemy
import time
from datetime import datetime
import json
from flask_cors import CORS
from flask import send_from_directory
import os
# from flask_talisman import Talisman
# from werkzeug.middleware.proxy_fix import ProxyFix



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
# Talisman(app, content_security_policy=None)
# app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)


# Define the absolute path to node_modules
# NODE_MODULES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static\node_modules')

# @app.route('/node_modules/<path:filename>')
# def serve_node_modules(filename):
#     try:
#         return send_from_directory(NODE_MODULES_PATH, filename)
#     except Exception as e:
#         print(f"Error serving node_modules: {e}")
#         return f"File not found: {filename}", 404
    

# @socketio.on('connect')
# def handle_connect():
#     print('Client connected')
#     # Emit a test message to confirm connection
#     socketio.emit('connection_test', {'message': 'Connection established'})


# @socketio.on('disconnect')
# def handle_disconnect():
#     print('Client disconnected')


# Store data in a global variable
# data_store = []

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensor_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the SensorData model
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    teensytime = db.Column(db.String(20), nullable=False)
    pressure1 = db.Column(db.Float, nullable=False)
    pressure2 = db.Column(db.Float, nullable=False)
    pressure3 = db.Column(db.Float, nullable=False)
    temperature1 = db.Column(db.Float, nullable=False)
    loadcell = db.Column(db.Float, nullable=False)
    # t3 = db.Column(db.Float, nullable=False)
    # t4 = db.Column(db.Float, nullable=False)
# Define the StatusData model
class StatusData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    k1 = db.Column(db.Integer, nullable=False)
    k2 = db.Column(db.Integer, nullable=False)
    k3 = db.Column(db.Integer, nullable=False)
    st = db.Column(db.String(20), nullable=False)


class SensorData0(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    teensytime = db.Column(db.String(20), nullable=False)
    pressure1 = db.Column(db.Float, nullable=False)
    pressure2 = db.Column(db.Float, nullable=False)
    pressure3 = db.Column(db.Float, nullable=False)
    temperature1 = db.Column(db.Float, nullable=False)
    loadcell = db.Column(db.Float, nullable=False)

class SensorData1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    teensytime = db.Column(db.String(20), nullable=False)
    pressure1 = db.Column(db.Float, nullable=False)
    pressure2 = db.Column(db.Float, nullable=False)
    pressure3 = db.Column(db.Float, nullable=False)
    temperature1 = db.Column(db.Float, nullable=False)
    loadcell = db.Column(db.Float, nullable=False)

# Create the database and the table
with app.app_context():
    db.create_all()



# Serial communication
ser = None
latest_message = None
data = None
status = None
# data_lock = threading.Lock()

def close_serial():
    global ser
    if ser and ser.is_open:
        ser.close()
        ser = None

def send_data(data):
    try:
        ser.write(data.encode('utf-8'))
        print(f"Sent: {data}")
    except serial.SerialException as e:
        print(f"Error sending data: {e}")

def serial_communication():
    global ser
    global latest_message

    def connect_to_serial():
        global ser
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            try:
                ser = serial.Serial(port.device, 115200)
                print(f"Connected to {port.device}")
                print(ser)
                return True
            except serial.SerialException as e:
                print(f"Error opening serial port {port.device}: {e}")
            if e.errno == 13:
                print("Permission denied. Try running the script as an administrator.")
        return False

    while True:
        if ser is None:
            socketio.emit('new_data', {'message': 'Attempting to connect to serial port'})
            print("Attempting to connect to serial port...")
            if not connect_to_serial():
                print("Failed to connect to any serial port. Retrying in 5 seconds...")
                time.sleep(5)
                continue

        try:
            raw_data = ser.readline()
            if raw_data:
                # buffer += raw_data.decode('utf-8', errors='ignore')
                # if '\n' in buffer:  # Assuming messages end with a newline
                #     message, buffer = buffer.split('\n', 1)
                #     latest_message = message.strip()  # Update the global variable
                #     # print(f"message: {latest_message}")
                #     filter_message(latest_message)
                # else:
                #     print("incomplete message:", buffer)
                message = raw_data.decode('utf-8').strip()
                # print(f"Received: {message}")
                filter_message(message)
        except UnicodeDecodeError:
            print(f"Failed to decode: {raw_data}")
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            close_serial()
        except Exception as e:
            print(f"Unexpected error: {e}")
            close_serial()
            # break


date1 = None
time1 = None
teensytime = None
pressure1 = None
pressure2 = None
pressure3 = None
temperature1 = None
loadcell = None
status_all_one_flag = False

def filter_message(message):
    if message.startswith("D:"):
        global data, date1, time1,teensytime, pressure1, pressure2, pressure3, temperature1, loadcell, status_all_one_flag
        data = message[2:]
        print("Data message received:", data)
        # Convert the data string to a dictionary
        data_dict = json.loads(data)
        # Assign values to variables
        date_time = datetime.now()
        date1 = date_time.strftime('%Y-%m-%d')
        time1 = date_time.strftime('%H:%M:%S:%f')[:-3]
        teensytime = data_dict.get('T')
        pressure1 = data_dict.get('p1')
        pressure2 = data_dict.get('p2')
        pressure3 = data_dict.get('p3')
        temperature1 = data_dict.get('T1')
        loadcell = data_dict.get('LC')

        # print("teensytime:", teensytime)
        # print("pressure1:", pressure1)
        # print("pressure2:", pressure2)
        # print("pressure3:", pressure3)
        # print("temperature1:", temperature1)
        # print("loadcell:", loadcell)
        # new_record = SensorData0(
        #     date=date1,
        #     time=time1,
        #     teensytime=teensytime,
        #     pressure1=pressure1,
        #     pressure2=pressure2,
        #     pressure3=pressure3,
        #     temperature1=temperature1,
        #     loadcell=loadcell
        # )

        # with app.app_context():
        #     db.session.add(new_record)
        #     db.session.commit()
            # Emit the new data to all connected clients
            # socketio.emit('new_data', {
            #     'date': date,
            #     'time': time,
            #     'pressure1': pressure1,
            #     'pressure2': pressure2,
            #     'pressure3': pressure3,
            #     'temperature1': temperature1,
            #     'temperature2': temperature2
            # })

    elif message.startswith("S:"):
        status = message[2:]
        print("Status message received:", status)
        status_dict = json.loads(status)

        with app.app_context():
            existing_record = StatusData.query.first()
            if existing_record is None:
                new_status = StatusData(
                    k1=status_dict.get('k1'),
                    k2=status_dict.get('k2'),
                    k3=status_dict.get('k3'),
                    st=status_dict.get('St')

                )
                db.session.add(new_status)
            else:
                existing_record.k1 = status_dict.get('k1')
                existing_record.k2 = status_dict.get('k2')
                existing_record.k3 = status_dict.get('k3')
                existing_record.st = status_dict.get('St')
            db.session.commit()
            # socketio.emit('status', {
            #     'k1': status_dict.get('k1'),
            #     'k2': status_dict.get('k2'),
            #     'k3': status_dict.get('k3')
            # })
        # Check if all status values are 1 and store in SensorData
            # if status_dict.get('k1') == 1 and status_dict.get('k2') == 1 and status_dict.get('k3') == 1:
            #     status_all_one_flag = True

            
            if all(status_dict.get(k) == 1 for k in ('k1', 'k2', 'k3')):
                new_record = SensorData(
                date=date1,
                time=time1,
                teensytime=teensytime,
                pressure1=pressure1,
                pressure2=pressure2,
                pressure3=pressure3,
                temperature1=temperature1,
                loadcell=loadcell
            )
            elif all(status_dict.get(k) == 1 for k in ('k1', 'k2')):
                new_record = SensorData1(
                date=date1,
                time=time1,
                teensytime=teensytime,
                pressure1=pressure1,
                pressure2=pressure2,
                pressure3=pressure3,
                temperature1=temperature1,
                loadcell=loadcell
                )
            else:
                new_record = SensorData0(
                date=date1,
                time=time1,
                teensytime=teensytime,
                pressure1=pressure1,
                pressure2=pressure2,
                pressure3=pressure3,
                temperature1=temperature1,
                loadcell=loadcell 
            )

            db.session.add(new_record)
            db.session.commit()

    else:
        print("Unknown message type:", message)

# @app.route('/data', methods=['POST'])
# def receive_data():
#     global data_store
#     try:
#         # Parse the incoming JSON data
#         data = request.json
#         data_store.append(data)
#         return jsonify({"status": "success", "data": data}), 200
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/visualize', methods=['GET'])
def visualize_data():
    records = SensorData0.query.order_by(SensorData0.id.desc()).all()
    data = [
        {"date": record.date,
        "time":record.time,
        "pressure1": record.pressure1,
        "pressure2": record.pressure2,
        "pressure3": record.pressure3,
        "temperature1": record.temperature1,
        "loadcell": record.loadcell}
        for record in records
    ]
    # global data
    # return jsonify(data), 200
    return render_template('visualize.html',data=data)


@app.route('/stream', methods=['GET'])
def stream_data():
    records = SensorData0.query.order_by(SensorData0.id.desc()).all()
    data = [
        {"date": record.date,
        "time":record.time,
        "pressure1": record.pressure1,
        "pressure2": record.pressure2,
        "pressure3": record.pressure3,
        "temperature1": record.temperature1,
        "loadcell": record.loadcell}
        for record in records
    ]
    # global data
    # return jsonify(data), 200
    return render_template('stream.html',data=data)


@app.route('/latest_data', methods=['GET'])
def latest_data():
    records = SensorData0.query.order_by(SensorData0.id.desc()).limit(1).all()
    data = [
        {
            "date": record.date,
            "time": record.time,
            "pressure1": record.pressure1,
            "pressure2": record.pressure2,
            "pressure3": record.pressure3,
            "temperature1": record.temperature1,
            "loadcell": record.loadcell
        }
        for record in records
    ]
    return jsonify(data), 200

@app.route('/status', methods=['GET'])
def get_status():
    status_record = StatusData.query.first()
    if status_record:
        status_data = {
            'k1': status_record.k1,
            'k2': status_record.k2,
            'k3': status_record.k3
        }
        return jsonify(status_data), 200
    return jsonify({"error": "No status available"}), 404

@app.route('/')
def index():
    print("index Status message received:------------------------", status)
    return render_template('index.html')

# @app.route('/node_modules/<path:path>')
# def serve_node_modules(path):
#     return send_from_directory('node_modules', path)

# @app.route('/assets/<path:path>')
# def serve_assets(path):
#     return send_from_directory('assets', path)

if __name__ == '__main__':
    # Start the serial communication in a separate thread
    # threading.Thread(target=serial_communication, daemon=True).start()
    socketio.start_background_task(serial_communication)
    app.run(host='0.0.0.0', port=5000,debug=True)
    # socketio.run(app, host='0.0.0.0', port=5000, debug=True)
