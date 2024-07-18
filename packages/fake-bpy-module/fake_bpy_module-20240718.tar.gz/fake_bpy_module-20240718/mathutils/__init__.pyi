"""
This module provides access to math operations.

[NOTE]
Classes, methods and attributes that accept vectors also accept other numeric sequences,
such as tuples, lists.

The mathutils module provides the following classes:

* Color,
* Euler,
* Matrix,
* Quaternion,
* Vector,

mathutils.geometry.rst
mathutils.bvhtree.rst
mathutils.kdtree.rst
mathutils.interpolate.rst
mathutils.noise.rst

:maxdepth: 1
:caption: Submodules

```../examples/mathutils.py```

"""

import typing
import collections.abc
import typing_extensions
from . import bvhtree
from . import geometry
from . import interpolate
from . import kdtree
from . import noise

GenericType1 = typing.TypeVar("GenericType1")
GenericType2 = typing.TypeVar("GenericType2")

class Color:
    """This object gives access to Colors in Blender.Most colors returned by Blender APIs are in scene linear color space, as defined by    the OpenColorIO configuration. The notable exception is user interface theming colors,    which are in sRGB color space."""

    b: float
    """ Blue color channel.

    :type: float
    """

    g: float
    """ Green color channel.

    :type: float
    """

    h: float
    """ HSV Hue component in [0, 1].

    :type: float
    """

    hsv: Vector | collections.abc.Sequence[float]
    """ HSV Values in [0, 1].

    :type: Vector | collections.abc.Sequence[float]
    """

    is_frozen: bool
    """ True when this object has been frozen (read-only).

    :type: bool
    """

    is_valid: bool
    """ True when the owner of this data is valid.

    :type: bool
    """

    is_wrapped: bool
    """ True when this object wraps external data (read-only).

    :type: bool
    """

    owner: typing.Any
    """ The item this is wrapping or None  (read-only)."""

    r: float
    """ Red color channel.

    :type: float
    """

    s: float
    """ HSV Saturation component in [0, 1].

    :type: float
    """

    v: float
    """ HSV Value component in [0, 1].

    :type: float
    """

    def copy(self) -> Color:
        """Returns a copy of this color.

        :return: A copy of the color.
        :rtype: Color
        """
        ...

    def freeze(self) -> Color:
        """Make this object immutable.After this the object can be hashed, used in dictionaries & sets.

        :return: An instance of this object.
        :rtype: Color
        """
        ...

    def from_aces_to_scene_linear(self) -> Color:
        """Convert from ACES2065-1 linear to scene linear color space.

        :return: A color in scene linear color space.
        :rtype: Color
        """
        ...

    def from_rec709_linear_to_scene_linear(self) -> Color:
        """Convert from Rec.709 linear color space to scene linear color space.

        :return: A color in scene linear color space.
        :rtype: Color
        """
        ...

    def from_scene_linear_to_aces(self) -> Color:
        """Convert from scene linear to ACES2065-1 linear color space.

        :return: A color in ACES2065-1 linear color space.
        :rtype: Color
        """
        ...

    def from_scene_linear_to_rec709_linear(self) -> Color:
        """Convert from scene linear to Rec.709 linear color space.

        :return: A color in Rec.709 linear color space.
        :rtype: Color
        """
        ...

    def from_scene_linear_to_srgb(self) -> Color:
        """Convert from scene linear to sRGB color space.

        :return: A color in sRGB color space.
        :rtype: Color
        """
        ...

    def from_scene_linear_to_xyz_d65(self) -> Color:
        """Convert from scene linear to CIE XYZ (Illuminant D65) color space.

        :return: A color in XYZ color space.
        :rtype: Color
        """
        ...

    def from_srgb_to_scene_linear(self) -> Color:
        """Convert from sRGB to scene linear color space.

        :return: A color in scene linear color space.
        :rtype: Color
        """
        ...

    def from_xyz_d65_to_scene_linear(self) -> Color:
        """Convert from CIE XYZ (Illuminant D65) to scene linear color space.

        :return: A color in scene linear color space.
        :rtype: Color
        """
        ...

    def __init__(self, rgb=(0.0, 0.0, 0.0)):
        """

        :param rgb:
        """
        ...

    def __get__(self, instance, owner) -> Color:
        """

        :param instance:
        :param owner:
        :return:
        :rtype: Color
        """
        ...

    def __set__(self, instance, value: Color | collections.abc.Sequence[float]):
        """

        :param instance:
        :param value:
        :type value: Color | collections.abc.Sequence[float]
        """
        ...

    def __add__(self, other: Color | collections.abc.Sequence[float]) -> Color:
        """

        :param other:
        :type other: Color | collections.abc.Sequence[float]
        :return:
        :rtype: Color
        """
        ...

    def __sub__(self, other: Color | collections.abc.Sequence[float]) -> Color:
        """

        :param other:
        :type other: Color | collections.abc.Sequence[float]
        :return:
        :rtype: Color
        """
        ...

    def __mul__(self, other: float | int) -> Color:
        """

        :param other:
        :type other: float | int
        :return:
        :rtype: Color
        """
        ...

    def __truediv__(self, other: float | int) -> Color:
        """

        :param other:
        :type other: float | int
        :return:
        :rtype: Color
        """
        ...

    def __radd__(self, other: Color | collections.abc.Sequence[float]) -> Color:
        """

        :param other:
        :type other: Color | collections.abc.Sequence[float]
        :return:
        :rtype: Color
        """
        ...

    def __rsub__(self, other: Color | collections.abc.Sequence[float]) -> Color:
        """

        :param other:
        :type other: Color | collections.abc.Sequence[float]
        :return:
        :rtype: Color
        """
        ...

    def __rmul__(self, other: float | int) -> Color:
        """

        :param other:
        :type other: float | int
        :return:
        :rtype: Color
        """
        ...

    def __rtruediv__(self, other: float | int) -> Color:
        """

        :param other:
        :type other: float | int
        :return:
        :rtype: Color
        """
        ...

    def __iadd__(self, other: Color | collections.abc.Sequence[float]) -> Color:
        """

        :param other:
        :type other: Color | collections.abc.Sequence[float]
        :return:
        :rtype: Color
        """
        ...

    def __isub__(self, other: Color | collections.abc.Sequence[float]) -> Color:
        """

        :param other:
        :type other: Color | collections.abc.Sequence[float]
        :return:
        :rtype: Color
        """
        ...

    def __imul__(self, other: float | int) -> Color:
        """

        :param other:
        :type other: float | int
        :return:
        :rtype: Color
        """
        ...

    def __itruediv__(self, other: float | int) -> Color:
        """

        :param other:
        :type other: float | int
        :return:
        :rtype: Color
        """
        ...

    @typing.overload
    def __getitem__(self, key: int) -> float:
        """

        :param key:
        :type key: int
        :return:
        :rtype: float
        """
        ...

    @typing.overload
    def __getitem__(self, key: slice) -> tuple[float, ...]:
        """

        :param key:
        :type key: slice
        :return:
        :rtype: tuple[float, ...]
        """
        ...

    @typing.overload
    def __setitem__(self, key: int, value: float):
        """

        :param key:
        :type key: int
        :param value:
        :type value: float
        """
        ...

    @typing.overload
    def __setitem__(self, key: slice, value: collections.abc.Iterable[float]):
        """

        :param key:
        :type key: slice
        :param value:
        :type value: collections.abc.Iterable[float]
        """
        ...

