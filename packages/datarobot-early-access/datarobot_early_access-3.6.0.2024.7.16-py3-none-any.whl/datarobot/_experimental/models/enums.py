#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
from __future__ import annotations

from typing import List

from strenum import StrEnum

# pylint: disable=unused-import
from datarobot.enums import (  # noqa: F401
    ListChatsSortQueryParams,
    ListComparisonChatsSortQueryParams,
    ListCustomModelValidationsSortQueryParams,
    ListLLMBlueprintsSortQueryParams,
    ListPlaygroundsSortQueryParams,
    ListVectorDatabasesSortQueryParams,
    PromptType,
    VectorDatabaseChunkingParameterType,
    VectorDatabaseDatasetLanguages,
    VectorDatabaseEmbeddingModel,
    VectorDatabaseExecutionStatus,
    VectorDatabaseSource,
)

# pylint: enable=unused-import


class VectorDatabaseChunkingMethod(StrEnum):
    """Text chunking method names for VectorDatabases."""

    RECURSIVE = "recursive"
    SEMANTIC = "semantic"


class AllEnumMixin:
    @classmethod
    def all(cls) -> List[str]:
        return [member.value for _, member in cls.__members__.items()]


class NotebookType(AllEnumMixin, StrEnum):
    STANDALONE = "plain"
    CODESPACE = "codespace"


class RunType(StrEnum):
    SCHEDULED = "scheduled"
    MANUAL = "manual"


class ScheduledRunStatus(StrEnum):
    """Possible statuses for scheduled notebook runs."""

    BLOCKED = "BLOCKED"
    CREATED = "CREATED"
    STARTED = "STARTED"
    EXPIRED = "EXPIRED"
    ABORTED = "ABORTED"
    INCOMPLETE = "INCOMPLETE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    INITIALIZED = "INITIALIZED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    COMPLETED_WITH_ERRORS = "COMPLETED_WITH_ERRORS"

    @classmethod
    def terminal_statuses(cls) -> List[str]:
        return [
            cls.ABORTED,
            cls.COMPLETED,
            cls.ERROR,
            cls.COMPLETED_WITH_ERRORS,
        ]


class NotebookPermissions(StrEnum):
    CAN_READ = "CAN_READ"
    CAN_UPDATE = "CAN_UPDATE"
    CAN_DELETE = "CAN_DELETE"
    CAN_SHARE = "CAN_SHARE"
    CAN_COPY = "CAN_COPY"
    CAN_EXECUTE = "CAN_EXECUTE"


class NotebookStatus(StrEnum):
    STOPPING = "stopping"
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    RESTARTING = "restarting"
    DEAD = "dead"
    DELETED = "deleted"


class CategoricalStatsMethods(StrEnum):
    MOST_FREQUENT = "most-frequent"


class NumericStatsMethods(StrEnum):
    MAX = "max"
    MIN = "min"
    AVG = "avg"
    STDDEV = "stddev"
    MEDIAN = "median"


class DataWranglingDialect(StrEnum):
    SNOWFLAKE = "snowflake"
    POSTGRES = "postgres"


class RecipeInputType(StrEnum):
    DATASOURCE = "datasource"


class DatetimeSamplingStrategy(StrEnum):
    EARLIEST = "earliest"
    LATEST = "latest"


class WranglingOperations(StrEnum):
    """Supported data wrangling operations."""

    COMPUTE_NEW = "compute-new"
    DROP_COLUMNS = "drop-columns"
    RENAME_COLUMNS = "rename-columns"
    FILTER = "filter"

    LAGS = "lags"
    WINDOW_CATEGORICAL_STATS = "window-categorical-stats"
    WINDOW_NUMERIC_STATS = "window-numeric-stats"
    TIME_SERIES = "time-series"


class SamplingOperations(StrEnum):
    """Supported data wrangling sampling operations."""

    RANDOM_SAMPLE = "random-sample"
    DATETIME_SAMPLE = "datetime-sample"


class DownsamplingOperations(StrEnum):
    """Supported data wrangling sampling operations."""

    RANDOM_SAMPLE = "random-sample"
    SMART_DOWNSAMPLING = "smart-downsampling"


class DataWranglingDataSourceTypes(StrEnum):
    JDBC = "jdbc"


class FilterOperationFunctions(StrEnum):
    """Operations, supported in FilterOperation."""

    EQUALS = "eq"
    NOT_EQUALS = "neq"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUALS = "lte"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUALS = "gte"
    IS_NULL = "null"
    IS_NOT_NULL = "notnull"
    BETWEEN = "between"
    CONTAINS = "contains"


class IncrementalLearningStatus(object):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    STOPPED = "stopped"
    ERROR = "error"

    ALL = [STARTED, IN_PROGRESS, COMPLETED, STOPPED, ERROR]


class IncrementalLearningItemStatus(object):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"

    ALL = [IN_PROGRESS, COMPLETED, ERROR]


class StorageType(StrEnum):
    """Supported data storages."""

    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    DATABRICKS = "databricks"
    AI_CATALOG = "aicatalog"
    DATASTAGE = "datastage"


class OriginStorageType(StrEnum):
    """Supported data sources."""

    SNOWFLAKE = StorageType.SNOWFLAKE
    BIGQUERY = StorageType.BIGQUERY
    DATABRICKS = StorageType.DATABRICKS
    AI_CATALOG = StorageType.AI_CATALOG


class ChunkingType(StrEnum):
    """Supported chunking types."""

    INCREMENTAL_LEARNING = "incrementalLearning"
    INCREMENTAL_LEARNING_OTV = "incrementalLearningOtv"
    SLICED_OFFSET_LIMIT = "slicedOffsetLimit"


class ChunkStorageType(StrEnum):
    """Supported chunk storage."""

    DATASTAGE = StorageType.DATASTAGE
    AI_CATALOG = StorageType.AI_CATALOG


class FeedbackSentiment(StrEnum):
    POSITIVE = "1"
    NEGATIVE = "0"


class GuardConditionComparator(StrEnum):
    """The comparator used in a guard condition."""

    GREATER_THAN = "greaterThan"
    LESS_THAN = "lessThan"
    EQUALS = "equals"
    NOT_EQUALS = "notEquals"
    IS = "is"
    IS_NOT = "isNot"
    MATCHES = "matches"
    DOES_NOT_MATCH = "doesNotMatch"
    CONTAINS = "contains"
    DOES_NOT_CONTAIN = "doesNotContain"


class AggregationType(StrEnum):
    """The type of the metric aggregation."""

    AVERAGE = "average"
    BINARY_PERCENTAGE = "percentYes"
    MULTICLASS_PERCENTAGE = "classPercentCoverage"
    NGRAM_IMPORTANCE = "ngramImportance"
    GUARD_CONDITION_PERCENTAGE = "guardConditionPercentYes"


class GuardType(StrEnum):
    """The type of the guard configuration used for moderation in production."""

    MODEL = "guardModel"
    NEMO = "nemo"  # NVidia NeMo
    OOTB = "ootb"  # 'Out of the box' metric, little or no configuration
    PII = "pii"
    USER_MODEL = "userModel"  # user-defined columns and target type


class VectorDatabaseRetrievers(StrEnum):
    """Vector database retriever names."""

    SINGLE_LOOKUP_RETRIEVER = "SINGLE_LOOKUP_RETRIEVER"
    CONVERSATIONAL_RETRIEVER = "CONVERSATIONAL_RETRIEVER"
    MULTI_STEP_RETRIEVER = "MULTI_STEP_RETRIEVER"
