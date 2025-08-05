from app.job.job_base import Job
from app.core.logger import log_event

class CleanupOrderJob(Job):
    name = "cleanup_order"

    def run(self) -> None:
        log_event(self.name, "cleanup_orders", {"message": "Cleaning expired orders..."})


if __name__ == "__main__":
    CleanupOrderJob().run()
