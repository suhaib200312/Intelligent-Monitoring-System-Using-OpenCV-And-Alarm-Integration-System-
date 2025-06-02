import cv2
import os
from datetime import datetime
import keyboard  # For Alt + Esc exit

def in_out():
    cap = cv2.VideoCapture(0)

    right, left = "", ""
    message = ""

    # ✅ Create 'IO' folder if it doesn't exist
    os.makedirs("IO", exist_ok=True)

    # ✅ Setup video recording with Date-Time in filename
    video_filename = f"IO/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter(video_filename, fourcc, 20, (640, 480))

    while True:
        ret, frame1 = cap.read()
        if not ret:
            print("Failed to grab frame1.")
            break
        frame1 = cv2.flip(frame1, 1)

        ret, frame2 = cap.read()
        if not ret:
            print("Failed to grab frame2.")
            break
        frame2 = cv2.flip(frame2, 1)

        diff = cv2.absdiff(frame2, frame1)
        diff = cv2.blur(diff, (5, 5))
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, threshd = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)

        contr, _ = cv2.findContours(threshd, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        x = 300  # Default center position

        if len(contr) > 0:
            max_cnt = max(contr, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(max_cnt)
            cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Movement Detection Logic
        if right == "" and left == "":
            if x > 500:
                right = True
            elif x < 200:
                left = True

        elif right:
            if x < 200:
                message = "PERSON MOVING LEFT SIDE"
                print(message)
                x = 300
                right, left = "", ""

        elif left:
            if x > 500:
                message = "PERSON MOVING RIGHT SIDE"
                print(message)
                x = 300
                right, left = "", ""

        # ✅ Put movement message
        text_x, text_y = 20, 430
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 1
        text_color = (0, 0, 255)
        thickness = 2

        cv2.putText(frame1, message, (text_x, text_y), font, font_scale, text_color, thickness)

        # ✅ Put Date-Time on frame
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame1, date_time, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # ✅ Write frame to video
        video_writer.write(frame1)

        cv2.imshow("Motion Detection", frame1)

        # ESC key or Alt+Esc key to stop
        if cv2.waitKey(1) == 27 or keyboard.is_pressed('alt+esc'):
            print("Exit key pressed. Exiting...")
            break

    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()
