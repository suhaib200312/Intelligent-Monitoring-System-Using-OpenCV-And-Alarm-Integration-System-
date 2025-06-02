import cv2
import os
from datetime import datetime

def record():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Ensure the recordings folder exists
    recordings_dir = "recordings"
    if not os.path.exists(recordings_dir):
        os.makedirs(recordings_dir)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    filename = f'{recordings_dir}/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.avi'
    out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        # Add timestamp overlay
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (50, 50), cv2.FONT_HERSHEY_COMPLEX,
                    0.6, (255, 255, 255), 2)

        out.write(frame)  # Save the frame to the video

        cv2.imshow("Press 'ESC' to stop recording", frame)

        if cv2.waitKey(1) == 27:  # ESC key to stop
            break

    # Release resources properly
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Recording saved as: {filename}")

