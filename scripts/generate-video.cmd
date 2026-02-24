@echo off
setlocal

REM Run from repo root
cd /d "%~dp0.."

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0generate-video.ps1"

endlocal
