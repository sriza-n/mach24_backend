import serial
import serial.tools.list_ports
import time
import threading

# List available ports
ports = list(serial.tools.list_ports.comports())
for port in ports:
    print(f"Available port: {port.device}")

# Try to connect to the first available port
ser = None
for port in ports:
    try:
        ser = serial.Serial(port.device, 9600)
        print(f"Connected to {port.device}")
        break
    except serial.SerialException as e:
        print(f"Error opening serial port {port.device}: {e}")

if ser is None:
    print("Failed to connect to any serial port.")
    exit(1)

def send_data(data):
    try:
        ser.write(data.encode('utf-8'))
        print(f"Sent: {data}")
    except serial.SerialException as e:
        print(f"Error sending data: {e}")




while True:
    try:
        # Read a line from the serial port
        raw_data = ser.readline()
        # Try to decode the data
        data = raw_data.decode('utf-8').rstrip()
        print(data)
        # send_data("Hello Arduino")
    except UnicodeDecodeError:
        print(f"Failed to decode: {raw_data}")
    except serial.SerialException as e:
        print(f"Serial error: {e}")
        break
