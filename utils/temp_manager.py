import tempfile
import shutil
import os

class TempManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._temp_dir = tempfile.mkdtemp()
        return cls._instance

    @property
    def path(self) -> str:
        return self._temp_dir

    def create_file(self, name, content=""):
        file_path = os.path.join(self._temp_dir, name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return str(file_path)
    
    def create_file_bytes(self, name, data=b""):
        file_path = os.path.join(self._temp_dir, name)
        with open(file_path, "wb") as f:
            f.write(data)
        return str(file_path)

    def get_file_path(self, name):
        return os.path.join(self._temp_dir, name)

    def cleanup(self):
        if os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir)
            self._temp_dir = None
            TempManager._instance = None