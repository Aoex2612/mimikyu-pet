#!/usr/bin/env python3
"""
Mimikyu Desktop Pet for Linux (Hyprland / Wayland / X11).
An interactive, autonomous roaming desktop companion.
"""

import os
import sys
import time
import random
import socket
import json

os.environ["GDK_BACKEND"] = "x11"

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GdkPixbuf, Gdk

GLib.set_prgname("desktop-pet")
GLib.set_application_name("desktop-pet")

def resolve_sprites_dir():
    """Finds the sprites folder by checking environment, relative paths, and XDG data paths."""
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
    # Default fallback
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sprites")

SPRITES_DIR = resolve_sprites_dir()

# Timing & Motion
TICK_INTERVAL_MS = 25       # 40 FPS for smooth window translation
ANIM_TICKS = 4              # 4 * 25ms = 100ms per sprite animation frame
BASE_MOVE_STEP = 1.15       # Pixels per 25ms tick
SCALE_FACTOR = 2.5          # 32x32 sprite -> 80x80 on-screen window

# Screen boundary padding (leaves room for top Waybar / screen edges)
PADDING_LEFT = 20.0
PADDING_RIGHT = 20.0
PADDING_TOP = 48.0
PADDING_BOTTOM = 15.0

IDLE_SLEEP_TIMEOUT = 300.0  # 5 minutes of inactivity before sleeping

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

def get_hypr_focused_monitor():
    """Queries Hyprland's IPC socket to find the currently active/focused monitor."""
    his = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    xdg_runtime = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    sock_path = os.path.join(xdg_runtime, "hypr", his, ".socket.sock") if his else ""
    if sock_path and os.path.exists(sock_path):
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(0.05)
            s.connect(sock_path)
            s.sendall(b"j/monitors")
            raw = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                raw += chunk
            s.close()
            if raw:
                for m in json.loads(raw.decode("utf-8")):
                    if m.get("focused"):
                        return m["name"]
        except Exception:
            pass
    return None

def get_hypr_cursor():
    """Queries Hyprland's IPC socket for the current cursor position."""
    his = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    xdg_runtime = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    sock_path = os.path.join(xdg_runtime, "hypr", his, ".socket.sock") if his else ""
    if sock_path and os.path.exists(sock_path):
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(0.04)
            s.connect(sock_path)
            s.sendall(b"j/cursorpos")
            raw = b""
            while True:
                chunk = s.recv(1024)
                if not chunk:
                    break
                raw += chunk
            s.close()
            if raw:
                data = json.loads(raw.decode("utf-8"))
                return float(data["x"]), float(data["y"])
        except Exception:
            pass
    return None, None

def get_cursor_pos():
    """Gets current cursor position via Hyprland IPC, falling back to GDK for other desktops."""
    cx, cy = get_hypr_cursor()
    if cx is not None and cy is not None:
        return cx, cy

    try:
        display = Gdk.Display.get_default()
        if display:
            seat = display.get_default_seat()
            if seat:
                pointer = seat.get_pointer()
                if pointer:
                    _, px, py = pointer.get_position()
                    return float(px), float(py)
    except Exception:
        pass
    return None, None

def choose_monitor(target_name=None):
    """Selects the target monitor (by explicit name, Hyprland focus, or cursor position)."""
    display = Gdk.Display.get_default()
    if not display:
        return None
    n = display.get_n_monitors()
    if n == 0:
        return None

    if target_name:
        target_name_lower = target_name.lower().strip()
        for i in range(n):
            m = display.get_monitor(i)
            model = (m.get_model() or "").lower()
            if target_name_lower in model:
                return m
            if target_name_lower in ("external", "hdmi", "ext") and "hdmi" in model:
                return m
            if target_name_lower in ("laptop", "internal", "edp", "int") and "edp" in model:
                return m

    focused_name = get_hypr_focused_monitor()
    if focused_name:
        for i in range(n):
            m = display.get_monitor(i)
            if m.get_model() == focused_name:
                return m

    seat = display.get_default_seat()
    if seat:
        pointer = seat.get_pointer()
        if pointer:
            _, cx, cy = pointer.get_position()
            m = display.get_monitor_at_point(cx, cy)
            if m:
                return m

    return display.get_monitor(0)

