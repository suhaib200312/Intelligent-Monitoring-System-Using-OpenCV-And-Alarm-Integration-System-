import cv2
import numpy as np
import time
import threading
import pygame
import smtplib
import os
import keyboard  # ✅ For Alt+Esc detection
from email.mime.text import MIMEText

# ✅ Load alarm sound
ALARM_SOUND = "alarm.mp3"  # Ensure this file exists in your directory

# ✅ SMS Alert Configuration (Using Email-to-SMS Gateway)
EMAIL_ADDRESS = "04ayishabegum@gmail.com"  # Your Gmail address
EMAIL_PASSWORD = "vzvp rjqq pxoi hkrn"  # Your App password
RECIPIENT_PHONE = "8015001704@airtelap.com"  # Recipient’s SMS Gateway address

# ✅ Initialize pygame mixer for sound playback
pygame.mixer.init()
pygame.mixer.music.load(ALARM_SOUND)

# ✅ Create alert directory if it doesn't exist
ALERT_DIR = "alert"
if not os.path.exists(ALERT_DIR):
    os.makedirs(ALERT_DIR)

# ✅ Function to Send SMS Alert
def send_sms_alert():
    try:
        msg = MIMEText("🚨 Alert! Motion detected in the surveillance area. Check immediately.")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = RECIPIENT_PHONE
        msg["Subject"] = "Motion Detected!"

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_PHONE, msg.as_string())

        print("✅ SMS alert sent successfully!")
    except Exception as e:
        print("❌ Failed to send SMS:", e)

# ✅ Function to Detect Motion, Play Alarm & Send SMS Alert
def noise():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Error: Could not open camera.")
        return

    print("✅ Motion detection started... (Press Alt + Esc to exit)")

    time.sleep(2)

    ret, frame1 = cap.read()
    if not ret:
        print("❌ Error: Could not read initial frame.")
        cap.release()
        return

    frame1_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    frame1_gray = cv2.GaussianBlur(frame1_gray, (5, 5), 0)

    alarm_triggered = False
    sms_sent = False
    frame_count = 0

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_filename = os.path.join(ALERT_DIR, "motion_footage.avi")
    out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))

    while True:
        ret, frame2 = cap.read()
        if not ret:
            print("❌ Error: Could not read frame.")
            break

        frame2_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        frame2_gray = cv2.GaussianBlur(frame2_gray, (5, 5), 0)

        diff = cv2.absdiff(frame1_gray, frame2_gray)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        frame1_gray = frame2_gray.copy()

        motion_detected = any(cv2.contourArea(contour) > 500 for contour in contours)

        if motion_detected:
            cv2.putText(frame2, "Motion Detected!", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            if not alarm_triggered:
                pygame.mixer.music.play()
                alarm_triggered = True

            if not sms_sent:
                threading.Thread(target=send_sms_alert, daemon=True).start()
                sms_sent = True

            out.write(frame2)

            frame_count += 1
            alert_filename = os.path.join(ALERT_DIR, f"motion_{frame_count}.jpg")
            cv2.imwrite(alert_filename, frame2)
            print(f"✅ Motion frame saved: {alert_filename}")

        else:
            alarm_triggered = False
            sms_sent = False

        # Display exit instruction
        cv2.putText(frame2, "Press Alt+Esc to exit", (10, frame2.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Motion Detection", frame2)

        # ✅ Exit if Alt+Esc are pressed
        if keyboard.is_pressed('alt') and keyboard.is_pressed('esc'):
            print("⚡ Alt+Esc detected. Exiting...")
            break

        # Extra: Also allow exit with ESC key
        if cv2.waitKey(1) == 27:
            print("⚡ ESC key pressed. Exiting...")
            break

    out.release()
    cap.release()
    cv2.destroyAllWindows()

# ✅ Direct call
if __name__ == "__main__":
    noise()
