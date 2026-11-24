from pathlib import Path
from typing import Protocol

from domain.models import Data


class UniversityRepository(Protocol):
    """Контракт чтения и записи данных университета в JSON."""

    def read(self, path: Path) -> dict[str, object]: ...

    def write(self, path: Path, data: Data) -> None: ...
