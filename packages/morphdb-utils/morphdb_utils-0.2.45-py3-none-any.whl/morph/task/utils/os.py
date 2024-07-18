import os


class OsUtils:
    @staticmethod
    def normalize_path(filename: str, project_root: str) -> str:
        return os.path.abspath(os.path.normpath(os.path.join(project_root, filename)))
