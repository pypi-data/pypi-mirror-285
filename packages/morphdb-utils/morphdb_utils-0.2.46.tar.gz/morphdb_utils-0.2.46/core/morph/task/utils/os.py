from __future__ import annotations

import os


class OsUtils:
    @staticmethod
    def is_at(abs_path: str) -> bool:
        return os.getcwd() == os.path.normpath(abs_path)

    @staticmethod
    def get_abs_path(filename: str, base_path: str) -> str:
        if os.path.isabs(filename):
            return os.path.abspath(os.path.normpath(filename))
        else:
            return os.path.abspath(os.path.normpath(os.path.join(base_path, filename)))
