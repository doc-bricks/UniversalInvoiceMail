@echo off
chcp 65001 >nul 2>&1
title UniversalInvoiceMail

echo ========================================
echo   UniversalInvoiceMail v2.3.0
echo ========================================
echo.

REM Prüfe ob Python verfügbar ist
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [FEHLER] Python nicht gefunden!
    echo Bitte Python installieren: https://python.org
    pause
    exit /b 1
)

REM Wechsle ins Script-Verzeichnis
cd /d "%~dp0"

echo Prüfe Abhängigkeiten...

REM Prüfe PySide6
pip show PySide6 >nul 2>&1
if %errorlevel% neq 0 (
    echo Installiere PySide6...
    pip install PySide6
)

REM Prüfe xhtml2pdf
pip show xhtml2pdf >nul 2>&1
if %errorlevel% neq 0 (
    echo Installiere xhtml2pdf...
    pip install xhtml2pdf
)

REM Prüfe keyring
pip show keyring >nul 2>&1
if %errorlevel% neq 0 (
    echo Installiere keyring...
    pip install keyring
)

echo.
echo Starte Anwendung...
echo.

REM Starte die App
python UniversalInvoiceMail.py

if %errorlevel% neq 0 (
    echo.
    echo [FEHLER] Anwendung beendet mit Fehlercode %errorlevel%
    pause
)
