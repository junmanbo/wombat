import subprocess
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings

# Get the project root directory (assuming this file is in backend/app/core)
# You might need to adjust this based on your actual project structure
# and where you run the application from.
PROJECT_ROOT = Path(__file__).parent.parent.parent


def run_collect_symbols():
    """Executes the collect_symbols.py script."""
    script_path = PROJECT_ROOT / "scripts" / "collect_symbols.py"
    print(f"Executing script: {script_path}")
    subprocess.run(["python", str(script_path)], check=True)
    print("Finished executing collect_symbols.py")


def run_collect_price_data():
    """Executes the collect_price_data.py script."""
    script_path = PROJECT_ROOT / "scripts" / "collect_price_data.py"
    print(f"Executing script: {script_path}")
    subprocess.run(["python", str(script_path)], check=True)
    print("Finished executing collect_price_data.py")


scheduler = AsyncIOScheduler(timezone=str(settings.TZ))

# Add jobs to the scheduler
# Runs every day at midnight
scheduler.add_job(run_collect_symbols, "cron", hour=0, minute=0)
scheduler.add_job(run_collect_price_data, "cron", hour=0, minute=2)
