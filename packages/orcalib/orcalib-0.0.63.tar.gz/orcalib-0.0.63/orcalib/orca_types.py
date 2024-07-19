"""
This module defines the types of columns that can be used to declare tables in the Orca database.

Examples:
    >>> TextT
    text

    >>> DocumentT.notnull
    document NOT NULL

    >>> IntT.unique
    int32 UNIQUE

    >>> VectorT[768]
    vector[768]

    >>> ImageT["PNG"]
    image[PNG]

    >>> class Sentiment(Enum):
    ...     neg = 0
    ...     pos = 1
    >>> EnumT[Sentiment]
    enum_as_int[neg=0,pos=1]
"""

import inspect
import io
import re
from abc import ABC, abstractmethod
from collections import abc
from enum import Enum, EnumMeta
from functools import partial
from typing import (
    Any,
    Iterator,
    Optional,
    Protocol,
    Sequence,
    Type,
    TypeVar,
    cast,
    runtime_checkable,
)

import numpy as np
import torch
from PIL import Image as PILImage

from orca_common import ImageFormat, NumericType, NumericTypeAlternative


class OrcaTypeHandle(ABC):
    """Base class for all Orca types. Derived classes represent the types of columns in a table."""

    # --- How to declare new types ---
    # 1. Create a new class that inherits from OrcaTypeHandle
    # 2. Decorate the class with the `@_register_column_type` decorator
    # 3. Implement the `parameters` property to return the type parameters as a list
    # 4. Make sure that the constructor takes the type parameters as arguments in the same order as they are returned by the `parameters` property
    # 5. Make sure the constructor can accept type parameters as `ActualType | str | None` (where `ActualType` is the type of the parameter)
    # 6. Implement the `__getitem__` method to allow type parameters to be specified using the `[]` operator

    # --- How to use the derived classes ---
    # VectorT[768]
    # VectorT[768].notnull
    # VectorT[768].unique
    # VectorT[768].notnull.unique

    # This is updated by the @_register_column_type decorator and manually for numeric types
    _name_to_type: dict[str, Type] = {}  # Maps type names to their corresponding classes

    def __init__(self, t_name: str, notnull: bool = False, unique: bool = False):
        """Initializes the type with the type name and constraints.

        Args:
            t_name: The name of the type, e.g., "vector" or "image"
            notnull: Whether the column must have a value
            unique: Whether the column must have a unique value
        """
        self.t_name = t_name
        self._notnull = notnull
        self._unique = unique

    @classmethod
    def from_string(cls, type_str: str) -> "OrcaTypeHandle":
        """Parses a type string into an OrcaTypeHandle.

        Essentially, you can reconstruct a type after using str(), repr(), or the type's `full_name` property.

        Args:
            type_str: The type string to parse

        Returns:
            An OrcaTypeHandle instance

        Examples:
            >>> OrcaTypeHandle.from_string("vector[128] NOT NULL UNIQUE") == VectorT[128].notnull.unique
            True

            >>> OrcaTypeHandle.from_string("image[PNG] UNIQUE") == ImageT["PNG"].unique
            True
        """

        # This regex has 4 capture groups that match the following for "vector[128] NOT NULL UNIQUE":
        # 1. The type name (e.g., "vector") - required
        # 2. The type parameters (e.g., "128" for a vector) - optional
        # 3. The NOT NULL constraint - optional
        # 4. The UNIQUE constraint - optional
        match = re.match(r"(\w+)(?:\[(.*?)\])?(?:\s(NOT NULL))?(?:\s(UNIQUE))?$", type_str)
        if not match:
            raise ValueError(f"Invalid type string: {type_str}")
        t_name, params, notnull, unique = match.groups()
        notnull = notnull is not None
        unique = unique is not None
        params = params.split(",") if params else []
        if t_name not in cls._name_to_type:
            raise ValueError(f"Unknown type: {t_name}")

        return cls._name_to_type[t_name](*params, notnull=notnull, unique=unique)

    def __eq__(self, other: Any) -> bool:
        """Returns True if the two types are equal, False otherwise.

        Args:
            other: The other type to compare with

        Returns:
            True if the types are equal, False otherwise
        """
        if not isinstance(other, OrcaTypeHandle):
            return False
        return (
            self.t_name == other.t_name
            and self._unique == other._unique
            and self._notnull == other._notnull
            and self.parameters == other.parameters
        )

    def __hash__(self) -> int:
        """
        Generate a hash that is unique to the type, including type parameters and constraints.

        Returns:
            Value of the hash
        """
        return hash((self.t_name, self._unique, self._notnull, *self.parameters))

    def __str__(self) -> str:
        """
        Get the type name, including type parameters and constraints.

        Returns:
            The string representation of the type

        Examples:
            >>> print(VectorT[768].notnull.unique)
            vector[768] NOT NULL UNIQUE

            >>> print(ImageT["PNG"].unique)
            image[PNG] UNIQUE
        """
        return f"{self.full_name}" + (" NOT NULL" if self._notnull else "") + (" UNIQUE" if self._unique else "")

    def __repr__(self) -> str:
        return self.__str__()

    def _clone_with_overrides(self, **kwargs):
        """Returns a copy of this type with the specified overrides.

        Args:
            **kwargs: The overrides to apply

        NOTE: This method should not be called directly. It is used internally.
        """
        cls = type(self)
        args = inspect.signature(cls.__init__).parameters

        def get_arg(arg) -> Any:
            """Returns the value of the argument, or None if it doesn't exist."""
            if arg in kwargs:
                return kwargs[arg]
            elif arg in args:
                if arg == "unique" or arg == "notnull":
                    return getattr(self, "_" + arg)
                # First check for a private field, then a public one
                return getattr(self, arg)
            else:
                return None

        init_args = {arg: get_arg(arg) for arg in args if arg not in ("self", "args", "kwargs")}
        return cls(**init_args)

    @property
    def is_vector(self) -> bool:
        """True if this is a vector type, False otherwise."""
        return False

    @property
    def vector_shape(self) -> None | int | tuple[int, ...]:
        """
        The shape of the vector, or `None` if this is not a vector type.

        Examples:
            >>> VectorT[768].vector_shape
            768

            >>> IntT.vector_shape
            None
        """
        return None

    @property
    def numpy_dtype(self) -> np.dtype | None:
        """Corresponding numpy type, or `None` if it doesn't exist."""
        return object

    @property
    def parameters(self) -> list[Any]:
        """
        The type parameters as a tuple.

        Note:
            These should be in the same order as the parameters in the constructor
        """
        return []  # by default, there are no parameters

    @property
    def notnull(self) -> "OrcaTypeHandle":
        """Set a constraint that the column must have a value."""
        return self._clone_with_overrides(notnull=True)

    @property
    def unique(self) -> "OrcaTypeHandle":
        """Set a constraint that each row in this column must have a unique value."""
        return self._clone_with_overrides(unique=True)

    def _get_param_strings(self) -> Iterator[str]:
        """Iterates through the string representations of the type parameters."""
        if any(param is None for param in self.parameters):
            assert all(
                param is None for param in self.parameters
            ), "Either all parameters must be None or none of them can be None"
            return

        for param in self.parameters:
            if isinstance(param, Enum):
                yield param.name
            else:
                yield str(param)

    @property
    def full_name(self):
        """
        The full name of the type, including type parameters.

        Examples:
            >>> VectorT[768].full_name
            'vector[768]'

            >>> IntT.full_name
            'int32'

            >>> ImageT["PNG"].full_name
            'image[PNG]'
        """
        param_strings = list(self._get_param_strings())
        if len(param_strings) > 0:
            return f"{self.t_name}[{','.join(param_strings)}]"
        else:
            return self.t_name


