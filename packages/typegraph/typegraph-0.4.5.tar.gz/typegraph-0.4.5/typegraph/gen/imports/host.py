from ..types import Result
from abc import abstractmethod
from typing import List, Protocol

class HostHost(Protocol):
    @abstractmethod
    def print(self, s: str) -> None:
        raise NotImplementedError
    @abstractmethod
    def expand_path(self, root: str, exclude: List[str]) -> Result[List[str], str]:
        raise NotImplementedError
    @abstractmethod
    def path_exists(self, path: str) -> Result[bool, str]:
        raise NotImplementedError
    @abstractmethod
    def read_file(self, path: str) -> Result[bytes, str]:
        raise NotImplementedError
    @abstractmethod
    def write_file(self, path: str, data: bytes) -> Result[None, str]:
        raise NotImplementedError

