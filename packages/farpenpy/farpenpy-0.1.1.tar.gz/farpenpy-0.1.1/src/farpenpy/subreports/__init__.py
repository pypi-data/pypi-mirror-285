import abc
from typing import List

from pydantic import BaseModel

from farpenpy.logger import log


class SubReport(abc.ABC):
    def __init__(self) -> None:
        log.info(f"Init ImportParser {self.__class__.__name__}")

    def process(self, page_data: list[str]) -> List[BaseModel]:
        found_data = []

        if self.trigger(page_data):
            log.info(f"{self.__class__.__name__} - triggered")
            found_data = self.handler(page_data)

        return found_data

    @abc.abstractmethod
    def trigger(self, page_data) -> bool: ...

    @abc.abstractmethod
    def handler(self, page_data) -> BaseModel: ...
