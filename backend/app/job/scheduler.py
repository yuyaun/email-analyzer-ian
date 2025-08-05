from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.job.jobs.cleanup_order import CleanupOrderJob
from app.job.jobs.sync_product import SyncProductJob
from app.core.logger import logger


def create_scheduler() -> BackgroundScheduler:
    """Create and configure the background scheduler."""
    scheduler = BackgroundScheduler()

    # Register jobs with their cron schedules. Comment out any job you want to disable.
    scheduler.add_job(
        CleanupOrderJob().run,
        CronTrigger(hour=1, minute=0),
        id="cleanup_order",
        name="cleanup_order",
    )
    scheduler.add_job(
        SyncProductJob().run,
        CronTrigger(minute=0),
        id="sync_product",
        name="sync_product",
    )
    logger.info("Scheduler jobs registered")
    return scheduler


scheduler = create_scheduler()


def start() -> None:
    """Start the background scheduler."""
    scheduler.start()
    logger.info("Scheduler started")


def shutdown() -> None:
    """Shutdown the background scheduler."""
    scheduler.shutdown()
    logger.info("Scheduler shutdown")


if __name__ == "__main__":
    start()
    try:
        # Keep the script running to allow scheduled jobs to execute
        import time

        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        shutdown()
