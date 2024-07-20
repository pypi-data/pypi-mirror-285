from abc import ABC, abstractmethod

from pydantic import BaseModel


class MetricBase(ABC, BaseModel):
    name: str = "accuracy"
    input_type: str = "int"
    output_type: str = None
    kwargs: dict = None

    @abstractmethod
    def parse_data(self):
        pass

    @abstractmethod
    def compute(self):
        pass

    # TODO: Add function to compute to automatically call the Accuracy()
