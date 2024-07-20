import logging
import traceback
from pathlib import Path

from tqdm import tqdm

from dicomselect.__version__ import __version__

LOG_FILENAME = 'dicomselect.log'


def progress_duration(progress: tqdm) -> str:
    hours, remainder = divmod(int(progress.format_dict['elapsed']), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours}:{minutes:02d}:{seconds:02d}'


class Logger:
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    def __init__(self):
        self._log: logging.Logger = None
        self._log_path: Path = None
        self._errors: int = 0
        self._error = set()

    @property
    def errors(self) -> int:
        return self._errors

    @property
    def log_path(self) -> Path:
        return self._log_path

    def init_logger(self, file: Path):
        self._errors = 0
        self._log = logging.getLogger(file.name)
        self._log.setLevel(logging.INFO)
        [self._log.removeHandler(h) for h in self._log.handlers]
        self._log_path = file
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._log_path, 'w'):
            pass

        formatter = logging.Formatter('--- %(levelname)s ---\n%(message)s')
        handler = logging.FileHandler(file.as_posix())
        handler.setFormatter(formatter)
        self._log.addHandler(handler)
        self._log.log(logging.INFO, 'dicomselect ' + __version__)

    def print(self, text: str, level: int = logging.INFO):
        print(text)
        self._log.log(level, text)

    def log(self, exc: BaseException | str | list[str], level: int = logging.ERROR, **kwargs):
        self._errors += 1

        if kwargs:
            name = kwargs.pop('name', '')
            text = [f'Error during {name}:'] if name else []
            for key, val in kwargs.items():
                text.append(f'\t{key}:\n\t\t{str(val)}\n')
            text.append('\t' + '\t'.join(traceback.format_exception(exc)))
            exc = '\n'.join(text)

        if isinstance(exc, Exception):
            self._log.log(level, traceback.format_exception(exc))
        else:
            self._log.log(level, str(exc))
