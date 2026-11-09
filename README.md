# 👻 Mimikyu Desktop Pet

An autonomous, interactive Pokémon desktop companion for Linux (Hyprland, Wayland & X11), written in Python with GTK 3.

Inspired by Pokémon Mystery Dungeon sprites, Mimikyu roams your screens, dashes around, reacts to clicks, and sleeps when you are away.

---

## ✨ Features

- **🐾 Autonomous Movement:** Walks and dashes naturally in 8 directions at a smooth 40 FPS.
- **⚡ Interactive Reactions:** Click on Mimikyu to make it flinch and shake in pain with directional tremors.
- **🖱️ Native Window Dragging:** Move Mimikyu anywhere using your window manager's native drag shortcut (`Super + Left Click`) without fighting the autonomous movement.
- **🖥️ Multi-Monitor Aware:** Automatically spawns on your currently focused monitor (via Hyprland IPC) or under your cursor, and roams across screen boundaries smoothly.
- **💤 Idle Sleep Mode:** Automatically curls up and goes to sleep after 5 minutes of cursor inactivity, and wakes up immediately when you move the mouse.
- **📐 Compact & Snug Canvas:** Sprites are cleanly cropped to a 32×32 pixel grid (80×80 px at 2.5× desktop scale), tightly wrapping the character without dead transparent space.
- **🚀 One-command Toggle:** Single command `mimikyu` toggles the pet on/off.

---

## 📦 Requirements

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

## 🛠️ Installation

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

3. Ensure `~/.local/bin` is in your `$PATH`.

---

## 🪟 Hyprland Configuration

To ensure Mimikyu floats borderless, ignores window wobbles/animations, and allows mouse interaction, add the following window rules to your Hyprland configuration.

### Standard `hyprland.conf`:
```ini
windowrule = float, title:^(desktop-pet)$
windowrule = pin, title:^(desktop-pet)$
windowrule = noblur, title:^(desktop-pet)$
windowrule = noborder, title:^(desktop-pet)$
windowrule = noshadow, title:^(desktop-pet)$
windowrule = noanim, title:^(desktop-pet)$
windowrule = noinitialfocus, title:^(desktop-pet)$
```

### Hyprland 0.57+ Lua (`hyprland.lua` / `hypr-user.lua`):
```lua
hl.window_rule({
    name             = "desktop-pet",
    match            = { title = "desktop-pet" },
    float            = true,
    no_blur          = true,
    pin              = true,
    border_size      = 0,
    no_shadow        = true,
    no_glow          = true,
    no_anim          = true,
    no_wobble        = true,
    no_initial_focus = true,
})
```

### Recommended Keybinding:
Add this to toggle Mimikyu with a shortcut (e.g., `Super + P`):
```ini
bind = $mainMod, P, exec, mimikyu
```

---

## 🎮 Controls

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
