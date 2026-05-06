"""Base adapter ABC — M3 milestone fills concrete contract."""

from abc import ABC, abstractmethod


class CLIAdapter(ABC):
    name: str = ""

    @abstractmethod
    def session_start_hook(self) -> str: ...

    @abstractmethod
    def session_end_hook(self) -> str: ...

    @abstractmethod
    def root_instruction_template(self) -> str: ...

    @abstractmethod
    def detect_installation(self) -> bool: ...
