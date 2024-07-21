# rocket_welder_camera/camera.py
import cv2
import threading
import socket
import struct
import numpy as np
from urllib.parse import urlparse

class RocketWelderCamera:
    def __init__(self, url):
        self.url = url
        parsed_url = urlparse(url)
        self.host = parsed_url.hostname
        self.port = parsed_url.port
        self.stream_name = parsed_url.path[1:]
        self.buffer_size = 10
        self.circular_buffer = [None] * self.buffer_size
        self.current_frame = -1
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.receive_frames)
        self.thread.daemon = True
        self.thread.start()

    @staticmethod
    def write_prefixed_ascii_string(socket, value):
        # Encode the string to ASCII bytes
        name = value.encode('ascii')
        
        # Send the length of the string as a single byte
        length_byte = len(name).to_bytes(1, 'little')
        socket.send(length_byte)
        
        # Send the actual ASCII bytes
        socket.send(name)

    def receive_frames(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        self.write_prefixed_ascii_string(sock,self.stream_name)

        while True:
            header_data = sock.recv(32)
            if len(header_data) != 32:
                continue
            
            frame_number, frame_size, stream_position, xor = struct.unpack('<QQQQ', header_data)
            xor_check = frame_number ^ frame_size ^ stream_position
            if frame_size == 0 or xor_check != xor:
                continue
            
            frame_size = int(frame_size)
            frame_data = b''
            
            while len(frame_data) < frame_size:
                packet = sock.recv(frame_size - len(frame_data))
                if not packet:
                    break
                frame_data += packet
            
            if len(frame_data) != frame_size:
                continue
            
            frame = np.frombuffer(frame_data, dtype=np.uint8)
            image = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            
            with self.lock:
                self.current_frame = (self.current_frame + 1) % self.buffer_size
                self.circular_buffer[self.current_frame] = image

    def get_frame(self):
        with self.lock:
            frame = self.circular_buffer[self.current_frame]
            if frame is not None:
                return frame
            else:
                return None
