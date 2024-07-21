# tests/test_camera.py
import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from rocket_welder_camera.camera import RocketWelderCamera
import struct

class TestRocketWelderCamera(unittest.TestCase):
    @patch('rocket_welder_camera.camera.socket.socket')
    @patch('rocket_welder_camera.camera.cv2.imdecode')
    def test_receive_frames(self, mock_imdecode, mock_socket):
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.recv.side_effect = [
            struct.pack('>QQQ', 1, 5, 1),  # Mock header
            b'\x00\x01\x02\x03\x04'        # Mock frame data
        ]
        
        mock_imdecode.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
        
        camera = RocketWelderCamera('tcp://pi-51:8082/a')
        camera.receive_frames()

        
        frame = camera.get_frame()
        
        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape, (480, 640, 3))
    
    def test_get_frame_empty_buffer(self):
        camera = RocketWelderCamera('tcp://pi-51:8082/a')
        frame = camera.get_frame()
        self.assertIsNone(frame)

if __name__ == '__main__':
    unittest.main()
