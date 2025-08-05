from app.job.job_base import Job
from app.core.logger import log_event

class SyncProductJob(Job):
    name = "sync_product"

    def run(self) -> None:
        log_event(self.name, "sync_product", {"message": "Syncing product info..."})


if __name__ == "__main__":
    SyncProductJob().run()
