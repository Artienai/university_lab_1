import json
from pathlib import Path
from tempfile import TemporaryDirectory

from domain.models import Data, UniversityError


def validate_path(path: Path) -> None:
    """Проверяет, что используется поддерживаемый формат JSON."""
    if path.suffix.lower() != ".json":
        raise UniversityError(
            "Для хранения данных используй файл с расширением .json"
        )


class FileRepository:
    """Реализует чтение и запись данных университета в JSON."""

    def read(self, path: Path) -> dict[str, object]:
        validate_path(path)
        try:
            groups = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise UniversityError(f"Некорректный JSON: {error}") from error

        if not isinstance(groups, dict):
            raise UniversityError("В JSON ожидаются группы записей")
        return groups

    def write(self, path: Path, data: Data) -> None:
        validate_path(path)
        groups = {
            kind: [vars(row) for row in rows.values()]
            for kind, rows in data.items()
        }
        text = json.dumps(groups, ensure_ascii=False, indent=2)

        with TemporaryDirectory(dir=path.parent) as folder:
            temp = Path(folder) / path.name
            temp.write_text(text + "\n", encoding="utf-8", newline="\n")
            temp.replace(path)
