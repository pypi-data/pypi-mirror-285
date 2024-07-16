import logging
from dataclasses import dataclass, field
from functools import cached_property
from typing import Iterable, Mapping, Optional, Sequence, Set, Tuple, Union

import immutables as immu
from pyparsing import ParseResults

from tesseract_olap.common import get_localization

from .aggregators import Aggregator, Count
from .enums import DimensionType, MemberType
from .formulas import expr

logger = logging.getLogger(__name__)

# Named types
Annotations = Mapping[str, Optional[str]]
AnyMeasure = Union["Measure", "CalculatedMeasure"]
CaptionSet = Mapping[str, str]


@dataclass(eq=True, frozen=True)
class Schema:
    """Base Schema class."""

    name: str
    annotations: Annotations = field(default_factory=immu.Map)
    cube_map: Mapping[str, "Cube"] = field(default_factory=immu.Map)
    default_locale: str = "xx"
    shared_dimension_map: Mapping[str, "Dimension"] = field(default_factory=immu.Map)
    shared_table_map: Mapping[str, "InlineTable"] = field(default_factory=immu.Map)

    @classmethod
    def join(cls, *args: "Schema"):
        name = ""
        default_locale = "xx"
        annotations = {}
        cube_map = {}
        shared_dimension_map = {}
        shared_table_map = {}

        for sch in args:
            if sch.name != "":
                name = sch.name

            if sch.default_locale != "":
                default_locale = sch.default_locale

            annotations.update(sch.annotations)
            cube_map.update(sch.cube_map)
            shared_dimension_map.update(sch.shared_dimension_map)
            shared_table_map.update(sch.shared_table_map)

        return cls(
            name=name,
            default_locale=default_locale,
            annotations=annotations,
            cube_map=cube_map,
            shared_dimension_map=shared_dimension_map,
            shared_table_map=shared_table_map,
        )


@dataclass(eq=True, frozen=True, repr=False)
class AccessControl:
    public: bool = True
    rules: Mapping[str, bool] = field(default_factory=immu.Map)

    def __repr__(self):
        return "Public" if self.public else f"Private(rules=<{len(self.rules)}>)"

    def is_authorized(self, roles: Iterable[str]) -> bool:
        if self.public:
            return True
        rules = self.rules
        roles = {roles} if isinstance(roles, str) else roles
        if any(rules.get(role) is False for role in roles):  # restricted
            return False
        return any(rules.get(role, False) for role in roles)  # allowed


@dataclass(eq=True, frozen=True, repr=False)
class InlineTable:
    name: str
    headers: Tuple[str, ...]
    types: Tuple[MemberType, ...]
    rows: Iterable[Tuple[Union[float, str], ...]]

    def __repr__(self):
        return f"{type(self).__name__}(name={repr(self.name)})"

    @staticmethod
    def infer_types(rows: Iterable[Tuple[Union[float, str], ...]]):
        return tuple(MemberType.from_values(column) for column in zip(*rows))


class Entity:
    name: str
    annotations: Annotations
    captions: CaptionSet
    acl: AccessControl
    visible: bool

    def get_annotation(self, name: str) -> Optional[str]:
        """Retrieves an annotation for the entity.
        If the annotation is not defined, raises a :class:`KeyError`.
        """
        return self.annotations[name]

    def get_caption(self, locale: str = "xx") -> str:
        """Retrieves the caption of the entity for a certain locale.
        If the a caption hasn't been defined for said locale, will attempt to
        return the fallback caption, and if not defined either, will return the
        entity name.
        """
        caption = get_localization(self.captions, locale)
        return self.name if caption is None else caption

    def get_locale_available(self) -> Set[str]:
        """Retrieves the list of locales for whose a caption has been defined in
        this entity.
        """
        return set(self.captions.keys())

    def is_authorized(self, roles: Iterable[str]) -> bool:
        return self.acl.is_authorized(roles)


@dataclass(eq=True, frozen=True)
class Cube(Entity):
    name: str
    table: Union["InlineTable", "Table", str]
    acl: AccessControl = field(default_factory=AccessControl)
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    dimension_map: Mapping[str, Union["Dimension", "DimensionUsage"]] = field(
        default_factory=immu.Map
    )
    measure_map: Mapping[str, "AnyMeasure"] = field(default_factory=immu.Map)
    subset_table: bool = False
    visible: bool = True


@dataclass(eq=True, frozen=True)
class Table:
    name: str
    primary_key: str
    schema: Optional[str] = None


