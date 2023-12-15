# This is a script to install the ESPMega Lightshow program on macOS
# If Homebrew is not installed, install it
if ! command -v brew &> /dev/null; then
    echo "Homebrew is not installed. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew is already installed. Updating Homebrew..."
    brew update
fi

# Install dependencies
echo "Installing dependencies..."
brew install python3@3.11

# Reload environment variables
echo "Reloading environment variables..."
source ~/.bash_profile

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install espmega_lightshow[homeassistant]

# Create program data directory in home directory
echo "Creating program data directory..."
mkdir -p ~/.espmega_lightshow

# Create shortcut to start program
echo "Creating desktop shortcut to start program..."
# Create debug shortcut (with console), use ~/.espmega_lightshow as working directory
echo "cd ~/.espmega_lightshow && python -m espmega_lightshow > ~/Desktop/ESPMega\ Lightshow\ \(Debug\).command"
chmod +x ~/Desktop/ESPMega\ Lightshow\ \(Debug\).command
# Create main shortcut (without console), use ~/.espmega_lightshow as working directory
echo "cd ~/.espmega_lightshow && python -m espmega_lightshow > ~/Desktop/ESPMega\ Lightshow.command"
chmod +x ~/Desktop/ESPMega\ Lightshow.command

