from enum import Enum


class TaskType(str, Enum):
    """Enum for task types"""

    CLASSIFICATION = "classification"
    MULTILABEL_CLASSIFICATION = "multilabel_classification"
    ATTRIBUTE_EXTRACTION = "attribute_extraction"


class FilterType(str, Enum):
    """Enum types for filters"""

    METADATA = "metadata"
    LABEL = "label"
    SIMILAR = "similar"


class FilterValueType(str, Enum):
    CONST = "string"
    METADATA = "metadata"
    LABEL = "label"


class OrderByDirectionType(str, Enum):
    ASC = "ASC"
    DESC = "DESC"
