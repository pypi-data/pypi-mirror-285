from itertools import (
    chain,
)
from typing import (
    TYPE_CHECKING,
    Dict,
    Optional,
    Type,
)

import celery
from celery.exceptions import (
    Ignore,
)
from celery.schedules import (
    crontab,
)
from django.conf import (
    settings,
)
from django.db.models import (
    CharField,
    Max,
)
from django.db.models.functions import (
    Cast,
)
from django.utils import (
    timezone,
)
from educommon.async_task.locker import (
    TaskLocker,
)
from educommon.async_task.models import (
    AsyncTaskType,
    RunningTask,
)
from educommon.async_task.tasks import (
    PeriodicAsyncTask,
)
from educommon.utils.date import (
    get_today_min_datetime,
)
from m3_db_utils.consts import (
    DEFAULT_ORDER_NUMBER,
)

from edu_rdm_integration.collect_and_export_data.models import (
    EduRdmCollectDataCommandProgress,
    EduRdmExportDataCommandProgress,
)
from edu_rdm_integration.collect_data.collect import (
    BaseCollectLatestModelsData,
)
from edu_rdm_integration.collect_data.helpers import (
    set_failed_status_suspended_collecting_data_stages,
)
from edu_rdm_integration.consts import (
    REGIONAL_DATA_MART_INTEGRATION_COLLECTING_DATA,
    REGIONAL_DATA_MART_INTEGRATION_EXPORTING_DATA,
    TASK_QUEUE_NAME,
)
from edu_rdm_integration.enums import (
    CommandType,
    FileUploadStatusEnum,
)
from edu_rdm_integration.export_data.export import (
    ExportLatestEntitiesData,
)
from edu_rdm_integration.export_data.helpers import (
    set_failed_status_suspended_exporting_data_stages,
)
from edu_rdm_integration.helpers import (
    get_collecting_managers_max_period_ended_dates,
    get_exporting_managers_max_period_ended_dates,
    UploadStatusHelper,
    save_command_log_link,
)
from edu_rdm_integration.models import (
    ExportingDataSubStageUploaderClientLog,
    RegionalDataMartEntityEnum,
    TransferredEntity,
)
from edu_rdm_integration.storages import (
    RegionalDataMartEntityStorage,
)

if TYPE_CHECKING:
    from datetime import (
        datetime,
    )

    from function_tools.managers import (
        RunnerManager,
    )


class PeriodicTaskLocker(TaskLocker):
    """Класс отвечающий за блокировку задач.

    Переопределён для возможности игнорирования повторного запуска для уже
    запущенных периодических задач.
    """

    def raise_if_locked(self, message: Optional[str] = None):
        """Если блокировано, то вызывает исключение."""
        if self.is_locked():
            self.debug(f'Add failed. Task {self.task_name} currently locked ({self.params})')

            raise Ignore()


class UniquePeriodicAsyncTask(PeriodicAsyncTask):
    """Уникальные периодические задачи."""

    abstract = True
    lock_expire_seconds = 60 * 60

    locker_class = PeriodicTaskLocker

    @property
    def locker_config(self) -> dict:
        """Настройки для механизма блокировок. """
        return {
            'lock_params': {'task_name': self.name},
            'lock_message': f'Task [{self.__name__}] is running',
            'lock_expire': self.lock_expire_seconds,
        }


class RDMCheckUploadStatus(UniquePeriodicAsyncTask):
    """Периодическая задача для сбора статусов по загрузке файла в витрину."""

    queue = TASK_QUEUE_NAME
    routing_key = TASK_QUEUE_NAME
    description = 'Сбор статусов загрузки данных в витрину "Региональная витрина данных"'
    lock_expire_seconds = settings.RDM_UPLOAD_STATUS_TASK_LOCK_EXPIRE_SECONDS
    task_type = AsyncTaskType.UNKNOWN
    run_every = crontab(
        minute=settings.RDM_UPLOAD_STATUS_TASK_MINUTE,
        hour=settings.RDM_UPLOAD_STATUS_TASK_HOUR,
        day_of_week=settings.RDM_UPLOAD_STATUS_TASK_DAY_OF_WEEK,
    )

    def process(self, *args, **kwargs):
        """Выполнение."""
        super().process(*args, **kwargs)

        # Получаем незавершенные загрузки данных в витрину
        in_progress_uploads = ExportingDataSubStageUploaderClientLog.objects.filter(
            file_upload_status=FileUploadStatusEnum.IN_PROGRESS,
            is_emulation=False,
        )

        UploadStatusHelper(in_progress_uploads).run()