@dataclass(eq=True, frozen=True)
class Dimension(Entity):
    name: str
    default_hierarchy: str
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    dim_type: DimensionType = DimensionType.STANDARD
    foreign_key: Optional[str] = None
    hierarchy_map: Mapping[str, "Hierarchy"] = field(default_factory=immu.Map)
    visible: bool = True

    def get_default_hierarchy(self):
        return self.hierarchy_map[self.default_hierarchy]


@dataclass(eq=True, frozen=True)
class Hierarchy(Entity):
    name: str
    primary_key: str
    table: Union["InlineTable", "Table", str, None]
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    default_member: Optional[Tuple[str, str]] = None
    level_map: Mapping[str, "Level"] = field(default_factory=immu.Map)
    visible: bool = True


@dataclass(eq=True, frozen=True)
class Level(Entity):
    name: str
    depth: int
    key_column: str
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    name_column_map: Mapping[str, str] = field(default_factory=immu.Map)
    key_type: MemberType = MemberType.STRING
    property_map: Mapping[str, "Property"] = field(default_factory=immu.Map)
    visible: bool = True

    def get_name_column(self, locale: str = "xx") -> Optional[str]:
        return get_localization(self.name_column_map, locale)

    def get_locale_available(self) -> Set[str]:
        return set(self.captions.keys()).union(self.name_column_map.keys())


@dataclass(eq=True, frozen=True)
class Property(Entity):
    name: str
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    key_column_map: Mapping[str, str] = field(default_factory=immu.Map)
    key_type: MemberType = MemberType.STRING
    visible: bool = True

    def get_key_column(self, locale: str = "xx") -> str:
        return get_localization(self.key_column_map, locale, force=True)

    def get_locale_available(self) -> Set[str]:
        return set(self.captions.keys()).union(self.key_column_map.keys())


@dataclass(eq=True, frozen=True)
class Measure(Entity):
    name: str
    key_column: str
    aggregator: Aggregator = field(default_factory=Count)
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    submeasures: Mapping[str, "AnyMeasure"] = field(default_factory=immu.Map)
    visible: bool = True

    def and_submeasures(self):
        yield self
        yield from self.submeasures.values()


@dataclass(eq=True, frozen=True)
class CalculatedMeasure(Entity):
    name: str
    formula: ParseResults
    aggregator: Aggregator = field(default_factory=Count)
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    submeasures: Mapping[str, "AnyMeasure"] = field(default_factory=immu.Map)
    visible: bool = True

    def and_submeasures(self):
        yield self
        yield from self.submeasures.values()

    @cached_property
    def dependencies(self) -> Set[str]:
        columns = set()

        def _resolve_dependencies(item: ParseResults):
            if isinstance(item, ParseResults):
                values = item.get("columns", [[]])
                assert isinstance(
                    values, Sequence
                ), f"Retrieved columns are not a sequence:{values!r}"
                columns.update(*values)
                for child in item:
                    _resolve_dependencies(child)

        _resolve_dependencies(self.formula)

        return columns

    @staticmethod
    def _parse_formula(formula: str) -> ParseResults:
        return expr.parse_string(formula, parse_all=True)


class Usage(Entity):
    """Defines a base class for Usage entities, so the type checker can enforce
    a bound class as a parameter.
    """

    source: str


@dataclass(eq=True, frozen=True)
class DimensionUsage(Usage):
    """Establishes the usage of a :class:`Schema`-level :class:`SharedDimension`
    inside a :class:`Cube`.
    """

    name: str
    source: str
    foreign_key: str
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    hierarchy_map: Mapping[str, "HierarchyUsage"] = field(default_factory=immu.Map)
    visible: bool = True


@dataclass(eq=True, frozen=True)
class HierarchyUsage(Usage):
    """Establishes the usage of a :class:`Hierarchy` defined in a
    :class:`SharedDimension`.
    """

    name: str
    source: str
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    level_map: Mapping[str, "LevelUsage"] = field(default_factory=immu.Map)
    visible: bool = True


@dataclass(eq=True, frozen=True)
class LevelUsage(Usage):
    """Establishes the usage of a :class:`Level` defined in a :class:`Hierarchy`
    under a :class:`SharedDimension`.
    """

    name: str
    source: str
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    property_map: Mapping[str, "PropertyUsage"] = field(default_factory=immu.Map)
    visible: bool = True


@dataclass(eq=True, frozen=True)
class PropertyUsage(Usage):
    """Establishes the usage of a :class:`Property` defined in a :class:`Level`
    under a :class:`SharedDimension`.
    """

    name: str
    source: str
    annotations: Annotations = field(default_factory=immu.Map)
    captions: CaptionSet = field(default_factory=immu.Map)
    visible: bool = True
