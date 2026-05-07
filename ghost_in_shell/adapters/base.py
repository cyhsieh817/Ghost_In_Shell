"""Base adapter ABC — M3 milestone fills concrete contract."""

from __future__ import annotations

import subprocess
from abc import ABC, abstractmethod


class CLIAdapter(ABC):
    name: str = ""
    cli_binary: str = ""

    @abstractmethod
    def session_start_hook(self) -> str: ...

    @abstractmethod
    def session_end_hook(self) -> str: ...

    @abstractmethod
    def root_instruction_template(self) -> str: ...

    @abstractmethod
    def detect_installation(self) -> bool: ...

    def launch(self, args: list[str]) -> int:
        """Launch the CLI binary with args (§7.3 generic wrapper)."""
        binary = self.cli_binary or self.name
        return subprocess.call([binary, *args])
