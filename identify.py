import cv2
import os
import numpy as np
import tkinter as tk
from tkinter import messagebox, simpledialog
import keyboard
import winsound
import csv

# ========================== PATHS ==========================
DATASET_DIR = "persons"
MODEL_FILE = "model.yml"
ATTENDANCE_FILE = "attendance.csv"
CASCADE_FILE = "haarcascade_frontalface_default.xml"

# ========================== UTILITIES ==========================
def ensure_directories():
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)

def count_trained_data():
    ensure_directories()
    return len(os.listdir(DATASET_DIR))

def id_exists(ids):
    ensure_directories()
    existing_ids = {file.split('-')[-1].split('.')[0] for file in os.listdir(DATASET_DIR)}
    return ids in existing_ids

def check_trained_data():
    ensure_directories()
    search_name = simpledialog.askstring("Search Data", "Enter name to check:")
    if not search_name:
        return
    trained_names = {file.split('-')[0] for file in os.listdir(DATASET_DIR)}
    if search_name in trained_names:
        messagebox.showinfo("Search Result", f"Data found for '{search_name}'.")
    else:
        messagebox.showwarning("Search Result", f"No data found for '{search_name}'.")

# ========================== DATA COLLECTION ==========================
def collect_data(name, ids):
    ensure_directories()
    cap = cv2.VideoCapture(0)
    cascade = cv2.CascadeClassifier(CASCADE_FILE)
    count = 1

    while count <= 20:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(50, 50))

        for (x, y, w, h) in faces:
            roi = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
            roi = cv2.equalizeHist(roi)
            filename = f"{name}-{count}-{ids}.jpg"
            cv2.imwrite(os.path.join(DATASET_DIR, filename), roi)
            count += 1

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Captured: {count-1}/20", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

        cv2.imshow("Face Capturing", frame)
        if cv2.waitKey(1) & 0xFF == 27 or keyboard.is_pressed("alt+esc"):
            break

    cap.release()
    cv2.destroyAllWindows()
    train_model()

# ========================== MODEL TRAINING ==========================
def train_model():
    print("Training model...")
    recog = cv2.face.LBPHFaceRecognizer_create()

    paths = [os.path.join(DATASET_DIR, file) for file in os.listdir(DATASET_DIR)]
    faces, ids = [], []

    for path in paths:
        try:
            img_gray = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            img_gray = cv2.equalizeHist(img_gray)
            face_id = int(os.path.basename(path).split('-')[-1].split('.')[0])
            faces.append(img_gray)
            ids.append(face_id)
        except Exception as e:
            print(f"Error processing {path}: {e}")

    if faces:
        recog.train(faces, np.array(ids))
        recog.save(MODEL_FILE)
        print("Model training complete!")
    else:
        print("No faces found. Capture data first!")

# ========================== IDENTIFICATION ==========================
def identify():
    if not os.path.exists(MODEL_FILE):
        messagebox.showerror("Error", "Model not found. Please add members first!")
        return

    cap = cv2.VideoCapture(0)
    cascade = cv2.CascadeClassifier(CASCADE_FILE)
    recog = cv2.face.LBPHFaceRecognizer_create()
    recog.read(MODEL_FILE)

    labels = {file.split('-')[-1].split('.')[0]: file.split('-')[0] for file in os.listdir(DATASET_DIR)}
    attendance_logged = set()
    unknown_detected = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(50, 50))
        found_unknown = False

        for (x, y, w, h) in faces:
            roi = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
            roi = cv2.equalizeHist(roi)
            label, confidence = recog.predict(roi)

            name = labels.get(str(label), "Unknown")
            if confidence < 50:
                text = name
                if name not in attendance_logged:
                    attendance_logged.add(name)
                    log_attendance(name)
            else:
                text = "Unknown"
                found_unknown = True

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if found_unknown and not unknown_detected:
            winsound.Beep(1000, 500)
            unknown_detected = True
        elif not found_unknown:
            unknown_detected = False

        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == 27 or keyboard.is_pressed("alt+esc"):
            break

    cap.release()
    cv2.destroyAllWindows()

# ========================== ATTENDANCE LOGGING ==========================
def log_attendance(name):
    ensure_directories()
    date = simpledialog.askstring("Date", "Enter today's date (YYYY-MM-DD):")
    if not date:
        return
    with open(ATTENDANCE_FILE, "a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, date])
    print(f"Attendance logged: {name} on {date}")

# ========================== GUI ==========================
def get_details():
    detail_window = tk.Toplevel()
    detail_window.geometry("300x200")
    detail_window.title("Enter Member Details")

    tk.Label(detail_window, text="Enter Name:").pack(pady=5)
    name_entry = tk.Entry(detail_window)
    name_entry.pack(pady=5)

    tk.Label(detail_window, text="Enter ID:").pack(pady=5)
    id_entry = tk.Entry(detail_window)
    id_entry.pack(pady=5)

    def submit():
        name = name_entry.get().strip()
        ids = id_entry.get().strip()

        if not name or not ids:
            messagebox.showwarning("Input Error", "Both fields are required!")
            return

        if id_exists(ids):
            messagebox.showerror("Duplicate ID", f"ID '{ids}' already exists! Please use a different ID.")
            return

        detail_window.destroy()
        collect_data(name, ids)

    tk.Button(detail_window, text="Submit", command=submit).pack(pady=10)

def maincall():
    root = tk.Tk()
    root.geometry("500x300")
    root.title("Face Recognition System")

    frame = tk.Frame(root, bg="lightgray", padx=20, pady=20)
    frame.pack(expand=True, fill="both")

    tk.Label(frame, text="Face Recognition System", font=("Helvetica", 20, "bold"), bg="lightgray").pack(pady=10)

    tk.Button(frame, text="Add Member", command=get_details, height=2, width=25, bg="blue", fg="white").pack(pady=10)
    tk.Button(frame, text="Start Recognition", command=identify, height=2, width=25, bg="green", fg="white").pack(pady=10)
    tk.Button(frame, text="Search Member", command=check_trained_data, height=2, width=25, bg="orange", fg="white").pack(pady=10)
    tk.Button(frame, text="Exit", command=root.destroy, height=2, width=25, bg="red", fg="white").pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    maincall()
