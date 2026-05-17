# placeholder
import os


class FileManager:

    @staticmethod
    def ensure_directory(path: str):
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def file_exists(path: str) -> bool:
        return os.path.exists(path)

    @staticmethod
    def read_text_file(path: str) -> str:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()

    @staticmethod
    def write_text_file(path: str, content: str):
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)