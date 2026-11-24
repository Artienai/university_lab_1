from application.university_service import UniversityService
from infrastructure.file_repository import FileRepository
from presentation.console import run


def main() -> None:
    repository = FileRepository()
    service = UniversityService(repository)
    run(service)


if __name__ == "__main__":
    main()
