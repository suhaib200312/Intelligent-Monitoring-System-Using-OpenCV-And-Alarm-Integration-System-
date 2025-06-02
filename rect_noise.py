import cv2
import keyboard
import pygame
import os
import time

# Initialize pygame mixer
pygame.mixer.init()
pygame.mixer.music.load("alarm.mp3")  # Make sure 'alarm.mp3' is in the same folder or give full path

donel = False
doner = False
x1, y1, x2, y2 = 0, 0, 0, 0
running = True  # Control variable for execution

# ✅ Create 'rect' folder if it doesn't exist
if not os.path.exists("rect"):
    os.makedirs("rect")

def select(event, x, y, flags, param):
    global x1, x2, y1, y2, donel, doner
    if event == cv2.EVENT_LBUTTONDOWN:
        x1, y1 = x, y
        donel = True
    elif event == cv2.EVENT_LBUTTONUP:
        x2, y2 = x, y
        doner = True
        print(f"✅ Region selected: ({x1}, {y1}) to ({x2}, {y2})")

def rect_noise():
    global x1, x2, y1, y2, donel, doner, running
    cap = cv2.VideoCapture(0)

    cv2.namedWindow("select_region")
    cv2.setMouseCallback("select_region", select)

    while running:
        if keyboard.is_pressed("alt") or keyboard.is_pressed("win+esc"):
            print("⚡ Forced exit: Alt or Windows + Esc pressed.")
            cap.release()
            cv2.destroyAllWindows()
            return

        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to capture frame. Exiting...")
            cap.release()
            return

        if donel:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.imshow("select_region", frame)

        key = cv2.waitKey(1)
        if key == 27:  # Esc key
            cap.release()
            cv2.destroyAllWindows()
            print("❌ Execution of rect_noise is stopped")
            return

        if doner:
            break

    cv2.destroyWindow("select_region")

    # ✅ Validate region
    height, width, _ = frame.shape
    x1, x2 = max(0, min(x1, width)), max(0, min(x2, width))
    y1, y2 = max(0, min(y1, height)), max(0, min(y2, height))

    if x1 >= x2 or y1 >= y2:
        print("❌ Invalid region selected. Try again.")
        cap.release()
        return

    # ✅ Setup Video Writer to save footage
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    video_filename = f"rect/motion_detection_{timestamp}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 'XVID' codec
    fps = 20.0  # Frame per second
    frame_size = (int(cap.get(3)), int(cap.get(4)))  # Width and height
    out = cv2.VideoWriter(video_filename, fourcc, fps, frame_size)
    print(f"🎥 Saving video to: {video_filename}")

    while running:
        if keyboard.is_pressed("alt") or keyboard.is_pressed("win+esc"):
            print("⚡ Forced exit: Alt or Windows + Esc pressed.")
            break

        ret1, frame1 = cap.read()
        ret2, frame2 = cap.read()

        if not ret1 or not ret2:
            print("❌ Failed to capture frames. Check the camera connection.")
            break

        frame1only = frame1[y1:y2, x1:x2]
        frame2only = frame2[y1:y2, x1:x2]

        if frame1only.size == 0 or frame2only.size == 0:
            print("❌ Selected region is empty. Try again.")
            break

        diff = cv2.absdiff(frame2only, frame1only)
        diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        diff = cv2.blur(diff, (5, 5))
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        contr, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contr:
            max_cnt = max(contr, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(max_cnt)
            cv2.rectangle(frame1, (x + x1, y + y1), (x + w + x1, y + h + y1), (0, 255, 0), 2)
            cv2.putText(frame1, "MOTION", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)

            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)  # Alarm plays continuously
        else:
            pygame.mixer.music.stop()
            cv2.putText(frame1, "NO MOTION", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)

        # ✅ Always draw selected region
        cv2.rectangle(frame1, (x1, y1), (x2, y2), (0, 0, 255), 1)

        # ✅ Save each frame into video
        out.write(frame1)

        cv2.imshow("Motion Detection", frame1)

        key = cv2.waitKey(1)
        if key == 27:
            break

    cap.release()
    out.release()  # ✅ Important to save the video properly
    pygame.mixer.music.stop()
    cv2.destroyAllWindows()
    print("✅ Execution of rect_noise is stopped")