class Euler:
    """This object gives access to Eulers in Blender.`Euler angles <https://en.wikipedia.org/wiki/Euler_angles>`__ on Wikipedia."""

    is_frozen: bool
    """ True when this object has been frozen (read-only).

    :type: bool
    """

    is_valid: bool
    """ True when the owner of this data is valid.

    :type: bool
    """

    is_wrapped: bool
    """ True when this object wraps external data (read-only).

    :type: bool
    """

    order: typing.Any
    """ Euler rotation order."""

    owner: typing.Any
    """ The item this is wrapping or None  (read-only)."""

    x: float
    """ Euler axis angle in radians.

    :type: float
    """

    y: float
    """ Euler axis angle in radians.

    :type: float
    """

    z: float
    """ Euler axis angle in radians.

    :type: float
    """

    def copy(self) -> Euler:
        """Returns a copy of this euler.

        :return: A copy of the euler.
        :rtype: Euler
        """
        ...

    def freeze(self) -> Euler:
        """Make this object immutable.After this the object can be hashed, used in dictionaries & sets.

        :return: An instance of this object.
        :rtype: Euler
        """
        ...

    def make_compatible(self, other):
        """Make this euler compatible with another,
        so interpolating between them works as intended.

                :param other:
        """
        ...

    def rotate(
        self,
        other: Euler
        | Matrix
        | Quaternion
        | collections.abc.Sequence[collections.abc.Sequence[float]]
        | collections.abc.Sequence[float],
    ):
        """Rotates the euler by another mathutils value.

        :param other: rotation component of mathutils value
        :type other: Euler | Matrix | Quaternion | collections.abc.Sequence[collections.abc.Sequence[float]] | collections.abc.Sequence[float]
        """
        ...

    def rotate_axis(self, axis: str, angle: float):
        """Rotates the euler a certain amount and returning a unique euler rotation
        (no 720 degree pitches).

                :param axis: single character in ['X, 'Y', 'Z'].
                :type axis: str
                :param angle: angle in radians.
                :type angle: float
        """
        ...

    def to_matrix(self) -> Matrix:
        """Return a matrix representation of the euler.

        :return: A 3x3 rotation matrix representation of the euler.
        :rtype: Matrix
        """
        ...

    def to_quaternion(self) -> Quaternion:
        """Return a quaternion representation of the euler.

        :return: Quaternion representation of the euler.
        :rtype: Quaternion
        """
        ...

    def zero(self):
        """Set all values to zero."""
        ...

    def __init__(self, angles=(0.0, 0.0, 0.0), order="XYZ"):
        """

        :param angles:
        :param order:
        """
        ...

    def __get__(self, instance, owner) -> Euler:
        """

        :param instance:
        :param owner:
        :return:
        :rtype: Euler
        """
        ...

    def __set__(self, instance, value: Euler | collections.abc.Sequence[float]):
        """

        :param instance:
        :param value:
        :type value: Euler | collections.abc.Sequence[float]
        """
        ...

    @typing.overload
    def __getitem__(self, key: int) -> float:
        """

        :param key:
        :type key: int
        :return:
        :rtype: float
        """
        ...

    @typing.overload
    def __getitem__(self, key: slice) -> tuple[float, ...]:
        """

        :param key:
        :type key: slice
        :return:
        :rtype: tuple[float, ...]
        """
        ...

    @typing.overload
    def __setitem__(self, key: int, value: float):
        """

        :param key:
        :type key: int
        :param value:
        :type value: float
        """
        ...

    @typing.overload
    def __setitem__(self, key: slice, value: collections.abc.Iterable[float]):
        """

        :param key:
        :type key: slice
        :param value:
        :type value: collections.abc.Iterable[float]
        """
        ...

