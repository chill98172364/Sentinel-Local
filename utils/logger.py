import os
import datetime
from typing import Optional

class Logger:
    _instance: Optional["Logger"] = None
    _level: int = 3
    _log_file: Optional[str] = None
    LEVELS = {"NONE": 0, "ERROR": 1, "WARN": 2, "INFO": 3, "DEBUG": 4}

    def __new__(cls, level="INFO", log_file = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._level = cls.LEVELS.get(level.upper(), 3)
            cls._instance._log_file = log_file
            if log_file:
                os.makedirs(os.path.dirname(log_file), exist_ok=True)
        return cls._instance

    def set_level(self, level):
        self._level = self.LEVELS.get(level.upper(), self._level)

    def _write(self, level_name, message):
        if self._level == 0:
            return
        level_value = self.LEVELS.get(level_name, 0)
        if level_value <= self._level:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f"[{timestamp}] [{level_name}] {message}"
            print(log_msg)
            if self._log_file:
                with open(self._log_file, "a", encoding="utf-8") as f:
                    f.write(log_msg + "\n")

    def error(self, message):
        self._write("ERROR", message)

    def warn(self, message):
        self._write("WARN", message)

    def info(self, message):
        self._write("INFO", message)

    def debug(self, message):
        self._write("DEBUG", message)
