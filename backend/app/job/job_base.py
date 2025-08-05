from abc import ABC, abstractmethod

class Job(ABC):
    name: str = "UnnamedJob"

    @abstractmethod
    def run(self) -> None:
        """Execute the job once."""
        ...