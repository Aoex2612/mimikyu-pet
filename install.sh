#!/bin/sh
set -e

# Installation script for Mimikyu Desktop Pet

REPO_DIR=$(cd "$(dirname "$0")" && pwd)
INSTALL_DIR="$HOME/.local/share/mimikyu"
BIN_TARGET="$HOME/.local/bin/mimikyu"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/128x128/apps"
PIXMAPS_DIR="$HOME/.local/share/pixmaps"

if [ "$1" = "--uninstall" ] || [ "$1" = "-u" ]; then
    echo "Uninstalling Mimikyu..."
    rm -rf "$INSTALL_DIR"
    rm -f "$BIN_TARGET"
    rm -f "$DESKTOP_DIR/mimikyu.desktop"
    rm -f "$ICON_DIR/mimikyu.png"
    rm -f "$PIXMAPS_DIR/mimikyu.png"
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi
    echo "Mimikyu has been completely uninstalled."
    exit 0
fi

echo "=== Installing Mimikyu Desktop Pet ==="

# Check Python and GTK3
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is required but not installed." >&2
    exit 1
fi

python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk" 2>/dev/null || {
    echo "Warning: PyGObject / GTK3 bindings not detected."
    echo "Please install them via your distribution package manager, e.g.:"
    echo "  Arch/Manjaro:  sudo pacman -S python-gobject gtk3"
    echo "  Debian/Ubuntu: sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0"
    echo "  Fedora:        sudo dnf install python3-gobject gtk3"
}

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$HOME/.local/bin"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$ICON_DIR"
mkdir -p "$PIXMAPS_DIR"

# Copy files
echo "Copying sprites and source..."
cp -r "$REPO_DIR/sprites" "$INSTALL_DIR/"
cp -r "$REPO_DIR/src" "$INSTALL_DIR/"

# Create launcher symlink
echo "Creating launcher in ~/.local/bin/mimikyu..."
ln -sf "$REPO_DIR/bin/mimikyu" "$BIN_TARGET"
chmod +x "$BIN_TARGET"

# Install Desktop entry & icons
echo "Installing application menu entry (.desktop) and icon..."
cp "$REPO_DIR/assets/mimikyu.desktop" "$DESKTOP_DIR/"
cp "$REPO_DIR/assets/mimikyu.png" "$ICON_DIR/mimikyu.png"
cp "$REPO_DIR/assets/mimikyu.png" "$PIXMAPS_DIR/mimikyu.png"

# Update desktop and icon caches if available
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
fi

echo ""
echo "Installation complete!"
echo "• Launch via terminal: mimikyu"
echo "• Launch via App Menu: Search for 'Mimikyu' in GNOME, KDE, Rofi, etc."
echo "Make sure ~/.local/bin is in your PATH."
