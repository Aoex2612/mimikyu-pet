#!/usr/bin/env python3
"""
Mimikyu Desktop Pet for Windows (Tkinter / Win32 API).
An interactive, autonomous roaming desktop companion.
"""

import os
import sys
import time
import random
import tkinter as tk
from PIL import Image, ImageTk

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
else:
    ctypes = None

def resolve_sprites_dir():
    """Finds the sprites folder (supporting PyInstaller bundles, relative paths, etc.)."""
    if hasattr(sys, "_MEIPASS"):
        bundled = os.path.join(sys._MEIPASS, "sprites")
        if os.path.isdir(bundled):
            return bundled

    candidates = [
        os.environ.get("MIMIKYU_SPRITES_DIR"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sprites"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites"),
        os.path.expanduser("~/.local/share/mimikyu/sprites"),
        os.path.expanduser("~/.config/bongocat/sprites"),
    ]
    for path in candidates:
        if path and os.path.isdir(path):
            return os.path.abspath(path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sprites")

SPRITES_DIR = resolve_sprites_dir()

# Timing & Motion
TICK_INTERVAL_MS = 25       # 40 FPS for smooth translation
ANIM_TICKS = 4              # 4 * 25ms = 100ms per sprite animation frame
BASE_MOVE_STEP = 1.15       # Pixels per 25ms tick
SCALE_FACTOR = 2.5          # 32x32 sprite -> 80x80 on-screen window
TARGET_SIZE = int(32 * SCALE_FACTOR)

# Screen boundary padding
PADDING_LEFT = 20.0
PADDING_RIGHT = 20.0
PADDING_TOP = 20.0
PADDING_BOTTOM = 60.0       # Leaves room for the Windows Taskbar

IDLE_SLEEP_TIMEOUT = 300.0  # 5 minutes of inactivity before sleeping
TRANSPARENT_KEY = "#010101" # Chroma key for Windows layered window transparency

DIR_NAMES = ["down", "down_right", "right", "up_right", "up", "up_left", "left", "down_left"]

DIRECTIONS = {
    "down":       {"delta": (0, BASE_MOVE_STEP),          "row": 0},
    "down_right": {"delta": (BASE_MOVE_STEP, BASE_MOVE_STEP),   "row": 1},
    "right":      {"delta": (BASE_MOVE_STEP, 0),          "row": 2},
    "up_right":   {"delta": (BASE_MOVE_STEP, -BASE_MOVE_STEP),  "row": 3},
    "up":         {"delta": (0, -BASE_MOVE_STEP),         "row": 4},
    "up_left":    {"delta": (-BASE_MOVE_STEP, -BASE_MOVE_STEP), "row": 5},
    "left":       {"delta": (-BASE_MOVE_STEP, 0),         "row": 6},
    "down_left":  {"delta": (-BASE_MOVE_STEP, BASE_MOVE_STEP),  "row": 7},
}

def get_system_screen_bounds():
    """Returns virtual screen bounding rectangle (covers all monitors on Windows)."""
    if sys.platform == "win32" and ctypes:
        try:
            u32 = ctypes.windll.user32
            min_x = u32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
            min_y = u32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
            width = u32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
            height = u32.GetSystemMetrics(79) # SM_CYVIRTUALSCREEN
            if width > 0 and height > 0:
                return float(min_x), float(min_y), float(width), float(height)
        except Exception:
            pass
    return 0.0, 0.0, 1920.0, 1080.0

def get_system_idle_seconds():
    """Returns the number of seconds since last user input on Windows."""
    if sys.platform == "win32" and ctypes:
        try:
            class LASTINPUTINFO(ctypes.Structure):
                _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
            lii = LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
            if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
                millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
                return millis / 1000.0
        except Exception:
            pass
    return 0.0

def get_cursor_pos():
    """Returns current global cursor position (x, y)."""
    if sys.platform == "win32" and ctypes:
        try:
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            pt = POINT()
            if ctypes.windll.user32.GetCursorPos(ctypes.byref(pt)):
                return float(pt.x), float(pt.y)
        except Exception:
            pass
    return None, None

class WindowsMimikyuPet:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mimikyu")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        # Set transparent chroma key
        try:
            self.root.wm_attributes("-transparentcolor", TRANSPARENT_KEY)
        except Exception:
            pass
        self.root.config(bg=TRANSPARENT_KEY)

        # Set ToolWindow style so it does not clutter Taskbar / Alt-Tab
        if sys.platform == "win32" and ctypes:
            self.root.after(10, self.apply_win32_styles)

        # Main image label
        self.label = tk.Label(self.root, bg=TRANSPARENT_KEY, bd=0, highlightthickness=0)
        self.label.pack()

        # Screen metrics
        vx, vy, vw, vh = get_system_screen_bounds()
        self.min_x = vx
        self.min_y = vy
        self.max_w = vw
        self.max_h = vh

        self.cur_w = TARGET_SIZE
        self.cur_h = TARGET_SIZE
        self.x = vx + (vw / 2.0) - (self.cur_w / 2.0)
        self.y = vy + (vh / 2.0) - (self.cur_h / 2.0)

        # State & animation
        self.sprites_cache = {}
        self.current_sprite_name = ""
        self.current_dir = "down"
        self.frame_idx = 0
        self.sleep_tick_counter = 0
        self.state = "walk"
        self.steps_left = 35

        self.tick_counter = 0
        self.last_activity_time = time.time()
        self.last_cursor_pos = get_cursor_pos()

        # Mouse dragging & click interaction
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_win_x = self.x
        self.drag_win_y = self.y

        self.label.bind("<Button-1>", self.on_mouse_down)
        self.label.bind("<B1-Motion>", self.on_mouse_drag)
        self.label.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.label.bind("<Button-3>", self.show_context_menu)

        # Right-click context menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Pet Mimikyu ❤️", command=self.trigger_hurt)
        self.menu.add_command(label="Take a Nap 💤", command=self.trigger_sleep)
        self.menu.add_command(label="Wake Up ⚡", command=self.trigger_wake)
        self.menu.add_separator()
        self.menu.add_command(label="Close Mimikyu", command=self.root.destroy)

        self.update_sprite()
        self.root.geometry(f"{self.cur_w}x{self.cur_h}+{int(self.x)}+{int(self.y)}")

        # Start game tick
        self.root.after(TICK_INTERVAL_MS, self.tick)

    def apply_win32_styles(self):
        """Hides window from taskbar and Alt-Tab using Windows API."""
        try:
            GWL_EXSTYLE = -20
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_APPWINDOW = 0x00040000
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if hwnd:
                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                style = (style | WS_EX_TOOLWINDOW) & ~WS_EX_APPWINDOW
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        except Exception:
            pass

    def on_mouse_down(self, event):
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        self.drag_win_x = self.x
        self.drag_win_y = self.y
        self.is_dragging = False
        self.last_activity_time = time.time()

    def on_mouse_drag(self, event):
        dx = event.x_root - self.drag_start_x
        dy = event.y_root - self.drag_start_y
        if abs(dx) > 3 or abs(dy) > 3:
            self.is_dragging = True
            self.x = self.drag_win_x + dx
            self.y = self.drag_win_y + dy
            self.root.geometry(f"+{int(self.x)}+{int(self.y)}")

    def on_mouse_up(self, event):
        if not self.is_dragging:
            # Single click without dragging -> trigger hurt reaction
            self.trigger_hurt()
        self.is_dragging = False

    def show_context_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def trigger_hurt(self):
        self.last_activity_time = time.time()
        self.state = "hurt"
        self.frame_idx = 0
        self.steps_left = 15
        self.update_sprite()

    def trigger_sleep(self):
        self.state = "sleep"
        self.frame_idx = 0
        self.sleep_tick_counter = 0
        self.update_sprite()

    def trigger_wake(self):
        self.state = "walk"
        self.frame_idx = 0
        self.steps_left = random.randint(25, 55)
        self.last_activity_time = time.time()
        self.update_sprite()

    def update_sprite(self):
        row = DIRECTIONS[self.current_dir]["row"]

        if self.state == "walk":
            frame_num = (row * 4) + (self.frame_idx % 4)
            filename = f"walk_frame_{frame_num:02d}.png"
        elif self.state == "dash":
            frame_num = (row * 10) + (self.frame_idx % 10)
            filename = f"charge_frame_{frame_num:02d}.png"
        elif self.state == "hurt":
            frame_num = (row * 2) + (self.frame_idx % 2)
            filename = f"hurt_frame_{frame_num:02d}.png"
        elif self.state == "sleep":
            frame_num = self.frame_idx % 2
            filename = f"sleep_frame_{frame_num:02d}.png"
        else:
            frame_num = (row * 4)
            filename = f"walk_frame_{frame_num:02d}.png"

        if filename == self.current_sprite_name:
            return

        if filename not in self.sprites_cache:
            path = os.path.join(SPRITES_DIR, filename)
            if os.path.exists(path):
                try:
                    im = Image.open(path).convert("RGBA")
                    # Replace fully transparent alpha with TRANSPARENT_KEY (RGB: 1, 1, 1)
                    bg = Image.new("RGBA", im.size, (1, 1, 1, 255))
                    composed = Image.alpha_composite(bg, im)
                    scaled = composed.resize((TARGET_SIZE, TARGET_SIZE), Image.Resampling.NEAREST)
                    photo = ImageTk.PhotoImage(scaled)
                    self.sprites_cache[filename] = photo
                except Exception as e:
                    print(f"Error loading {path}: {e}")
                    return
            else:
                return

        photo = self.sprites_cache[filename]
        self.label.config(image=photo)
        self.label.image = photo
        self.current_sprite_name = filename

    def check_user_idle(self):
        now = time.time()
        cur_pos = get_cursor_pos()

        # Check cursor movement
        if cur_pos != (None, None):
            if cur_pos != self.last_cursor_pos:
                self.last_cursor_pos = cur_pos
                if self.state == "sleep":
                    self.trigger_wake()
                self.last_activity_time = now

        # Check system-wide idle on Windows
        idle_sec = get_system_idle_seconds()
        if idle_sec > 0:
            if idle_sec >= IDLE_SLEEP_TIMEOUT and self.state not in ("sleep", "hurt"):
                self.trigger_sleep()
        else:
            if (now - self.last_activity_time) >= IDLE_SLEEP_TIMEOUT and self.state not in ("sleep", "hurt"):
                self.trigger_sleep()

    def tick(self):
        # Do not move while being dragged by user
        if not self.is_dragging:
            self.tick_counter += 1

            if self.tick_counter % 20 == 0:
                self.check_user_idle()

            is_anim_tick = (self.tick_counter % ANIM_TICKS == 0)
            if is_anim_tick:
                if self.state == "walk":
                    self.frame_idx = (self.frame_idx + 1) % 4
                elif self.state == "dash":
                    self.frame_idx = (self.frame_idx + 1) % 10
                elif self.state == "hurt":
                    self.frame_idx = (self.frame_idx + 1) % 2
                elif self.state == "sleep":
                    self.sleep_tick_counter += 1
                    if self.sleep_tick_counter >= 6:
                        self.sleep_tick_counter = 0
                        self.frame_idx = (self.frame_idx + 1) % 2

                # State transitions
                if self.state != "sleep":
                    if self.steps_left <= 0:
                        dice = random.random()
                        if dice < 0.25:
                            self.state = "dash"
                            self.frame_idx = 0
                            self.current_dir = random.choice(DIR_NAMES)
                            self.steps_left = random.randint(20, 35)
                        elif dice < 0.45:
                            self.state = "idle"
                            self.frame_idx = 0
                            self.steps_left = random.randint(15, 30)
                        else:
                            self.state = "walk"
                            self.frame_idx = 0
                            self.current_dir = random.choice(DIR_NAMES)
                            self.steps_left = random.randint(25, 55)
                    else:
                        self.steps_left -= 1

                self.update_sprite()

            # Translation
            if self.state in ("walk", "dash"):
                dx, dy = DIRECTIONS[self.current_dir]["delta"]
                mult = 2.2 if self.state == "dash" else 1.0
                self.x += dx * mult
                self.y += dy * mult

                min_bound_x = self.min_x + PADDING_LEFT
                max_bound_x = self.min_x + self.max_w - self.cur_w - PADDING_RIGHT
                min_bound_y = self.min_y + PADDING_TOP
                max_bound_y = self.min_y + self.max_h - self.cur_h - PADDING_BOTTOM

                if self.x < min_bound_x:
                    self.x = min_bound_x
                    self.current_dir = random.choice(["right", "up_right", "down_right"])
                elif self.x > max_bound_x:
                    self.x = max_bound_x
                    self.current_dir = random.choice(["left", "up_left", "down_left"])

                if self.y < min_bound_y:
                    self.y = min_bound_y
                    self.current_dir = random.choice(["down", "down_left", "down_right"])
                elif self.y > max_bound_y:
                    self.y = max_bound_y
                    self.current_dir = random.choice(["up", "up_left", "up_right"])

                self.root.geometry(f"+{int(self.x)}+{int(self.y)}")

        self.root.after(TICK_INTERVAL_MS, self.tick)

    def run(self):
        self.root.mainloop()

def main():
    pet = WindowsMimikyuPet()
    pet.run()

if __name__ == "__main__":
    main()