class NumericTypeHandle(OrcaTypeHandle):
    """
    Represents a numeric column type, such as `integer` or `float` that has
    a specific data type, e.g., `float16` or `int32`.
    """

    def __init__(
        self,
        dtype: NumericType | NumericTypeAlternative,
        length: int | None = None,
        notnull: bool = False,
        unique: bool = False,
    ):
        """
        Initializes the numeric type handle

        Args:
            dtype: The numeric type, e.g., `int32` or `float64`
            length: The length of the vector, or None if this is not a vector type
            notnull: Whether the column must have a value
            unique: Whether the column must have a unique value
        """
        if length is not None and isinstance(length, str):
            try:
                length = int(length)
            except ValueError:
                raise ValueError(f"Invalid length: {length}. Use None, an integer or a int string.")
        if not isinstance(dtype, NumericType):
            try:
                dtype = NumericType.from_type(dtype)
                assert isinstance(dtype, NumericType), f"Invalid dtype: {dtype}"
            except ValueError:
                raise ValueError(f"Invalid dtype: {dtype}. Use a torch/numpy type, a string, or a NumericType.")

        super().__init__(dtype.name, notnull, unique)

        self.dtype = dtype
        self.length = length

    def __getitem__(self, length: int) -> "NumericTypeHandle":
        """Returns a copy of this type with the specified vector length.

        Args:
            length: The length of the vector

        Examples:
            >>> VectorT[768].vector_shape
            768
        """
        return self._clone_with_overrides(length=length)

    @property
    def is_vector(self) -> bool:
        """`True` if this is a vector type, `False` otherwise."""
        return self.length is not None

    @property
    def vector_shape(self) -> None | int | tuple[int, ...]:
        """The shape of the vector, or `None` if this is not a vector type."""
        return self.length

    @property
    def is_scalar(self) -> bool:
        """`True` if this is a scalar type, `False` otherwise."""
        return self.length is None

    @property
    def parameters(self):
        return [self.dtype, self.length]

    @property
    def torch_dtype(self) -> torch.dtype | None:
        """The corresponding torch type, or None if it doesn't exist."""
        return self.dtype.torch_dtype

    @property
    def numpy_dtype(self) -> np.dtype | None:
        """The corresponding numpy type, or None if it doesn't exist."""
        return self.dtype.numpy_dtype

    @property
    def full_name(self) -> str:
        """
        The full name of the type.

        Examples:
            >>> VectorT[768].full_name
            'vector[768]'

            >>> IntT.full_name
            'int32'
        """
        if self.length is None:
            return self.t_name
        return f"{self.t_name}[{self.length}]"


