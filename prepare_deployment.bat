@echo off
echo ========================================
echo RAG Study Bot - Deployment Preparation
echo ========================================
echo.

echo Step 1: Backing up local files...
if exist app.py (
    copy app.py app_local_backup.py
    echo ✓ Backed up app.py to app_local_backup.py
)

echo.
echo Step 2: Switching to cloud-ready version...
if exist app_cloud.py (
    copy app_cloud.py app.py
    echo ✓ Copied app_cloud.py to app.py
)

if exist requirements_cloud.txt (
    copy requirements_cloud.txt requirements.txt
    echo ✓ Copied requirements_cloud.txt to requirements.txt
)

echo.
echo Step 3: Checking Git status...
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Git is installed
    git status
) else (
    echo ✗ Git is not installed. Please install Git first.
    echo Download from: https://git-scm.com/download/win
)

echo.
echo ========================================
echo Preparation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Get Groq API key from https://console.groq.com
echo 2. Initialize git: git init
echo 3. Add files: git add .
echo 4. Commit: git commit -m "Initial commit"
echo 5. Create GitHub repo and push
echo 6. Deploy on Streamlit Cloud
echo.
echo See DEPLOYMENT_GUIDE.md for detailed instructions
echo.
pause
