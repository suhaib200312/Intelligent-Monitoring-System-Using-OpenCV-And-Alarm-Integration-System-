import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as font
from PIL import Image, ImageTk
from in_out import in_out
from rect_noise import rect_noise
from record import record
from identify import maincall
from motion import noise
from monitor import find_motion
from secure_access import verify_and_open_folder
import os
import keyboard
import winsound  # <--- added for click sound


class SmartCCTVApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart CCTV Control Panel")
        self.root.geometry('1200x750')
        self.root.minsize(1000, 700)

        # Modern color scheme
        self.bg_color = '#1a1a2e'
        self.header_color = '#16213e'
        self.card_color = '#0f3460'
        self.accent_color = '#e94560'
        self.text_color = '#ffffff'
        self.secondary_text = '#b8b8b8'
        self.success_color = '#4cc9f0'
        self.button_color = '#4895ef'
        self.button_hover = '#3f37c9'

        self.root.configure(bg=self.bg_color)

        # Custom fonts
        self.title_font = font.Font(family='Helvetica', size=24, weight='bold')
        self.subtitle_font = font.Font(family='Helvetica', size=16, weight='bold')
        self.button_font = font.Font(family='Helvetica', size=12)
        self.small_font = font.Font(family='Helvetica', size=10)

        self.load_icons()
        self.setup_header()
        self.setup_sidebar()
        self.setup_main_content()
        self.setup_footer()
        self.check_exit_keys()

    def play_click_sound(self):
        winsound.MessageBeep(winsound.MB_OK)

    def load_icons(self):
        default_icons = {
            "monitor": "📺", "rectangle": "🔲", "record": "⏺️",
            "exit": "🚪", "in_out": "👥", "identify": "👤",
            "noise": "📢", "logo": "🔐", "dashboard": "📊",
            "settings": "⚙️", "alert": "🚨", "folder": "📁",
            "user": "👤", "power": "⏻"
        }

        self.icons = {}
        icon_paths = {
            "monitor": 'icons/lamp.png',
            "rectangle": 'icons/rectangle-of-cutted-line-geometrical-shape.png',
            "record": 'icons/recording.png',
            "exit": 'icons/exit.png',
            "in_out": 'icons/incognito.png',
            "identify": 'icons/recording.png',
            "noise": 'icons/security-camera.png',
            "logo": 'icons/spy.png',
            "dashboard": 'icons/dashboard.png',
            "settings": 'icons/settings.png',
            "alert": 'icons/alert.png',
            "folder": 'icons/folder.png',
            "user": 'icons/user.png',
            "power": 'icons/power.png'
        }

        for name, path in icon_paths.items():
            try:
                if os.path.exists(path):
                    img = Image.open(path)
                    size = (24, 24) if name != "logo" else (40, 40)
                    img = img.resize(size, Image.Resampling.LANCZOS)
                    if name != "logo":
                        img = img.convert("RGBA")
                        data = img.getdata()
                        new_data = []
                        for item in data:
                            if item[0] < 50 and item[1] < 50 and item[2] < 50:
                                new_data.append((255, 255, 255, item[3]))
                            else:
                                new_data.append(item)
                        img.putdata(new_data)

                    self.icons[name] = ImageTk.PhotoImage(img)
                else:
                    self.icons[name] = default_icons.get(name, "")
            except Exception as e:
                print(f"Error loading icon {path}: {e}")
                self.icons[name] = default_icons.get(name, "")

    def setup_header(self):
        header_frame = tk.Frame(self.root, bg=self.header_color, height=80)
        header_frame.pack(fill='x')

        logo_frame = tk.Frame(header_frame, bg=self.header_color)
        logo_frame.pack(side='left', padx=20)

        if isinstance(self.icons["logo"], str):
            logo_label = tk.Label(logo_frame, text=self.icons["logo"], font=("Arial", 24),
                                  bg=self.header_color, fg=self.text_color)
        else:
            logo_label = tk.Label(logo_frame, image=self.icons["logo"], bg=self.header_color)
        logo_label.pack(side='left', padx=10)

        title_label = tk.Label(
            logo_frame,
            text="Smart CCTV Control",
            font=self.title_font,
            fg=self.text_color,
            bg=self.header_color
        )
        title_label.pack(side='left', padx=10)

        self.status_var = tk.StringVar()
        self.status_var.set("● System Ready")
        status_frame = tk.Frame(header_frame, bg=self.header_color)
        status_frame.pack(side='right', padx=20)

        self.status_indicator = tk.Label(
            status_frame,
            textvariable=self.status_var,
            fg=self.success_color,
            bg=self.header_color,
            font=self.small_font
        )
        self.status_indicator.pack(side='right', padx=10)

    def setup_sidebar(self):
        sidebar_frame = tk.Frame(self.root, bg=self.card_color, width=220)
        sidebar_frame.pack(fill='y', side='left')
        sidebar_frame.pack_propagate(False)

        nav_options = [
            ("Dashboard", "dashboard", None),
            ("Monitor Footage", "monitor", lambda: verify_and_open_folder("monitor")),
            ("Recording Footage", "record", lambda: verify_and_open_folder("recordings")),
            ("Motion Alert Footage", "noise", lambda: verify_and_open_folder("alert")),
            ("IN/OUT Footage", "in_out", lambda: verify_and_open_folder("IO")),
            ("Settings", "settings", None)
        ]

        for text, icon, command in nav_options:
            btn = tk.Button(
                sidebar_frame,
                text=text,
                image=self.icons[icon] if not isinstance(self.icons.get(icon, ""), str) else None,
                compound='left',
                bg=self.card_color,
                fg=self.text_color,
                activebackground=self.button_hover,
                activeforeground=self.text_color,
                font=self.button_font,
                anchor='w',
                bd=0,
                padx=20,
                pady=12,
                highlightthickness=0,
                relief='flat',
                command=lambda c=command: [self.play_click_sound(), c()] if c else self.play_click_sound()
            )

            if isinstance(self.icons.get(icon, ""), str):
                btn.config(text=f"{self.icons.get(icon, '')}  {text}")

            btn.pack(fill='x', pady=2)

            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.button_hover))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.card_color))

    def setup_main_content(self):
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        section_label = tk.Label(
            main_frame,
            text="Security Features",
            font=self.subtitle_font,
            fg=self.text_color,
            bg=self.bg_color,
            anchor='w'
        )
        section_label.pack(fill='x', pady=(0, 15))

        cards_frame = tk.Frame(main_frame, bg=self.bg_color)
        cards_frame.pack(expand=True, fill='both')

        self.feature_buttons = [
            ("Live Monitor", find_motion, "monitor", '#3f37c9'),
            ("Motion Zones", rect_noise, "rectangle", '#4895ef'),
            ("Face Identify", maincall, "identify", '#4cc9f0'),
            ("Motion Alerts", noise, "noise", '#4361ee'),
            ("Record Video", record, "record", '#f72585'),
            ("In/Out Tracker", in_out, "in_out", '#7209b7')
        ]

        for i, (text, command, icon, color) in enumerate(self.feature_buttons):
            row = i // 3
            col = i % 3

            card = tk.Frame(
                cards_frame,
                bg=self.card_color,
                bd=0,
                highlightbackground=self.button_hover,
                highlightthickness=1,
                relief='flat'
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            cards_frame.grid_columnconfigure(col, weight=1)
            cards_frame.grid_rowconfigure(row, weight=1)

            if isinstance(self.icons.get(icon, ""), str):
                icon_label = tk.Label(
                    card,
                    text=self.icons.get(icon, ""),
                    font=("Arial", 40),
                    bg=self.card_color,
                    fg=color
                )
            else:
                icon_label = tk.Label(
                    card,
                    image=self.icons.get(icon),
                    bg=self.card_color
                )
            icon_label.pack(pady=(20, 10))

            title_label = tk.Label(
                card,
                text=text,
                font=self.button_font,
                fg=self.text_color,
                bg=self.card_color
            )
            title_label.pack(pady=(0, 15))

            action_btn = tk.Button(
                card,
                text="Activate",
                command=lambda c=command: [self.play_click_sound(), c()],
                bg=color,
                fg='white',
                activebackground=self.darken_color(color),
                activeforeground='white',
                font=self.small_font,
                bd=0,
                padx=15,
                pady=5,
                highlightthickness=0,
                relief='flat'
            )
            action_btn.pack(pady=(0, 20))

            card.bind("<Enter>", lambda e, c=card: c.config(bg=self.highlight_color(color)))
            card.bind("<Leave>", lambda e, c=card: c.config(bg=self.card_color))

            for child in card.winfo_children():
                child.bind("<Enter>", lambda e, c=card: c.config(bg=self.highlight_color(color)))
                child.bind("<Leave>", lambda e, c=card: c.config(bg=self.card_color))

    def setup_footer(self):
        footer_frame = tk.Frame(self.root, bg=self.header_color, height=50)
        footer_frame.pack(fill='x', side='bottom')

        sys_info = tk.Label(
            footer_frame,
            text="Smart CCTV v3.0 | © 2024 Security Systems Ltd.",
            font=self.small_font,
            fg=self.secondary_text,
            bg=self.header_color
        )
        sys_info.pack(side='left', padx=20)

        quick_actions = tk.Frame(footer_frame, bg=self.header_color)
        quick_actions.pack(side='right', padx=20)

        if isinstance(self.icons["power"], str):
            exit_btn = tk.Button(
                quick_actions,
                text=f"{self.icons['power']} Exit",
                command=self.confirm_exit,
                bg=self.accent_color,
                fg='white',
                activebackground=self.darken_color(self.accent_color),
                activeforeground='white',
                font=self.small_font,
                bd=0,
                padx=12,
                pady=4,
                highlightthickness=0,
                relief='flat'
            )
        else:
            exit_btn = tk.Button(
                quick_actions,
                image=self.icons["power"],
                command=self.confirm_exit,
                bg=self.accent_color,
                activebackground=self.darken_color(self.accent_color),
                bd=0,
                highlightthickness=0,
                relief='flat'
            )
        exit_btn.pack(side='right', padx=5)

    def highlight_color(self, color, factor=1.2):
        if color.startswith('#'):
            color = color[1:]
        rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        rgb = tuple(int(min(255, c * factor)) for c in rgb)
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

    def darken_color(self, color, factor=0.8):
        if color.startswith('#'):
            color = color[1:]
        rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        rgb = tuple(int(max(0, c * factor)) for c in rgb)
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

    def confirm_exit(self):
        self.play_click_sound()
        if messagebox.askyesno("Exit", "Are you sure you want to exit the CCTV system?"):
            self.exit_program()

    def exit_program(self):
        self.status_var.set("● Shutting down...")
        self.status_indicator.config(fg=self.accent_color)
        self.root.update()
        print("Thank you for using Smart CCTV System")
        self.root.quit()

    def check_exit_keys(self):
        if keyboard.is_pressed("alt") or keyboard.is_pressed("win+esc"):
            print("Forced exit: Alt or Windows + Esc pressed.")
            self.exit_program()
        self.root.after(100, self.check_exit_keys)


if __name__ == "__main__":
    root = tk.Tk()
    try:
        if os.path.exists('icons/spy.png'):
            img = Image.open('icons/spy.png')
            photo = ImageTk.PhotoImage(img)
            root.wm_iconphoto(True, photo)
    except Exception as e:
        print(f"Couldn't load window icon: {e}")

    app = SmartCCTVApp(root)
    root.protocol("WM_DELETE_WINDOW", app.confirm_exit)
    root.mainloop()