# Add all numeric types to the type dictionary
numeric_type_dict = {name: partial(NumericTypeHandle, dtype) for name, dtype in NumericType.__members__.items()}
# These are added for backwards compatibility
numeric_type_dict.update(
    {
        "integer": partial(NumericTypeHandle, NumericType.int32),
        "float": partial(NumericTypeHandle, NumericType.float32),
        "vector": partial(NumericTypeHandle, NumericType.float64),
    }
)

OrcaTypeHandle._name_to_type.update(numeric_type_dict)


def _register_column_type(type_name: str):
    """
    Decorator for registering a new OrcaTypeHandle

    Note:
        This is required to be able to instantiate the type using OrcaHandle.from_string(...)

    Args:
        type_name: The name of the type, e.g., "vector" or "image"
    """

    def wrapper(cls: Type[OrcaTypeHandle]) -> Type[OrcaTypeHandle]:
        OrcaTypeHandle._name_to_type[type_name] = cls
        return cls

    return wrapper


T = TypeVar("T")


@runtime_checkable
class CustomSerializable(Protocol[T]):
    """Protocol for column types that should be transferred as a file instead of a value."""

    @abstractmethod
    def binary_serialize(self, value: T) -> io.BytesIO:
        """Serializes the value as a binary stream, so we can send it to the server."""
        pass

    @abstractmethod
    def msgpack_deserialize(self, value: dict[str, Any]) -> T:
        """Deserializes the value from a msgpack-compatible dictionary."""
        pass


