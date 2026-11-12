@echo off
title Enviando para o GitHub...
echo ==============================================
echo   Enviando WorldBox Unlocker para o GitHub
echo ==============================================
echo.
"%LOCALAPPDATA%\Programs\PortableGit\cmd\git.exe" push -u origin main
echo.
echo ==============================================
echo   Concluido! Pressione qualquer tecla para sair.
echo ==============================================
pause
