import logging
from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Optional,
)


class BaseOperationData(ABC):
    """Базовый класс операций с данными."""

    def __init__(self, **kwargs):
        # Идентификатор команды для передачи сигналу manager_created
        self.command_id: Optional[int] = kwargs.get('command_id')

        self._file_handler: Optional[logging.FileHandler] = None

        self._add_file_handler()

    @property
    @abstractmethod
    def _log_file_path(self) -> str:
        """Путь до лог файла."""

    def _add_file_handler(self) -> None:
        """Добавляет обработчик логов."""
        if self.command_id:
            self._file_handler = logging.FileHandler(self._log_file_path)

            logging.getLogger('info_logger').addHandler(self._file_handler)
            logging.getLogger('exception_logger').addHandler(self._file_handler)

    def _remove_file_handler(self) -> None:
        """Удаляет обработчик логов."""
        if self._file_handler:
            logging.getLogger('info_logger').removeHandler(self._file_handler)
            logging.getLogger('exception_logger').removeHandler(self._file_handler)

            self._file_handler.close()
