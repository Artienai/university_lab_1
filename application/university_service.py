from pathlib import Path

from domain.models import Data, Record, TYPES, UniversityError
from domain.repository import UniversityRepository


def make_record(data: Data, kind: str, values: dict[str, object]) -> Record:
    """Создаёт объект и проверяет его поля и связи."""
    if kind not in TYPES:
        raise UniversityError("Неизвестный тип записи")
    if not isinstance(values, dict):
        raise UniversityError("Запись должна быть представлена объектом")

    constructor, columns = TYPES[kind]
    parsed: dict[str, str | int] = {}
    for field in ("id", *columns):
        if field not in values:
            raise UniversityError(f"Отсутствует поле {field}")
        value = values[field]
        if field in ("id", "student_id", "course_id", "hours", "grade"):
            try:
                value = int(str(value))
            except (ValueError, TypeError) as error:
                message = f"Поле {field} должно быть целым числом"
                raise UniversityError(message) from error
            if field == "grade":
                if value not in (2, 3, 4, 5):
                    raise UniversityError("Оценка должна быть от 2 до 5")
            elif value < 1:
                raise UniversityError(f"Поле {field} должно быть положительным")
        elif not isinstance(value, str) or not value.strip():
            raise UniversityError(f"Поле {field} не должно быть пустым")
        else:
            value = value.strip()
        parsed[field] = value

    for field, group in (("student_id", "students"), ("course_id", "courses")):
        if field in parsed and int(parsed[field]) not in data[group]:
            raise UniversityError(f"Не найдена связанная запись {field}")
    return constructor(**parsed)


class UniversityService:
    """Содержит CRUD-операции предметной области."""

    def __init__(self, repository: UniversityRepository):
        self.repository = repository
        self.data: Data = {kind: {} for kind in TYPES}

    def list_records(self, kind: str) -> list[Record]:
        if kind not in TYPES:
            raise UniversityError("Неизвестный тип записи")
        return list(self.data[kind].values())

    def get_record(self, kind: str, item_id: int) -> Record:
        if kind not in TYPES:
            raise UniversityError("Неизвестный тип записи")
        rows = self.data[kind]
        if item_id not in rows:
            raise UniversityError(f"Запись с ID {item_id} не найдена")
        return rows[item_id]

    def write_record(
        self, kind: str, values: dict[str, object], item_id: int | None = None
    ) -> Record:
        if kind not in TYPES:
            raise UniversityError("Неизвестный тип записи")
        rows = self.data[kind]
        if item_id is None:
            item_id = max(rows, default=0) + 1
        else:
            self.get_record(kind, item_id)
        item = make_record(self.data, kind, {**values, "id": item_id})
        rows[item_id] = item
        return item

    def delete_record(self, kind: str, item_id: int) -> None:
        self.get_record(kind, item_id)
        field = {"students": "student_id", "courses": "course_id"}.get(kind)
        if field and any(
            getattr(item, field) == item_id
            for item in self.data["enrollments"].values()
        ):
            raise UniversityError("Нельзя удалить запись, на которую есть ссылки")
        del self.data[kind][item_id]

    def load(self, path: Path) -> None:
        """Проверяет новый набор данных до замены."""
        groups = self.repository.read(path)
        if not isinstance(groups, dict) or set(groups) != set(TYPES):
            raise UniversityError("Неверная структура данных университета")
        data: Data = {kind: {} for kind in TYPES}
        for kind in TYPES:
            records = groups[kind]
            if not isinstance(records, list):
                raise UniversityError(f"В {kind} ожидается список записей")
            for values in records:
                item = make_record(data, kind, values)
                rows = data[kind]
                if item.id in rows:
                    raise UniversityError(f"Повторяющийся ID {item.id} в {kind}")
                rows[item.id] = item
        self.data = data

    def save(self, path: Path) -> None:
        self.repository.write(path, self.data)
