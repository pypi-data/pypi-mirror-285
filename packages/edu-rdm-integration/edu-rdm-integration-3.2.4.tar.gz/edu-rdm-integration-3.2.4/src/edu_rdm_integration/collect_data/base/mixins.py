from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    TYPE_CHECKING,
    Union,
)

from django.contrib.contenttypes.models import (
    ContentType,
)
from django.db.models import (
    Q,
)
from django.db.models.constants import (
    LOOKUP_SEP,
)

from educommon.audit_log.utils import (
    get_model_by_table,
)
from educommon.integration_entities.consts import (
    LOG_OPERATION_MAP,
)
from educommon.integration_entities.enums import (
    EntityLogOperation,
)

from edu_rdm_integration.collect_data.base.caches import (
    LogChange,
)
from edu_rdm_integration.helpers import (
    Graph,
)
from edu_rdm_integration.mapping import (
    MODEL_FIELDS_LOG_FILTER,
)
from edu_rdm_integration.utils import (
    build_related_model_graph,
)

if TYPE_CHECKING:
    from edu_rdm_integration.collect_data.base.caches import (
        IgnoreLogDependency,
    )


class ReformatLogsMixin:
    """Миксин для преобразования логов к удобному для работы виду в кешах помощников функций."""

    def _reformat_logs(self):
        """
        Производится преобразование логов к удобному для работы виду.

        Предполагается вложенные словари. На первом уровне ключом будет название
        модели, на втором идентификатор записи.
        """
        for log in self.raw_logs:
            model = get_model_by_table(log.table)._meta.label

            if getattr(self, '_log_only_models', None) and (model not in self._log_only_models):
                # Пропускаем, если модель не входит в список отслеживаемых
                continue

            operation = LOG_OPERATION_MAP[log.operation]

            if operation in EntityLogOperation.values:
                fields = log.transformed_data
            else:
                fields = {}

            # Если данных нет, то LogChange не формируем
            if not fields:
                continue

            log_change = LogChange(
                operation=operation,
                fields=fields,
            )

            if not self._filter_log(model, log_change):
                # Если модель не отслеживается, то запись лога не сохраняем
                continue

            if log_change.operation == EntityLogOperation.DELETE:
                self.logs[model][log.object_id] = [log_change, ]
            else:
                self.logs[model][log.object_id].append(log_change)

    @staticmethod
    def _filter_log(model: str, log_change: LogChange) -> bool:
        """
        Производится проверка изменений на отслеживаемые поля.
        """
        is_filtered = False

        if model in MODEL_FIELDS_LOG_FILTER[log_change.operation]:
            filter_fields = MODEL_FIELDS_LOG_FILTER[log_change.operation][model]
            if filter_fields:
                # Если заданы конкретные поля, которые должны отслеживать
                for field in log_change.fields:
                    if field in filter_fields:
                        # Достаточно, чтобы хотя бы одно поле попало под фильтр
                        is_filtered = True
                        break
            else:
                # Модель отслеживается, но перечень фильтруемых полей не задан,
                # значит фильтруем все поля модели
                is_filtered = True

        return is_filtered


class BaseIgnoreLogMixin:
    """Миксин для исключения логов не подлежащих обработке.

    Позволяет указать зависимость логов от состояния вышестоящих зависимых объектов.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._graph = Graph()
        self._dependency: Optional['IgnoreLogDependency'] = None

    @staticmethod
    def _add_lookup_prefix(q_filter: Q, lookup_path_args: List[str]) -> Q:
        """Функция принимает Q-объект и добавляет префикс к каждому указанному полю."""
        new_q = Q(_negated=q_filter.negated, _connector=q_filter.connector)

        for child in q_filter.children:
            if isinstance(child, Q):
                new_child = BaseIgnoreLogMixin._add_lookup_prefix(child, lookup_path_args)
            else:
                field_name, lookup_value = child

                if isinstance(field_name, str):
                    field_name = LOOKUP_SEP.join((*lookup_path_args, field_name))
                elif isinstance(field_name, tuple):
                    field_name = (LOOKUP_SEP.join((*lookup_path_args, field_name[0])),) + field_name[1:]

                new_child = (field_name, lookup_value)

            new_q.add(new_child, q_filter.connector)

        return new_q

    def _build_filter(
        self,
        lookup_path_args: List[str],
        filter_params: Union[Tuple[Q], Dict[str, Any]],
        is_valid_lookup: bool = False,
    ) -> Q:
        """Построение фильтра."""
        # Всегда строим OR, так как соответствие любому из параметров фильтра будет однозначно свидетельствовать, что
        # данные являются некорректными и должны быть исключены из последующей обработки
        q_filter = Q(_connector=Q.OR)

        if is_valid_lookup:
            if isinstance(filter_params, dict):
                for field_name, value in filter_params.items():
                    q_filter.add((LOOKUP_SEP.join((*lookup_path_args, field_name)), value), Q.OR)
            else:
                for filter_param in filter_params:
                    if isinstance(filter_param, Q):
                        q_filter |= self._add_lookup_prefix(filter_param, lookup_path_args)
                    else:
                        raise ValueError('Please, check `DependencyFilter.filters`, incorrect value!')

        return q_filter

    def _exclude_logs(self, model_label: str, object_model_ids: Iterable[int]):
        """Исключаем логи из обработки."""
        for object_id in object_model_ids:
            self.logs[model_label].pop(object_id)

    def _ignore_logs(self):
        """
        Исключение логов из обработки на основании описанных правил.
        """
        super()._ignore_logs()

        if not self._dependency:
            return

        model_label_separator = '.'

        for app_label, model_name in (model_label.split(model_label_separator) for model_label in self.logs):
            q_filter = Q(_connector=Q.OR)

            log_model = ContentType.objects.get(app_label=app_label.lower(), model=model_name.lower()).model_class()

            for dependency in self._dependency.dependency_filters:
                app_name, model_name = dependency.model_label.lower().split(model_label_separator)
                find_model = ContentType.objects.get(app_label=app_name, model=model_name).model_class()

                self._graph = build_related_model_graph(
                    self._graph, log_model, find_model, ignored_model_fields=self._dependency.ignore_model_fields
                )

                name_edges = self._graph.get_edges_between_vertices(
                    log_model._meta.model_name, find_model._meta.model_name
                )

                q_filter |= self._build_filter(
                    name_edges,
                    dependency.filters,
                    is_valid_lookup=bool(name_edges or find_model == log_model)
                )

            if q_filter:
                ignore_model_ids = log_model.objects.filter(
                    q_filter,
                    id__in=self.logs[log_model._meta.label],
                ).values_list('pk', flat=True)
                self._exclude_logs(log_model._meta.label, ignore_model_ids)
