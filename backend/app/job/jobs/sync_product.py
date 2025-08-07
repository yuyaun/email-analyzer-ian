"""排程工作：同步產品資訊。"""

from app.job.job_base import Job
from app.core.logger import log_event

class SyncProductJob(Job):
    """示範用的產品同步工作。"""

    name = "sync_product"

    def run(self) -> None:
        log_event(self.name, "sync_product", {"message": "Syncing product info..."})


if __name__ == "__main__":
    SyncProductJob().run()
