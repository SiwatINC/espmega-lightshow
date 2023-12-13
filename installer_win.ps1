# Request administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) { Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs; exit }

# Ask if the user wants to install home assistant api module
# Doing so will require python version 3.11.2
$installHomeAssistantApi = $false
$pythonInstalled = $false
while ($true) {
    $installHomeAssistantApi = Read-Host "Do you want to install the home assistant api module? (y/n)"
    if ($installHomeAssistantApi -eq "y" -or $installHomeAssistantApi -eq "n") {
        break
    }
}

# Check if python is installed
try {
    $pythonVersion = (Get-Command python).Version
    $pythonInstalled = $true
}
catch {
    $pythonInstalled = $false
}

# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Refresh env variables
$env:ChocolateyInstall = Convert-Path "$((Get-Command choco).Path)\..\.."   
Import-Module "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1"
refreshenv

# Check if python version is 3.11.2150.1013
if ($pythonInstalled) {
    if ($pythonVersion -ne "3.11.2150.1013") {
        Write-Output "Python version is not 3.11.2150.1013, installing python 3.11.2150.1013"
        # If home assistant api module is to be installed, install python 3.11.2150.1013
        if ($installHomeAssistantApi) {
            # Install python 3.11.2150.1013
            choco install -y python --version 3.11.2
        }
    }
}
else {
    choco install -y python --version 3.11.2
}
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