@_register_column_type("text")
class TextTypeHandle(OrcaTypeHandle):
    """Represents a text column type, such as `text` or `text NOT NULL UNIQUE`."""

    def __init__(self, notnull: bool = False, unique: bool = False):
        """
        Initializes the text type handle

        Args:
            notnull: Whether the column must have a value
            unique: Whether the column must have a unique value
        """
        super().__init__("text", notnull, unique)

    @property
    def numpy_dtype(self) -> np.dtype | None:
        """The corresponding numpy type: [`np.str_`][numpy.str_]"""
        return np.str_


class EnumTypeHandle(OrcaTypeHandle):
    """Represents an enum column type, such as `enum` or `enum NOT NULL UNIQUE`."""

    def __init__(
        self,
        store_as_string: bool = False,
        *args,
        notnull: bool = False,
        unique: bool = False,
        name_to_value: dict[str, int] | None = None,
    ):
        """
        Initializes the enum type handle

        Args:
            store_as_string: Whether the enum values are stored as strings (for modeling purposes you will usually want to store them as integers)
            notnull: Whether the column must have a value
            unique: Whether the column must have a unique value
            name_to_value: A dictionary of name-value pairs for the enum. You can also use the
                [`__getitem__`][orcalib.orca_types.EnumTypeHandle.__getitem__] method to specify the
                values. This is primarily used when cloning the type.
        """
        super().__init__("enum_as_str" if store_as_string else "enum_as_int", notnull, unique)

        def extract_arg(arg_string: str) -> tuple[str, int]:
            name, value = arg_string.split("=")
            return name, int(value)

        assert not (args and name_to_value), "Cannot pass the key values as both *args and name_to_value!"

        # If True, the enum values are stored as strings, otherwise as integers
        self.store_as_string = store_as_string

        if args:
            if not all(isinstance(arg, str) for arg in args):
                raise ValueError("All arguments must be strings of the format 'name=value', e.g., 'foo=1'")
            self.name_to_value = dict(extract_arg(arg) for arg in args)
        else:
            self.name_to_value: dict[str, int] = name_to_value or {}

    def __getitem__(self, *args) -> "EnumTypeHandle":
        """
        Set the enum values for this type.

        Examples:
            >>> class Sentiment(Enum):
            ...     neg = 0
            ...     pos = 1
            >>> EnumT[Sentiment]
            enum_as_int[neg=0,pos=1]

            >>> EnumT["foo", "bar"]
            enum_as_int[foo=0,bar=1]

            >>> EnumT["foo=2", "bar=3"]
            enum_as_int[foo=2,bar=3]

            >>> EnumT["foo=2", "bar"]
            enum_as_int[foo=2,bar=3]

            >>> EnumT[("foo", 1), ("bar", 2)]

            >>> EnumT[{"foo": 1, "bar": 2}]
            enum_as_int[foo=1,bar=2]
        """

        def is_str_int_tuple(value: Any) -> bool:
            return (
                isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], str) and isinstance(value[1], int)
            )

        name_to_value = None
        assert len(args) == 1, "Indexers must have exactly one argument."

        match args[0]:
            case abc.Sequence() as sequence if not isinstance(sequence, str):
                if all(isinstance(name, str) for name in sequence):
                    # If it's a sequence of strings, then we assume it's a list of names, and the values are the indices
                    # Example: EnumT[("foo", "bar")]
                    index = 0
                    name_to_value = {}
                    used_indices = set()
                    for arg in cast(Sequence[str], args[0]):
                        if "=" in arg:
                            # Example: EnumT["foo=1", "bar=2"]
                            name, new_index = arg.split("=")
                            new_index = int(new_index)
                            if new_index in used_indices:
                                raise ValueError(f"Duplicate index: {new_index}")
                            name_to_value[name] = new_index
                            used_indices.add(new_index)
                            index = new_index + 1
                        else:
                            # Example: EnumT["foo", "bar"]
                            name_to_value[arg] = index
                            used_indices.add(index)
                            index = index + 1
                        while index in used_indices:
                            # Skip over any indices that have already been used
                            index += 1
                elif all(is_str_int_tuple(value) for value in sequence):
                    # If it's a sequence of tuple[str, int], then we assume it's a list of name-value pairs
                    # Example: EnumT[[("foo", 1), ("bar", 2)]]
                    name_to_value = dict(sequence)
                else:
                    raise ValueError(f"Invalid type for enum: {sequence}")
            case dict() as name_to_value:
                # Example: EnumT[{"foo": 1, "bar": 2}]
                name_to_value = dict(name_to_value)
            case enum_type if isinstance(enum_type, EnumMeta):
                # Example: EnumT[MyEnum]
                # TODO: When we switch to python 3.11, we can use EnumType to simplify this.
                assert all(isinstance(member.value, int) for member in enum_type.__members__.values())
                # Ignoring the type check on member.value, since we know it's an int, but the static type checker doesn't
                name_to_value = {name: member.value for name, member in enum_type.__members__.items()}
            case _:
                raise ValueError(f"Invalid type for enum: {args[0]}")

        return self._clone_with_overrides(name_to_value=name_to_value)

    @property
    def parameters(self) -> list[Any]:
        """The type parameters as a tuple."""
        return sorted(self.name_to_value.items(), key=lambda item: item[1])

    def _get_param_strings(self) -> Iterator[str]:
        yield from (f"{name}={value}" for name, value in self.parameters)

    @property
    def as_string(self) -> "EnumTypeHandle":
        """Set this type to store its values as strings in the database"""
        return self._clone_with_overrides(store_as_string=True)

    @property
    def as_integer(self) -> "EnumTypeHandle":
        """Set this type to store its values as integers in the database"""
        return self._clone_with_overrides(store_as_string=False)

    @property
    def numpy_dtype(self) -> np.dtype:
        """The corresponding numpy type: [`np.int64`][numpy.int64] or [`np.str_`][numpy.str_] if
        the values are stored as strings"""
        return np.str_ if self.store_as_string else np.int64


