"""排程工作基底類別。"""

from abc import ABC, abstractmethod

class Job(ABC):
    """所有排程工作的抽象基底。"""

    name: str = "UnnamedJob"

    @abstractmethod
    def run(self) -> None:
        """Execute the job once."""
        ...