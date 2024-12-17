import requests
from flask import Flask, Response

app = Flask(__name__)

@app.route('/video')
def video_feed():
    ip_camera_url = "http://192.168.1.4:8080/video"
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)