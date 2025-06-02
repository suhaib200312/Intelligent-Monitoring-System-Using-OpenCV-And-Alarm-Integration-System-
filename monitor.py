import cv2
import time
import numpy as np
import pygame
import keyboard  # New import for detecting Alt + Esc keys

from spot_diff import spot_diff  # Assuming this is your custom function

def find_motion():
    motion_detected = False
    is_start_done = False
    alarm_playing = False

    # Initialize pygame mixer
    pygame.mixer.init()
    alarm_sound = pygame.mixer.Sound('alarm.mp3')  # Load your alarm sound

    cap = cv2.VideoCapture(0)

    print("Waiting for 2 seconds...")
    time.sleep(2)

    _, frm1 = cap.read()
    frm1 = cv2.cvtColor(frm1, cv2.COLOR_BGR2GRAY)

    while True:
        # Check if Alt + Esc is pressed
        if keyboard.is_pressed('alt') and keyboard.is_pressed('esc'):
            print("Alt + Esc pressed. Exiting immediately!")
            alarm_sound.stop()
            cap.release()
            cv2.destroyAllWindows()
            pygame.mixer.quit()
            return

        _, frm2 = cap.read()
        frm2 = cv2.cvtColor(frm2, cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(frm1, frm2)
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = [c for c in contours if cv2.contourArea(c) > 25]

        if len(contours) > 5:
            cv2.putText(thresh, "Motion Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
            motion_detected = True
            is_start_done = False

            if not alarm_playing:
                alarm_sound.play(-1)  # Play in loop
                alarm_playing = True

        elif motion_detected and len(contours) < 3:
            if not is_start_done:
                start = time.time()
                is_start_done = True

            end = time.time()

            if (end - start) > 4:
                _, frame2 = cap.read()
                cap.release()
                cv2.destroyAllWindows()
                alarm_sound.stop()
                pygame.mixer.quit()
                x = spot_diff(frm1, frame2)

                if x == 0:
                    print("Running again...")
                    return
                else:
                    print("Found motion")
                    return

        else:
            cv2.putText(thresh, "No Motion Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
            if alarm_playing:
                alarm_sound.stop()
                alarm_playing = False

        cv2.imshow("Motion Detection", thresh)

        _, frm1 = cap.read()
        frm1 = cv2.cvtColor(frm1, cv2.COLOR_BGR2GRAY)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    pygame.mixer.quit()
    return
