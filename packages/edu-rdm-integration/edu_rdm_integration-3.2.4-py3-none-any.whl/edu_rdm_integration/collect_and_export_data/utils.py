from educommon.async_task.models import (
    AsyncTaskType,
)

from edu_rdm_integration.collect_and_export_data.models import (
    EduRdmCollectDataCommandProgress,
    EduRdmExportDataCommandProgress,
)
from edu_rdm_integration.collect_data.collect import (
    BaseCollectModelsDataByGeneratingLogs,
)
from edu_rdm_integration.consts import (
    TASK_QUEUE_NAME,
)
from edu_rdm_integration.export_data.export import (
    ExportEntitiesData,
)
from edu_rdm_integration.helpers import (
    save_command_log_link,
)


class CollectCommandMixin:
    """Класс-примесь для запуска команды сборки моделей."""

    queue = TASK_QUEUE_NAME
    routing_key = TASK_QUEUE_NAME
    description = 'Сбор данных моделей РВД'
    task_type = AsyncTaskType.SYSTEM

    def get_collect_command(self, command_id: int) -> EduRdmCollectDataCommandProgress:
        """Возвращает экземпляр модели команды запуска."""
        command = EduRdmCollectDataCommandProgress.objects.get(id=command_id)

        return command

    def get_collect_models_class(self):
        """Возвращает класс для сбора данных."""
        return BaseCollectModelsDataByGeneratingLogs

    def run_collect_command(self, command) -> None:
        """Запуск команды сбора."""
        collect_models_data_class = self.get_collect_models_class()
        collect_models_data_class(
            models=(command.model_id,),
            logs_period_started_at=command.logs_period_started_at,
            logs_period_ended_at=command.logs_period_ended_at,
            command_id=command.id,
            institute_ids=tuple(command.institute_ids or ()),
        ).collect()

    def save_collect_command_logs(self, command_id: int, log_dir: str):
        """Сохранение ссылки на файл логов в команде."""
        try:
            command = self.get_collect_command(command_id)
        except EduRdmCollectDataCommandProgress.DoesNotExist:
            command = None

        if command:
            save_command_log_link(command, log_dir)


class ExportCommandMixin:
    """Класс-примесь для запуска команды выгрузки сущностей."""

    queue = TASK_QUEUE_NAME
    routing_key = TASK_QUEUE_NAME
    description = 'Экспорт данных сущностей РВД'
    task_type = AsyncTaskType.SYSTEM

    def get_export_command(self, command_id: int) -> EduRdmExportDataCommandProgress:
        """Возвращает экземпляр модели команды запуска."""
        command = EduRdmExportDataCommandProgress.objects.get(id=command_id)

        return command

    def run_export_command(self, command: EduRdmExportDataCommandProgress) -> None:
        """Запуск команды выгрузки."""
        ExportEntitiesData(
            entities=(command.entity_id,),
            period_started_at=command.period_started_at,
            period_ended_at=command.period_ended_at,
            command_id=command.id,
        ).export()

    def save_export_command_logs(self, command_id: int, log_dir: str):
        """Сохранение ссылки на файл логов в команде."""
        try:
            command = self.get_export_command(command_id)
        except EduRdmExportDataCommandProgress.DoesNotExist:
            command = None

        if command:
            save_command_log_link(command, log_dir)
