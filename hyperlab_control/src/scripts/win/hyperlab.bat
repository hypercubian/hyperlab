@echo off
setlocal

:: Define the paths
set "PYTHON_EXE=C:\Users\Hypercubian\Development\Hyperlab\hyperlab_control\.venv\Scripts\python.exe"
set "FABFILE=C:\Users\Hypercubian\Development\Hyperlab\hyperlab_control\fabfile.py"
set "PROJECT_DIR=C:\Users\Hypercubian\Development\Hyperlab\hyperlab_control"

:: Check if Python exists
if not exist "%PYTHON_EXE%" (
    echo Python virtual environment not found at %PYTHON_EXE%.
    exit /b 1
)

:: Change to the project directory
pushd "%PROJECT_DIR%"

:: Run Fabric explicitly with the fabfile
"%PYTHON_EXE%" -m fabric --collection=fabfile %*

:: Restore the original directory
popd