class MimikyuPet(Gtk.Window):
    def __init__(self, target_monitor_name=None):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)

        self.set_title("desktop-pet")
        self.set_role("desktop-pet")
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)

        self.cur_w = int(32 * SCALE_FACTOR)
        self.cur_h = int(32 * SCALE_FACTOR)

        # Monitor & initial placement
        self.monitor = choose_monitor(target_monitor_name)
        geom = self.monitor.get_geometry() if self.monitor else Gdk.Rectangle()
        if geom.width > 0:
            self.x = float(geom.x) + (float(geom.width) / 2.0) - (self.cur_w / 2.0)
            self.y = float(geom.y) + (float(geom.height) / 2.0) - (self.cur_h / 2.0)
        else:
            self.x = 960.0 - (self.cur_w / 2.0)
            self.y = 540.0 - (self.cur_h / 2.0)

        self.last_sent_x = int(self.x)
        self.last_sent_y = int(self.y)
        self.last_external_move_time = 0.0

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_click)
        self.connect("configure-event", self.on_configure)

        # Transparent RGBA visual
        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        self.image = Gtk.Image()
        self.add(self.image)

        # Sprite cache & state machine
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

        self.update_sprite()
        self.move(int(self.x), int(self.y))

        GLib.timeout_add(TICK_INTERVAL_MS, self.tick)

    def on_configure(self, widget, event):
        """Detects native external window dragging (e.g. Win + Left Click) while ignoring move echos."""
        dx = abs(event.x - self.last_sent_x)
        dy = abs(event.y - self.last_sent_y)
        if dx > 3 or dy > 3:
            self.x = float(event.x)
            self.y = float(event.y)
            self.last_sent_x = int(event.x)
            self.last_sent_y = int(event.y)
            self.last_external_move_time = time.time()
            display = self.get_display()
            m = display.get_monitor_at_point(int(self.x), int(self.y))
            if m:
                self.monitor = m
        return False

    def on_click(self, widget, event):
        """Clicking on Mimikyu triggers the hurt / shake reaction."""
        if event.button == 1:
            self.last_activity_time = time.time()
            self.state = "hurt"
            self.frame_idx = 0
            self.steps_left = 15
            self.update_sprite()
            return True
        return False

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
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
                    w = int(pixbuf.get_width() * SCALE_FACTOR)
                    h = int(pixbuf.get_height() * SCALE_FACTOR)
                    scaled = pixbuf.scale_simple(w, h, GdkPixbuf.InterpType.NEAREST)
                    self.sprites_cache[filename] = (scaled, w, h)
                except Exception as e:
                    print(f"Error loading {path}: {e}")
                    return
            else:
                return

        scaled, self.cur_w, self.cur_h = self.sprites_cache[filename]
        self.image.set_from_pixbuf(scaled)
        self.current_sprite_name = filename

    def check_user_idle(self):
        """Wakes Mimikyu on cursor movement; puts Mimikyu to sleep after timeout."""
        current_cursor = get_cursor_pos()
        now = time.time()

        if current_cursor != (None, None):
            if current_cursor != self.last_cursor_pos:
                self.last_cursor_pos = current_cursor
                if self.state == "sleep":
                    self.state = "walk"
                    self.frame_idx = 0
                    self.steps_left = random.randint(25, 55)
                self.last_activity_time = now

        if self.state not in ("sleep", "hurt"):
            idle_time = now - self.last_activity_time
            if idle_time >= IDLE_SLEEP_TIMEOUT:
                self.state = "sleep"
                self.frame_idx = 0
                self.sleep_tick_counter = 0

    def tick(self):
        # Pause autonomous movement while the user is actively dragging the window
        if time.time() - self.last_external_move_time < 0.25:
            return True

        self.tick_counter += 1

        # Check for cursor activity/sleep every ~500ms
        if self.tick_counter % 20 == 0:
            self.check_user_idle()

        # Sprite animation cadence (every 100ms)
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

        # Smooth position translation (40 FPS)
        if self.state in ("walk", "dash"):
            dx, dy = DIRECTIONS[self.current_dir]["delta"]
            mult = 2.2 if self.state == "dash" else 1.0
            self.x += dx * mult
            self.y += dy * mult

            display = self.get_display()
            monitor = display.get_monitor_at_point(int(self.x), int(self.y))
            if not monitor:
                monitor = self.monitor or display.get_monitor(0)
            else:
                self.monitor = monitor

            geom = monitor.get_geometry()
            min_x = float(geom.x) + PADDING_LEFT
            max_bound_x = float(geom.x + geom.width) - self.cur_w - PADDING_RIGHT
            min_y = float(geom.y) + PADDING_TOP
            max_bound_y = float(geom.y + geom.height) - self.cur_h - PADDING_BOTTOM

            if self.x < min_x:
                self.x = min_x
                self.current_dir = random.choice(["right", "up_right", "down_right"])
            elif self.x > max_bound_x:
                self.x = max_bound_x
                self.current_dir = random.choice(["left", "up_left", "down_left"])

            if self.y < min_y:
                self.y = min_y
                self.current_dir = random.choice(["down", "down_left", "down_right"])
            elif self.y > max_bound_y:
                self.y = max_bound_y
                self.current_dir = random.choice(["up", "up_left", "up_right"])

            self.last_sent_x = int(self.x)
            self.last_sent_y = int(self.y)
            self.move(self.last_sent_x, self.last_sent_y)

        return True

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    win = MimikyuPet(target)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    win.move(int(win.x), int(win.y))
    Gtk.main()
