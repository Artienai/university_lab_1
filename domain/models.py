class Student:
    """Студент университета."""

    def __init__(self, id: int, name: str, group: str):
        self.id = id
        self.name = name
        self.group = group


class Course:
    """Учебная дисциплина."""

    def __init__(self, id: int, title: str, hours: int):
        self.id = id
        self.title = title
        self.hours = hours


class Enrollment:
    """Оценка студента по учебной дисциплине."""

    def __init__(self, id: int, student_id: int, course_id: int, grade: int):
        self.id = id
        self.student_id = student_id
        self.course_id = course_id
        self.grade = grade


class UniversityError(Exception):
    """Ошибка предметной области университета."""


Record = Student | Course | Enrollment
Data = dict[str, dict[int, Record]]
TYPES: dict[str, tuple[type[Record], tuple[str, ...]]] = {
    "students": (Student, ("name", "group")),
    "courses": (Course, ("title", "hours")),
    "enrollments": (Enrollment, ("student_id", "course_id", "grade")),
}
