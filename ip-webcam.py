from flask import Flask, Response
import cv2
import requests
import numpy as np

app = Flask(__name__)

# Replace with the IP of your Android device's IP webcam
IP_WEBCAM_URL = "http://192.168.1.113:8080/video"

def generate_frames():
    while True:
        try:
            # Fetch video frame from the IP webcam
            response = requests.get(IP_WEBCAM_URL, stream=True)
            if response.status_code == 200:
                bytes_stream = bytes()
                for chunk in response.iter_content(chunk_size=1024):
                    bytes_stream += chunk
                    # Look for the start and end of a JPEG frame
                    a = bytes_stream.find(b'\xff\xd8')
                    b = bytes_stream.find(b'\xff\xd9')
                    if a != -1 and b != -1:
                        jpg = bytes_stream[a:b+2]
                        bytes_stream = bytes_stream[b+2:]
                        frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        if frame is not None:
                            _, buffer = cv2.imencode('.jpg', frame)
                            frame_bytes = buffer.tobytes()
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                        else:
                            print("Failed to decode frame")  # Debug print
            else:
                print("Failed to fetch video stream, status code:", response.status_code)
                break
        except Exception as e:
            print("Error fetching video stream:", e)
            break

@app.route('/')
def index():
    return "Welcome to the IP Webcam Stream. Go to /video_feed to see the video stream."

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)