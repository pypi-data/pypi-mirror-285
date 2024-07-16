"""All code relating to the Blockset class"""

from bisect import bisect_left
from copy import deepcopy
from enum import Enum
from json import JSONEncoder
from typing import Self
from warnings import warn
from blocksets.classes.block import Block
from blocksets.classes.exceptions import (
    DimensionMismatchError,
    ExpectedBlockSetError,
    InvalidDimensionsError,
    NotFiniteError,
)


class OperationType(Enum):
    """Simple enumeration for add, remove and toggle operations"""

    ADD = "+"
    REMOVE = "-"
    TOGGLE = "~"


class BlockSet:
    """A set of Blocks which are of the same dimension.

    Although the class offers methods and behaviour similar to that of a set,
    the actual construction of the set using Blocks happens via an operation
    stack which gets resolved during a normalisation process.

    In normalized form all the resulting blocks are disjoint and are kept on the
    operation stack as add operations

    The normalisation process resolves overlapping and redundancy such that any
    2 sets of equal content (i.e. the same set of pixels) will have the same
    representation in terms of the blocks used to represent the space.

    Methods and operators mirror those of the native set class - Modify the
    content (add, remove, toggle) - Compare (equality, subset, superset) -
    Compare operations (intersection, union, difference)

    There is some extra validation on some methods to ensure the supplied
    arguments are, or can be interpreted as a Block/BlockSet and match the
    dimension of the current content.

    Normalisation is required and important (for accurate comparisons) but also
    costly. We only want to perform it when its absolutely necessary and so
    clients are advised to group together modification calls as much as possible
    in order to minimise the amount of normalising required and especially so if
    performance is of a significant concern.

    Some methods/properties will perform normalisation automatically if required.

    Once constructed, Block objects can be appended to the operation stack via
    the add, remove and toggle methods.

    """

    def __init__(self, dimensions: int | None = None) -> None:
        """Create a Blockset, optionally provide the dimensions for more strict and performant use

        Args:
            dimensions (int | None, optional): Specify the dimensions if you like. Defaults to None.

        Raises:
            InvalidDimensionsError: If not an integer or < 1
        """
        self.clear()
        if dimensions is not None:
            if not isinstance(dimensions, int):
                raise InvalidDimensionsError()
            if dimensions < 1:
                raise InvalidDimensionsError()
        self._dimensions = dimensions
        self._marker_ordinates = []
        self._marker_stack = []

    #
    # Representation
    #

    def __repr__(self) -> str:
        op_stack = [(op.value, blk.norm) for op, blk in self._operation_stack]
        return str(op_stack)

    def __str__(self) -> str:
        self.normalise()
        if self.is_finite:
            return f"BlockSet ({self.dimensions}D): {len(self)} Blocks, {self.measure} Units"
        return f"BlockSet ({self.dimensions}D): {len(self)} Blocks - Infinite"

    def __format__(self, format_spec) -> str:
        return format(str(self), format_spec)

    #
    # Existence & Iteration
    #

    def __bool__(self) -> bool:
        return not self.is_empty

    def __iter__(self):
        for blk in self._blocks():
            yield blk

    def __len__(self):
        return len(self._operation_stack)

    def __contains__(self, item) -> bool:
        if self.dimensions is None:
            return False
        else:
            item = Block.parse_to_dimension(self.dimensions, item)
        temp_bs = BlockSet(self.dimensions)
        temp_bs.add(item)
        return temp_bs <= self

    def units(self):
        """Generator for the unit tuples within all the blocks

        Raises:
            NotFiniteError: If any of the blocks are infinite

        Yields:
            tuple: A unit pixel
        """
        self.normalise()
        if not self.is_finite:
            raise NotFiniteError()
        for blk in self:
            for u in blk:
                yield u

    #
    # Comparisons
    #

    def __eq__(self, value: object) -> bool:
        self._validate_operation_argument(value)
        # leverage python set equals operation
        value_set = set(value)
        self_set = set(self)
        return self_set == value_set

    def __ge__(self, value: object) -> Self:
        return self.issuperset(value)

    def __gt__(self, value: object) -> Self:
        return self.issuperset(value) and self != value

    def __le__(self, value: object) -> Self:
        return self.issubset(value)

    def __lt__(self, value: object) -> Self:
        return self.issubset(value) and self != value

    #
    # Operations
    #

    def __and__(self, value: object) -> Self:
        return self.intersection(value)

    def __iand__(self, value: object) -> Self:
        return self.intersection_update(value)

    def __or__(self, value: object) -> Self:
        return self.union(value)

    def __ior__(self, value: object) -> Self:
        return self.update(value)

    def __sub__(self, value: object) -> Self:
        return self.difference(value)

    def __xor__(self, value: object) -> Self:
        return self.symmetric_difference(value)

    def __ixor__(self, value: object) -> Self:
        return self.symmetric_difference_update(value)

    #
    # Properties
    #

    @property
    def dimensions(self) -> int:
        """Returns number of dimensions of the blockset

        Returns:
            int: The dimension of the contained blocks
        """
        if self._dimensions:
            return self._dimensions

        if self._operation_stack:
            _, block = self._operation_stack[0]
            if isinstance(block, Block):
                return block.dimensions

        return None

    @property
    def is_empty(self) -> bool:
        """Returns True if empty

        Returns:
            bool: True if empty
        """
        self.normalise()
        return not bool(self._operation_stack)

    @property
    def is_finite(self) -> bool:
        """Returns True if all blocks are finite

        Returns:
            bool: True if finite
        """
        self.normalise()
        return all(blk.is_finite for blk in self)

    @property
    def is_normalised(self) -> bool:
        """Return the normalisation state

        Returns:
            bool: True if the BlockSet is in a Normalised state
        """
        return self._normalised

    @property
    def measure(self) -> int:
        """Returns the total amount of space the block set is taking up.
        This is effectively the sum of all the disjoint block measures after
        normalisation.

        Returns:
            int: unit count = sum of disjoint block measures
        """
        self.normalise()
        return sum(blk.measure for blk in self)

    #
    # Deprecated properties
    #

    @property
    def block_count(self) -> int:
        """Returns the number of block operations on the stack.
        After normalisation this is simply the number of blocks

        Returns:
            int: block count

        **NOTE: This property is deprecated in favour of `len()` after a `normalise()`
        and will not be available as of the first major release.**
        """
        warn(
            "This property is deprecated in favour of len() after normalise() "
            "and will not be available as of the first major release.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.normalise()
        return len(self._operation_stack)

    @property
    def unit_count(self) -> int:
        """Returns the total amount of space the block set is taking up.
        This is effectively the sum of all the disjoint block measures after
        normalisation.

        Returns:
            int: point count

        **NOTE: This property is deprecated in favour of `measure`
        and will not be available as of the first major release.**
        """
        warn(
            "This property is deprecated in favour of measure "
            "and will not be available as of the first major release.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.normalise()
        return sum(blk.measure for blk in self)

    #
    # Content modifiers (Block Operations)
    #

    def add(self, blk: Block):
        """Append an add block operation to the stack

        Args:
            blk (Block): A block
        """
        blk = Block.parse_to_dimension(self.dimensions, blk)
        self._operation_stack.append((OperationType.ADD, blk))
        self._normalised = False

    def clear(self):
        """Clear the operation stack"""
        self._normalised = True
        self._operation_stack = []

    def remove(self, blk: Block):
        """Append a remove block operation to the stack

        Args:
            blk (Block): A block
        """

        blk = Block.parse_to_dimension(self.dimensions, blk)
        self._operation_stack.append((OperationType.REMOVE, blk))
        self._normalised = False

    def toggle(self, blk: Block):
        """Append a toggle block operation to the stack

        Args:
            blk (Block): A block
        """
        blk = Block.parse_to_dimension(self.dimensions, blk)
        self._operation_stack.append((OperationType.TOGGLE, blk))
        self._normalised = False

    #
    # Normalisation
    #

    def normalise(self):
        """Normalise the BlockSet

        This will analyse all the operations stack and resolve it to a disjoint set of add operations
        removing redundancy.
        """

        def markers_to_ordinates(marker_tuple):
            return tuple(
                self._marker_ordinates[d][m] for d, m in enumerate(marker_tuple)
            )

        if self._normalised:
            return

        self._refresh_marker_ordinates()
        self._refresh_marker_stack()

        normalised_markers = self._normalise_recursively(self._marker_stack)

        # replace the operation stack with ADD operations for the normalised result
        self._operation_stack = [
            (
                OperationType.ADD,
                Block(markers_to_ordinates(a), (markers_to_ordinates(b))),
            )
            for a, b in normalised_markers
        ]

        self._normalised = True

    #
    # Set operations - implementation
    # returning a new blockset
    #

    def difference(self, other: Self) -> Self:
        """Return a new block set representing the difference `self - other`

        Args:
            other (BlockSet): The BlockSet being removed

        Raises:
            ExpectedBlockSetError: If not given a BlockSet for other

        Returns:
            BlockSet: self - other

        """

        # There is no need to normalise self or the result as we are simply
        # adding further REMOVE operations. But this does mean the other block
        # set will become normalised upon iterating over the blocks.

        self._validate_operation_argument(other)
        # we are not looking to update this block set so we take a copy
        # of self as the starting point for building the result
        result = deepcopy(self)
        for blk in other:
            result.remove(blk)
        return result

    def intersection(self, other: Self) -> Self:
        """Return a new block set representing the intersection with the other `self & other`.

        Args:
            other (BlockSet): The BlockSet to intersect with

        Returns:
            BlockSet: self ∩ other
        """
        # The result is achieved by taking a copy of self, removing the other
        # and then toggling the original self.

        self._validate_operation_argument(other)
        # we are not looking to update this block set so we take a copy
        # of self as the starting point for building the result
        result = deepcopy(self)
        result.normalise()
        self_blocks = set(result)
        other.normalise()

        for blk in other:
            result.remove(blk)

        for blk in self_blocks:
            result.toggle(blk)

        result.normalise()
        return result

    def symmetric_difference(self, other: Self) -> Self:
        """Return a new block set representing the symmetric difference (xor) with the other
        `self ^ other`

        Args:
            other (BlockSet): The BlockSet being XOR'd

        Raises:
            ExpectedBlockSetError: If not given a BlockSet for other

        Returns:
            BlockSet: self ⊕ other
        """

        # We should normalise the copy of self first as we over laying
        # further TOGGLE operations.

        self._validate_operation_argument(other)
        # we are not looking to update this block set so we take a copy
        # of self as the starting point for building the result
        result = deepcopy(self)
        result.normalise()
        for blk in other:
            result.toggle(blk)
        return result

    def union(self, other: Self) -> Self:
        """Return a new block set representing a union with another `self | other`

        Args:
            other (BlockSet): The BlockSet to union with

        Raises:
            ExpectedBlockSetError: If not given a BlockSet for other

        Returns:
            BlockSet: self ∪ other
        """

        # There is no need to normalise self or the result as we are simply
        # adding further ADD operations. But this does mean the other block
        # set will become normalised upon iterating over the blocks.

        self._validate_operation_argument(other)

        # we are not looking to update this block set so we take a copy
        # of self as the starting point for building the result
        result = deepcopy(self)
        for blk in other:
            result.add(blk)
        return result

    #
    # Set operations - implementation
    # updating a blockset
    #

    def difference_update(self, other: Self) -> Self:
        """Remove space from self that is in the other.

        Args:
            other (BlockSet): The BlockSet being removed

        Raises:
            ExpectedBlockSetError: If not given a BlockSet for other

        Returns:
            BlockSet: self
        """
        self._validate_operation_argument(other)
        for blk in other:
            self.remove(blk)
        return self

    def intersection_update(self, other: Self) -> Self:
        """Remove space from self that is not in the other

        Args:
            other (BlockSet): The intersecting BlockSet

        Returns:
            BlockSet: self
        """

        # Because of the way we do intersection it makes sense to leverage
        # the intersection method and effectively copy the resulting stack

        self._validate_operation_argument(other)
        result = self.intersection(other)
        self._operation_stack = result._operation_stack
        self._normalised = result._normalised
        return self

    def symmetric_difference_update(self, other: Self) -> Self:
        """Adds the symmetric differences between self and other

        Args:
            other (BlockSet): The differing BlockSet

        Raises:
            ExpectedBlockSetError: If not given a BlockSet for other

        Returns:
            BlockSet: self
        """
        self._validate_operation_argument(other)
        self.normalise()
        for blk in other:
            self.toggle(blk)
        return self

    def update(self, other: Self) -> Self:
        """Update this block set with another, effectively applying the union to self

        Args:
            other (BlockSet): The BlockSet being added

        Returns:
            BlockSet: self
        """
        self._validate_operation_argument(other)
        for blk in other:
            self.add(blk)
        return self

    #
    # Comparisons - implementation
    #

    def isdisjoint(self, other: Self) -> bool:
        """Returns `True` if the block sets are completely disjoint from each other

        Args:
            other (BlockSet): Compare to

        Returns:
            bool: True if there is no overlapping space
        """
        self._validate_operation_argument(other)
        self.normalise()
        other.normalise()
        # 2 possible approaches
        # a) Get the intersection, return True if empty
        # b) Compare the cross product of blocks
        # Under which cases/circumstances one out performs the other
        # can be explored, for now we'll go with reuse of intersection
        result = self & other
        return result.is_empty

    def issubset(self, other: Self) -> bool:
        """Returns `True` if self is a subset of other `self <= other`

        Args:
            other (BlockSet): Compare to

        Returns:
            bool: True if self is a subset of other
        """
        self._validate_operation_argument(other)
        self.normalise()
        other.normalise()
        # Either union = other or intersection = self
        # for now union = other seems the most simple
        result = self | other
        return result == other

    def issuperset(self, other: Self) -> bool:
        """Returns `True` if self is a superset of other `self >= other`

        Args:
            other (BlockSet): Compare to

        Returns:
            bool: True if self is a superset of other
        """
        self._validate_operation_argument(other)
        self.normalise()
        other.normalise()
        # Either union = self or intersection = other
        # for now union = self seems the most simple
        result = self | other
        return result == self

    #
    # Other
    #

    def apply_json_obj(self, json_obj):
        """Applies layers from a json object

        We expect the json representation to be a list of pairs [operation, block].
        Where operation is either +,-,~ and the block is a tuple pair [A,B] where A/B are
        the coordinates of the opposite corners.

        The BlockSetEncoder class can be used to create the json from the blockset

        `json_str = json.dumps(blockset_object, cls=BlockSetEncoder)`

        Args:
            json_obj: Expecting a list of (operation, block) tuples
        """
        for op, n in json_obj:
            blk = Block.parse(n)
            if op == OperationType.ADD.value:
                self.add(blk)
            elif op == OperationType.REMOVE.value:
                self.remove(blk)
            elif op == OperationType.TOGGLE.value:
                self.toggle(blk)

    #
    # Private
    #

    def _blocks(self):
        """Generator for all the disjoint blocks after normalising

        Yields:
           Block: a block object
        """
        self.normalise()

        # after normalisation we have only add operations on disjoint blocks
        for _, blk in self._operation_stack:
            yield blk

    def _validate_operation_argument(self, a):
        """Validates the supplied argument

        Args:
            a: Expected block set

        Raises:
            ExpectedBlockSetError: If not a BlockSet object
            DimensionMismatchError: If of different dimension
        """
        if not isinstance(a, BlockSet):
            raise ExpectedBlockSetError()
        if a.dimensions != self.dimensions:
            raise DimensionMismatchError()

    def _refresh_marker_ordinates(self):
        """Refreshes _marker_ordinates which stores actual ordinate values of
        the grid markers"""

        self._marker_ordinates.clear()
        for d in range(self.dimensions):
            markers = set()
            for _, blk in self._operation_stack:
                markers.add(blk.a[d])
                markers.add(blk.b[d])
            markers = list(sorted(markers))
            self._marker_ordinates.append(markers)

    def _refresh_marker_stack(self):
        """Refreshes _marker_stack which is equivalent to _operation_stack but
        expressed as grid markers instead of the block ordinates"""

        self._marker_stack.clear()
        for op, blk in self._operation_stack:
            a = []
            b = []
            for d in range(self.dimensions):
                markers = self._marker_ordinates[d]
                a.append(bisect_left(markers, blk.a[d]))
                b.append(bisect_left(markers, blk.b[d]))
            entry = (op, (tuple(a), tuple(b)))
            self._marker_stack.append(entry)

    def _normalise_recursively(self, marker_stack: list, dimension: int = 0) -> set:
        """Return a normalised set of block markers

        Args:
            marker_stack (list): The marker stack to resolve
        """

        # Being in the last dimension is a special case so we note it up front
        last_dimension = False
        if self.dimensions == dimension + 1:
            last_dimension = True

        # Final result set
        normalised_blocks = set()

        # Used to handle the changes found in cross sections as scan through
        prev_normalised_x_sec = set()
        change_marker = None

        # For each marker in this dimension we get the cross section of
        # normalised blocks of the lower dimension.

        # If there is a change in the normalised blocks between cross sections
        # then this indicates we should create blocks in this dimension and add
        # them to our result set.

        for m in range(len(self._marker_ordinates[dimension])):

            # Get the operation stack for the lower dimension at this marker
            # If this is the last dimension then only the operation makes sense
            cross_section = [
                (op, None if last_dimension else (blk[0][1:], blk[1][1:]))
                for op, blk in marker_stack
                if blk[0][0] <= m < blk[1][0]
            ]

            if last_dimension:
                # If we are resolving the last dimension then we just need to
                # resolve the operations in reverse order (i.e. stack pop)
                # for this marker point.
                state = False
                for op, _ in cross_section[::-1]:
                    if op == OperationType.ADD:
                        state = not state
                        break
                    if op == OperationType.REMOVE:
                        break
                    if op == OperationType.TOGGLE:
                        state = not state

                # If the point should be present (i.e. True) then we represent that
                # as the set {True}, if not then the empty set.
                # This allows us to compare 2 cross sections as sets
                # in a consistent manner for all dimensions
                normalised_x_sec = set()
                if state:
                    normalised_x_sec = {True}

            else:
                # Get the normalised representation of this cross section
                # using recursion
                normalised_x_sec = self._normalise_recursively(
                    cross_section, dimension + 1
                )

            # By only adding blocks when there are cross section changes
            # we should hopefully remove redundant blocks
            if normalised_x_sec != prev_normalised_x_sec:

                if change_marker is not None:
                    if last_dimension and prev_normalised_x_sec:
                        normalised_blocks.add(((change_marker,), (m,)))
                    if not last_dimension:
                        for x in prev_normalised_x_sec:
                            a = (change_marker,) + x[0]
                            b = (m,) + x[1]
                            normalised_blocks.add((a, b))

                change_marker = m
                prev_normalised_x_sec = normalised_x_sec

        return normalised_blocks


class BlockSetEncoder(JSONEncoder):
    """Custom JSONEncoder for Blocksets
    Usage:
    json.dumps(data, cls=BlockSetEncoder)
    """

    def default(self, o):
        if isinstance(o, Block):
            return o.norm
        if isinstance(o, BlockSet):
            return list((op, blk.norm) for op, blk in o._operation_stack)
        if isinstance(o, OperationType):
            return o.value

        # Let the base class default method raise the TypeError
        return super().default(o)
