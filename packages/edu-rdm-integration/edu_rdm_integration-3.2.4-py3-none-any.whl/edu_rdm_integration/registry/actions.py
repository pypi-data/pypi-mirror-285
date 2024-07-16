from m3 import (
    OperationResult,
)
from m3.actions import (
    ControllerCache,
)
from m3_ext.ui.containers import (
    ExtGridCheckBoxSelModel,
)
from objectpack.actions import (
    BaseAction,
    ObjectPack,
    SelectorWindowAction,
)

from edu_rdm_integration.models import (
    RegionalDataMartEntityEnum,
    TransferredEntity,
)


class EntitySelectPack(ObjectPack):
    """Пак выбора сущностей для сбора и экспорта данных."""

    title = 'Сущность РВД'
    model = RegionalDataMartEntityEnum
    _is_primary_for_model = False

    list_sort_order = ('order_number', )

    columns = [
        {
            'data_index': 'key',
            'header': 'Сущность',
        },
        {
            'data_index': 'title',
            'header': 'Описание',
        },
    ]

    def get_rows_query(self, request, context):
        """Возвращает выборку из БД для получения списка данных.

        Ранее выбранные сущности не отображаются в списке.
        """
        query = super().get_rows_query(request, context)

        return query.filter(transferredentity__isnull=True)


class TransferredEntityAddWindowAction(SelectorWindowAction):
    """Экшн показа окна выбора сущностей для сбора и экспорта данных."""

    def configure_action(self, request, context):
        """Конфигурирует экшн."""
        self.data_pack = ControllerCache.find_pack(EntitySelectPack)
        self.callback_url = self.parent.save_action.absolute_url()

    def configure_window(self, win, request, context):
        """Конфигурирует окно выбора."""
        win.grid.sm = ExtGridCheckBoxSelModel()
        win.grid.store.id_property = 'key'

        return win


class TransferredEntitySaveAction(BaseAction):
    """Экшн сохранения выбранных сущностей для сбора и экспорта данных."""

    def context_declaration(self):
        """Объявляет контекст экшна."""
        return {
            'id': {'type': 'str_list', 'default': []},
        }

    def run(self, request, context):
        """Обеспечивает выполнение запроса."""
        self.parent.model.objects.bulk_create([
            self.parent.model(entity_id=key)
            for key in context.id
        ])

        return OperationResult(success=True)


class TransferredEntityPack(ObjectPack):
    """Пак сущностей, по которым должен быть произведен сбор и экспорт данных."""

    title = 'Сущности для сбора и экспорта данных'
    model = TransferredEntity

    can_delete = True

    list_sort_order = ('entity__order_number', )

    need_check_permission = True

    columns = [
        {
            'data_index': 'entity.key',
            'header': 'Сущность',
        },
        {
            'data_index': 'entity.title',
            'header': 'Описание',
        },
    ]

    def __init__(self):
        super().__init__()

        self.add_window_action = TransferredEntityAddWindowAction()
        self.replace_action('new_window_action', self.add_window_action)

        self.save_entity_action = TransferredEntitySaveAction()
        self.replace_action('save_action', self.save_entity_action)

    def configure_grid(self, grid, *args, **kwargs):
        """Конфигурирует грид."""
        super().configure_grid(grid, *args, **kwargs)

        grid.sm = ExtGridCheckBoxSelModel()

    def extend_menu(self, menu):
        """Расширяет главное меню."""
        return menu.SubMenu(
            'Администрирование',
            menu.SubMenu(
                'Региональная витрина данных',
                menu.Item(
                    self.title,
                    self.list_window_action,
                ),
            ),
        )
