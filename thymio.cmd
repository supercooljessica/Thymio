@echo off
rem Windows launcher for tools\thymio.py. Sets up .venv on first run.
rem Usage: thymio list   (in PowerShell: .\thymio list)
setlocal
set "ROOT=%~dp0"
set "PY=%ROOT%.venv\Scripts\python.exe"

"%PY%" -c "import tdmclient" 2>nul || (
    echo Setting up the Python environment in .venv - first run only...
    py -3 -m venv "%ROOT%.venv" 2>nul || python -m venv "%ROOT%.venv"
    if not exist "%PY%" (
        echo Python 3 was not found. Install it from https://www.python.org/downloads/
        echo and tick "Add python.exe to PATH" in the installer, then try again.
        exit /b 1
    )
    "%PY%" -m pip install --quiet --disable-pip-version-check -r "%ROOT%requirements.txt" || exit /b 1
)

"%PY%" "%ROOT%tools\thymio.py" %*
