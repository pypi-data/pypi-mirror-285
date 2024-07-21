# SDK for Rocket Welder

Example

```python
# main.py
import cv2
from rocket_welder_camera.camera import RocketWelderCamera

def main():
    url = 'tcp://{YOUR-HOST}:{YOUR-PORT}/{STREAM-NAME}'
    cam = RocketWelderCamera(url)

    cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
    
    while True:
        frame = cam.get_frame()
        if frame is not None:
            # Display the frame
            cv2.imshow('Frame', frame)
            
            # Print the current frame number
            # print(f'Frame number: {cam.current_frame}')
        
        # Exit loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
```

Usually, YOUR-PORT is 7000 and YOUR-STREAM is "default".