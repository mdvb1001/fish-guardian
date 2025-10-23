#!/usr/bin/env python3
"""
Simple camera web stream for Fish Guardian
Access at http://192.168.0.213:5000
"""
from flask import Flask, Response
from picamera2 import Picamera2
import cv2
import time

app = Flask(__name__)

# Initialize camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (1280, 720), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()
time.sleep(2)

def generate_frames():
    """Generate frames for streaming"""
    while True:
        # Capture frame
        frame_rgb = picam2.capture_array()
        frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        # Add timestamp overlay
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Encode as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Yield frame in multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        time.sleep(0.1)  # ~10 FPS for streaming

@app.route('/')
def index():
    """Landing page with video feed"""
    return '''
    <html>
    <head>
        <title>Fish Guardian - Live Camera</title>
        <style>
            body {
                background-color: #1a1a1a;
                color: #fff;
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 20px;
            }
            h1 {
                color: #4CAF50;
            }
            img {
                max-width: 95%;
                border: 3px solid #4CAF50;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.5);
            }
            .info {
                margin-top: 20px;
                padding: 15px;
                background-color: #2a2a2a;
                border-radius: 5px;
                display: inline-block;
            }
            .warning {
                color: #ff9800;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <h1>🐟 Fish Guardian - Live Camera Feed</h1>
        <img src="/video_feed" alt="Camera Feed">
        <div class="info">
            <p><strong>Resolution:</strong> 1280x720</p>
            <p><strong>Stream FPS:</strong> ~10 FPS</p>
            <p class="warning">⚠️ Monitoring service is currently stopped for viewing</p>
            <p>Close this page when done to restart data collection</p>
        </div>
    </body>
    </html>
    '''

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("=" * 70)
    print("Fish Guardian Camera Stream")
    print("=" * 70)
    print()
    print("Access the stream at:")
    print("  http://192.168.0.213:5000")
    print()
    print("Press Ctrl+C to stop streaming")
    print("=" * 70)

    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    except KeyboardInterrupt:
        print("\nStopping camera stream...")
        picam2.stop()
        print("Camera stopped. Restart fish-guardian service to resume monitoring.")
