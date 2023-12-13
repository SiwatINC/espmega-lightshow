rmdir dist /s /q
python ./setup.py sdist
# Get filename of the tar.gz file
for /f "delims=" %%a in ('dir /b dist\*.tar.gz') do set filename=%%a
pip3 install dist/%filename%