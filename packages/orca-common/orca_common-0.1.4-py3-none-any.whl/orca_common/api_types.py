from enum import Enum
from typing import Any

from typing_extensions import deprecated


class Order(str, Enum):
    """
    Specifies the order of a column in a query.

    Attributes:
        ASC: Ascending order
        DESC: Descending order
        DEFAULT: Use the default order of the column
    """

    ASC = "ASC"
    DESC = "DESC"
    DEFAULT = "DEFAULT"

    # These are just here for backwards compatibility but deprecated.
    # Use Order.ASC and Order.DESC instead since they map to the enum values
    ASCENDING = "ASC"
    DESCENDING = "DESC"


class TableCreateMode(str, Enum):
    """
    Options for create_table if the table already exists

    Attributes:
        ERROR_IF_TABLE_EXISTS: Raise exception if the table exists
        REPLACE_CURR_TABLE: Replace existing table with the same name
        RETURN_CURR_TABLE: Return the existing table when create_table is called
    """

    ERROR_IF_TABLE_EXISTS = "ERROR_IF_TABLE_EXISTS"
    REPLACE_CURR_TABLE = "REPLACE_CURR_TABLE"
    RETURN_CURR_TABLE = "RETURN_CURR_TABLE"


class ImageFormat(str, Enum):
    """
    Image format enum. Used with the Image column type.

    Attributes:
        JPEG: JPEG format
        PNG: PNG format
        TIFF: TIFF format
        GIF: GIF format
        BMP: BMP format
    """

    JPEG = "JPEG"
    PNG = "PNG"
    TIFF = "TIFF"
    GIF = "GIF"
    BMP = "BMP"


class OperationEnum(str, Enum):
    NOT = "$!"
    AND = "$&"
    OR = "$|"
    GREATER_THAN = "$GT"
    LESS_THAN = "$LT"
    GREATER_THAN_OR_EQUAL = "$GTE"
    LESS_THAN_OR_EQUAL = "$LTE"
    EQUAL = "$EQ"
    NOT_EQUAL = "$NEQ"
    LIKE = "$LIKE"
    NOT_LIKE = "$NLIKE"


class CatchupStatus(str, Enum):
    """
    Index status enum. Used to check the status of a catchup operation.

    Attributes:
        IN_PROGRESS: Index is still catching up
        COMPLETED: Index has caught up
        FAILED: Catchup operation failed
        CANCELLED: Catchup operation was cancelled
        CANCELLING: Catchup operation is in the process of being cancelled
    """

    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    CANCELLING = "CANCELLING"


ColumnName = str
"""Column name type alias"""
TableName = str
"""Table name type alias"""
RowDict = dict[ColumnName, Any]
"""Row dictionary type alias"""

OrderByColumns = ColumnName | tuple[ColumnName, Order] | list[ColumnName | tuple[ColumnName, Order]]
