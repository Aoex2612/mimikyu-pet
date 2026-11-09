# Mimikyu Desktop Pet

An autonomous, interactive Pokémon desktop companion for Linux (Hyprland, Wayland & X11), written in Python with GTK 3.

Inspired by Pokémon Mystery Dungeon sprites, Mimikyu roams your screens, dashes around, reacts to clicks, and sleeps when you are away.

---

## Why Mimikyu?

Because I love him, duh.

## Features

- **Autonomous Movement:** Walks and dashes naturally in 8 directions at a smooth 40 FPS.
- **Interactive Reactions:** Click on Mimikyu to make it flinch and shake in pain with directional tremors.
- **Idle Sleep Mode:** Automatically curls up and goes to sleep after 5 minutes of cursor inactivity, and wakes up immediately when you move the mouse.
- **Compact & Snug Canvas:** Sprites are cleanly cropped to a 32×32 pixel grid (80×80 px at 2.5× desktop scale), tightly wrapping the character without dead transparent space.
- **One-command Toggle:** Single command `mimikyu` toggles the pet on/off.

---

## Requirements

- **Python 3.8+**
- **GTK 3** & **PyGObject**

### Distribution Packages

- **Arch Linux / Manjaro:**
  ```bash
  sudo pacman -S python-gobject gtk3
  ```
- **Debian / Ubuntu / Pop!_OS:**
  ```bash
  sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
  ```
- **Fedora:**
  ```bash
  sudo dnf install python3-gobject gtk3
  ```

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Aoex2612/mimikyu-pet.git
   cd mimikyu-pet
   ```

2. **Run the installer:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

   This will:
   - Copy sprites and source to `~/.local/share/mimikyu/`
   - Symlink the launcher executable to `~/.local/bin/mimikyu`
   - Install `mimikyu.desktop` and application icons so it appears in your system app launcher (GNOME, KDE Plasma, XFCE, Rofi, Wofi, etc.)

3. Ensure `~/.local/bin` is in your `$PATH`.

---

## 🚀 Launching Mimikyu

- **From the Application Menu:** Search for **Mimikyu** in your desktop environment's launcher (GNOME Activities, KDE Kickoff, Rofi, etc.) and click to toggle on/off.
- **From the Terminal:**
  ```bash
  mimikyu
  ```
- **From a specific monitor:**
  ```bash
  mimikyu HDMI-A-1
  ```

---

## Hyprland Configuration

Since this program was originally made in the Hyperland desktop enviroment, some rules ensuring that shows correctly have been included. See `desktop-pet.conf`.

## Controls

| Action | Control | Description |
|---|---|---|
| **Toggle On/Off** | `mimikyu` in terminal or keybind | Starts or gracefully closes Mimikyu |
| **Damage / Shake** | `Left Click` on Mimikyu | Triggers the damage reaction and trembling |
| **Move / Relocate** | `Super + Left Click` (drag) | Hyprland native window dragging |
| **Wake Up** | Move your mouse cursor | Wakes Mimikyu from sleep mode |
| **Specific Monitor** | `mimikyu HDMI-A-1` / `mimikyu laptop` | Launch directly on a target monitor |

---

## 📁 Project Structure

```text
mimikyu-pet/
├── assets/              # App icon (.png) and .desktop menu entry
│   ├── mimikyu.desktop
│   └── mimikyu.png
├── sprites/             # 130 32x32 PNG sprite frames
├── src/
│   └── mimikyu.py       # Main GTK3 desktop pet implementation
├── bin/
│   └── mimikyu          # Portable POSIX sh toggle script
├── hyprland/
│   └── desktop-pet.conf # Ready-to-source Hyprland rules
├── install.sh           # One-command installer / uninstaller
├── requirements.txt     # Python dependencies
├── LICENSE              # MIT License
└── README.md
```

---

## 📜 Credits

- Sprite artwork sourced from the **Pokémon Mystery Dungeon** series and the [PMD SpriteCollab](https://sprites.pmdcollab.org/) community project.
- Pokémon and Mimikyu are trademarks of Nintendo, Game Freak, and The Pokémon Company.

---

## 📄 License

This project is open-source under the [MIT License](LICENSE).
