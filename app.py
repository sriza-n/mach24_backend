# .venv\Scripts\activate
# pip install Flask-SQLAlchemy
# pip install -U flask-cors
# pip install flask-socketio
# pip freeze > requirements.txt
# Create venv
# python -m venv .venv
# pip install -r requirements.txt
from flask import Flask, jsonify , render_template , Response
import logging
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
import requests
# from flask_talisman import Talisman

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
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
    # pressure3 = db.Column(db.Float, nullable=False)
    St = db.Column(db.Integer, nullable=False)
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
    # St = db.Column(db.Integer, nullable=False)


class SensorData0(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    teensytime = db.Column(db.String(20), nullable=False)
    pressure1 = db.Column(db.Float, nullable=False)
    pressure2 = db.Column(db.Float, nullable=False)
    # pressure3 = db.Column(db.Float, nullable=False)
    St = db.Column(db.Integer, nullable=False)
    temperature1 = db.Column(db.Float, nullable=False)
    loadcell = db.Column(db.Float, nullable=False)

# class SensorData1(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.String(20), nullable=False)
#     time = db.Column(db.String(20), nullable=False)
#     teensytime = db.Column(db.String(20), nullable=False)
#     pressure1 = db.Column(db.Float, nullable=False)
#     pressure2 = db.Column(db.Float, nullable=False)
#     # pressure3 = db.Column(db.Float, nullable=False)
#     St = db.Column(db.Integer, nullable=False)
#     temperature1 = db.Column(db.Float, nullable=False)
#     loadcell = db.Column(db.Float, nullable=False)

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

# # Constants
# DATA_PREFIX = "D:"
# STATUS_PREFIX = "S:"
# DATETIME_FORMAT = '%Y-%m-%d'
# TIME_FORMAT = '%H:%M:%S:%f'
# STATUS_KEYS = ['k1', 'k2', 'k3']


# class DataProcessor:
#     def __init__(self):
#         self.current_data = {}
        
#     def process_sensor_data(self, message):
#         try:
#             data = json.loads(message[len(DATA_PREFIX):])
#             date_time = datetime.now()
            
#             self.current_data = {
#                 'date': date_time.strftime(DATETIME_FORMAT),
#                 'time': date_time.strftime(TIME_FORMAT)[:-3],
#                 'teensytime': data.get('T'),
#                 'pressure1': data.get('p1'),
#                 'pressure2': data.get('p2'),
#                 'St': data.get('ST'),
#                 'temperature1': data.get('T1'),
#                 'loadcell': data.get('LC')
#             }
#             return self.current_data
#         except json.JSONDecodeError:
#             logger.error("Invalid JSON in sensor data")
#             return None

#     def process_status_data(self, message):
#         try:
#             status = json.loads(message[len(STATUS_PREFIX):])
#             return {key: status.get(key) for key in STATUS_KEYS}
#             # return status
#         except json.JSONDecodeError:
#             logger.error("Invalid JSON in status data")
#             return None

# # Create persistent processor instance
# data_processor = DataProcessor()

# def filter_message(message):
#     db_manager = DatabaseManager()
    
#     try:
#         if message.startswith(DATA_PREFIX):
#             data = data_processor.process_sensor_data(message)
#             if data:
#                 logger.info(f"Data received: {data}")
                
#         elif message.startswith(STATUS_PREFIX):
#             status = data_processor.process_status_data(message)
#             if status and data_processor.current_data:
#                 logger.info(f"Status received: {status}")
#                 try:
#                     with app.app_context():
#                         db_manager.save_sensor_data(data_processor.current_data, status)
#                         logger.info("Data saved successfully")
#                 except Exception as e:
#                     logger.error(f"Database save error: {str(e)}")
                
#         else:
#             logger.warning(f"Unknown message type: {message}")
            
#     except Exception as e:
#         logger.error(f"Error processing message: {str(e)}")
#         raise

# class DatabaseManager:
#     @staticmethod
#     def save_sensor_data(data, status):
#         try:
#             print("\n=== Database Save Operation ===")
#             print(f"St value: {data.get('St')}")
            
#             # Create record based on St value
#             if data.get('St') == 1:
#                 model = SensorData0
#                 print("Using SensorData0 table")
#             else:
#                 model = SensorData
#                 print("Using SensorData table")

#             # Create new record
#             new_record = model(
#                 date=data['date'],
#                 time=data['time'],
#                 teensytime=data['teensytime'],
#                 pressure1=data['pressure1'],
#                 pressure2=data['pressure2'],
#                 St=data['St'],
#                 temperature1=data['temperature1'],
#                 loadcell=data['loadcell']
#             )

#             # Save and verify
#             db.session.add(new_record)
#             db.session.commit()
#             print(f"Successfully saved record to {model.__name__}")
#             return True

#         except Exception as e:
#             print(f"Error in save_sensor_data: {e}")
#             db.session.rollback()
#             raise
# class DatabaseManager:
#     @staticmethod
#     def save_sensor_data(data, status):
#         try:
#             # Determine which table to use based on status
#             if all(status.get(k) == 1 for k in STATUS_KEYS):
#                 model = SensorData
#             elif all(status.get(k) == 1 for k in STATUS_KEYS[:2]):
#                 model = SensorData1
#             else:
#                 model = SensorData0

#             new_record = model(**data)
#             db.session.add(new_record)
            
#             # Update status table
#             status_record = StatusData(**status)
#             db.session.query(StatusData).delete()
#             db.session.add(status_record)
            
#             db.session.commit()
#             socketio.emit('new_data', data)
#             socketio.emit('status_update', status)
#             return True
            
#         except Exception as e:
#             logger.error(f"Database error: {str(e)}")
#             db.session.rollback()
#             return False

date1 = None
time1 = None
teensytime = None
pressure1 = None
pressure2 = None
St = None
temperature1 = None
loadcell = None
status_all_one_flag = False

def filter_message(message):
    if message.startswith("D:"):
        try:
            data = json.loads(message[2:])
            print("Data message received:", data)
            
            # Create record data with current timestamp
            date_time = datetime.now()
            record_data = {
                'date': date_time.strftime('%Y-%m-%d'),
                'time': date_time.strftime('%H:%M:%S:%f')[:-3],
                'teensytime': data.get('T'),
                'pressure1': data.get('p1'),
                'pressure2': data.get('p2'),
                'St': data.get('ST'),  # Default to 0 if ST not present
                'temperature1': data.get('T1'),
                'loadcell': data.get('LC')
            }

            with app.app_context():
                # Choose table based on ST value
                model = SensorData if data.get('ST') == 1 else SensorData0
                new_record = model(**record_data)
                db.session.add(new_record)
                db.session.commit()
                # print(f"Data saved to {model.__name__}")

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        except Exception as e:
            print(f"Error saving data: {e}")
            db.session.rollback()

    # ... rest of the existing code for status messages ...

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
    records = SensorData.query.order_by(SensorData.id.desc()).all()
    data = [
        {"date": record.date,
        "time":record.time,
        "pressure1": record.pressure1,
        "pressure2": record.pressure2,
        # "pressure3": record.pressure3,
        "temperature1": record.temperature1,
        "loadcell": record.loadcell}
        for record in records
    ]
    # global data
    # return jsonify(data), 200
    return render_template('visualize.html',data=data)


@app.route('/stream', methods=['GET'])
def stream_data():
    records = SensorData.query.order_by(SensorData.id.desc()).all()
    data = [
        {"date": record.date,
        "time":record.time,
        "pressure1": record.pressure1,
        "pressure2": record.pressure2,
        # "pressure3": record.pressure3,
        "temperature1": record.temperature1,
        "loadcell": record.loadcell}
        for record in records
    ]
    # global data
    # return jsonify(data), 200
    return render_template('stream.html',data=data)


@app.route('/latest_data', methods=['GET'])
def latest_data():
    records = SensorData.query.order_by(SensorData.id.desc()).limit(1).all()
    data = [
        {
            "date": record.date,
            "time": record.time,
            "pressure1": record.pressure1,
            "pressure2": record.pressure2,
            # "pressure3": record.pressure3,
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

@app.route('/video')
def video_feed():
    ip_camera_url = "http://192.168.1.2:8080/video"
    response = requests.get(ip_camera_url, stream=True)
    if response.status_code != 200:
        return f"Error: Unable to access the camera stream (status code {response.status_code})"
    
    boundary = response.headers['Content-Type'].split('boundary=')[-1]
    boundary = boundary.encode()
    print(f"Boundary: {boundary.decode()}")  # Debugging: Print boundary

    def generate():
        buffer = b""
        for chunk in response.iter_content(chunk_size=8192):
            buffer += chunk
            while True:
                start = buffer.find(boundary)
                if start == -1:
                    break
                end = buffer.find(boundary, start + len(boundary))
                if end == -1:
                    break
                frame = buffer[start + len(boundary):end]
                buffer = buffer[end:]
                if frame:
                    header_end = frame.find(b'\r\n\r\n')
                    if header_end != -1:
                        frame = frame[header_end + 4:]
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    return Response(generate(), content_type='multipart/x-mixed-replace; boundary=frame')


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
