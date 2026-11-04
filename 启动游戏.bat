@echo off
chcp 936 >nul
setlocal enabledelayedexpansion
title 森林冰火人 H5 - 本地服务器
cd /d "%~dp0"

set "PORT=8123"
set "PY="
where python  >nul 2>nul && set "PY=python"
if not defined PY (where py      >nul 2>nul && set "PY=py")
if not defined PY (where python3 >nul 2>nul && set "PY=python3")

if not defined PY (
  echo.
  echo  [错误] 没有检测到 Python。
  echo  请先安装 Python 3 ^(https://www.python.org/downloads/^)，
  echo  安装时勾选 "Add Python to PATH"，然后重新双击本文件。
  echo.
  pause
  exit /b 1
)

:findport
%PY% -c "import socket,sys;s=socket.socket();r=s.connect_ex(('127.0.0.1',!PORT!));s.close();sys.exit(0 if r else 1)" >nul 2>nul
if errorlevel 1 (
  set /a PORT+=1
  if !PORT! GTR 8199 (
    echo.
    echo  [错误] 8123-8199 端口都被占用了，请先关闭其它本地服务。
    echo.
    pause
    exit /b 1
  )
  goto findport
)

set "URL=http://127.0.0.1:!PORT!/"

echo.
echo  ============================================
echo    森林冰火人 H5  ·  本地离线大厅
echo  ============================================
echo.
echo    访问地址 : !URL!
echo    游戏目录 : %~dp0games
echo    存档文件 : %~dp0saves\progress.json
echo.
echo    提示：浏览器会自动打开。
echo          关闭本窗口即停止本地服务器。
echo.
echo  ============================================
echo.

rem 后台起本地服务（静态文件 + 存档同步接口，同一控制台，关窗即停）
start /b "" %PY% "tools\serve.py" !PORT!
%PY% -c "import time;time.sleep(2)"

rem 打开默认浏览器
start "" "!URL!"

echo.
echo  服务运行中，按任意键停止 ...
pause >nul