class CheckSuspendedExportedStagePeriodicTask(UniquePeriodicAsyncTask):
    """Периодическая задача поиска зависших этапов/подэтапов экспорта."""

    queue = TASK_QUEUE_NAME
    routing_key = TASK_QUEUE_NAME
    description = 'Поиск зависших этапов/подэтапов экспорта в "Региональная витрина данных"'
    lock_expire_seconds = settings.RDM_CHECK_SUSPEND_TASK_LOCK_EXPIRE_SECONDS
    task_type = AsyncTaskType.SYSTEM
    run_every = crontab(
        minute=settings.RDM_CHECK_SUSPEND_TASK_MINUTE,
        hour=settings.RDM_CHECK_SUSPEND_TASK_HOUR,
        day_of_week=settings.RDM_CHECK_SUSPEND_TASK_DAY_OF_WEEK,
    )

    def process(self, *args, **kwargs):
        """Выполнение задачи."""
        super().process(*args, **kwargs)

        change_status_collecting_result = set_failed_status_suspended_collecting_data_stages()
        change_status_exporting_result = set_failed_status_suspended_exporting_data_stages()

        task_result = {
            'Прервано сборок': (
                f'Этапов {change_status_collecting_result["change_stage_count"]}'
                f' и подэтапов {change_status_collecting_result["change_sub_stage_count"]}'
            ),
            'Прервано выгрузок': (
                f'Этапов {change_status_exporting_result["change_stage_count"]}'
                f' и подэтапов {change_status_exporting_result["change_sub_stage_count"]}'
            ),
        }

        self.set_progress(
            values=task_result
        )