# We need to add the enum types to the type dictionary, because we can't use a decorator
# to register a single class with multiple names
enum_type_dict = {
    "enum_as_str": partial(EnumTypeHandle, True),
    "enum_as_int": partial(EnumTypeHandle, False),
}

OrcaTypeHandle._name_to_type.update(enum_type_dict)


# TODO: Implement this in the database
# @_register_column_type("bool")
# class BoolTypeHandle(OrcaTypeHandle):
#     """Represents a boolean column type"""

#     def __init__(self, notnull: bool = False, unique: bool = False):
#         """
#         Initializes the boolean type handle

#         Args:
#             notnull: Whether the column must have a value
#             unique: Whether the column must have a unique value
#         """
#         super().__init__("bool", notnull, unique)

#     @property
#     def numpy_dtype(self) -> np.dtype | None:
#         """The corresponding numpy type [`np.bool_`][numpy.bool_]"""
#         return np.bool_


@_register_column_type("document")
class DocumentTypeHandle(OrcaTypeHandle):
    """Represents a document column type."""

    def __init__(self, notnull: bool = False, unique: bool = False):
        """
        Initializes the document type handle

        Args:
            notnull: Whether the column must have a value
            unique: Whether the column must have a unique value
        """
        super().__init__("document", notnull, unique)

    @property
    def numpy_dtype(self) -> np.dtype | None:
        """The corresponding numpy type [`np.str_`][numpy.str_]"""
        return np.str_