class Matrix:
    """This object gives access to Matrices in Blender, supporting square and rectangular
    matrices from 2x2 up to 4x4.
    """

    col: typing.Any
    """ Access the matrix by columns, 3x3 and 4x4 only, (read-only)."""

    is_frozen: bool
    """ True when this object has been frozen (read-only).

    :type: bool
    """

    is_identity: bool
    """ True if this is an identity matrix (read-only).

    :type: bool
    """

    is_negative: bool
    """ True if this matrix results in a negative scale, 3x3 and 4x4 only, (read-only).

    :type: bool
    """

    is_orthogonal: bool
    """ True if this matrix is orthogonal, 3x3 and 4x4 only, (read-only).

    :type: bool
    """

    is_orthogonal_axis_vectors: bool
    """ True if this matrix has got orthogonal axis vectors, 3x3 and 4x4 only, (read-only).

    :type: bool
    """

    is_valid: bool
    """ True when the owner of this data is valid.

    :type: bool
    """

    is_wrapped: bool
    """ True when this object wraps external data (read-only).

    :type: bool
    """

    median_scale: float
    """ The average scale applied to each axis (read-only).

    :type: float
    """

    owner: typing.Any
    """ The item this is wrapping or None  (read-only)."""

    row: typing.Any
    """ Access the matrix by rows (default), (read-only)."""

    translation: Vector
    """ The translation component of the matrix.

    :type: Vector
    """

    @classmethod
    def Diagonal(cls, vector: Vector | collections.abc.Sequence[float]) -> Matrix:
        """Create a diagonal (scaling) matrix using the values from the vector.

        :param vector: The vector of values for the diagonal.
        :type vector: Vector | collections.abc.Sequence[float]
        :return: A diagonal matrix.
        :rtype: Matrix
        """
        ...

    @classmethod
    def Identity(cls, size: int) -> Matrix:
        """Create an identity matrix.

        :param size: The size of the identity matrix to construct [2, 4].
        :type size: int
        :return: A new identity matrix.
        :rtype: Matrix
        """
        ...

    @classmethod
    def LocRotScale(
        cls,
        location: Vector | collections.abc.Sequence[float] | None,
        rotation: Euler | Quaternion | collections.abc.Sequence[float] | None,
        scale: Vector | collections.abc.Sequence[float] | None,
    ) -> Matrix:
        """Create a matrix combining translation, rotation and scale,
        acting as the inverse of the decompose() method.Any of the inputs may be replaced with None if not needed.

                :param location: The translation component.
                :type location: Vector | collections.abc.Sequence[float] | None
                :param rotation: The rotation component.
                :type rotation: Euler | Quaternion | collections.abc.Sequence[float] | None
                :param scale: The scale component.
                :type scale: Vector | collections.abc.Sequence[float] | None
                :return: Combined transformation matrix.
                :rtype: Matrix
        """
        ...

    @classmethod
    def OrthoProjection(
        cls, axis: Vector | collections.abc.Sequence[float] | str, size: int
    ) -> Matrix:
        """Create a matrix to represent an orthographic projection.

                :param axis: Can be any of the following: ['X', 'Y', 'XY', 'XZ', 'YZ'],
        where a single axis is for a 2D matrix.
        Or a vector for an arbitrary axis
                :type axis: Vector | collections.abc.Sequence[float] | str
                :param size: The size of the projection matrix to construct [2, 4].
                :type size: int
                :return: A new projection matrix.
                :rtype: Matrix
        """
        ...

    @classmethod
    def Rotation(
        cls,
        angle: float,
        size: int,
        axis: Vector | collections.abc.Sequence[float] | str | None,
    ) -> Matrix:
        """Create a matrix representing a rotation.

                :param angle: The angle of rotation desired, in radians.
                :type angle: float
                :param size: The size of the rotation matrix to construct [2, 4].
                :type size: int
                :param axis: a string in ['X', 'Y', 'Z'] or a 3D Vector Object
        (optional when size is 2).
                :type axis: Vector | collections.abc.Sequence[float] | str | None
                :return: A new rotation matrix.
                :rtype: Matrix
        """
        ...

    @classmethod
    def Scale(
        cls,
        factor: float,
        size: int,
        axis: Vector | collections.abc.Sequence[float] | None,
    ) -> Matrix:
        """Create a matrix representing a scaling.

        :param factor: The factor of scaling to apply.
        :type factor: float
        :param size: The size of the scale matrix to construct [2, 4].
        :type size: int
        :param axis: Direction to influence scale. (optional).
        :type axis: Vector | collections.abc.Sequence[float] | None
        :return: A new scale matrix.
        :rtype: Matrix
        """
        ...

    @classmethod
    def Shear(cls, plane: str, size: int, factor: float) -> Matrix:
        """Create a matrix to represent an shear transformation.

                :param plane: Can be any of the following: ['X', 'Y', 'XY', 'XZ', 'YZ'],
        where a single axis is for a 2D matrix only.
                :type plane: str
                :param size: The size of the shear matrix to construct [2, 4].
                :type size: int
                :param factor: The factor of shear to apply. For a 3 or 4 size matrix
        pass a pair of floats corresponding with the plane axis.
                :type factor: float
                :return: A new shear matrix.
                :rtype: Matrix
        """
        ...

    @classmethod
    def Translation(cls, vector: Vector | collections.abc.Sequence[float]) -> Matrix:
        """Create a matrix representing a translation.

        :param vector: The translation vector.
        :type vector: Vector | collections.abc.Sequence[float]
        :return: An identity matrix with a translation.
        :rtype: Matrix
        """
        ...

    def adjugate(self):
        """Set the matrix to its adjugate.`Adjugate matrix <https://en.wikipedia.org/wiki/Adjugate_matrix>`__ on Wikipedia."""
        ...

    def adjugated(self) -> Matrix:
        """Return an adjugated copy of the matrix.

        :return: the adjugated matrix.
        :rtype: Matrix
        """
        ...

    def copy(self) -> Matrix:
        """Returns a copy of this matrix.

        :return: an instance of itself
        :rtype: Matrix
        """
        ...

    def decompose(self) -> tuple[Vector, Quaternion, Vector]:
        """Return the translation, rotation, and scale components of this matrix.

        :return: tuple of translation, rotation, and scale
        :rtype: tuple[Vector, Quaternion, Vector]
        """
        ...

    def determinant(self) -> float:
        """Return the determinant of a matrix.`Determinant <https://en.wikipedia.org/wiki/Determinant>`__ on Wikipedia.

        :return: Return the determinant of a matrix.
        :rtype: float
        """
        ...

    def freeze(self) -> Matrix:
        """Make this object immutable.After this the object can be hashed, used in dictionaries & sets.

        :return: An instance of this object.
        :rtype: Matrix
        """
        ...

    def identity(self):
        """Set the matrix to the identity matrix.`Identity matrix <https://en.wikipedia.org/wiki/Identity_matrix>`__ on Wikipedia."""
        ...

    def invert(
        self,
        fallback: Matrix
        | collections.abc.Sequence[collections.abc.Sequence[float]] = None,
    ):
        """Set the matrix to its inverse.`Inverse matrix <https://en.wikipedia.org/wiki/Inverse_matrix>`__ on Wikipedia.

                :param fallback: Set the matrix to this value when the inverse cannot be calculated
        (instead of raising a `ValueError` exception).
                :type fallback: Matrix | collections.abc.Sequence[collections.abc.Sequence[float]]
        """
        ...

    def invert_safe(self):
        """Set the matrix to its inverse, will never error.
        If degenerated (e.g. zero scale on an axis), add some epsilon to its diagonal, to get an invertible one.
        If tweaked matrix is still degenerated, set to the identity matrix instead.`Inverse Matrix <https://en.wikipedia.org/wiki/Inverse_matrix>`__ on Wikipedia.

        """
        ...

    def inverted(self, fallback: typing.Any = None) -> Matrix:
        """Return an inverted copy of the matrix.

                :param fallback: return this when the inverse can't be calculated
        (instead of raising a `ValueError`).
                :type fallback: typing.Any
                :return: the inverted matrix or fallback when given.
                :rtype: Matrix
        """
        ...

    def inverted_safe(self) -> Matrix:
        """Return an inverted copy of the matrix, will never error.
        If degenerated (e.g. zero scale on an axis), add some epsilon to its diagonal, to get an invertible one.
        If tweaked matrix is still degenerated, return the identity matrix instead.

                :return: the inverted matrix.
                :rtype: Matrix
        """
        ...

    def lerp(
        self,
        other: Matrix | collections.abc.Sequence[collections.abc.Sequence[float]],
        factor: float,
    ) -> Matrix:
        """Returns the interpolation of two matrices. Uses polar decomposition, see   "Matrix Animation and Polar Decomposition", Shoemake and Duff, 1992.

        :param other: value to interpolate with.
        :type other: Matrix | collections.abc.Sequence[collections.abc.Sequence[float]]
        :param factor: The interpolation value in [0.0, 1.0].
        :type factor: float
        :return: The interpolated matrix.
        :rtype: Matrix
        """
        ...

    def normalize(self):
        """Normalize each of the matrix columns."""
        ...

    def normalized(self) -> Matrix:
        """Return a column normalized matrix

        :return: a column normalized matrix
        :rtype: Matrix
        """
        ...

    def resize_4x4(self):
        """Resize the matrix to 4x4."""
        ...

    def rotate(
        self,
        other: Euler
        | Matrix
        | Quaternion
        | collections.abc.Sequence[collections.abc.Sequence[float]]
        | collections.abc.Sequence[float],
    ):
        """Rotates the matrix by another mathutils value.

        :param other: rotation component of mathutils value
        :type other: Euler | Matrix | Quaternion | collections.abc.Sequence[collections.abc.Sequence[float]] | collections.abc.Sequence[float]
        """
        ...

    def to_2x2(self) -> Matrix:
        """Return a 2x2 copy of this matrix.

        :return: a new matrix.
        :rtype: Matrix
        """
        ...

    def to_3x3(self) -> Matrix:
        """Return a 3x3 copy of this matrix.

        :return: a new matrix.
        :rtype: Matrix
        """
        ...

    def to_4x4(self) -> Matrix:
        """Return a 4x4 copy of this matrix.

        :return: a new matrix.
        :rtype: Matrix
        """
        ...

    def to_euler(
        self,
        order: str | None,
        euler_compat: Euler | collections.abc.Sequence[float] | None,
    ) -> Euler:
        """Return an Euler representation of the rotation matrix
        (3x3 or 4x4 matrix only).

                :param order: Optional rotation order argument in
        ['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX'].
                :type order: str | None
                :param euler_compat: Optional euler argument the new euler will be made
        compatible with (no axis flipping between them).
        Useful for converting a series of matrices to animation curves.
                :type euler_compat: Euler | collections.abc.Sequence[float] | None
                :return: Euler representation of the matrix.
                :rtype: Euler
        """
        ...

    def to_quaternion(self) -> Quaternion:
        """Return a quaternion representation of the rotation matrix.

        :return: Quaternion representation of the rotation matrix.
        :rtype: Quaternion
        """
        ...

    def to_scale(self) -> Vector:
        """Return the scale part of a 3x3 or 4x4 matrix.

        :return: Return the scale of a matrix.
        :rtype: Vector
        """
        ...

    def to_translation(self) -> Vector:
        """Return the translation part of a 4 row matrix.

        :return: Return the translation of a matrix.
        :rtype: Vector
        """
        ...

    def transpose(self):
        """Set the matrix to its transpose.`Transpose <https://en.wikipedia.org/wiki/Transpose>`__ on Wikipedia."""
        ...

    def transposed(self) -> Matrix:
        """Return a new, transposed matrix.

        :return: a transposed matrix
        :rtype: Matrix
        """
        ...

    def zero(self):
        """Set all the matrix values to zero."""
        ...

    def __init__(
        self,
        rows=(
            (1.0, 0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        ),
    ):
        """

        :param rows:
        """
        ...

    def __get__(self, instance, owner) -> Matrix:
        """

        :param instance:
        :param owner:
        :return:
        :rtype: Matrix
        """
        ...

    def __set__(
        self,
        instance,
        value: Matrix | collections.abc.Sequence[collections.abc.Sequence[float]],
    ):
        """

        :param instance:
        :param value:
        :type value: Matrix | collections.abc.Sequence[collections.abc.Sequence[float]]
        """
        ...

    @typing.overload
    def __getitem__(self, key: int) -> Vector:
        """

        :param key:
        :type key: int
        :return:
        :rtype: Vector
        """
        ...

    @typing.overload
    def __getitem__(self, key: slice) -> tuple[Vector, ...]:
        """

        :param key:
        :type key: slice
        :return:
        :rtype: tuple[Vector, ...]
        """
        ...

    @typing.overload
    def __setitem__(self, key: int, value: Vector | collections.abc.Iterable[float]):
        """

        :param key:
        :type key: int
        :param value:
        :type value: Vector | collections.abc.Iterable[float]
        """
        ...

    @typing.overload
    def __setitem__(
        self,
        key: slice,
        value: collections.abc.Iterable[Vector | collections.abc.Iterable[float]],
    ):
        """

        :param key:
        :type key: slice
        :param value:
        :type value: collections.abc.Iterable[Vector | collections.abc.Iterable[float]]
        """
        ...

    def __len__(self) -> int:
        """

        :return:
        :rtype: int
        """
        ...

    def __add__(
        self, other: Matrix | collections.abc.Sequence[collections.abc.Sequence[float]]
    ) -> Matrix:
        """

        :param other:
        :type other: Matrix | collections.abc.Sequence[collections.abc.Sequence[float]]
        :return:
        :rtype: Matrix
        """
        ...

    def __sub__(
        self, other: Matrix | collections.abc.Sequence[collections.abc.Sequence[float]]
    ) -> Matrix:
        """

        :param other:
        :type other: Matrix | collections.abc.Sequence[collections.abc.Sequence[float]]
        :return:
        :rtype: Matrix
        """
        ...

    def __mul__(self, other: float | int) -> Matrix:
        """

        :param other:
        :type other: float | int
        :return:
        :rtype: Matrix
        """
        ...

    @typing.overload
    def __matmul__(
        self, other: Matrix | collections.abc.Sequence[collections.abc.Sequence[float]]
    ) -> Matrix:
        """

        :param other:
        :type other: Matrix | collections.abc.Sequence[collections.abc.Sequence[float]]
        :return:
        :rtype: Matrix
        """
        ...

    @typing.overload
    def __matmul__(self, other: Vector | collections.abc.Sequence[float]) -> Vector:
        """

        :param other:
        :type other: Vector | collections.abc.Sequence[float]
        :return:
        :rtype: Vector
        """
        ...

    def __radd__(
        self, other: Matrix | collections.abc.Sequence[collections.abc.Sequence[float]]
    ) -> Matrix:
        """

        :param other:
        :type other: Matrix | collections.abc.Sequence[collections.abc.Sequence[float]]
        :return:
        :rtype: Matrix
        """
        ...

    def __rsub__(
        self, other: Matrix | collections.abc.Sequence[collections.abc.Sequence[float]]
    ) -> Matrix:
        """

        :param other:
        :type other: Matrix | collections.abc.Sequence[collections.abc.Sequence[float]]
        :return:
        :rtype: Matrix
        """
        ...

    def __rmul__(self, other: float | int) -> Matrix:
        """

        :param other:
        :type other: float | int
        :return:
        :rtype: Matrix
        """
        ...

    def __imul__(self, other: float | int) -> Matrix:
        """

        :param other:
        :type other: float | int
        :return:
        :rtype: Matrix
        """
        ...

class Quaternion:
    """This object gives access to Quaternions in Blender.The constructor takes arguments in various forms:"""

    angle: float
    """ Angle of the quaternion.

    :type: float
    """

    axis: Vector
    """ Quaternion axis as a vector.

    :type: Vector
    """

    is_frozen: bool
    """ True when this object has been frozen (read-only).

    :type: bool
    """

    is_valid: bool
    """ True when the owner of this data is valid.

    :type: bool
    """

    is_wrapped: bool
    """ True when this object wraps external data (read-only).

    :type: bool
    """

    magnitude: float
    """ Size of the quaternion (read-only).

    :type: float
    """

    owner: typing.Any
    """ The item this is wrapping or None  (read-only)."""

    w: float
    """ Quaternion axis value.

    :type: float
    """

    x: float
    """ Quaternion axis value.

    :type: float
    """

    y: float
    """ Quaternion axis value.

    :type: float
    """

    z: float
    """ Quaternion axis value.

    :type: float
    """

    def conjugate(self):
        """Set the quaternion to its conjugate (negate x, y, z)."""
        ...

    def conjugated(self) -> Quaternion:
        """Return a new conjugated quaternion.

        :return: a new quaternion.
        :rtype: Quaternion
        """
        ...

    def copy(self) -> Quaternion:
        """Returns a copy of this quaternion.

        :return: A copy of the quaternion.
        :rtype: Quaternion
        """
        ...

    def cross(self, other: Quaternion | collections.abc.Sequence[float]) -> Quaternion:
        """Return the cross product of this quaternion and another.

        :param other: The other quaternion to perform the cross product with.
        :type other: Quaternion | collections.abc.Sequence[float]
        :return: The cross product.
        :rtype: Quaternion
        """
        ...

    def dot(self, other: Quaternion | collections.abc.Sequence[float]) -> float:
        """Return the dot product of this quaternion and another.

        :param other: The other quaternion to perform the dot product with.
        :type other: Quaternion | collections.abc.Sequence[float]
        :return: The dot product.
        :rtype: float
        """
        ...

    def freeze(self) -> Quaternion:
        """Make this object immutable.After this the object can be hashed, used in dictionaries & sets.

        :return: An instance of this object.
        :rtype: Quaternion
        """
        ...

    def identity(self):
        """Set the quaternion to an identity quaternion."""
        ...

    def invert(self):
        """Set the quaternion to its inverse."""
        ...

    def inverted(self) -> Quaternion:
        """Return a new, inverted quaternion.

        :return: the inverted value.
        :rtype: Quaternion
        """
        ...

    def make_compatible(self, other):
        """Make this quaternion compatible with another,
        so interpolating between them works as intended.

                :param other:
        """
        ...

    def negate(self):
        """Set the quaternion to its negative."""
        ...

    def normalize(self):
        """Normalize the quaternion."""
        ...

    def normalized(self) -> Quaternion:
        """Return a new normalized quaternion.

        :return: a normalized copy.
        :rtype: Quaternion
        """
        ...

    def rotate(
        self,
        other: Euler
        | Matrix
        | Quaternion
        | collections.abc.Sequence[collections.abc.Sequence[float]]
        | collections.abc.Sequence[float],
    ):
        """Rotates the quaternion by another mathutils value.

        :param other: rotation component of mathutils value
        :type other: Euler | Matrix | Quaternion | collections.abc.Sequence[collections.abc.Sequence[float]] | collections.abc.Sequence[float]
        """
        ...

    def rotation_difference(
        self, other: Quaternion | collections.abc.Sequence[float]
    ) -> Quaternion:
        """Returns a quaternion representing the rotational difference.

        :param other: second quaternion.
        :type other: Quaternion | collections.abc.Sequence[float]
        :return: the rotational difference between the two quat rotations.
        :rtype: Quaternion
        """
        ...

    def slerp(
        self, other: Quaternion | collections.abc.Sequence[float], factor: float
    ) -> Quaternion:
        """Returns the interpolation of two quaternions.

        :param other: value to interpolate with.
        :type other: Quaternion | collections.abc.Sequence[float]
        :param factor: The interpolation value in [0.0, 1.0].
        :type factor: float
        :return: The interpolated rotation.
        :rtype: Quaternion
        """
        ...

    def to_axis_angle(self) -> tuple[Vector, float]:
        """Return the axis, angle representation of the quaternion.

        :return: axis, angle.
        :rtype: tuple[Vector, float]
        """
        ...

    def to_euler(
        self,
        order: str | None,
        euler_compat: Euler | collections.abc.Sequence[float] | None,
    ) -> Euler:
        """Return Euler representation of the quaternion.

                :param order: Optional rotation order argument in
        ['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX'].
                :type order: str | None
                :param euler_compat: Optional euler argument the new euler will be made
        compatible with (no axis flipping between them).
        Useful for converting a series of matrices to animation curves.
                :type euler_compat: Euler | collections.abc.Sequence[float] | None
                :return: Euler representation of the quaternion.
                :rtype: Euler
        """
        ...

    def to_exponential_map(self):
        """Return the exponential map representation of the quaternion.This representation consist of the rotation axis multiplied by the rotation angle.
        Such a representation is useful for interpolation between multiple orientations.To convert back to a quaternion, pass it to the `Quaternion` constructor.

                :return: exponential map.
        """
        ...

    def to_matrix(self) -> Matrix:
        """Return a matrix representation of the quaternion.

        :return: A 3x3 rotation matrix representation of the quaternion.
        :rtype: Matrix
        """
        ...

    def to_swing_twist(self, axis) -> tuple[Quaternion, float]:
        """Split the rotation into a swing quaternion with the specified
        axis fixed at zero, and the remaining twist rotation angle.

                :param axis: twist axis as a string in ['X', 'Y', 'Z']
                :return: swing, twist angle.
                :rtype: tuple[Quaternion, float]
        """
        ...

    def __init__(self, seq=(1.0, 0.0, 0.0, 0.0)):
        """

        :param seq:
        """
        ...

    def __get__(self, instance, owner) -> Quaternion:
        """

        :param instance:
        :param owner:
        :return:
        :rtype: Quaternion
        """
        ...

    def __set__(self, instance, value: Quaternion | collections.abc.Sequence[float]):
        """

        :param instance:
        :param value:
        :type value: Quaternion | collections.abc.Sequence[float]
        """
        ...

    def __len__(self) -> int:
        """

        :return:
        :rtype: int
        """
        ...

    @typing.overload
    def __getitem__(self, key: int) -> float:
        """

        :param key:
        :type key: int
        :return:
        :rtype: float
        """
        ...

    @typing.overload
    def __getitem__(self, key: slice) -> tuple[float, ...]:
        """

        :param key:
        :type key: slice
        :return:
        :rtype: tuple[float, ...]
        """
        ...

    @typing.overload
    def __setitem__(self, key: int, value: float):
        """

        :param key:
        :type key: int
        :param value:
        :type value: float
        """
        ...

    @typing.overload
    def __setitem__(self, key: slice, value: collections.abc.Iterable[float]):
        """

        :param key:
        :type key: slice
        :param value:
        :type value: collections.abc.Iterable[float]
        """
        ...

    def __add__(
        self, other: Quaternion | collections.abc.Sequence[float]
    ) -> Quaternion:
        """

        :param other:
        :type other: Quaternion | collections.abc.Sequence[float]
        :return:
        :rtype: Quaternion
        """
        ...

    def __sub__(
        self, other: Quaternion | collections.abc.Sequence[float]
    ) -> Quaternion:
        """

        :param other:
        :type other: Quaternion | collections.abc.Sequence[float]
        :return:
        :rtype: Quaternion
        """
        ...

    def __mul__(
        self, other: Quaternion | collections.abc.Sequence[float] | float | int
    ) -> Quaternion:
        """

        :param other:
        :type other: Quaternion | collections.abc.Sequence[float] | float | int
        :return:
        :rtype: Quaternion
        """
        ...

    @typing.overload
    def __matmul__(
        self, other: Quaternion | collections.abc.Sequence[float]
    ) -> Quaternion:
        """

        :param other:
        :type other: Quaternion | collections.abc.Sequence[float]
        :return:
        :rtype: Quaternion
        """
        ...

    @typing.overload
    def __matmul__(self, other: Vector | collections.abc.Sequence[float]) -> Vector:
        """

        :param other:
        :type other: Vector | collections.abc.Sequence[float]
        :return:
        :rtype: Vector
        """
        ...

    def __radd__(
        self, other: Quaternion | collections.abc.Sequence[float]
    ) -> Quaternion:
        """

        :param other:
        :type other: Quaternion | collections.abc.Sequence[float]
        :return:
        :rtype: Quaternion
        """
        ...

    def __rsub__(
        self, other: Quaternion | collections.abc.Sequence[float]
    ) -> Quaternion:
        """

        :param other:
        :type other: Quaternion | collections.abc.Sequence[float]
        :return:
        :rtype: Quaternion
        """
        ...

    def __rmul__(
        self, other: Quaternion | collections.abc.Sequence[float] | float | int
    ) -> Quaternion:
        """

        :param other:
        :type other: Quaternion | collections.abc.Sequence[float] | float | int
        :return:
        :rtype: Quaternion
        """
        ...

    def __imul__(
        self, other: Quaternion | collections.abc.Sequence[float] | float | int
    ) -> Quaternion:
        """

        :param other:
        :type other: Quaternion | collections.abc.Sequence[float] | float | int
        :return:
        :rtype: Quaternion
        """
        ...

class Vector:
    """This object gives access to Vectors in Blender."""

    is_frozen: bool
    """ True when this object has been frozen (read-only).

    :type: bool
    """

    is_valid: bool
    """ True when the owner of this data is valid.

    :type: bool
    """

    is_wrapped: bool
    """ True when this object wraps external data (read-only).

    :type: bool
    """

    length: float
    """ Vector Length.

    :type: float
    """

    length_squared: float
    """ Vector length squared (v.dot(v)).

    :type: float
    """

    magnitude: float
    """ Vector Length.

    :type: float
    """

    owner: typing.Any
    """ The item this is wrapping or None  (read-only)."""

    w: float
    """ Vector W axis (4D Vectors only).

    :type: float
    """

    ww: Vector
    """ 

    :type: Vector
    """

    www: Vector
    """ 

    :type: Vector
    """

    wwww: Vector
    """ 

    :type: Vector
    """

    wwwx: Vector
    """ 

    :type: Vector
    """

    wwwy: Vector
    """ 

    :type: Vector
    """

    wwwz: Vector
    """ 

    :type: Vector
    """

    wwx: Vector
    """ 

    :type: Vector
    """

    wwxw: Vector
    """ 

    :type: Vector
    """

    wwxx: Vector
    """ 

    :type: Vector
    """

    wwxy: Vector
    """ 

    :type: Vector
    """

    wwxz: Vector
    """ 

    :type: Vector
    """

    wwy: Vector
    """ 

    :type: Vector
    """

    wwyw: Vector
    """ 

    :type: Vector
    """

    wwyx: Vector
    """ 

    :type: Vector
    """

    wwyy: Vector
    """ 

    :type: Vector
    """

    wwyz: Vector
    """ 

    :type: Vector
    """

    wwz: Vector
    """ 

    :type: Vector
    """

    wwzw: Vector
    """ 

    :type: Vector
    """

    wwzx: Vector
    """ 

    :type: Vector
    """

    wwzy: Vector
    """ 

    :type: Vector
    """

    wwzz: Vector
    """ 

    :type: Vector
    """

    wx: Vector
    """ 

    :type: Vector
    """

    wxw: Vector
    """ 

    :type: Vector
    """

    wxww: Vector
    """ 

    :type: Vector
    """

    wxwx: Vector
    """ 

    :type: Vector
    """

    wxwy: Vector
    """ 

    :type: Vector
    """

    wxwz: Vector
    """ 

    :type: Vector
    """

    wxx: Vector
    """ 

    :type: Vector
    """

    wxxw: Vector
    """ 

    :type: Vector
    """

    wxxx: Vector
    """ 

    :type: Vector
    """

    wxxy: Vector
    """ 

    :type: Vector
    """

    wxxz: Vector
    """ 

    :type: Vector
    """

    wxy: Vector
    """ 

    :type: Vector
    """

    wxyw: Vector
    """ 

    :type: Vector
    """

    wxyx: Vector
    """ 

    :type: Vector
    """

    wxyy: Vector
    """ 

    :type: Vector
    """

    wxyz: Vector
    """ 

    :type: Vector
    """

    wxz: Vector
    """ 

    :type: Vector
    """

    wxzw: Vector
    """ 

    :type: Vector
    """

    wxzx: Vector
    """ 

    :type: Vector
    """

    wxzy: Vector
    """ 

    :type: Vector
    """

    wxzz: Vector
    """ 

    :type: Vector
    """

    wy: Vector
    """ 

    :type: Vector
    """

    wyw: Vector
    """ 

    :type: Vector
    """

    wyww: Vector
    """ 

    :type: Vector
    """

    wywx: Vector
    """ 

    :type: Vector
    """

    wywy: Vector
    """ 

    :type: Vector
    """

    wywz: Vector
    """ 

    :type: Vector
    """

    wyx: Vector
    """ 

    :type: Vector
    """

    wyxw: Vector
    """ 

    :type: Vector
    """

    wyxx: Vector
    """ 

    :type: Vector
    """

    wyxy: Vector
    """ 

    :type: Vector
    """

    wyxz: Vector
    """ 

    :type: Vector
    """

    wyy: Vector
    """ 

    :type: Vector
    """

    wyyw: Vector
    """ 

    :type: Vector
    """

    wyyx: Vector
    """ 

    :type: Vector
    """

    wyyy: Vector
    """ 

    :type: Vector
    """

    wyyz: Vector
    """ 

    :type: Vector
    """

    wyz: Vector
    """ 

    :type: Vector
    """

    wyzw: Vector
    """ 

    :type: Vector
    """

    wyzx: Vector
    """ 

    :type: Vector
    """

    wyzy: Vector
    """ 

    :type: Vector
    """

    wyzz: Vector
    """ 

    :type: Vector
    """

    wz: Vector
    """ 

    :type: Vector
    """

    wzw: Vector
    """ 

    :type: Vector
    """

    wzww: Vector
    """ 

    :type: Vector
    """

    wzwx: Vector
    """ 

    :type: Vector
    """

    wzwy: Vector
    """ 

    :type: Vector
    """

    wzwz: Vector
    """ 

    :type: Vector
    """

    wzx: Vector
    """ 

    :type: Vector
    """

    wzxw: Vector
    """ 

    :type: Vector
    """

    wzxx: Vector
    """ 

    :type: Vector
    """

    wzxy: Vector
    """ 

    :type: Vector
    """

    wzxz: Vector
    """ 

    :type: Vector
    """

    wzy: Vector
    """ 

    :type: Vector
    """

    wzyw: Vector
    """ 

    :type: Vector
    """

    wzyx: Vector
    """ 

    :type: Vector
    """

    wzyy: Vector
    """ 

    :type: Vector
    """

    wzyz: Vector
    """ 

    :type: Vector
    """

    wzz: Vector
    """ 

    :type: Vector
    """

    wzzw: Vector
    """ 

    :type: Vector
    """

    wzzx: Vector
    """ 

    :type: Vector
    """

    wzzy: Vector
    """ 

    :type: Vector
    """

    wzzz: Vector
    """ 

    :type: Vector
    """

    x: float
    """ Vector X axis.

    :type: float
    """

    xw: Vector
    """ 

    :type: Vector
    """

    xww: Vector
    """ 

    :type: Vector
    """

    xwww: Vector
    """ 

    :type: Vector
    """

    xwwx: Vector
    """ 

    :type: Vector
    """

    xwwy: Vector
    """ 

    :type: Vector
    """

    xwwz: Vector
    """ 

    :type: Vector
    """

    xwx: Vector
    """ 

    :type: Vector
    """

    xwxw: Vector
    """ 

    :type: Vector
    """

    xwxx: Vector
    """ 

    :type: Vector
    """

    xwxy: Vector
    """ 

    :type: Vector
    """

    xwxz: Vector
    """ 

    :type: Vector
    """

    xwy: Vector
    """ 

    :type: Vector
    """

    xwyw: Vector
    """ 

    :type: Vector
    """

    xwyx: Vector
    """ 

    :type: Vector
    """

    xwyy: Vector
    """ 

    :type: Vector
    """

    xwyz: Vector
    """ 

    :type: Vector
    """

    xwz: Vector
    """ 

    :type: Vector
    """

    xwzw: Vector
    """ 

    :type: Vector
    """

    xwzx: Vector
    """ 

    :type: Vector
    """

    xwzy: Vector
    """ 

    :type: Vector
    """

    xwzz: Vector
    """ 

    :type: Vector
    """

    xx: Vector
    """ 

    :type: Vector
    """

    xxw: Vector
    """ 

    :type: Vector
    """

    xxww: Vector
    """ 

    :type: Vector
    """

    xxwx: Vector
    """ 

    :type: Vector
    """

    xxwy: Vector
    """ 

    :type: Vector
    """

    xxwz: Vector
    """ 

    :type: Vector
    """

    xxx: Vector
    """ 

    :type: Vector
    """

    xxxw: Vector
    """ 

    :type: Vector
    """

    xxxx: Vector
    """ 

    :type: Vector
    """

    xxxy: Vector
    """ 

    :type: Vector
    """

    xxxz: Vector
    """ 

    :type: Vector
    """

    xxy: Vector
    """ 

    :type: Vector
    """

    xxyw: Vector
    """ 

    :type: Vector
    """

    xxyx: Vector
    """ 

    :type: Vector
    """

    xxyy: Vector
    """ 

    :type: Vector
    """

    xxyz: Vector
    """ 

    :type: Vector
    """

    xxz: Vector
    """ 

    :type: Vector
    """

    xxzw: Vector
    """ 

    :type: Vector
    """

    xxzx: Vector
    """ 

    :type: Vector
    """

    xxzy: Vector
    """ 

    :type: Vector
    """

    xxzz: Vector
    """ 

    :type: Vector
    """

    xy: Vector
    """ 

    :type: Vector
    """

    xyw: Vector
    """ 

    :type: Vector
    """

    xyww: Vector
    """ 

    :type: Vector
    """

    xywx: Vector
    """ 

    :type: Vector
    """

    xywy: Vector
    """ 

    :type: Vector
    """

    xywz: Vector
    """ 

    :type: Vector
    """

    xyx: Vector
    """ 

    :type: Vector
    """

    xyxw: Vector
    """ 

    :type: Vector
    """

    xyxx: Vector
    """ 

    :type: Vector
    """

    xyxy: Vector
    """ 

    :type: Vector
    """

    xyxz: Vector
    """ 

    :type: Vector
    """

    xyy: Vector
    """ 

    :type: Vector
    """

    xyyw: Vector
    """ 

    :type: Vector
    """

    xyyx: Vector
    """ 

    :type: Vector
    """

    xyyy: Vector
    """ 

    :type: Vector
    """

    xyyz: Vector
    """ 

    :type: Vector
    """

    xyz: Vector
    """ 

    :type: Vector
    """

    xyzw: Vector
    """ 

    :type: Vector
    """

    xyzx: Vector
    """ 

    :type: Vector
    """

    xyzy: Vector
    """ 

    :type: Vector
    """

    xyzz: Vector
    """ 

    :type: Vector
    """

    xz: Vector
    """ 

    :type: Vector
    """

    xzw: Vector
    """ 

    :type: Vector
    """

    xzww: Vector
    """ 

    :type: Vector
    """

    xzwx: Vector
    """ 

    :type: Vector
    """

    xzwy: Vector
    """ 

    :type: Vector
    """

    xzwz: Vector
    """ 

    :type: Vector
    """

    xzx: Vector
    """ 

    :type: Vector
    """

    xzxw: Vector
    """ 

    :type: Vector
    """

    xzxx: Vector
    """ 

    :type: Vector
    """

    xzxy: Vector
    """ 

    :type: Vector
    """

    xzxz: Vector
    """ 

    :type: Vector
    """

    xzy: Vector
    """ 

    :type: Vector
    """

    xzyw: Vector
    """ 

    :type: Vector
    """

    xzyx: Vector
    """ 

    :type: Vector
    """

    xzyy: Vector
    """ 

    :type: Vector
    """

    xzyz: Vector
    """ 

    :type: Vector
    """

    xzz: Vector
    """ 

    :type: Vector
    """

    xzzw: Vector
    """ 

    :type: Vector
    """

    xzzx: Vector
    """ 

    :type: Vector
    """

    xzzy: Vector
    """ 

    :type: Vector
    """

    xzzz: Vector
    """ 

    :type: Vector
    """

    y: float
    """ Vector Y axis.

    :type: float
    """

    yw: Vector
    """ 

    :type: Vector
    """

    yww: Vector
    """ 

    :type: Vector
    """

    ywww: Vector
    """ 

    :type: Vector
    """

    ywwx: Vector
    """ 

    :type: Vector
    """

    ywwy: Vector
    """ 

    :type: Vector
    """

    ywwz: Vector
    """ 

    :type: Vector
    """

    ywx: Vector
    """ 

    :type: Vector
    """

    ywxw: Vector
    """ 

    :type: Vector
    """

    ywxx: Vector
    """ 

    :type: Vector
    """

    ywxy: Vector
    """ 

    :type: Vector
    """

    ywxz: Vector
    """ 

    :type: Vector
    """

    ywy: Vector
    """ 

    :type: Vector
    """

    ywyw: Vector
    """ 

    :type: Vector
    """

    ywyx: Vector
    """ 

    :type: Vector
    """

    ywyy: Vector
    """ 

    :type: Vector
    """

    ywyz: Vector
    """ 

    :type: Vector
    """

    ywz: Vector
    """ 

    :type: Vector
    """

    ywzw: Vector
    """ 

    :type: Vector
    """

    ywzx: Vector
    """ 

    :type: Vector
    """

    ywzy: Vector
    """ 

    :type: Vector
    """

    ywzz: Vector
    """ 

    :type: Vector
    """

    yx: Vector
    """ 

    :type: Vector
    """

    yxw: Vector
    """ 

    :type: Vector
    """

    yxww: Vector
    """ 

    :type: Vector
    """

    yxwx: Vector
    """ 

    :type: Vector
    """

    yxwy: Vector
    """ 

    :type: Vector
    """

    yxwz: Vector
    """ 

    :type: Vector
    """

    yxx: Vector
    """ 

    :type: Vector
    """

    yxxw: Vector
    """ 

    :type: Vector
    """

    yxxx: Vector
    """ 

    :type: Vector
    """

    yxxy: Vector
    """ 

    :type: Vector
    """

    yxxz: Vector
    """ 

    :type: Vector
    """

    yxy: Vector
    """ 

    :type: Vector
    """

    yxyw: Vector
    """ 

    :type: Vector
    """

    yxyx: Vector
    """ 

    :type: Vector
    """

    yxyy: Vector
    """ 

    :type: Vector
    """

    yxyz: Vector
    """ 

    :type: Vector
    """

    yxz: Vector
    """ 

    :type: Vector
    """

    yxzw: Vector
    """ 

    :type: Vector
    """

    yxzx: Vector
    """ 

    :type: Vector
    """

    yxzy: Vector
    """ 

    :type: Vector
    """

    yxzz: Vector
    """ 

    :type: Vector
    """

    yy: Vector
    """ 

    :type: Vector
    """

    yyw: Vector
    """ 

    :type: Vector
    """

    yyww: Vector
    """ 

    :type: Vector
    """

    yywx: Vector
    """ 

    :type: Vector
    """

    yywy: Vector
    """ 

    :type: Vector
    """

    yywz: Vector
    """ 

    :type: Vector
    """

    yyx: Vector
    """ 

    :type: Vector
    """

    yyxw: Vector
    """ 

    :type: Vector
    """

    yyxx: Vector
    """ 

    :type: Vector
    """

    yyxy: Vector
    """ 

    :type: Vector
    """

    yyxz: Vector
    """ 

    :type: Vector
    """

    yyy: Vector
    """ 

    :type: Vector
    """

    yyyw: Vector
    """ 

    :type: Vector
    """

    yyyx: Vector
    """ 

    :type: Vector
    """

    yyyy: Vector
    """ 

    :type: Vector
    """

    yyyz: Vector
    """ 

    :type: Vector
    """

    yyz: Vector
    """ 

    :type: Vector
    """

    yyzw: Vector
    """ 

    :type: Vector
    """

    yyzx: Vector
    """ 

    :type: Vector
    """

    yyzy: Vector
    """ 

    :type: Vector
    """

    yyzz: Vector
    """ 

    :type: Vector
    """

    yz: Vector
    """ 

    :type: Vector
    """

    yzw: Vector
    """ 

    :type: Vector
    """

    yzww: Vector
    """ 

    :type: Vector
    """

    yzwx: Vector
    """ 

    :type: Vector
    """

    yzwy: Vector
    """ 

    :type: Vector
    """

    yzwz: Vector
    """ 

    :type: Vector
    """

    yzx: Vector
    """ 

    :type: Vector
    """

    yzxw: Vector
    """ 

    :type: Vector
    """

    yzxx: Vector
    """ 

    :type: Vector
    """

    yzxy: Vector
    """ 

    :type: Vector
    """

    yzxz: Vector
    """ 

    :type: Vector
    """

    yzy: Vector
    """ 

    :type: Vector
    """

    yzyw: Vector
    """ 

    :type: Vector
    """

    yzyx: Vector
    """ 

    :type: Vector
    """

    yzyy: Vector
    """ 

    :type: Vector
    """

    yzyz: Vector
    """ 

    :type: Vector
    """

    yzz: Vector
    """ 

    :type: Vector
    """

    yzzw: Vector
    """ 

    :type: Vector
    """

    yzzx: Vector
    """ 

    :type: Vector
    """

    yzzy: Vector
    """ 

    :type: Vector
    """

    yzzz: Vector
    """ 

    :type: Vector
    """

    z: float
    """ Vector Z axis (3D Vectors only).

    :type: float
    """

    zw: Vector
    """ 

    :type: Vector
    """

    zww: Vector
    """ 

    :type: Vector
    """

    zwww: Vector
    """ 

    :type: Vector
    """

    zwwx: Vector
    """ 

    :type: Vector
    """

    zwwy: Vector
    """ 

    :type: Vector
    """

    zwwz: Vector
    """ 

    :type: Vector
    """

    zwx: Vector
    """ 

    :type: Vector
    """

    zwxw: Vector
    """ 

    :type: Vector
    """

    zwxx: Vector
    """ 

    :type: Vector
    """

    zwxy: Vector
    """ 

    :type: Vector
    """

    zwxz: Vector
    """ 

    :type: Vector
    """

    zwy: Vector
    """ 

    :type: Vector
    """

    zwyw: Vector
    """ 

    :type: Vector
    """

    zwyx: Vector
    """ 

    :type: Vector
    """

    zwyy: Vector
    """ 

    :type: Vector
    """

    zwyz: Vector
    """ 

    :type: Vector
    """

    zwz: Vector
    """ 

    :type: Vector
    """

    zwzw: Vector
    """ 

    :type: Vector
    """

    zwzx: Vector
    """ 

    :type: Vector
    """

    zwzy: Vector
    """ 

    :type: Vector
    """

    zwzz: Vector
    """ 

    :type: Vector
    """

    zx: Vector
    """ 

    :type: Vector
    """

    zxw: Vector
    """ 

    :type: Vector
    """

    zxww: Vector
    """ 

    :type: Vector
    """

    zxwx: Vector
    """ 

    :type: Vector
    """

    zxwy: Vector
    """ 

    :type: Vector
    """

    zxwz: Vector
    """ 

    :type: Vector
    """

    zxx: Vector
    """ 

    :type: Vector
    """

    zxxw: Vector
    """ 

    :type: Vector
    """

    zxxx: Vector
    """ 

    :type: Vector
    """

    zxxy: Vector
    """ 

    :type: Vector
    """

    zxxz: Vector
    """ 

    :type: Vector
    """

    zxy: Vector
    """ 

    :type: Vector
    """

    zxyw: Vector
    """ 

    :type: Vector
    """

    zxyx: Vector
    """ 

    :type: Vector
    """

    zxyy: Vector
    """ 

    :type: Vector
    """

    zxyz: Vector
    """ 

    :type: Vector
    """

    zxz: Vector
    """ 

    :type: Vector
    """

    zxzw: Vector
    """ 

    :type: Vector
    """

    zxzx: Vector
    """ 

    :type: Vector
    """

    zxzy: Vector
    """ 

    :type: Vector
    """

    zxzz: Vector
    """ 

    :type: Vector
    """

    zy: Vector
    """ 

    :type: Vector
    """

    zyw: Vector
    """ 

    :type: Vector
    """

    zyww: Vector
    """ 

    :type: Vector
    """

    zywx: Vector
    """ 

    :type: Vector
    """

    zywy: Vector
    """ 

    :type: Vector
    """

    zywz: Vector
    """ 

    :type: Vector
    """

    zyx: Vector
    """ 

    :type: Vector
    """

    zyxw: Vector
    """ 

    :type: Vector
    """

    zyxx: Vector
    """ 

    :type: Vector
    """

    zyxy: Vector
    """ 

    :type: Vector
    """

    zyxz: Vector
    """ 

    :type: Vector
    """

    zyy: Vector
    """ 

    :type: Vector
    """

    zyyw: Vector
    """ 

    :type: Vector
    """

    zyyx: Vector
    """ 

    :type: Vector
    """

    zyyy: Vector
    """ 

    :type: Vector
    """

    zyyz: Vector
    """ 

    :type: Vector
    """

    zyz: Vector
    """ 

    :type: Vector
    """

    zyzw: Vector
    """ 

    :type: Vector
    """

    zyzx: Vector
    """ 

    :type: Vector
    """

    zyzy: Vector
    """ 

    :type: Vector
    """

    zyzz: Vector
    """ 

    :type: Vector
    """

    zz: Vector
    """ 

    :type: Vector
    """

    zzw: Vector
    """ 

    :type: Vector
    """

    zzww: Vector
    """ 

    :type: Vector
    """

    zzwx: Vector
    """ 

    :type: Vector
    """

    zzwy: Vector
    """ 

    :type: Vector
    """

    zzwz: Vector
    """ 

    :type: Vector
    """

    zzx: Vector
    """ 

    :type: Vector
    """

    zzxw: Vector
    """ 

    :type: Vector
    """

    zzxx: Vector
    """ 

    :type: Vector
    """

    zzxy: Vector
    """ 

    :type: Vector
    """

    zzxz: Vector
    """ 

    :type: Vector
    """

    zzy: Vector
    """ 

    :type: Vector
    """

    zzyw: Vector
    """ 

    :type: Vector
    """

    zzyx: Vector
    """ 

    :type: Vector
    """

    zzyy: Vector
    """ 

    :type: Vector
    """

    zzyz: Vector
    """ 

    :type: Vector
    """

    zzz: Vector
    """ 

    :type: Vector
    """

    zzzw: Vector
    """ 

    :type: Vector
    """

    zzzx: Vector
    """ 

    :type: Vector
    """

    zzzy: Vector
    """ 

    :type: Vector
    """

    zzzz: Vector
    """ 

    :type: Vector
    """

    @classmethod
    def Fill(cls, size: int, fill: float = 0.0):
        """Create a vector of length size with all values set to fill.

        :param size: The length of the vector to be created.
        :type size: int
        :param fill: The value used to fill the vector.
        :type fill: float
        """
        ...

    @classmethod
    def Linspace(cls, start: int, stop: int, size: int):
        """Create a vector of the specified size which is filled with linearly spaced values between start and stop values.

        :param start: The start of the range used to fill the vector.
        :type start: int
        :param stop: The end of the range used to fill the vector.
        :type stop: int
        :param size: The size of the vector to be created.
        :type size: int
        """
        ...

    @classmethod
    def Range(cls, start: int, stop: int, step: int = 1):
        """Create a filled with a range of values.

        :param start: The start of the range used to fill the vector.
        :type start: int
        :param stop: The end of the range used to fill the vector.
        :type stop: int
        :param step: The step between successive values in the vector.
        :type step: int
        """
        ...

    @classmethod
    def Repeat(cls, vector: Vector | collections.abc.Sequence[float], size: int):
        """Create a vector by repeating the values in vector until the required size is reached.

        :param vector: The vector to draw values from.
        :type vector: Vector | collections.abc.Sequence[float]
        :param size: The size of the vector to be created.
        :type size: int
        """
        ...

    def angle(
        self,
        other: Vector | collections.abc.Sequence[float],
        fallback: typing.Any = None,
    ) -> float:
        """Return the angle between two vectors.

                :param other: another vector to compare the angle with
                :type other: Vector | collections.abc.Sequence[float]
                :param fallback: return this when the angle can't be calculated (zero length vector),
        (instead of raising a `ValueError`).
                :type fallback: typing.Any
                :return: angle in radians or fallback when given
                :rtype: float
        """
        ...

    def angle_signed(
        self, other: Vector | collections.abc.Sequence[float], fallback: typing.Any
    ) -> float:
        """Return the signed angle between two 2D vectors (clockwise is positive).

                :param other: another vector to compare the angle with
                :type other: Vector | collections.abc.Sequence[float]
                :param fallback: return this when the angle can't be calculated (zero length vector),
        (instead of raising a `ValueError`).
                :type fallback: typing.Any
                :return: angle in radians or fallback when given
                :rtype: float
        """
        ...

    def copy(self) -> Vector:
        """Returns a copy of this vector.

        :return: A copy of the vector.
        :rtype: Vector
        """
        ...

    def cross(self, other: Vector | collections.abc.Sequence[float]) -> Vector:
        """Return the cross product of this vector and another.

        :param other: The other vector to perform the cross product with.
        :type other: Vector | collections.abc.Sequence[float]
        :return: The cross product.
        :rtype: Vector
        """
        ...

    def dot(self, other: Vector | collections.abc.Sequence[float]) -> float:
        """Return the dot product of this vector and another.

        :param other: The other vector to perform the dot product with.
        :type other: Vector | collections.abc.Sequence[float]
        :return: The dot product.
        :rtype: float
        """
        ...

    def freeze(self) -> Vector:
        """Make this object immutable.After this the object can be hashed, used in dictionaries & sets.

        :return: An instance of this object.
        :rtype: Vector
        """
        ...

    def lerp(
        self, other: Vector | collections.abc.Sequence[float], factor: float
    ) -> Vector:
        """Returns the interpolation of two vectors.

        :param other: value to interpolate with.
        :type other: Vector | collections.abc.Sequence[float]
        :param factor: The interpolation value in [0.0, 1.0].
        :type factor: float
        :return: The interpolated vector.
        :rtype: Vector
        """
        ...

    def negate(self):
        """Set all values to their negative."""
        ...

    def normalize(self):
        """Normalize the vector, making the length of the vector always 1.0."""
        ...

    def normalized(self) -> Vector:
        """Return a new, normalized vector.

        :return: a normalized copy of the vector
        :rtype: Vector
        """
        ...

    def orthogonal(self) -> Vector:
        """Return a perpendicular vector.

        :return: a new vector 90 degrees from this vector.
        :rtype: Vector
        """
        ...

    def project(self, other: Vector | collections.abc.Sequence[float]) -> Vector:
        """Return the projection of this vector onto the other.

        :param other: second vector.
        :type other: Vector | collections.abc.Sequence[float]
        :return: the parallel projection vector
        :rtype: Vector
        """
        ...

    def reflect(self, mirror: Vector | collections.abc.Sequence[float]) -> Vector:
        """Return the reflection vector from the mirror argument.

        :param mirror: This vector could be a normal from the reflecting surface.
        :type mirror: Vector | collections.abc.Sequence[float]
        :return: The reflected vector matching the size of this vector.
        :rtype: Vector
        """
        ...

    def resize(self, size=3):
        """Resize the vector to have size number of elements.

        :param size:
        """
        ...

    def resize_2d(self):
        """Resize the vector to 2D  (x, y)."""
        ...

    def resize_3d(self):
        """Resize the vector to 3D  (x, y, z)."""
        ...

    def resize_4d(self):
        """Resize the vector to 4D (x, y, z, w)."""
        ...

    def resized(self, size=3) -> Vector:
        """Return a resized copy of the vector with size number of elements.

        :param size:
        :return: a new vector
        :rtype: Vector
        """
        ...

    def rotate(
        self,
        other: Euler
        | Matrix
        | Quaternion
        | collections.abc.Sequence[collections.abc.Sequence[float]]
        | collections.abc.Sequence[float],
    ):
        """Rotate the vector by a rotation value.

        :param other: rotation component of mathutils value
        :type other: Euler | Matrix | Quaternion | collections.abc.Sequence[collections.abc.Sequence[float]] | collections.abc.Sequence[float]
        """
        ...

    def rotation_difference(
        self, other: Vector | collections.abc.Sequence[float]
    ) -> Quaternion:
        """Returns a quaternion representing the rotational difference between this
        vector and another.

                :param other: second vector.
                :type other: Vector | collections.abc.Sequence[float]
                :return: the rotational difference between the two vectors.
                :rtype: Quaternion
        """
        ...

    def slerp(
        self,
        other: Vector | collections.abc.Sequence[float],
        factor: float,
        fallback: typing.Any = None,
    ) -> Vector:
        """Returns the interpolation of two non-zero vectors (spherical coordinates).

                :param other: value to interpolate with.
                :type other: Vector | collections.abc.Sequence[float]
                :param factor: The interpolation value typically in [0.0, 1.0].
                :type factor: float
                :param fallback: return this when the vector can't be calculated (zero length vector or direct opposites),
        (instead of raising a `ValueError`).
                :type fallback: typing.Any
                :return: The interpolated vector.
                :rtype: Vector
        """
        ...

    def to_2d(self) -> Vector:
        """Return a 2d copy of the vector.

        :return: a new vector
        :rtype: Vector
        """
        ...

    def to_3d(self) -> Vector:
        """Return a 3d copy of the vector.

        :return: a new vector
        :rtype: Vector
        """
        ...

    def to_4d(self) -> Vector:
        """Return a 4d copy of the vector.

        :return: a new vector
        :rtype: Vector
        """
        ...

    def to_track_quat(self, track: str, up: str) -> Quaternion:
        """Return a quaternion rotation from the vector and the track and up axis.

        :param track: Track axis in ['X', 'Y', 'Z', '-X', '-Y', '-Z'].
        :type track: str
        :param up: Up axis in ['X', 'Y', 'Z'].
        :type up: str
        :return: rotation from the vector and the track and up axis.
        :rtype: Quaternion
        """
        ...

    def to_tuple(self, precision: int = -1) -> tuple:
        """Return this vector as a tuple with.

        :param precision: The number to round the value to in [-1, 21].
        :type precision: int
        :return: the values of the vector rounded by precision
        :rtype: tuple
        """
        ...

    def zero(self):
        """Set all values to zero."""
        ...

    def __init__(self, seq=(0.0, 0.0, 0.0)):
        """

        :param seq:
        """
        ...

    def __get__(self, instance, owner) -> Vector:
        """

        :param instance:
        :param owner:
        :return:
        :rtype: Vector
        """
        ...

    def __set__(self, instance, value: Vector | collections.abc.Sequence[float]):
        """

        :param instance:
        :param value:
        :type value: Vector | collections.abc.Sequence[float]
        """
        ...

    def __len__(self) -> int:
        """

        :return:
        :rtype: int
        """
        ...

    @typing.overload
    def __getitem__(self, key: int) -> float:
        """

        :param key:
        :type key: int
        :return:
        :rtype: float
        """
        ...

    @typing.overload
    def __getitem__(self, key: slice) -> tuple[float, ...]:
        """

        :param key:
        :type key: slice
        :return:
        :rtype: tuple[float, ...]
        """
        ...

    @typing.overload
    def __setitem__(self, key: int, value: float):
        """

        :param key:
        :type key: int
        :param value:
        :type value: float
        """
        ...

    @typing.overload
    def __setitem__(self, key: slice, value: collections.abc.Iterable[float]):
        """

        :param key:
        :type key: slice
        :param value:
        :type value: collections.abc.Iterable[float]
        """
        ...

    def __neg__(self) -> Vector:
        """

        :return:
        :rtype: Vector
        """
        ...

    def __add__(self, other: Vector | collections.abc.Sequence[float]) -> Vector:
        """

        :param other:
        :type other: Vector | collections.abc.Sequence[float]
        :return:
        :rtype: Vector
        """
        ...

    def __sub__(self, other: Vector | collections.abc.Sequence[float]) -> Vector:
        """

        :param other:
        :type other: Vector | collections.abc.Sequence[float]
        :return:
        :rtype: Vector
        """
        ...

    def __mul__(self, other: float | int) -> Vector:
        """

        :param other:
        :type other: float | int
        :return:
        :rtype: Vector
        """
        ...

    def __truediv__(self, other: float | int) -> Vector:
        """

        :param other:
        :type other: float | int
        :return:
        :rtype: Vector
        """
        ...

    @typing.overload
    def __matmul__(self, other: Vector | collections.abc.Sequence[float]) -> float:
        """

        :param other:
        :type other: Vector | collections.abc.Sequence[float]
        :return:
        :rtype: float
        """
        ...

    @typing.overload
    def __matmul__(
        self, other: Matrix | collections.abc.Sequence[collections.abc.Sequence[float]]
    ) -> Vector:
        """

        :param other:
        :type other: Matrix | collections.abc.Sequence[collections.abc.Sequence[float]]
        :return:
        :rtype: Vector
        """
        ...

    def __radd__(self, other: Vector | collections.abc.Sequence[float]) -> Vector:
        """

        :param other:
        :type other: Vector | collections.abc.Sequence[float]
        :return:
        :rtype: Vector
        """
        ...

    def __rsub__(self, other: Vector | collections.abc.Sequence[float]) -> Vector:
        """

        :param other:
        :type other: Vector | collections.abc.Sequence[float]
        :return:
        :rtype: Vector
        """
        ...

    def __rmul__(self, other: float | int) -> Vector:
        """

        :param other:
        :type other: float | int
        :return:
        :rtype: Vector
        """
        ...

    def __rtruediv__(self, other: float | int) -> Vector:
        """

        :param other:
        :type other: float | int
        :return:
        :rtype: Vector
        """
        ...

    def __iadd__(self, other: Vector | collections.abc.Sequence[float]) -> Vector:
        """

        :param other:
        :type other: Vector | collections.abc.Sequence[float]
        :return:
        :rtype: Vector
        """
        ...

    def __isub__(self, other: Vector | collections.abc.Sequence[float]) -> Vector:
        """

        :param other:
        :type other: Vector | collections.abc.Sequence[float]
        :return:
        :rtype: Vector
        """
        ...

    def __imul__(self, other: float | int) -> Vector:
        """

        :param other:
        :type other: float | int
        :return:
        :rtype: Vector
        """
        ...

    def __itruediv__(self, other: float | int) -> Vector:
        """

        :param other:
        :type other: float | int
        :return:
        :rtype: Vector
        """
        ...
