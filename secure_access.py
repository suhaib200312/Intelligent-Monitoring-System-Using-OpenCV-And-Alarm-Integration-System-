import os
import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess
import platform


# Set your Admin Password here
ADMIN_PASSWORD = "smartcctv123"  # Change if needed

def open_folder(path):
    """Open a folder cross-platform"""
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", path])
        else:  # Linux
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        print(f"Failed to open folder: {e}")

def verify_and_open_folder(folder_path):
    """Prompt password before allowing folder access"""
    root = tk.Tk()
    root.withdraw()

    password = simpledialog.askstring("Authentication", "Enter Admin Password:", show="*")

    if password == ADMIN_PASSWORD:
        if os.path.exists(folder_path):
            messagebox.showinfo("Access Granted", "Access Granted! Opening folder...")
            open_folder(folder_path)
        else:
            messagebox.showerror("Error", "Folder does not exist!")
    else:
        messagebox.showerror("Access Denied", "Wrong Password! Access Denied.")

    root.destroy()
