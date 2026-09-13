import tkinter as tk
from tkinter import ttk, messagebox
import threading, time, random
import pyautogui

# Clipchamp 1920x1080 reference layout from the user's screenshot.
# Coordinates are scaled to the current screen resolution.
REFERENCE_W, REFERENCE_H = 1920, 1080

# Safe right-side Clipchamp tool buttons visible in the supplied screenshot.
TOOLS = {
    "Filters": (1868, 281),
    "Effects": (1868, 350),
    "Adjust colours": (1868, 420),
    "Speed": (1868, 480),
    "Fade": (1868, 204),
}

# Approximate panel area where filter/effect choices appear after opening a tool.
# Kept away from Export/Share and the timeline.
PANEL = (1360, 115, 1780, 800)

class ClipchampBot:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.thread = None
        self.stop_event = threading.Event()
        self.status = tk.StringVar(value="Stopped")
        self.log_lines = []

        root.title("Clipchamp Activity Bot")
        root.geometry("430x520")
        root.resizable(False, False)

        frm = ttk.Frame(root, padding=16)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Clipchamp Activity Bot",
                  font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(frm, text="Designed for the 1920×1080 layout in your screenshot.",
                  foreground="#555").pack(anchor="w", pady=(2, 12))

        status_frame = ttk.LabelFrame(frm, text="Status", padding=10)
        status_frame.pack(fill="x", pady=(0, 12))
        ttk.Label(status_frame, textvariable=self.status,
                  font=("Segoe UI", 11, "bold")).pack(anchor="w")

        opts = ttk.LabelFrame(frm, text="Activities", padding=10)
        opts.pack(fill="x", pady=(0, 12))

        self.vars = {}
        for name in TOOLS:
            v = tk.BooleanVar(value=True)
            self.vars[name] = v
            ttk.Checkbutton(opts, text=name, variable=v).pack(anchor="w", pady=2)

        settings = ttk.LabelFrame(frm, text="Timing", padding=10)
        settings.pack(fill="x", pady=(0, 12))

        ttk.Label(settings, text="Minimum delay (seconds)").grid(row=0, column=0, sticky="w")
        self.min_delay = tk.DoubleVar(value=1.5)
        ttk.Spinbox(settings, from_=0.5, to=20, increment=0.5,
                    textvariable=self.min_delay, width=8).grid(row=0, column=1, padx=8)

        ttk.Label(settings, text="Maximum delay (seconds)").grid(row=1, column=0, sticky="w", pady=(7,0))
        self.max_delay = tk.DoubleVar(value=4.0)
        ttk.Spinbox(settings, from_=1, to=30, increment=0.5,
                    textvariable=self.max_delay, width=8).grid(row=1, column=1, padx=8, pady=(7,0))

        ttk.Label(settings, text="Tip: keep Clipchamp maximized.").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(8,0))

        buttons = ttk.Frame(frm)
        buttons.pack(fill="x", pady=(4, 8))
        self.start_btn = ttk.Button(buttons, text="START", command=self.start)
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.stop_btn = ttk.Button(buttons, text="STOP", command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=(5,0))

        ttk.Label(frm, text="Emergency stop: move mouse to the top-left corner.",
                  foreground="#a33").pack(anchor="w")

        log_frame = ttk.LabelFrame(frm, text="Activity log", padding=6)
        log_frame.pack(fill="both", expand=True, pady=(10,0))
        self.log = tk.Text(log_frame, height=7, state="disabled", wrap="word")
        self.log.pack(fill="both", expand=True)

        root.bind("<F8>", lambda e: self.start())
        root.bind("<F9>", lambda e: self.stop())

    def write_log(self, text):
        self.log_lines.append(text)
        self.log_lines = self.log_lines[-50:]
        self.root.after(0, self._refresh_log)

    def _refresh_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.insert("end", "\n".join(self.log_lines))
        self.log.see("end")
        self.log.configure(state="disabled")

    def scale(self, x, y):
        w, h = pyautogui.size()
        return int(x * w / REFERENCE_W), int(y * h / REFERENCE_H)

    def safe_move(self, x, y, duration=None):
        sx, sy = self.scale(x, y)
        if duration is None:
            duration = random.uniform(0.25, 0.9)
        pyautogui.moveTo(sx, sy, duration=duration)

    def safe_click_tool(self, name):
        x, y = TOOLS[name]
        self.safe_move(x + random.randint(-7,7), y + random.randint(-7,7))
        pyautogui.click()
        self.write_log(f"Opened: {name}")

    def random_panel_activity(self):
        # Randomly move within the editor's right panel and click only a
        # conservative inner region. This is intentionally NOT a whole-screen
        # random clicker.
        x1, y1, x2, y2 = PANEL
        x = random.randint(x1 + 30, x2 - 30)
        y = random.randint(y1 + 80, y2 - 60)
        self.safe_move(x, y)
        if random.random() < 0.55:
            pyautogui.click()
            self.write_log(f"Panel test click at ({x},{y})")
        else:
            self.write_log(f"Panel movement to ({x},{y})")

    def start(self):
        if self.running:
            return
        selected = [n for n,v in self.vars.items() if v.get()]
        if not selected:
            messagebox.showwarning("No activities", "Select at least one activity.")
            return
        try:
            mn, mx = float(self.min_delay.get()), float(self.max_delay.get())
        except Exception:
            messagebox.showerror("Timing", "Please enter valid delay values.")
            return
        if mn <= 0 or mx < mn:
            messagebox.showerror("Timing", "Maximum delay must be >= minimum delay.")
            return

        self.running = True
        self.stop_event.clear()
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status.set("Running — press F9 to stop")
        self.write_log("Bot started.")
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status.set("Stopped")
        self.write_log("Bot stopped.")

    def worker(self):
        selected = [n for n,v in self.vars.items() if v.get()]
        while not self.stop_event.is_set():
            # Move cursor through a few safe-ish UI locations, avoiding the
            # timeline and the Export button.
            for _ in range(random.randint(2,4)):
                if self.stop_event.is_set():
                    break
                self.safe_move(
                    random.randint(360, 1280),
                    random.randint(100, 500)
                )
                time.sleep(random.uniform(0.15, 0.6))

            if self.stop_event.is_set():
                break

            activity = random.choice(selected)
            self.safe_click_tool(activity)
            time.sleep(random.uniform(0.7, 1.5))
            self.random_panel_activity()

            # Random delay before next activity.
            try:
                delay = random.uniform(float(self.min_delay.get()),
                                       float(self.max_delay.get()))
            except Exception:
                delay = 2.0
            self.stop_event.wait(delay)

        self.root.after(0, self._stopped_from_worker)

    def _stopped_from_worker(self):
        if not self.running:
            return
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status.set("Stopped")
        self.write_log("Bot stopped.")

def main():
    pyautogui.PAUSE = 0.08
    pyautogui.FAILSAFE = True
    root = tk.Tk()
    ClipchampBot(root)
    root.mainloop()

if __name__ == "__main__":
    main()
