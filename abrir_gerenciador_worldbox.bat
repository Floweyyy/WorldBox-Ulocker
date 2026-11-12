@echo off
chcp 65001 >nul
setlocal
title WorldBox - Gerenciador de Conquistas, Steam e Itens Ocultos
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
    python "%~dp0worldbox_achievements_manager.py" %*
    goto :done
)

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "%~dp0worldbox_achievements_manager.py" %*
    goto :done
)

echo [ERRO] Python nao encontrado no PATH do sistema.
pause
exit /b 1

:done
if errorlevel 1 (
    echo.
    echo [ERRO] O script encerrou com erro.
    pause
)
endlocal
