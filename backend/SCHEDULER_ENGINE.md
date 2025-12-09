# Scheduler Engine Service

## Overview

The Scheduler Engine is a standalone microservice responsible for running scheduled batch jobs independently from the FastAPI backend. This separation ensures that:

- Backend service failures don't affect scheduled data collection
- Scheduled jobs don't impact API performance
- Each service can be scaled independently
- Better resource management and monitoring

## Architecture

```
┌─────────────────┐     ┌──────────────────┐
│                 │     │                  │
│  FastAPI        │     │  Scheduler       │
│  Backend        │     │  Engine          │
│  (API Service)  │     │  (Batch Jobs)    │
│                 │     │                  │
└────────┬────────┘     └────────┬─────────┘
         │                       │
         │                       │
         └───────────┬───────────┘
                     │
              ┌──────▼──────┐
              │             │
              │  PostgreSQL │
              │  Database   │
              │             │
              └─────────────┘
```

## Scheduled Jobs

The Scheduler Engine manages the following jobs:

1. **Symbol Collection** (Daily at 00:00)
   - Collects trading symbols from Upbit and KIS exchanges
   - Updates the symbols table with latest available symbols

2. **Price Data Collection** (Daily at 00:02)
   - Collects historical OHLCV (Open, High, Low, Close, Volume) data
   - Runs for all exchanges (Upbit and KIS)

## Running the Services

### Option 1: Docker Compose (Recommended)

Start all services including the scheduler engine:

```bash
# Start all services
docker-compose up -d

# View scheduler engine logs
docker-compose logs -f scheduler-engine

# Stop all services
docker-compose down
```

The scheduler engine will automatically start with the backend and run independently.

### Option 2: Local Development

#### Start Backend API

```bash
cd backend
source .venv/bin/activate  # or use uv venv activate

# Run backend API
fastapi dev app/main.py
```

#### Start Scheduler Engine (Separate Terminal)

```bash
cd backend
source .venv/bin/activate  # or use uv venv activate

# Run scheduler engine
python -m app.scheduler_engine
```

### Option 3: Systemd Service (Production)

#### Installation

1. Copy the service file:

```bash
sudo cp backend/deployment/scheduler-engine.service /etc/systemd/system/
```

2. Create log directory:

```bash
sudo mkdir -p /var/log/wombat
sudo chown www-data:www-data /var/log/wombat
```

3. Update the service file paths if your installation directory is different from `/opt/wombat/backend`

4. Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable scheduler-engine

# Start the service
sudo systemctl start scheduler-engine

# Check status
sudo systemctl status scheduler-engine
```

#### Management

```bash
# View logs
sudo journalctl -u scheduler-engine -f

# Restart service
sudo systemctl restart scheduler-engine

# Stop service
sudo systemctl stop scheduler-engine

# Disable service
sudo systemctl disable scheduler-engine
```

## Configuration

The Scheduler Engine uses the same environment variables as the backend:

- `POSTGRES_SERVER`: Database host
- `POSTGRES_PORT`: Database port
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `TZ`: Timezone for scheduling (e.g., "Asia/Seoul")
- `SENTRY_DSN`: (Optional) Sentry DSN for error tracking

## Manual Job Execution

You can manually run collection scripts without waiting for the scheduler:

### Collect Symbols

```bash
cd backend
python scripts/collect_symbols.py
```

### Collect Price Data

```bash
cd backend

# Collect from all exchanges (default: 1 day back)
python scripts/collect_price_data.py --exchange all

# Collect from specific exchange
python scripts/collect_price_data.py --exchange upbit --days-back 7

# Collect with custom options
python scripts/collect_price_data.py --exchange kis --market KOSPI --days-back 30
```

## Monitoring

### Health Check

The scheduler engine logs its status and job executions. Monitor it using:

**Docker:**
```bash
docker-compose logs -f scheduler-engine
```

**Systemd:**
```bash
sudo journalctl -u scheduler-engine -f
```

**Local:**
Check console output where the scheduler engine is running.

### Expected Log Output

```
============================================================
Starting Scheduler Engine Service
Timezone: Asia/Seoul
Current time: 2025-12-08 22:00:00
============================================================
Scheduled job: Collect symbols at 00:00 daily
Scheduled job: Collect price data at 00:02 daily
Scheduler engine started successfully
Scheduled jobs:
  - Collect Symbols from Exchanges (ID: collect_symbols): cron[hour='0', minute='0']
  - Collect Price Data from Exchanges (ID: collect_price_data): cron[hour='0', minute='2']
```

## Troubleshooting

### Scheduler Engine Won't Start

1. Check database connectivity:
   ```bash
   psql -h localhost -U your_user -d your_db
   ```

2. Verify environment variables are set correctly

3. Check logs for specific error messages

### Jobs Not Running

1. Verify timezone settings match your requirements
2. Check system time is correct
3. Review logs for job execution errors

### Database Connection Issues

1. Ensure PostgreSQL is running
2. Verify database credentials in `.env` file
3. Check network connectivity between scheduler and database

## Development

### Modifying Schedule

To change job schedules, edit [app/scheduler_engine.py](app/scheduler_engine.py):

```python
def setup_jobs(self):
    # Change schedule here
    self.scheduler.add_job(
        self.run_collect_symbols,
        "cron",
        hour=0,      # Hour (0-23)
        minute=0,    # Minute (0-59)
        id="collect_symbols",
        name="Collect Symbols from Exchanges",
        replace_existing=True,
    )
```

### Adding New Jobs

1. Create a new script in `backend/scripts/`
2. Add job method in `SchedulerEngine` class
3. Register job in `setup_jobs()` method

Example:

```python
async def run_new_job(self):
    """Executes a new batch job."""
    try:
        logger.info("Starting new job...")
        # Your job logic here
        logger.info("New job completed successfully")
    except Exception:
        logger.error("New job failed", exc_info=True)

def setup_jobs(self):
    # ... existing jobs ...

    self.scheduler.add_job(
        self.run_new_job,
        "cron",
        hour=12,
        minute=0,
        id="new_job",
        name="New Batch Job",
    )
```

## Migration Notes

### Before (Monolithic)

- Scheduler ran within FastAPI lifespan
- Backend crash = scheduler crash
- Shared resources and potential performance impact

### After (Microservices)

- Scheduler runs as independent service
- Backend and scheduler can fail independently
- Better resource isolation
- Easier monitoring and scaling

### Breaking Changes

If you were relying on the scheduler running within FastAPI, you need to:

1. Start the scheduler engine separately (see "Running the Services")
2. Update deployment scripts/configurations
3. Update monitoring/logging configurations

## See Also

- [Backend README](README.md)
- [Collector Documentation](app/engine/collectors/)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
