import tempfile
import unittest
from pathlib import Path

from application.university_service import UniversityService
from domain.models import UniversityError
from infrastructure.file_repository import FileRepository


class UniversityServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = UniversityService(FileRepository())
        self.student = self.service.write_record(
            "students", {"name": "Иванов Иван", "group": "ИДБ-25-14"}
        )
        self.course = self.service.write_record(
            "courses", {"title": "Прикладное программирование", "hours": 72}
        )

    def test_create_update_and_delete(self) -> None:
        enrollment = self.service.write_record(
            "enrollments",
            {"student_id": 1, "course_id": 1, "grade": 4},
        )
        updated = self.service.write_record(
            "enrollments",
            {"student_id": 1, "course_id": 1, "grade": 5},
            enrollment.id,
        )
        self.assertEqual(updated.grade, 5)
        self.service.delete_record("enrollments", enrollment.id)
        self.service.delete_record("students", self.student.id)
        self.service.delete_record("courses", self.course.id)
        self.assertEqual(self.service.list_records("students"), [])

    def test_referenced_records_cannot_be_deleted(self) -> None:
        self.service.write_record(
            "enrollments",
            {"student_id": 1, "course_id": 1, "grade": 5},
        )
        with self.assertRaises(UniversityError):
            self.service.delete_record("students", self.student.id)
        with self.assertRaises(UniversityError):
            self.service.delete_record("courses", self.course.id)

    def test_grade_and_foreign_keys_are_validated(self) -> None:
        with self.assertRaises(UniversityError):
            self.service.write_record(
                "enrollments",
                {"student_id": 1, "course_id": 1, "grade": 6},
            )
        with self.assertRaises(UniversityError):
            self.service.write_record(
                "enrollments",
                {"student_id": 99, "course_id": 1, "grade": 5},
            )

    def test_json_roundtrip(self) -> None:
        self.service.write_record(
            "enrollments",
            {"student_id": 1, "course_id": 1, "grade": 5},
        )
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "university.json"
            self.service.save(path)
            restored = UniversityService(FileRepository())
            restored.load(path)
            self.assertEqual(len(restored.list_records("students")), 1)
            self.assertEqual(len(restored.list_records("courses")), 1)
            self.assertEqual(
                restored.list_records("enrollments")[0].grade, 5
            )

    def test_xml_file_is_not_supported(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "university.xml"
            with self.assertRaises(UniversityError):
                self.service.save(path)


if __name__ == "__main__":
    unittest.main()
