# Type alias for types that can be used to construct a NumericTypeHandle
# NOTE: "Type" is included because numpy dtypes are subclasses of "Type"
import re
from enum import Enum, auto
from typing import Optional, Type

import numpy as np
import torch

NumericTypeAlternative = np.dtype | Type | str


class NumericType(str, Enum):
    """Represents a specific numeric type, e.g., `int32` or `float64`."""

    int8 = auto()
    int16 = auto()
    int32 = auto()
    int64 = auto()

    uint8 = auto()
    uint16 = auto()
    uint32 = auto()
    uint64 = auto()

    float16 = auto()
    float32 = auto()
    float64 = auto()

    bfloat16 = auto()

    @classmethod
    def from_type(cls, value: NumericTypeAlternative) -> "NumericType":
        """Returns the corresponding numeric type from a string, pytorch dtype, or torch dtype."""
        if isinstance(value, str):
            value = value.lower()
            if value not in cls.__members__:
                raise ValueError(f"Invalid type: {value}")
            return cls[value]
        elif isinstance(value, type):
            match = re.match(r"<class 'numpy\.(\w+)'>", str(value))
            if not match:
                raise ValueError(f"Invalid type: {value}. Must be a numpy type, e.g. np.float32.")
            return cls[match.group(1)]
        elif isinstance(value, torch.dtype):
            split = str(value).split(".")
            assert len(split) == 2, f"Invalid type: {value}"
            assert split[0] == "torch", f"Invalid type: {value}"
            return cls[split[1]]

        raise ValueError(f"Invalid type: {value}")

    @property
    def base_type(self) -> str:
        """Returns the base type, e.g., `int` or `float`."""
        match = re.match(r"([a-zA-z]+)\d+", self.name)
        assert match, f"Invalid numeric type: {self.name}"
        np.int8

        return match.group(1)

    @property
    def bit_width(self) -> int:
        """Returns the bit width of the type, e.g., 32 for `int32`."""
        match = re.match(r"[a-zA-z]+(\d+)", self.name)
        assert match, f"Invalid numeric type: {self.name}"
        return int(match.group(1))

    @property
    def numpy_dtype(self) -> Optional[np.dtype]:
        """Returns the corresponding numpy type, or None if it doesn't exist."""
        return getattr(np, self.name, None)

    @property
    def torch_dtype(self) -> Optional[torch.dtype]:
        """Returns the corresponding torch type, or None if it doesn't exist."""
        return getattr(torch, self.name, None)