@_register_column_type("image")
class ImageTypeHandle(
    OrcaTypeHandle,
    CustomSerializable[PILImage.Image],
):
    """Represents an image column type"""

    def __init__(
        self,
        format: ImageFormat | str | None,
        notnull: bool = False,
        unique: bool = False,
    ):
        """
        Initializes the image type handle

        Args:
            format: The image format, for example "PNG" or ImageFormat.PNG
            notnull: Whether the column must have a value
            unique: Whether the column must have a unique value
        """
        super().__init__("image", notnull, unique)
        if isinstance(format, str):
            format = ImageFormat(format)

        self.format = format

    @property
    def parameters(self) -> list[Any]:
        """The type parameters as a tuple."""
        return [self.format]

    def __getitem__(self, format: ImageFormat | str) -> "ImageTypeHandle":
        """
        Sets the image format for this type.

        Examples:
            >>> ImageT["JPG"]
            image[JPG]
        """
        return self._clone_with_overrides(format=format)

    ##### CustomSerializable methods #####

    def binary_serialize(self, value: PILImage.Image) -> io.BytesIO:
        """
        Serializes the image as a binary stream, to send it to the server.

        Args:
            value: The image to serialize

        Returns:
            The serialized image
        """
        # We're not using a context manager clarify that the stream is open after this function returns
        byte_stream = io.BytesIO()
        value.save(byte_stream, format=self.format.name)
        byte_stream.seek(0)  # Reset the pointer to the beginning of the stream
        return byte_stream

    def msgpack_deserialize(self, value: dict[str, Any]) -> PILImage.Image:
        """
        Deserializes the image from a msgpack-compatible dictionary.

        Args:
            value: The msgpack-compatible dictionary to deserialize

        Returns:
            The deserialized image
        """
        image_data = value.get(f"__{self.full_name}__", None)
        assert image_data is not None, f"Expected image data for type {self.full_name}, got {value} instead"
        byte_stream = io.BytesIO(image_data)
        image = PILImage.open(byte_stream, formats=[self.format.name])
        return image


# Primitive types
TextT = TextTypeHandle()
"""Represents a text column type"""

DocumentT = DocumentTypeHandle()
"""
Represents a document column type

A document is a long text that needs to be broken up for indexing
"""

EnumT = EnumTypeHandle()
"""
Represents an Enum column type.

This must be used with the `[]` operator to specify the enum values.

Examples:
    >>> class Sentiment(Enum):
    ...     neg = 0
    ...     pos = 1
    >>> EnumT[Sentiment]
    enum_as_int[neg=0,pos=1]

    >>> EnumT["foo", "bar"]
    enum_as_int[foo=0,bar=1]

    >>> EnumT["foo=2", "bar=3"]
    enum_as_int[foo=2,bar=3]

    >>> EnumT["foo=2", "bar"]
    enum_as_int[foo=2,bar=3]

    >>> EnumT[("foo", 1), ("bar", 2)]

    >>> EnumT[{"foo": 1, "bar": 2}]
    enum_as_int[foo=1,bar=2]
"""


# Numeric types

IntT = NumericTypeHandle(dtype=NumericType.int32)
"""Represents an integer column type"""

FloatT = NumericTypeHandle(dtype=NumericType.float32)
"""Represents a float column type"""

# BoolT = BoolTypeHandle()
Int8T = NumericTypeHandle(dtype=NumericType.int8)
Int16T = NumericTypeHandle(dtype=NumericType.int16)
Int32T = NumericTypeHandle(dtype=NumericType.int32)
Int64T = NumericTypeHandle(dtype=NumericType.int64)

UInt8T = NumericTypeHandle(dtype=NumericType.uint8)
UInt16T = NumericTypeHandle(dtype=NumericType.uint16)
UInt32T = NumericTypeHandle(dtype=NumericType.uint32)
UInt64T = NumericTypeHandle(dtype=NumericType.uint64)

Float16T = NumericTypeHandle(dtype=NumericType.float16)
Float32T = NumericTypeHandle(dtype=NumericType.float32)
Float64T = NumericTypeHandle(dtype=NumericType.float64)

BFloat16T = NumericTypeHandle(NumericType.bfloat16)


# Parameterized types
VectorT = Float64T
"""
Represents a vector column type.

This must be used with the `[]` operator to specify the vector length.

Examples:
    >>> VectorT[768]
    vector[768]
"""


ImageT = ImageTypeHandle(None)
"""
Represents an image column type.

This must be used with the `[]` operator to specify the image format.

Examples:
    >>> ImageT["JPG"]
    image[JPG]
"""
