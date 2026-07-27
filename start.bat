@echo off
chcp 65001 >nul 2>&1
title UniversalInvoiceMail

echo ========================================
echo   UniversalInvoiceMail v2.3.0
echo ========================================
echo.

cd /d "%~dp0"

if exist "dist\UniversalInvoiceMail_v2.3.0\UniversalInvoiceMail_v2.3.0.exe" (
    echo Starte EXE...
    start "" "dist\UniversalInvoiceMail_v2.3.0\UniversalInvoiceMail_v2.3.0.exe"
    exit /b 0
)

if exist "releases\v2.3.0\UniversalInvoiceMail_v2.3.0\UniversalInvoiceMail_v2.3.0.exe" (
    echo Starte Release-EXE...
    start "" "releases\v2.3.0\UniversalInvoiceMail_v2.3.0\UniversalInvoiceMail_v2.3.0.exe"
    exit /b 0
)

REM Pruefe ob Python verfuegbar ist
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [FEHLER] Python nicht gefunden!
    echo Bitte Python installieren: https://python.org
    pause
    exit /b 1
)

echo Pruefe Abhaengigkeiten...

REM Pruefe PySide6
pip show PySide6 >nul 2>&1
if %errorlevel% neq 0 (
    echo Installiere PySide6...
    pip install PySide6
)

REM Pruefe xhtml2pdf
pip show xhtml2pdf >nul 2>&1
if %errorlevel% neq 0 (
    echo Installiere xhtml2pdf...
    pip install xhtml2pdf
)

REM Pruefe keyring
pip show keyring >nul 2>&1
if %errorlevel% neq 0 (
    echo Installiere keyring...
    pip install keyring
)

echo.
echo Starte Anwendung...
echo.

python UniversalInvoiceMail.py

if %errorlevel% neq 0 (
    echo.
    echo [FEHLER] Anwendung beendet mit Fehlercode %errorlevel%
    pause
)
