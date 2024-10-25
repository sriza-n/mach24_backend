# .venv\Scripts\activate
# pip install Flask-SQLAlchemy
# pip install -U flask-cors
from flask import Flask, request, jsonify , render_template
import serial
import serial.tools.list_ports
import threading
from flask_sqlalchemy import SQLAlchemy
import time
# import requests

app = Flask(__name__)

# Store data in a global variable
data_store = []

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensor_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the SensorData model
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    waterTemperature = db.Column(db.Float, nullable=False)
    waterLevel = db.Column(db.Float, nullable=False)
    phValue = db.Column(db.Float, nullable=False)

# Create the database and the table
with app.app_context():
    db.create_all()


# Serial communication
ser = None
latest_message = None

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
                return True
            except serial.SerialException as e:
                print(f"Error opening serial port {port.device}: {e}")
                return False

    while True:
        if ser is None or not ser.is_open:
            print("Attempting to connect to serial port...")
            if not connect_to_serial():
                print("Failed to connect to any serial port. Retrying in 5 seconds...")
                time.sleep(5)
                continue

        try:
            raw_data = ser.readline()
            if raw_data:
                buffer += raw_data.decode('utf-8', errors='ignore')
                if '\n' in buffer:  # Assuming messages end with a newline
                    message, buffer = buffer.split('\n', 1)
                    latest_message = message.strip()  # Update the global variable
                    print(f"message: {latest_message}")
                else:
                    print("incomplete message:", buffer)
        except UnicodeDecodeError:
            print(f"Failed to decode: {raw_data}")
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            close_serial()
        except Exception as e:
            print(f"Unexpected error: {e}")
            close_serial()
            break

# Start the serial communication in a separate thread
threading.Thread(target=serial_communication, daemon=True).start()



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
    # Here you would implement your visualization logic
    # For simplicity, we just return the stored data
    # return jsonify(data_store), 200
    send_data("Hello Arduino")
    return render_template('visualize.html')

@app.route('/')
def index():
    # print(f"message: {latest_message}")
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
