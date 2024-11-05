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
# import requests

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Emit a test message to confirm connection
    socketio.emit('connection_test', {'message': 'Connection established'})


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


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
    pressure1 = db.Column(db.Float, nullable=False)
    pressure2 = db.Column(db.Float, nullable=False)
    pressure3 = db.Column(db.Float, nullable=False)
    temperature1 = db.Column(db.Float, nullable=False)
    temperature2 = db.Column(db.Float, nullable=False)
    # t3 = db.Column(db.Float, nullable=False)
    # t4 = db.Column(db.Float, nullable=False)
# Define the StatusData model
class StatusData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    k1 = db.Column(db.Integer, nullable=False)
    k2 = db.Column(db.Integer, nullable=False)
    k3 = db.Column(db.Integer, nullable=False)
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
    buffer = ""

    def connect_to_serial():
        global ser
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            try:
                ser = serial.Serial(port.device, 9600, timeout=1)
                print(f"Connected to {port.device}")
                print(ser)
                return True
            except serial.SerialException as e:
                print(f"Error opening serial port {port.device}: {e}")
        return False

    while True:
        if ser is None or not ser.is_open:
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


def filter_message(message):

    if message.startswith("data:"):
        global data
        data = message[5:]
        print("Data message received:", data)
        # Convert the data string to a dictionary
        data_dict = json.loads(data)
        # Assign values to variables
        pressure1 = data_dict.get('p1')
        pressure2 = data_dict.get('p2')
        pressure3 = data_dict.get('p3')
        temperature1 = data_dict.get('t1')
        temperature2 = data_dict.get('t2')
        date = datetime.now().strftime('%Y-%m-%d')
        time = datetime.now().strftime('%H:%M:%S:%f')[:-3]
        # print(f"pressure1: {pressure1}, pressure2: {pressure2}, pressure3: {pressure3}, temperature1: {temperature1}, temperature2: {temperature2}")
        
        # Perform database operations within the application context
        with app.app_context():
            new_record = SensorData(
            date=date,
            time=time, 
            pressure1=pressure1,
            pressure2=pressure2,
            pressure3=pressure3,
            temperature1=temperature1,
            temperature2=temperature2
            )
            db.session.add(new_record)
            db.session.commit()
            # Emit the new data to all connected clients
            # print("Emitting new data event")
            # Check if there are any connected clients
            socketio.emit('new_data', {
                    'date': date,
                    'time': time,
                    'pressure1': pressure1,
                    'pressure2': pressure2,
                    'pressure3': pressure3,
                    'temperature1': temperature1,
                    'temperature2': temperature2
                })
            
        # Process data message
    
    elif message.startswith("status:"):
        global status
        status = message[7:]
        print("Status message received:", status)
        # Convert the status string to a dictionary
        status_dict = json.loads(status)
        # Assign values to variables
        k1 = status_dict.get('k1')
        k2 = status_dict.get('k2')
        k3 = status_dict.get('k3')
        
        # Perform database operations within the application context
        with app.app_context():
            existing_record = StatusData.query.first()
            if existing_record is None:
                new_status = StatusData(k1=k1, k2=k2, k3=k3)
                db.session.add(new_status)
            else:
                existing_record.k1 = k1
                existing_record.k2 = k2
                existing_record.k3 = k3
            db.session.commit()
        # Process status message
    else:
        print("Unknown message type:", message)


# Start the serial communication in a separate thread
# threading.Thread(target=serial_communication, daemon=True).start()
socketio.start_background_task(serial_communication)

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
    # records = SensorData.query.order_by(SensorData.id.desc()).limit(1).all()
    # data = [
    #     {"date": record.date,
    #     "time":record.time,
    #     "pressure1": record.pressure1,
    #     "pressure2": record.pressure2,
    #     "pressure3": record.pressure3,
    #     "temperature1": record.temperature1,
    #     "temperature2": record.temperature2}
    #     for record in records
    # ]
    # global data
    # return jsonify(data), 200
    return render_template('visualize.html')

@app.route('/latest_data', methods=['GET'])
def latest_data():
    records = SensorData.query.order_by(SensorData.id.desc()).limit(1).all()
    data = [
        {
            "date": record.date,
            "time": record.time,
            "pressure1": record.pressure1,
            "pressure2": record.pressure2,
            "pressure3": record.pressure3,
            "temperature1": record.temperature1,
            "temperature2": record.temperature2
        }
        for record in records
    ]
    return jsonify(data), 200


@app.route('/')
def index():
    # print(f"message: {latest_message}")
    print("index Status message received:------------------------", status)
    return render_template('index.html')



if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000,debug=True)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
