# CrisisLens by Team Arcane - Emergency Response Analytics Platform 

This README contains information about setup, directory and some troubleshooting tips as well. Please follow the commands accurately.

## Video 
Click to be re-directed to the video 

[![Watch the CrisisLens Video](https://img.youtube.com/vi/rXwxeOp-iQY/maxresdefault.jpg)](https://www.youtube.com/watch?v=rXwxeOp-iQY)

**or** follow the link: https://youtube.com/shorts/rXwxeOp-iQY?feature=share

## Software Prerequisites

**Required:**
- Docker Desktop
- Git
- Git LFS (Large File Storage)

### Installing Docker Desktop

1. Download from: https://www.docker.com/products/docker-desktop/
2. Run the installer and follow prompts
3. If prompted to install WSL 2, accept the installation (It is likely that a command prompt will appear, and prompt you to press any key to start WSL 2 installation)
4. After installation, launch Docker Desktop and ensure it's running (check system tray)

### Installing Git

1. Download from: https://git-scm.com/download/win
2. Run installer with default settings
3. Verify: 
```cmd
git --version
```

### Installing Git LFS 

Git LFS now comes installed with Git by default, you can verify installation in cmd by typing: 

```cmd
git lfs version
```

## If LFS is not installed, please follow the steps below.

**Option A:**

```cmd
winget install GitHub.GitLFS
```

**Option B (Manual):**
1. Download from: https://git-lfs.github.com/
2. Run installer
3. Run: 
```cmd
git lfs install
```

**Why Git LFS is needed:** Database files (~169 MB) require LFS to download properly. Without it, files will only be a few KB.

## Running the Application

### First-Time Setup (10-15 minutes)

1. Clone the repository:

```cmd
cd Desktop (or any place of your choice)
git clone https://github.com/Syed-rzv/CrisisLens-Submission.git
cd CrisisLens-Submission
```

Git LFS will automatically download database files (~169 MB).

2. Verify database files downloaded:

```cmd
cd database
dir
```

Check that `06_emergency_data.sql` is around 160 MB (not a few KB).

If files are small, run: 
```cmd
git lfs pull
```

3. Start the application:

```cmd
cd ..
docker compose --env-file .env.docker up
```

First time: Docker downloads images and imports data (~5-10 minutes).

Wait for these messages at the end after all containers are set up:

```
crisislens-backend   |  * Running on all addresses (0.0.0.0)
crisislens-backend   |  * Running on http://127.0.0.1:5000
crisislens-backend   |  * Running on http://172.18.0.6:5000
crisislens-backend   | Press CTRL+C to quit
```

4. Access the system:
- Open browser: http://localhost:3000
- Username: `admin`
- Password: `admin123`

### Stopping the Application

To stop: Press `Ctrl + C` (twice if needed) or run:
```cmd
docker compose --env-file .env.docker down
```


**Key Folders:**
- **frontend/src/** - React components and pages for the dashboard
- **crisislens-API/** - Main backend folder with flask API script, forecasting, etc.
- **database/** - SQL scripts for database initialization and sample data
- **Classifier/** - Machine learning Classifier module

## Troubleshooting

**Docker not running:**
- Open Docker Desktop from Start Menu
- Wait for whale icon to show "Docker Desktop is running"

**WSL 2 installation incomplete:**

```cmd
wsl --update
```

Then restart your computer and try again.

**Database files are tiny (~100 bytes):**

```cmd
git lfs install
git lfs pull
docker compose --env-file .env.docker down
docker compose --env-file .env.docker up
```

**"Table 'capstone.users' doesn't exist":**

```cmd
docker compose --env-file .env.docker down
docker volume rm crisislens-submission_mysql_data
docker compose --env-file .env.docker up
```

**Port 3306 or 5000 already in use:**
Stop any local MySQL services, or modify port mappings in `docker-compose.yml`.

## Expected Timings

**First-Time Setup:**
- Docker image download: 5-7 minutes
- Database import: 5-10 minutes
- Total: ~15 minutes

**Subsequent Startups:**
- All services: ~30 seconds
- Dashboard ready: ~1 minute

**System Usage:**
- Login: Instant
- Dashboard load: 2-3 seconds
- ML classification: <1 second
- Forecasting page: 1-2 seconds
- Anomaly detection: 1-2 seconds

## Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`

For the best experience, use Chrome or Edge browser.
