# История изменений

Все изменения проекта должны быть отражены в этом файле.

Формат основан на [Keep a Changelog](http://keepachangelog.com/)
и проект следует [Семантическому версионированию](http://semver.org/).

## [x.y.z] - гггг-мм-дд

Здесь должно быть расширенное описание того, что было сделано, какие есть планы у команды по дальнейшему развитию.
Желательно будущие цели привязывать к конкретным задачам. Т.е. на каждую цель нужно поставить отдельную задачу и
отразить ее номер здесь.

### Добавлено

- [ПРОЕКТ-ZZZZ](https://jira.bars.group/browse/ПРОЕКТ-ZZZZ)
  PATCH Название задачи или изменения.

- [ПРОЕКТ-YYYY](https://jira.bars.group/browse/ПРОЕКТ-YYYY)
  MINOR Название задачи или изменения.

- [ПРОЕКТ-XXXX](https://jira.bars.group/browse/ПРОЕКТ-XXXX)
  MAJOR Название задачи или изменения.

### Изменено

### Исправлено

### Удалено

## 3.2.5  - 2024-07-16
Добавлен параметр use_times_limit в BaseCollectLatestModelsData для использования переданных параметров logs_period_started_at и logs_period_ended_at

### Изменено
- [EDUSCHL-22070](https://jira.bars.group/browse/EDUSCHL-22070)
  PATCH Добавлен параметр use_times_limit в BaseCollectLatestModelsData для использования переданных параметров logs_period_started_at и  logs_period_ended_at

## 3.2.4 - 2024-07-16
Внесены корректировки в запросы используемые в функциях get_collecting_managers_max_period_ended_dates и get_exporting_managers_max_period_ended_dates.

### Изменено
- [EDUSCHL-22217](https://jira.bars.group/browse/EDUSCHL-22217)
  PATCH Внесены корректировки в запросы используемые в функциях get_collecting_managers_max_period_ended_dates и get_exporting_managers_max_period_ended_dates.
  В подзапросах отсутствовало условие фильтрации по статусу.


## 3.2.3 - 2024-06-06
Внесены корректировки в запросы используемые в функциях get_collecting_managers_max_period_ended_dates и get_exporting_managers_max_period_ended_dates.

### Изменено
- [EDUSCHL-21804](https://jira.bars.group/browse/EDUSCHL-21804)
  PATCH Внесены корректировки в запросы используемые в функциях get_collecting_managers_max_period_ended_dates и get_exporting_managers_max_period_ended_dates.
  Дата и время окончания предыдущего сбора/экспорта могла быть не корректно определена.


## 3.2.2 - 2024-05-21
Изменения в переодической задаче TransferLatestEntitiesDataPeriodicTask,
Изменено определение даты последнего успешного этапа сбора у менеджеров Функций сбора и экспорта.
Изменения получения крайней даты из переданного поля по указанным моделям в BaseCollectLatestModelsData.
Удалён параметр RDM_TRANSFER_TASK_TIMEDELTA.

### Изменено
- [EDUSCHL-21804](https://jira.bars.group/browse/EDUSCHL-21804)
  PATCH Изменение определения даты последнего успешного этапа сбора у менеджеров Функций сбора и экспорта
  Изменения получения крайней даты из переданного поля по указанным моделям в BaseCollectLatestModelsData.
  Реализованы функции get_collecting_managers_max_period_ended_dates и get_exporting_managers_max_period_ended_dates 
  для получения даты времени успешного этапа сбора/экспорта.


## 3.2.1 - 2024-05-03
Понижен уровень логирования при возникновении ошибки отправки запросов в РВД с ERROR до WARNING

### Изменено
- [EDUSCHL-21903](https://jira.bars.group/browse/EDUSCHL-21903)
  PATCH Понижен уровень логирования при возникновении ошибки отправки запросов в РВД


## 3.2.0 - 2024-05-02
Периодические задачи RDMCheckUploadStatus, CheckSuspendedExportedStagePeriodicTask, 
TransferLatestEntitiesDataPeriodicTask сделаны уникальными.

### Изменено
- [EDUSCHL-21891](https://jira.bars.group/browse/EDUSCHL-21891)
  MINOR Периодические задачи RDMCheckUploadStatus, CheckSuspendedExportedStagePeriodicTask, 
  TransferLatestEntitiesDataPeriodicTask сделаны уникальными. Во время действия блокировки не будет возможности 
  поставить новую подобную задачу.


## 3.1.1 - 2024-05-03
Понижен уровень логирования при возникновении ошибки отправки запросов в РВД с ERROR до WARNING

### Изменено
- [EDUSCHL-21903](https://jira.bars.group/browse/EDUSCHL-21903)
  PATCH Понижен уровень логирования при возникновении ошибки отправки запросов в РВД


## 3.1.0 - 2024-04-23
Добавлена поддержка setuptools 69.*.
Поднята минимальная версия пакета pip 23.2.1

### Изменено
- [EDUSCHL-21761](https://jira.bars.group/browse/EDUSCHL-21761)
  MINOR Добавлена поддержка setuptools 69.*. Поднять минимальную версию pip до 23.2.1.


## 3.0.4 - 2024-04-17
Возвращено проставление подэтапа выгрузки всем записям модели.

### Изменено
- [EDUSCHL-21761](https://jira.bars.group/browse/EDUSCHL-21761)
  PATCH Возвращено проставление подэтапа выгрузки всем записям модели.


## 3.0.3 - 2024-04-11
В классах примесей CollectCommandMixin и ExportCommandMixin указана очередь для celery используемая в рамках пакета.
Указано базовое описание и тип задачи для отражения в реестре "Асинхронные задачи".

### Изменено
- [EDUSCHL-21793](https://jira.bars.group/browse/EDUSCHL-21793)
  PATCH В классах примесей CollectCommandMixin и ExportCommandMixin указана очередь для celery 
  используемая в рамках пакета.


## 3.0.2 - 2024-04-11
Изменены типы полей ОГРН и ОКФС в сущности Organisations на строковые.
Исправлен тип передаваемого параметра institute_ids при выполнении поставленной задачи.
Исправлена ошибка проставления подэтапа выгрузки у неотправленных записей.

### Изменено
- [EDUCLLG-8336](https://jira.bars.group/browse/EDUCLLG-8336)
  PATCH Изменены типы полей ОГРН и ОКФС в сущности Organisations на строковые.
- [EDUSCHL-21743](https://jira.bars.group/browse/EDUSCHL-21743)
  PATCH Исправлен тип передаваемого параметра institute_ids при выполнении поставленной задачи.
- [EDUSCHL-21761](https://jira.bars.group/browse/EDUSCHL-21761)
  PATCH Исправлена ошибка проставления подэтапа.


## 3.0.1 - 2024-04-03
Убрано окружение кавычками пустых необязательных полей.

### Изменено

- [EDUCLLG-8325](https://jira.bars.group/browse/EDUCLLG-8325)
  PATCH Убрано окружение кавычками пустых необязательных полей.


## 3.0.0 - 2024-04-02
Расширены возможности кастомизации поведения метода `BaseExportDataFunctionHelper.prepare_record`.

### Добавлено

- [EDUCLLG-8325](https://jira.bars.group/browse/EDUCLLG-8325)
  MAJOR Добавлена возможность отдельно указывать, как формировать строковое
    представление полей в зависимости от их типа и обязательности. **Требуется добавить
    параметр `required_fields` в метод `prepare_record` helper-а функции**.


## [2.2.1] - 2024-03-28
 Исправление наследования Meta в моделях EduRdmCollectDataCommandProgress и EduRdmExportDataCommandProgress

### Исправлено

- [EDUSCHL-21569](https://jira.bars.group/browse/EDUSCHL-21569)
  MINOR Перенести оставшиеся общие асинхронные задачи из ЭШ в пакет edu_rdm_integration


## [2.2.0] - 2024-03-20

Из ЭШ перенесена периодическая задача по сбору и выгрузке данных в РВД.

Также из ЭШ перенесены и переименованы модели:
 - CollectDataCommandProgress перименована в  EduRdmCollectDataCommandProgress
 - ExportDataCommandProgress перименована в EduRdmExportDataCommandProgress
 - Добавлены миксины CollectCommandMixin и ExportCommandMixin

### Добавлено

- [EDUSCHL-21569](https://jira.bars.group/browse/EDUSCHL-21569)
  MINOR Перенести оставшиеся общие асинхронные задачи из ЭШ в пакет edu_rdm_integration


## [2.1.0] - 2024-03-18

Добавлена поддержка Django 3.1.

### Добавлено

- [EDUSCHL-18052](https://jira.bars.group/browse/EDUSCHL-18052)
  MINOR Поднять версию Django до 3.1.14


## [2.0.3] - 2024-03-11

Добавлено сохранение чанка логов в `list` перед его использованием в запускаемых классах в методе `_get_runnable_objects` класса `BaseCollectingDataRunner`.

### Исправлено

- [EDUSCHL-21581](https://jira.bars.group/browse/EDUSCHL-21581)
  PATCH Добавлено сохранение чанка логов в `list` перед его использованием в запускаемых классах в методе `_get_runnable_objects` класса `BaseCollectingDataRunner`.


## [2.0.2] - 2024-03-07

Откатил изменения сделанные в версии 2.0.1. Данные доработки приводили к невозможности отправить данные.

### Исправлено

- [EDUSCHL-21503](https://jira.bars.group/browse/EDUSCHL-21503)
  PATCH Откатил изменения сделанные в версии 2.0.1


## [2.0.1] - 2024-03-01

Изменена работа метода _calculate_last_finished_entity_export класса BaseExportLatestEntitiesData

### Исправлено

- [EDUSCHL-21503](https://jira.bars.group/browse/EDUSCHL-21503)
  PATCH ЭШ. Все модели РВД. Некорректное определение начала периода экспорта командой при сборе 
  командой collect_latest_models_data 


## [2.0.0] - 2024-02-21

Параметр school_ids переименован в institute_ids.

### Изменено

- [EDUSCHL-20485](https://jira.bars.group/browse/EDUSCHL-20485)
  MAJOR Произвести переименование параметра school_ids на institute_ids


## [1.0.2] - 2024-03-06

Добавлено разбиение на чанки запроса на обновление поля modified у невыгруженных записей,
при запуске команды `export_latest_entities_data`.

### Исправлено

- [EDUSCHL-21572](https://jira.bars.group/browse/EDUSCHL-21572)
  PATCH Добавлено разбиение на чанки запроса на обновление в методе `_update_model_modified_field` 
  класса `BaseExportLatestEntitiesData`.


## [1.0.1] - 2024-02-20

Исправлено ограничение сбора логов периодом `RDM_TRANSFER_TASK_TIMEDELTA` в `BaseCollectLatestModelsData`

### Исправлено

- [EDUSCHL-21413](https://jira.bars.group/browse/EDUSCHL-21413)
  PATCH Исправлено ограничение сбора логов периодом `RDM_TRANSFER_TASK_TIMEDELTA` в `BaseCollectLatestModelsData`


## [1.0.0] - 2024-01-31

Удален дублирующийся клаcc `LogChange` из `collect_data.non_calculated.base.caches`.

### Удалено

- [EDUSCHL-21308](https://jira.bars.group/browse/EDUSCHL-21308)
  MAJOR Удален дублирующийся клаcc `LogChange` из `collect_data.non_calculated.base.caches`.


## [0.10.2] - 2024-02-05

Рефакторинг принудительного запуска функций без добавления их в очередь на исполнение.

В класс кеша BaseCollectingExportedDataFunctionCacheStorage расчетных и не расчетных функций добавлен метод _ignore_logs.
Добавлена утилита build_related_model_graph для построения графа связей между моделями. 
Добавлен миксин BaseIgnoreLogMixin, для исключения из обработки логов на основании описанных зависимостей.

### Добавлено

- [EDUSCHL-20550](https://jira.bars.group/browse/EDUSCHL-20550)
  MINOR В класс кеша BaseCollectingExportedDataFunctionCacheStorage добавлен метод _ignore_logs. 
  Добавлена утилита build_related_model_graph. Добавлен миксин BaseIgnoreLogMixin.

### Изменено

- [EDUSCHL-20274](https://jira.bars.group/browse/EDUSCHL-20274)
  MINOR Рефакторинг принудительного запуска функций без добавления их в очередь на исполнение.


## [0.10.1] - 2024-02-02

Изменение в формировании LogChange.
Не формируется LogChange с пустым fields.

### Изменено

- [EDUSCHL-21251](https://jira.bars.group/browse/EDUSCHL-21251)
  PATCH Изменение в формировании LogChange.


## [0.10.0] - 2024-01-19

Добавлена поддержка Django 3.0.
В класс кеша BaseCollectingExportedDataFunctionCacheStorage расчетных и не расчетных функций добавлен метод _ignore_logs.
Добавлена утилита build_related_model_graph для построения графа связей между моделями. 
Добавлен миксин BaseIgnoreLogMixin, для исключения из обработки логов на основании описанных зависимостей.

### Добавлено

- [EDUSCHL-18051](https://jira.bars.group/browse/EDUSCHL-18051)
  MINOR Поднять версию Django до 3.0.14
- [EDUSCHL-20550](https://jira.bars.group/browse/EDUSCHL-20550)
  MINOR В класс кеша BaseCollectingExportedDataFunctionCacheStorage добавлен метод _ignore_logs. 
  Добавлена утилита build_related_model_graph. Добавлен миксин BaseIgnoreLogMixin.


## [0.9.2] - 2024-01-17

Добавлена явная регистрация периодических асинхронных задач Celery.
Поднятие версии зависимостей пакета celery.

### Изменено

- [EDUSCHL-14950](https://jira.bars.group/browse/EDUSCHL-14950)
  PATCH Добавлена явная регистрация периодических асинхронных задач Celery.


## [0.9.1] - 2024-01-11

Добавлен реестр выбора сущностей для сбора и выгрузки данных.
Удалена настройка RDM_TRANSFER_TASK_ENTITIES, вместо перечисления сущностей в конфиге используется реестр и модель
  TransferredEntity.

### Добавлено

- [EDUSCHL-21112](https://jira.bars.group/browse/EDUSCHL-21112)
  MINOR Добавлен реестр выбора сущностей для сбора и выгрузки данных.

### Удалено

- [EDUSCHL-21112](https://jira.bars.group/browse/EDUSCHL-21112)
  MINOR Удалена настройка RDM_TRANSFER_TASK_ENTITIES.


## [0.9.0] - 2023-12-29

Из ЭШ перенесены периодические задачи по сбору статусов загрузки файлов в витрину, а также
по поиску зависших этапов/подэтапов экспорта.

Также из ЭШ перенесены менедж-команды: 
- check_upload_status - проверка состояния отправленных данных в витрину,
- collect_lastest_models_data - сбор на основе логов за период с последней сборки до указанной даты,
- export_latest_entities_data - экспорт данных за период с последней сборки до указанной даты.

Типы получаемых из log_change.fields полей соответствуют типам полей из логируемых моделей.  

### Добавлено

- [EDUSCHL-21013](https://jira.bars.group/browse/EDUSCHL-21013)
  MINOR Перенесена часть асинхронных РВД задач из ЭШ, а также часть менедж-команд

### Изменено

- [EDUSCHL-20793](https://jira.bars.group/browse/EDUSCHL-20793)
  MINOR Типы получаемых из log_change.fields полей должны соответствовать типам полей из логируемых моделей


## [0.8.6] - 2023-12-18

В метод _clean_data класса BaseCollectingFunctionTestCase добавлена возможность обрабатывать поля относящиеся к 
  списковому типу (ArrayField).

### Добавлено

- [EDUSCHL-19606](https://jira.bars.group/browse/EDUSCHL-19606)
  PATCH В метод _clean_data класса BaseCollectingFunctionTestCase добавлена возможность обрабатывать поля относящиеся к 
  списковому типу (ArrayField).


## [0.8.5] - 2023-12-14

Формирование логов вынесено на уровень команды, а не менеджера.
Добавлено формирование логов на этапе экспорта данных.

### Добавлено

- [EDUSCHL-20073](https://jira.bars.group/browse/EDUSCHL-20073)
  MINOR Логи при экспорте данных

### Изменено

- [EDUSCHL-20073](https://jira.bars.group/browse/EDUSCHL-20073)
  MINOR Формирование логов вынесено на уровень команды, а не менеджера.


## [0.8.4] - 2023-12-13

Создание базовых хэлперов BaseCollectingDataFunctionHelper, BaseCollectingDataRunnerHelper.
Создание нового метода get_filtered_operations в BaseCollectingDataFunctionHelper.

### Добавлено

- [EDUSCHL-21029](https://jira.bars.group/browse/EDUSCHL-21029)
  MINOR Создание базовых хэлперов.

## [0.8.3] - 2023-12-13

Исправление ошибок и несоответствий в журнале логов

### Изменено

- [EDUCLLG-8103](https://jira.bars.group/browse/EDUCLLG-8103)
  MINOR Исправление ошибок и несоответствий в журнале логов .

## [0.8.2] - 2023-12-11

Поднятие версии m3-db-utils,изменение UploaderClientLogManager
### Изменено

- [EDUCLLG-7736](https://jira.bars.group/browse/EDUCLLG-7736)
  MINOR Поднята версии m3-db-utils до 0.3.10, редактирован `UploaderClientLogManager`.

## [0.8.1] - 2023-12-08

Исправлена ошибка внутри EntityEnumRegisterMixin
### Изменено

- [EDUCLLG-8098](https://jira.bars.group/browse/EDUCLLG-8098)
  PATCH Добавлена проверка на наличие атрибута main_model_enum.

## [0.8.0] - 2023-12-08

Вынесен функционал просмотра логов РВД из ЭШ.
Удалено перечисление UploadStatusEnum.
Удалена модель UploadStatus статусов загрузки в витрину. Вместо неё добавлена модель-перечисление DataMartRequestStatus.

### Изменено

- [EDUCLLG-7736](https://jira.bars.group/browse/EDUCLLG-7736)
  MINOR Вынесен функционал просмотра логов РВД из ЭШ.

### Удалено

- [EDUSCHL-20965](https://jira.bars.group/browse/EDUSCHL-20965)
  MINOR - Удалено перечисление UploadStatusEnum. Удалена модель UploadStatus статусов загрузки в витрину.

### Добавлено

- [EDUSCHL-20965](https://jira.bars.group/browse/EDUSCHL-20965)
  MINOR - Вместо удаленной модели UploadStatus добавлена модель-перечисление DataMartRequestStatus.


## [0.7.3] - 2023-12-07

Исправлена аннотация в шаблоне managers.py-tpl для функции экспорта.

### Исправлено

- [EDUSCHL-19604](https://jira.bars.group/browse/EDUSCHL-19604)
  PATCH Исправлена аннотация в шаблоне managers.py-tpl для функции экспорта.


## [0.7.2] - 2023-12-05

В метод _clean_data класса BaseCollectingFunctionTestCase добавлена возможность обрабатывать поля относящиеся к 
  временному типу.
Добавление обработки plugins_info при генерации списка данных формирования команд.

### Добавлено

- [EDUSCHL-19507](https://jira.bars.group/browse/EDUSCHL-19507)
  PATCH В метод _clean_data класса BaseCollectingFunctionTestCase добавлена возможность обрабатывать поля относящиеся к 
  временному типу. 
- [EDUSCHL-19507](https://jira.bars.group/browse/EDUSCHL-19507)
  PATCH Добавление обработки plugins_info при генерации списка данных формирования команд.


## [0.7.1] - 2023-12-02

Доработано получение множества моделей на основе данных plugins_info при работе метода _get_loggable_models.

### Изменено

- [EDUSCHL-19576](https://jira.bars.group/browse/EDUSCHL-20954)
  PATCH Доработано получение множества моделей на основе данных plugins_info при работе метода _get_loggable_models.


## [0.7.0] - 2023-12-02

Добавлено формирование логов для последующего скачивания. 
Доработаны шаблоны реализации Функций сбора и выгрузки данных.
Написана документация для реализации функционала новой Сущности.
Добавлено получение моделей на основе данных plugins_info при работе метода _get_loggable_models.

### Добавлено

- [EDUSCHL-20072](https://jira.bars.group/browse/EDUSCHL-20072)
  MINOR - Реестр сбора и выгрузки. Логи

- [EDUSCHL-20954](https://jira.bars.group/browse/EDUSCHL-20954)
  PATCH Добавлена документация для реализации функционала новой Сущности.

### Изменено

- [EDUSCHL-20954](https://jira.bars.group/browse/EDUSCHL-20954)
  PATCH Произведена доработка шаблонов Функций сбора и выгрузки данных.

- [EDUSCHL-19576](https://jira.bars.group/browse/EDUSCHL-19576)
  PATCH - Добавлено получение моделей на основе данных plugins_info при работе метода _get_loggable_models.


## [0.6.10] - 2023-11-30

При добавлении префикса RDM_EXPORT_ENTITY_ID_PREFIX в классе BaseExportDataFunctionHelper 
учтены поля из get_ignore_prefix_key_fields.

### Изменено

- [EDUSCHL-20961](https://jira.bars.group/browse/EDUSCHL-20961)
  PATCH - При добавлении префикса RDM_EXPORT_ENTITY_ID_PREFIX в классе BaseExportDataFunctionHelper учтены поля 
        - из get_ignore_prefix_key_fields.


## [0.6.9] - 2023-11-30

Доработка обработки ответа при отправке файлов в РВД.
Добавлены менедж-команды для загрузки данных и запроса статуса загрузки в РВД с использованием uploader-client.
Добавлена инструкция по реализации тестов РВД.
В BaseCollectingFunctionTestCase добавлен метод создания подэтапов сбора данных.

### Добавлено

- [EDUSCHL-20946](https://jira.bars.group/browse/EDUSCHL-20946)
  PATCH - Доработка обработки ответа при отправке файлов в РВД.

- [EDUSCHL-20946](https://jira.bars.group/browse/EDUSCHL-20946)
  MINOR - Добавлены менедж-команды для загрузки данных и запроса статуса загрузки в РВД с использованием uploader-client.

- [EDUSCHL-20951](https://jira.bars.group/browse/EDUSCHL-20951)
  MINOR - Инструкция по реализации тестов РВД

- [EDUSCHL-20951](https://jira.bars.group/browse/EDUSCHL-20951)
  MINOR - Добавлен метод создания подэтапов сбора данных


## [0.6.8] - 2023-11-24

Скорректировано описание сущности РВД TELECOM.
Рефакторинг обновления полей modified у невыгруженных записей при работе экспорта сущностей.
Временное решение обеспечения совместимости регистрации моделей и сущностей старого и нового подхода.
Добавлена возможность отправки запросов в РВД через Proxy API uploader_client.
Изменено формирование логов для последующей обработки.

### Добавлено

- [EDUSCHL-20854](https://jira.bars.group/browse/EDUSCHL-20854)
  MINOR - Добавлена возможность отправки запросов через Proxy API.

### Изменено

- [EDUSCHL-20808](https://jira.bars.group/browse/EDUSCHL-20808)
  MINOR - При сборе модели командой collect_latest_models_data сжигается память

### Исправлено

- [EDUSCHL-20884](https://jira.bars.group/browse/EDUSCHL-20884)
  PATCH - Изменено название поля rank на rank_contact в сущности РВД TelecomEntity.

- [EDUSCHL-20711](https://jira.bars.group/browse/EDUSCHL-20711)
  PATCH - Доработан метод BaseExportLatestEntitiesData._update_model_modified_field.

- [EDUSCHL-20858](https://jira.bars.group/browse/EDUSCHL-20858)
  PATCH - Временное решение обеспечения совместимости регистрации моделей и сущностей старого и нового подхода.


## [0.6.7] - 2023-11-01

Добавлен миксин EntityEnumRegisterMixin для регистрации сущностей в RegionalDataMartEntityEnum.
Миксин ModelEnumRegisterMixin для регистрации моделей в RegionalDataMartModelEnum.
Добавлены методы для запуска регистрации моделей и сущностей.

### Добавлено

- [EDUCLLG-7632](https://jira.bars.group/browse/EDUCLLG-7632)
  PATCH - Добавлен функционал регистрации моделей и сущностей в моделях-перечислениях.


## [0.6.6] - 2023-10-16

Добавлен базовый класс для тестирования Функций сбора, добавлена явная зависимость Django.

### Добавлено

- [EDUSCHL-20684](https://jira.bars.group/browse/EDUSCHL-20684)
  PATCH - Базовый класс для тестирования Функций сбора;
- [EDUSCHL-20684](https://jira.bars.group/browse/EDUSCHL-20684)
  PATCH - Добавлена зависимость Django.


## [0.6.5] - 2023-10-11

Получение метода генерации логов вынесено в отдельный метод для избавления от необходимости хранить все методы в одном классе.

### Исправлено

- [EDUCLLG-7634](https://jira.bars.group/browse/EDUCLLG-7634)
  PATCH - Получение метода генерации логов вынесено в отдельный метод для избавления от необходимости хранить все методы в одном классе;

- [EDUSCHL-20571](https://jira.bars.group/browse/EDUSCHL-20571)
  PATCH - При сборе актуальных данных моделей отслеживаются уже запущенные сборы и новый сбор по модели не запускается.

- [EDUSCHL-20571](https://jira.bars.group/browse/EDUSCHL-20571)
  PATCH - Указание назначения полей модели-перечисления сущностей RegionalDataMartEntityEnum;

- [EDUSCHL-20571](https://jira.bars.group/browse/EDUSCHL-20571)
  PATCH - Добавление возможности получения значений модели-перечисления RegionalDataMartEntityEnum моделей РВД для указанных сущностей.


## [0.6.4] - 2023-10-09

Исправлена ошибка сборки, из-за которой файлы шаблонов *.py-tpl не попадали в пакет.

### Добавлено

- [EDUCLLG-7634](https://jira.bars.group/browse/EDUCLLG-7634)
  PATCH - Добавлено включение шаблонов *.py-tpl в пакет при сборке.


## [0.6.3] - 2023-10-05

Доработка модели AbstractCollectDataCommandProgress и класса BaseFirstCollectModelsDataCommandsGenerator.

### Добавлено

- [EDUSCHL-20350](https://jira.bars.group/browse/EDUSCHL-20350)
  PATCH - Добавлено формирование id генерации для команд в классе BaseFirstCollectModelsDataCommandsGenerator.
        - Добавлены поля created, generation_id и institute_ids в модель AbstractCollectDataCommandProgress.


## [0.6.2] - 2023-10-04

### Изменено

- [EDUCLLG-7942](https://jira.bars.group/browse/EDUCLLG-7942)
  PATCH Доработка сборки документации.


## [0.6.1] - 2023-10-02

Дополнение поведения BaseExportDataFunctionHelper.

### Изменено

- [EDUSCHL-20535](https://jira.bars.group/browse/EDUSCHL-20535)
  PATCH - В логике BaseExportDataFunctionHelper добавлена очистка строковых полей от управляющих символов.


## [0.6.0] - 2023-09-29

Добавлена функция set_failed_status_suspended_exporting_data_stages для определения и перевода зависших этапов/подэтапов экспорта в статус (FAILED).
Добавлена функция set_failed_status_suspended_collecting_data_stages для определения и перевода зависших этапов/подэтапов сбора в статус (FAILED).

### Добавлено

- [EDUSCHL-20487](https://jira.bars.group/browse/EDUSCHL-20487)
  MINOR Добавлена функция ```set_failed_status_suspended_exporting_data_stages```.

- [EDUSCHL-20487](https://jira.bars.group/browse/EDUSCHL-20487)
  MINOR Добавлена функция ```set_failed_status_suspended_collecting_data_stages```.

## [0.5.9] - 2023-09-25

Повышена версия wheel

### Изменено

- [EDUCLLG-7939](https://jira.bars.group/browse/EDUCLLG-7939)
  PATCH - Повышена версия wheel

## [0.5.8] - 2023-09-13

Исправлена ошибка добавления в описание асинхронной задачи списка выгруженных сущностей
BaseExportLatestEntitiesData._set_description_to_async_task.

### Исправлено

- [EDUSCHL-20334](https://jira.bars.group/browse/EDUSCHL-20334)
  PATCH - Баг с обновлением поля description в BaseExportLatestEntitiesData._set_description_to_async_task.

## [0.5.7] - 2023-09-12

Баг фикс и дополнение поведения BaseExportLatestEntitiesData.

### Изменено

- [EDUSCHL-20435](https://jira.bars.group/browse/EDUSCHL-20435)
  PATCH - BaseExportLatestEntitiesData теперь поддерживает выгрузку ни разу невыгруженных сущностей.

### Исправлено

- [EDUSCHL-20435](https://jira.bars.group/browse/EDUSCHL-20435)
  PATCH - Баг с условием в фильтре в BaseExportLatestEntitiesData._update_model_modified_field.


## [0.5.6] - 2023-09-06

Доработаны классы BaseExportLatestEntitiesData и BaseExportEntitiesData.

### Исправлено

- [EDUSCHL-20435](https://jira.bars.group/browse/EDUSCHL-20435)
  PATCH - Исправлено нахождение левой границы в классе ExportLatestEntitiesData;
        - Добавлена проверка на наличие запущенных или готовых к выгрузке сущностей;
        - Добавлен параметр update_modified, который обновляет поле modified у собранных моделей,
          чтобы выгрузить невыгруженные записи.


## [0.5.5] - 2023-09-04

Добавление pip в зависимости сборки пакета.

### Добавлено

- [EDUSCHL-19919](https://jira.bars.group/browse/EDUSCHL-19919)
  PATCH Добавление pip в зависимости сборки пакета.


## [0.5.4] - 2023-09-04

split_by_days_count переименовал в split_by_quantity.

### Изменено

- [EDUSCHL-20302](https://jira.bars.group/browse/EDUSCHL-20302)
  PATCH split_by_days_count переименовал в split_by_quantity.


## [0.5.3] - 2023-09-03

Изменены параметры формирования подпериодов в generate_first_collect_models_data_script.

### Изменено

- [EDUSCHL-20302](https://jira.bars.group/browse/EDUSCHL-20302)
  PATCH Изменены параметры формирования подпериодов в generate_first_collect_models_data_script.


## [0.5.2] - 2023-08-28

Замена базового класса функций.

### Изменено

- [EDUSCHL-20344](https://jira.bars.group/browse/EDUSCHL-20344)
  PATCH Замена базового класса функций на WebEduLazySavingPredefinedQueueFunction.


## [0.5.1] - 2023-08-22

Для BaseFirstCollectModelsDataCommandsGenerator добавлено условие - если не заполнен creating_trigger_models,
то словарь с данными для команды не передается.

### Исправлено

- [EDUSCHL-20227](https://jira.bars.group/browse/EDUSCHL-20227)
  PATCH Если у сущности не заполнен creating_trigger_models, то в генераторе BaseFirstCollectModelsDataCommandsGenerator
  не формируется словарь с параметрами для команды.

- [EDUSCHL-20229](https://jira.bars.group/browse/EDUSCHL-20229)
  PATCH Если у сущности не заполнен creating_trigger_models, то в генераторе BaseFirstCollectModelsDataCommandsGenerator
  не формируется словарь с параметрами для команды.


## [0.5.0] - 2023-08-19

Дополнительная функциональность WebEduEntityValueCache была перенесена в EntityCache в function_tools.

### Удалено

- [EDUSCHL-20277](https://jira.bars.group/browse/EDUSCHL-20277)
  MINOR Удален WebEduEntityValueCache.

- [EDUSCHL-20277](https://jira.bars.group/browse/EDUSCHL-20277)
  MINOR Удален WebEduEntityCacheExtended.


## [0.4.7] - 2023-08-17

Изменено формирование очередности сбора/экспорта моделей/сущностей. Вместо отдельных перечислений используется существующее поле `order_number` модели-перечисления `TitledModelEnum`. В случае, когда `order_number` не указан, т.е. будет использоваться значение по умолчанию `DEFAULT_ORDER_NUMBER`, модель/сущность будет исключена из сбора/экспорта.

### Изменено

- [EDUSCHL-19164](https://jira.bars.group/browse/EDUSCHL-19164)
  MINOR Изменено формирование очередности сбора/экспорта моделей/сущностей.

## [0.4.6] - 2023-08-16

Удален лишний вызов метода _prepare_logs

### Исправлено

- [EDUSCHL-19991](https://jira.bars.group/browse/EDUSCHL-19991)
  PATCH удален лишний вызов метода ```_prepare_logs``` в методе  ```__init__``` класса ```BaseCollectingCalculatedExportedDataFunctionCacheStorage```

## [0.4.5] - 2023-08-09

Объединение обрабатываемых логов относящихся к одному объекту

### Добавлено

- [EDUSCHL-19991](https://jira.bars.group/browse/EDUSCHL-19991)
 PATCH Новый миксин ```ReformatLogsMixin``` , новое поле is_merge_logs и новый метод _merge_logs у класса ```BaseCollectingExportedDataFunctionCacheStorage```

## [0.4.4] - 2023-08-12

Исправлен баг с timedelta

### Исправлено

- [EDUSCHL-20200](https://jira.bars.group/browse/EDUSCHL-20200)
  PATCH Исправлен баг с timedelta.

## [0.4.3] - 2023-08-12

Исправлен баг с timedelta

### Исправлено

- [EDUSCHL-20200](https://jira.bars.group/browse/EDUSCHL-20200)
  PATCH Исправлен баг с timedelta.

## [0.4.2] - 2023-08-11

Исправление ошибки учета миллисекунд, при генерации скриптов сбора и выгрузки данных. В текущий момент chunk_size все
равно работает некорректно. Это связано с тем, что при обнулении миллисекунд за одной записью выборки может скрываться
большое количество, например, которые были созданы или обновлены скриптами. Проблему необходимо решить в будущем, но
текущего решения хватает для эксплуатации.
В выборках моделей и логов не должна входить правая граница периода выборки.

### Исправлено

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH Исправлена ошибка учета миллисекунд в выборках при генерации скриптов с командами для сбора и выгрузки данных.

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH В выборках моделей и логов не должна входить правая граница периода выборки.

## [0.4.1] - 2023-08-09

Доработки для реализации принудительного выполнения функций экспорта данных сущностей.

### Добавлено

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH Доработки для реализации принудительного выполнения функций экспорта данных сущностей.

## [0.4.0] - 2023-08-09

Реализованы общие классы для команд сбора/экспорта.

### Добавлено

- [EDUSCHL-20200](https://jira.bars.group/browse/EDUSCHL-20200)
  MINOR Добавлены общие модели, методы и классы.

### Изменено

- [EDUSCHL-20200](https://jira.bars.group/browse/EDUSCHL-20200)
  MINOR Реализованы общие классы для команд сбора/экспорта.

## [0.3.3] - 2023-08-08

Добавлено принудительное выполнение функций в ранере для экономии памяти.

### Исправлено

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH Добавлено принудительное выполнение функций в ранере для экономии памяти.

## [0.3.2] - 2023-08-08

Откат к спискам необработанных логов. Исправлена ошибка бесконечного создания чанков логов.

### Исправлено

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH Откат к спискам необработанных логов.

## [0.3.1] - 2023-08-08

Организована передача необработанных логов в виде генератора.

### Изменено

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH Организована передача необработанных логов в виде генератора.

## [0.3.0] - 2023-08-06

Добавление функциональности для отложенного заполнения кешей. Заполнение производится перед началом работы запускаемого
объекта.

### Добавлено

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH Добавлено отложенное заполнение кешей хелперов функций.

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  MINOR Добавлено проставление подэтапа выгрузки данных у записей моделей.

## [0.2.2] - 2023-08-06

Для API РВД добавлена поддержка параметра типа операции для загрузки данных.

### Добавлено

- [EDUSCHL-19920](https://jira.bars.group/browse/EDUSCHL-19920)
  PATCH Для API РВД добавлена поддержка параметра типа операции для загрузки данных.

## [0.2.1] - 2023-08-05

Восстановление сборки пакета после ухода с poetry.

### Исправлено

- [EDUSCHL-19919](https://jira.bars.group/browse/EDUSCHL-19919)
  PATCH Восстановление сборки пакета после миграции с poetry.

## [0.2.0] - 2023-08-04

Перенос стратегий формирования Функций используемых в генерации исходников.

### Добавлено

- [EDUSCHL-19919](https://jira.bars.group/browse/EDUSCHL-19919)
  MINOR Перенесены стратегии создания Функций из ЭШ.

## [0.1.4] - 2023-08-03

Возвращение ранее удаленных зависимостей миграции

### Изменено

- [EDUSCHL-20209](https://jira.bars.group/browse/EDUSCHL-20209)
  PATCH Возвращение зависимостей миграции.

- [EDUSCHL-20209](https://jira.bars.group/browse/EDUSCHL-20209)
  PATCH Доработки по формированию документации.

- [EDUSCHL-20200](https://jira.bars.group/browse/EDUSCHL-20200)
  Закреплены версии зависимостей, добавлена ссылка на uploader-client

## [0.1.3] - 2023-07-24

Для раскатки миграций на ЭШ, пришлось закомментировать зависимости в initial-миграции.

### Изменено

- [EDUSCHL-19919](https://jira.bars.group/browse/EDUSCHL-19919)
  PATCH Вынести общую часть для работы с РВД из ЭШ для использования в ЭК.

## [0.1.2] - 2023-07-23

Внесены изменения в кодовую базу после переноса механизма логирования из ЭШ в educommon.

### Изменено

- [EDUSCHL-19919](https://jira.bars.group/browse/EDUSCHL-19919)
  PATCH Вынести общую часть для работы с РВД из ЭШ для использования в ЭК.

## [0.1.0] - 2023-07-18

Внесены изменения в кодовую базу после переноса механизма логирования из ЭШ в educommon.

### Добавлено

- [EDUSCHL-19919](https://jira.bars.group/browse/EDUSCHL-19919)
  MINOR Перенос базовых компонентов интеграции с РВД из ЭШ.
