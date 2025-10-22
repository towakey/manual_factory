@echo off
chcp 65001 >nul
cls
echo ===============================================================
echo    Manual Factory - Portable Web Server
echo    Python Standard Library Only
echo ===============================================================
echo.
echo Starting server...
echo.
echo Access URL: http://localhost:8000/
echo.
echo Login:
echo   Email: admin@example.com
echo   Password: admin123
echo.
echo Press Ctrl+C to stop the server
echo ===============================================================
echo.

python server_wsgi.py 8000

pause
