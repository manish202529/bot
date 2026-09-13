import random
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui

REFERENCE_W, REFERENCE_H = 1920, 1080

TOOLS = {
    "Filters": (1868, 281),
    "Effects": (1868, 350),
    "Adjust colours": (1868, 420),
    "Speed": (1868, 480),
    "Fade": (1868, 204),
}

PANEL = (1360, 115, 1780, 800)
pyautogui.PAUSE = 0.08
pyautogui.FAILSAFE = True


class ClipchampBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipchamp Activity Bot")
        self.root.geometry("470x650")
        self.root.minsize(450, 620)
        self.running = False
        self.worker = None

        self.activity_vars = {name: tk.BooleanVar(value=True) for name in TOOLS}
        self.min_delay = tk.DoubleVar(value=5)
        self.max_delay = tk.DoubleVar(value=15)
        self.status_var = tk.StringVar(value="Stopped")

        self.build_ui()
        self.root.bind_all("<F8>", lambda e: self.start())
        self.root.bind_all("<F9>", lambda e: self.stop())
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def build_ui(self):
        main = ttk.Frame(self.root, padding=14)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Clipchamp Activity Bot",
                  font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(main, text="Designed for the 1920×1080 Clipchamp layout.").pack(
            anchor="w", pady=(0, 10))

        status = ttk.LabelFrame(main, text="Status", padding=10)
        status.pack(fill="x", pady=(0, 8))
        ttk.Label(status, textvariable=self.status_var,
                  font=("Segoe UI", 13, "bold")).pack(anchor="w")

        # FIX: Start/Stop buttons are now near the top and always visible.
        buttons = ttk.Frame(main)
        buttons.pack(fill="x", pady=(0, 10))
        self.start_button = ttk.Button(buttons, text="START (F8)", command=self.start)
        self.start_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.stop_button = ttk.Button(buttons, text="STOP (F9)", command=self.stop)
        self.stop_button.pack(side="left", fill="x", expand=True, padx=(5, 0))

        activities = ttk.LabelFrame(main, text="Activities", padding=10)
        activities.pack(fill="x", pady=(0, 8))
        for name, var in self.activity_vars.items():
            ttk.Checkbutton(activities, text=name, variable=var).pack(anchor="w", pady=2)

        timing = ttk.LabelFrame(main, text="Timing", padding=10)
        timing.pack(fill="x", pady=(0, 8))

        row = ttk.Frame(timing)
        row.pack(fill="x", pady=3)
        ttk.Label(row, text="Minimum delay (seconds)", width=25).pack(side="left")
        ttk.Spinbox(row, from_=1, to=300, textvariable=self.min_delay, width=8).pack(side="left")

        row = ttk.Frame(timing)
        row.pack(fill="x", pady=3)
        ttk.Label(row, text="Maximum delay (seconds)", width=25).pack(side="left")
        ttk.Spinbox(row, from_=1, to=300, textvariable=self.max_delay, width=8).pack(side="left")

        info = ttk.LabelFrame(main, text="How to use", padding=10)
        info.pack(fill="both", expand=True)
        text = ("1. Open Clipchamp and start your video.\n"
                "2. Keep the 1920×1080 layout used for this bot.\n"
                "3. Select the activities you want.\n"
                "4. Click START or press F8.\n"
                "5. Click STOP or press F9 when finished.\n\n"
                "Emergency stop: move the mouse to the top-left corner.\n"
                "The bot avoids Export, Share, Import and Settings.")
        ttk.Label(info, text=text, justify="left", wraplength=410).pack(anchor="w")

    def scaled(self, point):
        w, h = pyautogui.size()
        return int(point[0] * w / REFERENCE_W), int(point[1] * h / REFERENCE_H)

    def start(self):
        if self.running:
            return
        selected = [n for n, v in self.activity_vars.items() if v.get()]
        if not selected:
            messagebox.showwarning("No activities selected", "Select at least one activity.")
            return
        try:
            mn, mx = float(self.min_delay.get()), float(self.max_delay.get())
        except Exception:
            messagebox.showerror("Invalid timing", "Enter valid delay values.")
            return
        if mn <= 0 or mx < mn:
            messagebox.showerror("Invalid timing", "Maximum delay must be >= minimum delay.")
            return

        self.running = True
        self.status_var.set("Running")
        self.start_button.state(["disabled"])
        self.worker = threading.Thread(target=self.loop, args=(selected, mn, mx), daemon=True)
        self.worker.start()

    def stop(self):
        self.running = False
        self.status_var.set("Stopped")
        if hasattr(self, "start_button"):
            self.start_button.state(["!disabled"])

    def loop(self, selected, mn, mx):
        while self.running:
            try:
                x1, y1, x2, y2 = PANEL
                p = (random.randint(x1 + 30, x2 - 30),
                     random.randint(y1 + 30, y2 - 30))
                pyautogui.moveTo(*self.scaled(p), duration=random.uniform(.15, .5))
                name = random.choice(selected)
                pyautogui.click(*self.scaled(TOOLS[name]))
                end = time.time() + random.uniform(mn, mx)
                while self.running and time.time() < end:
                    time.sleep(.2)
            except pyautogui.FailSafeException:
                self.root.after(0, self.stop)
                break
            except Exception:
                self.root.after(0, self.stop)
                break

    def close(self):
        self.running = False
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    try:
        ttk.Style().theme_use("vista")
    except Exception:
        pass
    ClipchampBot(root)
    root.mainloop()
