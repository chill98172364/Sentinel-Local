import tempfile
import shutil
import os
import random, string

class TempManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._temp_dir = tempfile.mkdtemp()
        return cls._instance

    @property
    def path(self) -> str:
        return str(self._temp_dir)

    def rand_str(self, length:int=5):
        characters = string.ascii_letters + string.digits 
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string

    def create_file(self, name, content=""):
        file_path = os.path.join(self.path, name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return str(file_path)
    
    def create_file_bytes(self, name, data=b""):
        file_path = os.path.join(self.path, name)
        with open(file_path, "wb") as f:
            f.write(data)
        return str(file_path)
    
    def create_folder(self, name = None):
        if name == None:
            name = self.rand_str()
        folder_name = os.path.join(self.path, name)
        os.makedirs(folder_name)
        return folder_name

    def get_file_path(self, name):
        return os.path.join(self.path, name)

    def cleanup(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
            self._temp_dir = None
            TempManager._instance = None