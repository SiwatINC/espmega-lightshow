#!/bin/bash

# Install Python3 and espmega_lightshow
sudo apt-get install -y python3 python3-pip
pip3 install --upgrade espmega_lightshow

# Get python3 path
pythonPath=$(which python3)

# Get site-packages path
pythonRootPath=$(python3 -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")

# Create esp_mega_lightshow folder in the user's home directory if it doesn't exist
mkdir -p "$HOME/.espmega_lightshow"

# Create start menu shortcut
targetFile="$HOME/.local/share/applications/ESPMega Lightshow.desktop"
echo "[Desktop Entry]
Version=1.0
Type=Application
Name=ESPMega Lightshow
Exec=$pythonPath -m espmega_lightshow
Icon=$pythonRootPath/espmega_lightshow/icon.ico
Path=$HOME/.espmega_lightshow
Terminal=false" > "$targetFile"

# Add alias to .bashrc
echo "alias espmega_lightshow='$pythonPath -m espmega_lightshow'" >> "$HOME/.bashrc"