class TransferLatestEntitiesDataPeriodicTask(UniquePeriodicAsyncTask):
    """Периодическая задача сбора и выгрузки данных."""

    queue = TASK_QUEUE_NAME
    routing_key = TASK_QUEUE_NAME
    description = 'Периодическая задача сбора и экспорта данных РВД'
    lock_expire_seconds = settings.RDM_TRANSFER_TASK_LOCK_EXPIRE_SECONDS
    task_type = AsyncTaskType.UNKNOWN
    run_every = crontab(
        minute=settings.RDM_TRANSFER_TASK_MINUTE,
        hour=settings.RDM_TRANSFER_TASK_HOUR,
        day_of_week=settings.RDM_TRANSFER_TASK_DAY_OF_WEEK,
    )

    def __init__(self) -> None:
        super().__init__()

        self._collecting_data_managers: Dict[str, Type['RunnerManager']] = {}
        self._collecting_data_manager_to_logs_period_end: Dict[str, 'datetime'] = {}

        self._exporting_data_managers: Dict[str, Type['RunnerManager']] = {}
        self._exporting_data_manager_to_period_end: Dict[str, 'datetime'] = {}

        self._transferred_entities = []

    def process(self, *args, **kwargs):
        """Выполняет задачу."""
        super().process(*args, **kwargs)

        self._collect_transferred_entities()
        self._collect_managers()
        self._calculate_collecting_managers_logs_period_ended_at()
        self._calculate_exporting_managers_ended_at()

        task_id = RunningTask.objects.filter(
            pk=self.request.id,
        ).values_list('pk', flat=True).first()

        model_enum_values = RegionalDataMartEntityEnum.get_entities_model_enums(
            entity_enums=self._transferred_entities,
            is_sorted=True,
        )

        filtered_model_enum_values = filter(lambda model: model.order_number != DEFAULT_ORDER_NUMBER, model_enum_values)
        for model_enum_value in filtered_model_enum_values:
            self._run_collect_model_data(model_enum_value.key, task_id)

        for entity_enum_value in sorted(self._transferred_entities, key=lambda entity: entity.order_number):
            self._run_export_entity_data(entity_enum_value.key, task_id)

    def _run_collect_model_data(self, model: str, task_id: str) -> None:
        """Запускает сбор данных модели РВД."""
        command = self._create_collect_command(model, task_id)
        collect_model_data = self._prepare_collect_model_data_class(command)
        collect_model_data.collect()

        command.refresh_from_db(fields=['stage_id'])
        save_command_log_link(command, settings.RDM_COLLECT_LOG_DIR)

    def _run_export_entity_data(self, entity: str, task_id: str) -> None:
        """Запускает экспорт данных сущности РВД."""
        command = self._create_export_command(entity, task_id)
        if command:
            export_entity_data = self._prepare_export_entity_data_class(command)
            export_entity_data.export()

            command.refresh_from_db(fields=['stage_id'])
            save_command_log_link(command, settings.RDM_EXPORT_LOG_DIR)

    def _collect_transferred_entities(self) -> None:
        """Собирает сущности РВД, по которым будет произведен сбор и экспорт данных."""
        self._transferred_entities = [
            RegionalDataMartEntityEnum.get_model_enum_value(key=entity)
            for entity in TransferredEntity.objects.values_list('entity', flat=True)
        ]

    def _collect_managers(self) -> None:
        """Собирает менеджеры Функций для сбора и выгрузки данных."""
        entity_storage = RegionalDataMartEntityStorage()
        entity_storage.prepare()

        collecting_models_data_managers_map = entity_storage.prepare_entities_manager_map(
            tags={REGIONAL_DATA_MART_INTEGRATION_COLLECTING_DATA},
        )
        exporting_entities_data_managers_map = entity_storage.prepare_entities_manager_map(
            tags={REGIONAL_DATA_MART_INTEGRATION_EXPORTING_DATA},
        )

        for transferred_entity in self._transferred_entities:
            for model in chain((transferred_entity.main_model_enum, ), transferred_entity.additional_model_enums):
                collect_manager_class = collecting_models_data_managers_map.get(model.key)
                if collect_manager_class:
                    self._collecting_data_managers[model.key] = collect_manager_class

            export_manager_class = exporting_entities_data_managers_map.get(transferred_entity.key)
            if export_manager_class:
                self._exporting_data_managers[transferred_entity.key] = export_manager_class

    def _calculate_collecting_managers_logs_period_ended_at(self) -> None:
        """Определяет дату последнего успешного этапа сбора у менеджеров Функций сбора."""
        self._collecting_data_manager_to_logs_period_end = get_collecting_managers_max_period_ended_dates(
            self._collecting_data_managers.values()
        )

    def _calculate_exporting_managers_ended_at(self) -> None:
        """Определяет дату последнего успешного подэтапа экспорта у менеджеров Функций экспорта."""
        self._exporting_data_manager_to_period_end = get_exporting_managers_max_period_ended_dates(
            self._exporting_data_managers.values()
        )

    def _create_collect_command(self, model: str, task_id: str) -> EduRdmCollectDataCommandProgress:
        """Создает команду сбора данных моделей РВД."""
        manager = self._collecting_data_managers[model]
        manager_last_collected = (
            self._collecting_data_manager_to_logs_period_end.get(manager.uuid)
            or get_today_min_datetime()
        )

        period_started_at = manager_last_collected
        period_ended_at = timezone.now()

        return EduRdmCollectDataCommandProgress.objects.create(
            model_id=model,
            logs_period_started_at=period_started_at,
            logs_period_ended_at=period_ended_at,
            task_id=task_id,
            type=CommandType.AUTO,
        )

    def _create_export_command(self, entity: str, task_id: str) -> Optional[EduRdmExportDataCommandProgress]:
        """Создает команду экспорта данных сущностей РВД."""
        manager = self._exporting_data_managers[entity]
        manager_last_exported = self._exporting_data_manager_to_period_end.get(manager.uuid)

        if manager_last_exported:
            period_started_at = manager_last_exported
            period_ended_at = timezone.now()

            return EduRdmExportDataCommandProgress.objects.create(
                entity_id=entity,
                period_started_at=period_started_at,
                period_ended_at=period_ended_at,
                task_id=task_id,
                type=CommandType.AUTO,
            )

    def _prepare_collect_model_data_class(
        self,
        command: EduRdmCollectDataCommandProgress
    ) -> BaseCollectLatestModelsData:
        """Подготавливает объект класса сбора данных моделей РВД."""
        return BaseCollectLatestModelsData(
            models=[command.model_id],
            logs_period_started_at=command.logs_period_started_at,
            logs_period_ended_at=command.logs_period_ended_at,
            command_id=command.id,
            use_times_limit=True,
        )

    def _prepare_export_entity_data_class(self, command: EduRdmExportDataCommandProgress) -> ExportLatestEntitiesData:
        """Подготавливает объект класса экспорта данных сущностей РВД.

        При экспорте данных передаем параметр task_id для обновления поля "Описание"
        наименованиями выгруженных сущностей.
        """
        return ExportLatestEntitiesData(
            entities=[command.entity_id],
            period_started_at=command.period_started_at,
            period_ended_at=command.period_ended_at,
            command_id=command.id,
            task_id=self.request.id,
        )


celery_app = celery.app.app_or_default()
celery_app.register_task(RDMCheckUploadStatus)
celery_app.register_task(CheckSuspendedExportedStagePeriodicTask)
celery_app.register_task(TransferLatestEntitiesDataPeriodicTask)
