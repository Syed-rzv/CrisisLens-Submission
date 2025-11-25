# CrisisLens by Team Arcane- Emergency Response Analytics Platform 

This READ ME contains information about setup, directory and some troubleshooting tips as well.

Software Prerequisites

**Required:**
- Docker Desktop
- Git
- Git LFS (Large File Storage)

### Installing Docker Desktop

1. Download from: https://www.docker.com/products/docker-desktop/
2. Run the installer and follow prompts
3. If prompted to install WSL 2, accept the installation
4. After installation, launch Docker Desktop and ensure it's running (check system tray)

### Installing Git

1. Download from: https://git-scm.com/download/win
2. Run installer with default settings
3. Verify: `git --version`

### Installing Git LFS

**Option A (Recommended):**
in cmd: 
winget install GitHub.GitLFS


**Option B (Manual):**
1. Download from: https://git-lfs.github.com/
2. Run installer
3. Run: `git lfs install`

**Why Git LFS is needed:** Database files (169 MB) require LFS to download properly. Without it, files will only be a few KB.

## Running the Application

### First-Time Setup (10-15 minutes)

1. Clone the repository:

in cmd:

cd Desktop (or any location of your choice)
git clone https://github.com/Syed-rzv/CrisisLens-Submission.git
cd CrisisLens-Submission


Git LFS will automatically download database files (~169 MB).

2. Verify database files downloaded:

in cmd:
cd database
dir


Check that `06_emergency_data.sql` is ~337 MB (not a few KB).

If files are small, run: `git lfs pull`

3. Start the application:

cd ..
docker compose --env-file .env.docker up

First time: Docker downloads images (~2 GB) and imports data (~5-10 minutes).

Wait for these messages:

crisislens-mysql    | ready for connections
crisislens-backend  | Running on http://0.0.0.0:5000
crisislens-frontend | Local: http://localhost:5173


4. Access the system:
- Open browser: http://localhost:3000
- Username: `admin`
- Password: `admin123`



To stop: Press `Ctrl + C` (twice if needed) or run `docker compose --env-file .env.docker down`

## Project Structure

```
CrisisLens-Submission/
├── frontend/                 # React + Vite + Tailwind CSS
│   ├── src/
│   │   ├── components/      # Dashboard, charts, UI components
│   │   ├── pages/           # Temporal analysis, forecasting, anomalies, login
│   │   ├── context/         # Filters and Authentication context
│   │   ├── hooks/           # Data fetching and processing
│   │   └── utils/           # Helper functions and data transformation
│   └── Dockerfile
│
├── crisislens-API/          # Flask Backend API
│   ├── app.py              # Main Flask application and routes
│   ├── auth.py             # Authentication and JWT tokens
│   ├── routes/             # API endpoints (data, forecasting, anomalies, uploads)
│   ├── Classifier/         # ML models (XGBoost, SARIMA, Isolation Forest)
│   ├── worker.py           # Redis background job processing
│   └── Dockerfile
│
├── database/                # Database initialization scripts
│   ├── 02_users.sql        # Admin and analyst user accounts
│   ├── 03_anomaly_events.sql
│   ├── 04_forecasted_calls.sql
│   ├── 05_enriched_calls.sql
│   └── 06_emergency_data.sql  # 663K+ emergency call records
│
├── docker-compose.yml       # Docker service orchestration
├── .env.docker             # Environment variables and database credentials
└── README.md               # This file
```

**Key Folders:**
- **frontend/src/** - React components and pages for the dashboard
- **crisislens-API/** - Main backend folder with flask API script, forecasting, etc.
- **database/** - SQL scripts for database initialization and sample data
- **Classifier/** - Machine learning Classifier

## Troubleshooting

**Docker not running:**
- Open Docker Desktop from Start Menu
- Wait for whale icon to show "Docker Desktop is running"

**WSL 2 installation incomplete:**
in cmd:
wsl --update

Then restart your computer and try again.

**Database files are tiny (~100 bytes):**
in cmd:
git lfs install
git lfs pull
docker compose --env-file .env.docker down
docker compose --env-file .env.docker up


**"Table 'capstone.users' doesn't exist":**
in cmd:
docker compose --env-file .env.docker down
docker volume rm crisislens-submission_mysql_data
docker compose --env-file .env.docker up


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