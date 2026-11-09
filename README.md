# Mimikyu Desktop Pet

An autonomous, interactive Pokémon desktop companion for Linux and Windows, written in Python.

Inspired by Pokémon Mystery Dungeon sprites, Mimikyu roams your screens, dashes around, reacts to clicks, and sleeps when you are away.

---

## Why Mimikyu?

Because I love him, duh. Open to porting other Pokémon though, if requested.

---

## Features

- **Autonomous Movement:** Walks and dashes naturally in 8 directions at a smooth 40 FPS.
- **Interactive Reactions:** Click on Mimikyu to make it flinch and shake in pain with directional tremors.
- **Drag & Relocate:**
  - **Linux:** Move Mimikyu anywhere using your window manager's native shortcut (`Super + Left Click`).
  - **Windows:** Click and drag directly with your mouse (`Left Click + Drag`).
- **Right-Click Menu (Windows):** Right-click Mimikyu anytime to pet him, tell him to nap, wake him up, or exit.
- **Multi-Monitor Aware:** Roams seamlessly across virtual screens and multiple displays.
- **Idle Sleep Mode:** Automatically curls up and goes to sleep after 5 minutes of cursor inactivity, and wakes up immediately when you move the mouse.
- **Compact & Snug Canvas:** Sprites are cleanly cropped to a 32×32 pixel grid (80×80 px at 2.5× desktop scale), tightly wrapping the character without dead transparent space.
- **One-command Toggle:** Single command or shortcut toggles the pet on/off.

---

## Linux Setup

### Requirements
- **Python 3.8+**
- **GTK 3** & **PyGObject**

```bash
# Arch Linux / Manjaro:
sudo pacman -S python-gobject gtk3

# Debian / Ubuntu / Pop!_OS:
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0

# Fedora:
sudo dnf install python3-gobject gtk3
```

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Aoex2612/mimikyu-pet.git
   cd mimikyu-pet
   ```
2. Run the installer:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

   This will:
   - Copy sprites and source to `~/.local/share/mimikyu/`
   - Symlink the launcher executable to `~/.local/bin/mimikyu`
   - Install `mimikyu.desktop` and application icons so it appears in your system app launcher (GNOME, KDE Plasma, XFCE, Rofi, Wofi, etc.)

3. Ensure `~/.local/bin` is in your `$PATH`.

### Hyprland Configuration
Since this program was originally made in the Hyprland desktop environment, window rules ensuring it displays borderless and without jitter are included. See `hyprland/desktop-pet.conf`

---

## Windows Setup

Download the `Mimikyu.exe` file from the release. You can also build your own executable if you want running the `build-exe.bat` file.

---

## Controls

| Action | Linux Control | Windows Control | Description |
|---|---|---|---|
| **Toggle On/Off** | `mimikyu` in terminal or keybind | Run `mimikyu.bat` or Right-click → *Close* | Starts or gracefully closes Mimikyu |
| **Damage / Shake** | `Left Click` on Mimikyu | `Left Click` on Mimikyu | Triggers damage reaction and trembling |
| **Move / Drag** | `Super + Left Click` (drag) | `Left Click + Drag` | Drag Mimikyu to any spot on your screen |
| **Context Menu** | — | `Right Click` on Mimikyu | Quick actions: Pet, Nap, Wake up, Close |
| **Wake Up** | Move mouse cursor | Move mouse cursor | Wakes Mimikyu from sleep mode |
| **Specific Monitor** | `mimikyu HDMI-A-1` / `mimikyu laptop` | Automatic (spans all monitors) | Direct monitor selection |

---

## Project Structure

```text
mimikyu-pet/
├── assets/              # App icons (.png, .ico) and .desktop menu entry
│   ├── mimikyu.desktop
│   ├── mimikyu.ico
│   └── mimikyu.png
├── sprites/             # 130 32x32 PNG sprite frames
├── src/
│   ├── mimikyu.py       # Cross-platform dispatcher & Linux GTK3 implementation
│   └── mimikyu_windows.py # Native Windows Tkinter/Win32 implementation
├── bin/
│   ├── mimikyu          # Portable POSIX sh launcher (Linux)
│   └── mimikyu.bat      # Silent background launcher (Windows)
├── hyprland/
│   └── desktop-pet.conf # Ready-to-source Hyprland rules
├── build_exe.bat        # One-click Windows PyInstaller .exe compiler
├── install.sh           # One-command Linux installer / uninstaller
├── requirements.txt     # Python dependencies
├── LICENSE              # MIT License
└── README.md
```

---

## Credits

- Sprite artwork sourced from the **Pokémon Mystery Dungeon** series and the [PMD SpriteCollab](https://sprites.pmdcollab.org/) community project.
- Pokémon and Mimikyu are trademarks of Nintendo, Game Freak, and The Pokémon Company.

---

## License

This project is open-source under the [MIT License](LICENSE).
