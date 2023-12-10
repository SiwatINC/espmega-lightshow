# Request administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) { Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs; exit }

# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Refresh env variables
$env:ChocolateyInstall = Convert-Path "$((Get-Command choco).Path)\..\.."   
Import-Module "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1"
refreshenv

# Install Python3 and espmega_lightshow
choco install -y python3
pip3 install --upgrade espmega_lightshow

# Get python.exe path
$pythonPath = (Get-Command pythonw).Source

# Create espmega_lightshow folder in user's home directory
$espmegaLightshowPath = "$env:USERPROFILE\espmega_lightshow"
if (-not (Test-Path $espmegaLightshowPath)) {
    New-Item -ItemType Directory -Force -Path $espmegaLightshowPath
}

# Create desktop shortcut
$targetFile = "$env:USERPROFILE\Desktop\ESPMega Lightshow.lnk"
$wshshell = New-Object -ComObject WScript.Shell
$shortcut = $wshshell.CreateShortcut($targetFile)
$shortcut.TargetPath = $pythonPath
$shortcut.Arguments = "-m espmega_lightshow"
# Set the working directory to the espmega_lightshow folder in the user's home directory
$shortcut.WorkingDirectory = $espmegaLightshowPath
# Get Python base path
$pythonRootPath = (Get-Command python).Source | Split-Path -Parent
# Set the icon to icon.ico in the same directory as this python script
$shortcut.IconLocation = $pythonRootPath + "\lib\site-packages\espmega_lightshow\icon.ico"
$shortcut.Save()

# Create start menu shortcut
$targetFile = "$env:USERPROFILE\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\ESPMega Lightshow.lnk"
$wshshell = New-Object -ComObject WScript.Shell
$shortcut = $wshshell.CreateShortcut($targetFile)
$shortcut.TargetPath = $pythonPath
$shortcut.Arguments = "-m espmega_lightshow"
# Set the working directory to the espmega_lightshow folder in the user's home directory
$shortcut.WorkingDirectory = $espmegaLightshowPath
# Set the icon to icon.ico in the same directory as this python script
$shortcut.IconLocation = $pythonRootPath + "\lib\site-packages\espmega_lightshow\icon.ico"
$shortcut.Save()

# Get python.exe path
$pythonDbgPath = (Get-Command python).Source

# Create start menu shortcut to launch the program in debug mode, debug mode runs on python.exe instead of pythonw.exe
$targetFile = "$env:USERPROFILE\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\ESPMega Lightshow (Debug).lnk"
$wshshell = New-Object -ComObject WScript.Shell
$shortcut = $wshshell.CreateShortcut($targetFile)
$shortcut.TargetPath = $pythonDbgPath
$shortcut.Arguments = "-m espmega_lightshow"
# Set the working directory to the espmega_lightshow folder in the user's home directory
$shortcut.WorkingDirectory = $espmegaLightshowPath
# Set the icon to icon.ico in the same directory as this python script
$shortcut.IconLocation = $pythonRootPath + "\lib\site-packages\espmega_lightshow\icon.ico"
$shortcut.Save()
