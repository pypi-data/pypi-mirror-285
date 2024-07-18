from mikro_next.scalars import (
    FourByFourMatrix,
    ArrayLike,
    ParquetLike,
    Upload,
    Micrometers,
    FiveDVector,
    FileLike,
    Milliseconds,
)
from mikro_next.traits import (
    HasParquetStoreAccesor,
    HasZarrStoreTrait,
    HasZarrStoreAccessor,
    HasPresignedDownloadAccessor,
    HasParquestStoreTrait,
    IsVectorizableTrait,
    HasDownloadAccessor,
)
from typing import Optional, Union, Tuple, Literal, Iterator, List, AsyncIterator
from pydantic import BaseModel, Field
from enum import Enum
from rath.scalars import ID
from mikro_next.funcs import subscribe, aexecute, execute, asubscribe
from datetime import datetime
from mikro_next.rath import MikroNextRath


class RoiKind(str, Enum):
    ELLIPSIS = "ELLIPSIS"
    POLYGON = "POLYGON"
    LINE = "LINE"
    RECTANGLE = "RECTANGLE"
    SPECTRAL_RECTANGLE = "SPECTRAL_RECTANGLE"
    TEMPORAL_RECTANGLE = "TEMPORAL_RECTANGLE"
    CUBE = "CUBE"
    SPECTRAL_CUBE = "SPECTRAL_CUBE"
    TEMPORAL_CUBE = "TEMPORAL_CUBE"
    HYPERCUBE = "HYPERCUBE"
    SPECTRAL_HYPERCUBE = "SPECTRAL_HYPERCUBE"
    PATH = "PATH"
    FRAME = "FRAME"
    SLICE = "SLICE"
    POINT = "POINT"


class ColorMap(str, Enum):
    VIRIDIS = "VIRIDIS"
    PLASMA = "PLASMA"
    INFERNO = "INFERNO"
    MAGMA = "MAGMA"
    RED = "RED"
    GREEN = "GREEN"
    BLUE = "BLUE"
    INTENSITY = "INTENSITY"


class Blending(str, Enum):
    ADDITIVE = "ADDITIVE"
    MULTIPLICATIVE = "MULTIPLICATIVE"


class RenderNodeKind(str, Enum):
    CONTEXT = "CONTEXT"
    OVERLAY = "OVERLAY"
    GRID = "GRID"
    SPIT = "SPIT"


class ProvenanceFilter(BaseModel):
    during: Optional[str] = None
    and_: Optional["ProvenanceFilter"] = Field(alias="AND", default=None)
    or_: Optional["ProvenanceFilter"] = Field(alias="OR", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class StrFilterLookup(BaseModel):
    exact: Optional[str] = None
    i_exact: Optional[str] = Field(alias="iExact", default=None)
    contains: Optional[str] = None
    i_contains: Optional[str] = Field(alias="iContains", default=None)
    in_list: Optional[Tuple[str, ...]] = Field(alias="inList", default=None)
    gt: Optional[str] = None
    gte: Optional[str] = None
    lt: Optional[str] = None
    lte: Optional[str] = None
    starts_with: Optional[str] = Field(alias="startsWith", default=None)
    i_starts_with: Optional[str] = Field(alias="iStartsWith", default=None)
    ends_with: Optional[str] = Field(alias="endsWith", default=None)
    i_ends_with: Optional[str] = Field(alias="iEndsWith", default=None)
    range: Optional[Tuple[str, ...]] = None
    is_null: Optional[bool] = Field(alias="isNull", default=None)
    regex: Optional[str] = None
    i_regex: Optional[str] = Field(alias="iRegex", default=None)
    n_exact: Optional[str] = Field(alias="nExact", default=None)
    n_i_exact: Optional[str] = Field(alias="nIExact", default=None)
    n_contains: Optional[str] = Field(alias="nContains", default=None)
    n_i_contains: Optional[str] = Field(alias="nIContains", default=None)
    n_in_list: Optional[Tuple[str, ...]] = Field(alias="nInList", default=None)
    n_gt: Optional[str] = Field(alias="nGt", default=None)
    n_gte: Optional[str] = Field(alias="nGte", default=None)
    n_lt: Optional[str] = Field(alias="nLt", default=None)
    n_lte: Optional[str] = Field(alias="nLte", default=None)
    n_starts_with: Optional[str] = Field(alias="nStartsWith", default=None)
    n_i_starts_with: Optional[str] = Field(alias="nIStartsWith", default=None)
    n_ends_with: Optional[str] = Field(alias="nEndsWith", default=None)
    n_i_ends_with: Optional[str] = Field(alias="nIEndsWith", default=None)
    n_range: Optional[Tuple[str, ...]] = Field(alias="nRange", default=None)
    n_is_null: Optional[bool] = Field(alias="nIsNull", default=None)
    n_regex: Optional[str] = Field(alias="nRegex", default=None)
    n_i_regex: Optional[str] = Field(alias="nIRegex", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class OffsetPaginationInput(BaseModel):
    offset: int
    limit: int

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class ImageFilter(BaseModel):
    name: Optional[StrFilterLookup] = None
    ids: Optional[Tuple[ID, ...]] = None
    store: Optional["ZarrStoreFilter"] = None
    dataset: Optional["DatasetFilter"] = None
    transformation_views: Optional["AffineTransformationViewFilter"] = Field(
        alias="transformationViews", default=None
    )
    timepoint_views: Optional["TimepointViewFilter"] = Field(
        alias="timepointViews", default=None
    )
    provenance: Optional[ProvenanceFilter] = None
    and_: Optional["ImageFilter"] = Field(alias="AND", default=None)
    or_: Optional["ImageFilter"] = Field(alias="OR", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class ZarrStoreFilter(BaseModel):
    shape: Optional["IntFilterLookup"] = None
    and_: Optional["ZarrStoreFilter"] = Field(alias="AND", default=None)
    or_: Optional["ZarrStoreFilter"] = Field(alias="OR", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class IntFilterLookup(BaseModel):
    exact: Optional[int] = None
    i_exact: Optional[int] = Field(alias="iExact", default=None)
    contains: Optional[int] = None
    i_contains: Optional[int] = Field(alias="iContains", default=None)
    in_list: Optional[Tuple[int, ...]] = Field(alias="inList", default=None)
    gt: Optional[int] = None
    gte: Optional[int] = None
    lt: Optional[int] = None
    lte: Optional[int] = None
    starts_with: Optional[int] = Field(alias="startsWith", default=None)
    i_starts_with: Optional[int] = Field(alias="iStartsWith", default=None)
    ends_with: Optional[int] = Field(alias="endsWith", default=None)
    i_ends_with: Optional[int] = Field(alias="iEndsWith", default=None)
    range: Optional[Tuple[int, ...]] = None
    is_null: Optional[bool] = Field(alias="isNull", default=None)
    regex: Optional[str] = None
    i_regex: Optional[str] = Field(alias="iRegex", default=None)
    n_exact: Optional[int] = Field(alias="nExact", default=None)
    n_i_exact: Optional[int] = Field(alias="nIExact", default=None)
    n_contains: Optional[int] = Field(alias="nContains", default=None)
    n_i_contains: Optional[int] = Field(alias="nIContains", default=None)
    n_in_list: Optional[Tuple[int, ...]] = Field(alias="nInList", default=None)
    n_gt: Optional[int] = Field(alias="nGt", default=None)
    n_gte: Optional[int] = Field(alias="nGte", default=None)
    n_lt: Optional[int] = Field(alias="nLt", default=None)
    n_lte: Optional[int] = Field(alias="nLte", default=None)
    n_starts_with: Optional[int] = Field(alias="nStartsWith", default=None)
    n_i_starts_with: Optional[int] = Field(alias="nIStartsWith", default=None)
    n_ends_with: Optional[int] = Field(alias="nEndsWith", default=None)
    n_i_ends_with: Optional[int] = Field(alias="nIEndsWith", default=None)
    n_range: Optional[Tuple[int, ...]] = Field(alias="nRange", default=None)
    n_is_null: Optional[bool] = Field(alias="nIsNull", default=None)
    n_regex: Optional[str] = Field(alias="nRegex", default=None)
    n_i_regex: Optional[str] = Field(alias="nIRegex", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class DatasetFilter(BaseModel):
    id: Optional[ID] = None
    name: Optional[StrFilterLookup] = None
    provenance: Optional[ProvenanceFilter] = None
    and_: Optional["DatasetFilter"] = Field(alias="AND", default=None)
    or_: Optional["DatasetFilter"] = Field(alias="OR", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class AffineTransformationViewFilter(BaseModel):
    is_global: Optional[bool] = Field(alias="isGlobal", default=None)
    provenance: Optional[ProvenanceFilter] = None
    and_: Optional["AffineTransformationViewFilter"] = Field(alias="AND", default=None)
    or_: Optional["AffineTransformationViewFilter"] = Field(alias="OR", default=None)
    stage: Optional["StageFilter"] = None
    pixel_size: Optional["FloatFilterLookup"] = Field(alias="pixelSize", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class StageFilter(BaseModel):
    ids: Optional[Tuple[ID, ...]] = None
    search: Optional[str] = None
    id: Optional[ID] = None
    kind: Optional[str] = None
    name: Optional[StrFilterLookup] = None
    provenance: Optional[ProvenanceFilter] = None
    and_: Optional["StageFilter"] = Field(alias="AND", default=None)
    or_: Optional["StageFilter"] = Field(alias="OR", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class FloatFilterLookup(BaseModel):
    exact: Optional[float] = None
    i_exact: Optional[float] = Field(alias="iExact", default=None)
    contains: Optional[float] = None
    i_contains: Optional[float] = Field(alias="iContains", default=None)
    in_list: Optional[Tuple[float, ...]] = Field(alias="inList", default=None)
    gt: Optional[float] = None
    gte: Optional[float] = None
    lt: Optional[float] = None
    lte: Optional[float] = None
    starts_with: Optional[float] = Field(alias="startsWith", default=None)
    i_starts_with: Optional[float] = Field(alias="iStartsWith", default=None)
    ends_with: Optional[float] = Field(alias="endsWith", default=None)
    i_ends_with: Optional[float] = Field(alias="iEndsWith", default=None)
    range: Optional[Tuple[float, ...]] = None
    is_null: Optional[bool] = Field(alias="isNull", default=None)
    regex: Optional[str] = None
    i_regex: Optional[str] = Field(alias="iRegex", default=None)
    n_exact: Optional[float] = Field(alias="nExact", default=None)
    n_i_exact: Optional[float] = Field(alias="nIExact", default=None)
    n_contains: Optional[float] = Field(alias="nContains", default=None)
    n_i_contains: Optional[float] = Field(alias="nIContains", default=None)
    n_in_list: Optional[Tuple[float, ...]] = Field(alias="nInList", default=None)
    n_gt: Optional[float] = Field(alias="nGt", default=None)
    n_gte: Optional[float] = Field(alias="nGte", default=None)
    n_lt: Optional[float] = Field(alias="nLt", default=None)
    n_lte: Optional[float] = Field(alias="nLte", default=None)
    n_starts_with: Optional[float] = Field(alias="nStartsWith", default=None)
    n_i_starts_with: Optional[float] = Field(alias="nIStartsWith", default=None)
    n_ends_with: Optional[float] = Field(alias="nEndsWith", default=None)
    n_i_ends_with: Optional[float] = Field(alias="nIEndsWith", default=None)
    n_range: Optional[Tuple[float, ...]] = Field(alias="nRange", default=None)
    n_is_null: Optional[bool] = Field(alias="nIsNull", default=None)
    n_regex: Optional[str] = Field(alias="nRegex", default=None)
    n_i_regex: Optional[str] = Field(alias="nIRegex", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class TimepointViewFilter(BaseModel):
    is_global: Optional[bool] = Field(alias="isGlobal", default=None)
    provenance: Optional[ProvenanceFilter] = None
    and_: Optional["TimepointViewFilter"] = Field(alias="AND", default=None)
    or_: Optional["TimepointViewFilter"] = Field(alias="OR", default=None)
    era: Optional["EraFilter"] = None
    ms_since_start: Optional[float] = Field(alias="msSinceStart", default=None)
    index_since_start: Optional[int] = Field(alias="indexSinceStart", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class EraFilter(BaseModel):
    id: Optional[ID] = None
    begin: Optional[datetime] = None
    provenance: Optional[ProvenanceFilter] = None
    and_: Optional["EraFilter"] = Field(alias="AND", default=None)
    or_: Optional["EraFilter"] = Field(alias="OR", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class PartialChannelViewInput(BaseModel):
    collection: Optional[ID] = None
    z_min: Optional[int] = Field(alias="zMin", default=None)
    z_max: Optional[int] = Field(alias="zMax", default=None)
    x_min: Optional[int] = Field(alias="xMin", default=None)
    x_max: Optional[int] = Field(alias="xMax", default=None)
    y_min: Optional[int] = Field(alias="yMin", default=None)
    y_max: Optional[int] = Field(alias="yMax", default=None)
    t_min: Optional[int] = Field(alias="tMin", default=None)
    t_max: Optional[int] = Field(alias="tMax", default=None)
    c_min: Optional[int] = Field(alias="cMin", default=None)
    c_max: Optional[int] = Field(alias="cMax", default=None)
    channel: ID

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class PartialAffineTransformationViewInput(BaseModel):
    collection: Optional[ID] = None
    z_min: Optional[int] = Field(alias="zMin", default=None)
    z_max: Optional[int] = Field(alias="zMax", default=None)
    x_min: Optional[int] = Field(alias="xMin", default=None)
    x_max: Optional[int] = Field(alias="xMax", default=None)
    y_min: Optional[int] = Field(alias="yMin", default=None)
    y_max: Optional[int] = Field(alias="yMax", default=None)
    t_min: Optional[int] = Field(alias="tMin", default=None)
    t_max: Optional[int] = Field(alias="tMax", default=None)
    c_min: Optional[int] = Field(alias="cMin", default=None)
    c_max: Optional[int] = Field(alias="cMax", default=None)
    stage: Optional[ID] = None
    affine_matrix: FourByFourMatrix = Field(alias="affineMatrix")

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class PartialAcquisitionViewInput(BaseModel):
    collection: Optional[ID] = None
    z_min: Optional[int] = Field(alias="zMin", default=None)
    z_max: Optional[int] = Field(alias="zMax", default=None)
    x_min: Optional[int] = Field(alias="xMin", default=None)
    x_max: Optional[int] = Field(alias="xMax", default=None)
    y_min: Optional[int] = Field(alias="yMin", default=None)
    y_max: Optional[int] = Field(alias="yMax", default=None)
    t_min: Optional[int] = Field(alias="tMin", default=None)
    t_max: Optional[int] = Field(alias="tMax", default=None)
    c_min: Optional[int] = Field(alias="cMin", default=None)
    c_max: Optional[int] = Field(alias="cMax", default=None)
    description: Optional[str] = None
    acquired_at: Optional[datetime] = Field(alias="acquiredAt", default=None)
    operator: Optional[ID] = None

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class PartialLabelViewInput(BaseModel):
    collection: Optional[ID] = None
    z_min: Optional[int] = Field(alias="zMin", default=None)
    z_max: Optional[int] = Field(alias="zMax", default=None)
    x_min: Optional[int] = Field(alias="xMin", default=None)
    x_max: Optional[int] = Field(alias="xMax", default=None)
    y_min: Optional[int] = Field(alias="yMin", default=None)
    y_max: Optional[int] = Field(alias="yMax", default=None)
    t_min: Optional[int] = Field(alias="tMin", default=None)
    t_max: Optional[int] = Field(alias="tMax", default=None)
    c_min: Optional[int] = Field(alias="cMin", default=None)
    c_max: Optional[int] = Field(alias="cMax", default=None)
    fluorophore: Optional[ID] = None
    primary_antibody: Optional[ID] = Field(alias="primaryAntibody", default=None)
    secondary_antibody: Optional[ID] = Field(alias="secondaryAntibody", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class PartialRGBViewInput(BaseModel):
    collection: Optional[ID] = None
    z_min: Optional[int] = Field(alias="zMin", default=None)
    z_max: Optional[int] = Field(alias="zMax", default=None)
    x_min: Optional[int] = Field(alias="xMin", default=None)
    x_max: Optional[int] = Field(alias="xMax", default=None)
    y_min: Optional[int] = Field(alias="yMin", default=None)
    y_max: Optional[int] = Field(alias="yMax", default=None)
    t_min: Optional[int] = Field(alias="tMin", default=None)
    t_max: Optional[int] = Field(alias="tMax", default=None)
    c_min: Optional[int] = Field(alias="cMin", default=None)
    c_max: Optional[int] = Field(alias="cMax", default=None)
    context: Optional[ID] = None
    gamma: Optional[float] = None
    contrast_limit_min: Optional[float] = Field(alias="contrastLimitMin", default=None)
    contrast_limit_max: Optional[float] = Field(alias="contrastLimitMax", default=None)
    rescale: Optional[bool] = None
    scale: Optional[float] = None
    active: Optional[bool] = None
    color_map: Optional[ColorMap] = Field(alias="colorMap", default=None)
    base_color: Optional[Tuple[float, ...]] = Field(alias="baseColor", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class PartialTimepointViewInput(BaseModel):
    collection: Optional[ID] = None
    z_min: Optional[int] = Field(alias="zMin", default=None)
    z_max: Optional[int] = Field(alias="zMax", default=None)
    x_min: Optional[int] = Field(alias="xMin", default=None)
    x_max: Optional[int] = Field(alias="xMax", default=None)
    y_min: Optional[int] = Field(alias="yMin", default=None)
    y_max: Optional[int] = Field(alias="yMax", default=None)
    t_min: Optional[int] = Field(alias="tMin", default=None)
    t_max: Optional[int] = Field(alias="tMax", default=None)
    c_min: Optional[int] = Field(alias="cMin", default=None)
    c_max: Optional[int] = Field(alias="cMax", default=None)
    era: Optional[ID] = None
    ms_since_start: Optional[Milliseconds] = Field(alias="msSinceStart", default=None)
    index_since_start: Optional[int] = Field(alias="indexSinceStart", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class PartialOpticsViewInput(BaseModel):
    collection: Optional[ID] = None
    z_min: Optional[int] = Field(alias="zMin", default=None)
    z_max: Optional[int] = Field(alias="zMax", default=None)
    x_min: Optional[int] = Field(alias="xMin", default=None)
    x_max: Optional[int] = Field(alias="xMax", default=None)
    y_min: Optional[int] = Field(alias="yMin", default=None)
    y_max: Optional[int] = Field(alias="yMax", default=None)
    t_min: Optional[int] = Field(alias="tMin", default=None)
    t_max: Optional[int] = Field(alias="tMax", default=None)
    c_min: Optional[int] = Field(alias="cMin", default=None)
    c_max: Optional[int] = Field(alias="cMax", default=None)
    instrument: Optional[ID] = None
    objective: Optional[ID] = None
    camera: Optional[ID] = None

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class TreeInput(BaseModel):
    id: Optional[str] = None
    children: Tuple["TreeNodeInput", ...]

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class TreeNodeInput(BaseModel):
    kind: RenderNodeKind
    label: Optional[str] = None
    context: Optional[str] = None
    gap: Optional[int] = None
    children: Optional[Tuple["TreeNodeInput", ...]] = None

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class CreateRGBContextInput(BaseModel):
    name: Optional[str] = None
    thumbnail: Optional[ID] = None
    image: ID
    views: Optional[Tuple[PartialRGBViewInput, ...]] = None
    z: Optional[int] = None
    t: Optional[int] = None
    c: Optional[int] = None

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class UpdateRGBContextInput(BaseModel):
    id: ID
    name: Optional[str] = None
    thumbnail: Optional[ID] = None
    views: Optional[Tuple[PartialRGBViewInput, ...]] = None
    z: Optional[int] = None
    t: Optional[int] = None
    c: Optional[int] = None

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class ViewBase(BaseModel):
    z_min: Optional[int] = Field(alias="zMin")
    z_max: Optional[int] = Field(alias="zMax")


class ChannelView(ViewBase, BaseModel):
    typename: Optional[Literal["ChannelView"]] = Field(alias="__typename", exclude=True)
    id: ID
    channel: "Channel"

    class Config:
        """A config class"""

        frozen = True


class AffineTransformationViewStage(BaseModel):
    typename: Optional[Literal["Stage"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class AffineTransformationView(ViewBase, BaseModel):
    typename: Optional[Literal["AffineTransformationView"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    affine_matrix: FourByFourMatrix = Field(alias="affineMatrix")
    stage: AffineTransformationViewStage

    class Config:
        """A config class"""

        frozen = True


class TimepointView(ViewBase, BaseModel):
    typename: Optional[Literal["TimepointView"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    ms_since_start: Optional[Milliseconds] = Field(alias="msSinceStart")
    index_since_start: Optional[int] = Field(alias="indexSinceStart")
    era: "Era"

    class Config:
        """A config class"""

        frozen = True


class OpticsViewObjective(BaseModel):
    typename: Optional[Literal["Objective"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    serial_number: str = Field(alias="serialNumber")

    class Config:
        """A config class"""

        frozen = True


class OpticsViewCamera(BaseModel):
    typename: Optional[Literal["Camera"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    serial_number: str = Field(alias="serialNumber")

    class Config:
        """A config class"""

        frozen = True


class OpticsViewInstrument(BaseModel):
    typename: Optional[Literal["Instrument"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    serial_number: str = Field(alias="serialNumber")

    class Config:
        """A config class"""

        frozen = True


class OpticsView(ViewBase, BaseModel):
    typename: Optional[Literal["OpticsView"]] = Field(alias="__typename", exclude=True)
    objective: Optional[OpticsViewObjective]
    camera: Optional[OpticsViewCamera]
    instrument: Optional[OpticsViewInstrument]

    class Config:
        """A config class"""

        frozen = True


class LabelView(ViewBase, BaseModel):
    typename: Optional[Literal["LabelView"]] = Field(alias="__typename", exclude=True)
    id: ID
    fluorophore: Optional["Fluorophore"]
    primary_antibody: Optional["Antibody"] = Field(alias="primaryAntibody")
    secondary_antibody: Optional["Antibody"] = Field(alias="secondaryAntibody")

    class Config:
        """A config class"""

        frozen = True


class RGBView(ViewBase, BaseModel):
    typename: Optional[Literal["RGBView"]] = Field(alias="__typename", exclude=True)
    id: ID
    color_map: ColorMap = Field(alias="colorMap")
    contrast_limit_min: Optional[float] = Field(alias="contrastLimitMin")
    contrast_limit_max: Optional[float] = Field(alias="contrastLimitMax")
    gamma: Optional[float]
    rescale: bool
    active: bool
    c_min: Optional[int] = Field(alias="cMin")
    c_max: Optional[int] = Field(alias="cMax")
    full_colour: str = Field(alias="fullColour")
    base_color: Optional[Tuple[int, ...]] = Field(alias="baseColor")

    class Config:
        """A config class"""

        frozen = True


class Camera(BaseModel):
    typename: Optional[Literal["Camera"]] = Field(alias="__typename", exclude=True)
    sensor_size_x: Optional[int] = Field(alias="sensorSizeX")
    sensor_size_y: Optional[int] = Field(alias="sensorSizeY")
    pixel_size_x: Optional[Micrometers] = Field(alias="pixelSizeX")
    pixel_size_y: Optional[Micrometers] = Field(alias="pixelSizeY")
    name: str
    serial_number: str = Field(alias="serialNumber")

    class Config:
        """A config class"""

        frozen = True


class TableOrigins(HasZarrStoreTrait, BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class Table(HasParquestStoreTrait, BaseModel):
    typename: Optional[Literal["Table"]] = Field(alias="__typename", exclude=True)
    origins: Tuple[TableOrigins, ...]
    id: ID
    name: str
    store: "ParquetStore"

    class Config:
        """A config class"""

        frozen = True


class Credentials(BaseModel):
    typename: Optional[Literal["Credentials"]] = Field(alias="__typename", exclude=True)
    access_key: str = Field(alias="accessKey")
    status: str
    secret_key: str = Field(alias="secretKey")
    bucket: str
    key: str
    session_token: str = Field(alias="sessionToken")
    store: str

    class Config:
        """A config class"""

        frozen = True


class AccessCredentials(BaseModel):
    typename: Optional[Literal["AccessCredentials"]] = Field(
        alias="__typename", exclude=True
    )
    access_key: str = Field(alias="accessKey")
    secret_key: str = Field(alias="secretKey")
    bucket: str
    key: str
    session_token: str = Field(alias="sessionToken")
    path: str

    class Config:
        """A config class"""

        frozen = True


class FileOrigins(HasZarrStoreTrait, BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class File(BaseModel):
    typename: Optional[Literal["File"]] = Field(alias="__typename", exclude=True)
    origins: Tuple[FileOrigins, ...]
    id: ID
    name: str
    store: "BigFileStore"

    class Config:
        """A config class"""

        frozen = True


class Stage(BaseModel):
    typename: Optional[Literal["Stage"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class ROIImage(HasZarrStoreTrait, BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class ROI(IsVectorizableTrait, BaseModel):
    typename: Optional[Literal["ROI"]] = Field(alias="__typename", exclude=True)
    id: ID
    image: ROIImage
    vectors: Tuple[FiveDVector, ...]
    kind: RoiKind

    class Config:
        """A config class"""

        frozen = True


class Objective(BaseModel):
    typename: Optional[Literal["Objective"]] = Field(alias="__typename", exclude=True)
    id: ID
    na: Optional[float]
    name: str
    serial_number: str = Field(alias="serialNumber")

    class Config:
        """A config class"""

        frozen = True


class RGBContextImage(HasZarrStoreTrait, BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    id: ID
    store: "ZarrStore"
    "The store where the image data is stored."

    class Config:
        """A config class"""

        frozen = True


class RGBContext(BaseModel):
    typename: Optional[Literal["RGBContext"]] = Field(alias="__typename", exclude=True)
    id: ID
    views: Tuple[RGBView, ...]
    image: RGBContextImage
    pinned: bool
    name: str
    z: int
    t: int
    c: int
    blending: Blending

    class Config:
        """A config class"""

        frozen = True


class HistoryStuffApp(BaseModel):
    """An app."""

    typename: Optional[Literal["App"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class HistoryStuff(BaseModel):
    typename: Optional[Literal["History"]] = Field(alias="__typename", exclude=True)
    id: ID
    app: Optional[HistoryStuffApp]

    class Config:
        """A config class"""

        frozen = True


class Dataset(BaseModel):
    typename: Optional[Literal["Dataset"]] = Field(alias="__typename", exclude=True)
    name: str
    description: Optional[str]
    history: Tuple[HistoryStuff, ...]

    class Config:
        """A config class"""

        frozen = True


class Instrument(BaseModel):
    typename: Optional[Literal["Instrument"]] = Field(alias="__typename", exclude=True)
    id: ID
    model: Optional[str]
    name: str
    serial_number: str = Field(alias="serialNumber")

    class Config:
        """A config class"""

        frozen = True


class Antibody(BaseModel):
    typename: Optional[Literal["Antibody"]] = Field(alias="__typename", exclude=True)
    name: str
    epitope: Optional[str]

    class Config:
        """A config class"""

        frozen = True


class Fluorophore(BaseModel):
    typename: Optional[Literal["Fluorophore"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    emission_wavelength: Optional[Micrometers] = Field(alias="emissionWavelength")
    excitation_wavelength: Optional[Micrometers] = Field(alias="excitationWavelength")

    class Config:
        """A config class"""

        frozen = True


class ImageOrigins(HasZarrStoreTrait, BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class ImageViewsBase(BaseModel):
    pass

    class Config:
        """A config class"""

        frozen = True


class ImageViewsChannelView(ImageViewsBase, ChannelView):
    pass

    class Config:
        """A config class"""

        frozen = True


class ImageViewsAffineTransformationView(ImageViewsBase, AffineTransformationView):
    pass

    class Config:
        """A config class"""

        frozen = True


class ImageViewsLabelView(ImageViewsBase, LabelView):
    pass

    class Config:
        """A config class"""

        frozen = True


class ImageViewsTimepointView(ImageViewsBase, TimepointView):
    pass

    class Config:
        """A config class"""

        frozen = True


class ImageViewsOpticsView(ImageViewsBase, OpticsView):
    pass

    class Config:
        """A config class"""

        frozen = True


class ImageRgbcontexts(BaseModel):
    typename: Optional[Literal["RGBContext"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    views: Tuple[RGBView, ...]

    class Config:
        """A config class"""

        frozen = True


class Image(HasZarrStoreTrait, BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    origins: Tuple[ImageOrigins, ...]
    id: ID
    name: str
    store: "ZarrStore"
    "The store where the image data is stored."
    views: Tuple[
        Union[
            ImageViewsChannelView,
            ImageViewsAffineTransformationView,
            ImageViewsLabelView,
            ImageViewsTimepointView,
            ImageViewsOpticsView,
        ],
        ...,
    ]
    rgb_contexts: Tuple[ImageRgbcontexts, ...] = Field(alias="rgbContexts")

    class Config:
        """A config class"""

        frozen = True


class Era(BaseModel):
    typename: Optional[Literal["Era"]] = Field(alias="__typename", exclude=True)
    id: ID
    begin: Optional[datetime]
    name: str

    class Config:
        """A config class"""

        frozen = True


class SnapshotStore(HasPresignedDownloadAccessor, BaseModel):
    typename: Optional[Literal["MediaStore"]] = Field(alias="__typename", exclude=True)
    key: str
    presigned_url: str = Field(alias="presignedUrl")

    class Config:
        """A config class"""

        frozen = True


class Snapshot(BaseModel):
    typename: Optional[Literal["Snapshot"]] = Field(alias="__typename", exclude=True)
    id: ID
    store: SnapshotStore
    name: str

    class Config:
        """A config class"""

        frozen = True


class ZarrStore(HasZarrStoreAccessor, BaseModel):
    typename: Optional[Literal["ZarrStore"]] = Field(alias="__typename", exclude=True)
    id: ID
    key: str
    "The key where the data is stored."
    bucket: str
    "The bucket where the data is stored."
    path: Optional[str]
    "The path to the data. Relative to the bucket."

    class Config:
        """A config class"""

        frozen = True


class ParquetStore(HasParquetStoreAccesor, BaseModel):
    typename: Optional[Literal["ParquetStore"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    key: str
    bucket: str
    path: str

    class Config:
        """A config class"""

        frozen = True


class BigFileStore(HasDownloadAccessor, BaseModel):
    typename: Optional[Literal["BigFileStore"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    key: str
    bucket: str
    path: str
    presigned_url: str = Field(alias="presignedUrl")

    class Config:
        """A config class"""

        frozen = True


class Channel(BaseModel):
    typename: Optional[Literal["Channel"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    excitation_wavelength: Optional[float] = Field(alias="excitationWavelength")

    class Config:
        """A config class"""

        frozen = True


class CreateCameraMutationCreatecamera(BaseModel):
    typename: Optional[Literal["Camera"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class CreateCameraMutation(BaseModel):
    create_camera: CreateCameraMutationCreatecamera = Field(alias="createCamera")

    class Arguments(BaseModel):
        serial_number: str = Field(alias="serialNumber")
        name: Optional[str] = Field(default=None)
        pixel_size_x: Optional[Micrometers] = Field(alias="pixelSizeX", default=None)
        pixel_size_y: Optional[Micrometers] = Field(alias="pixelSizeY", default=None)
        sensor_size_x: Optional[int] = Field(alias="sensorSizeX", default=None)
        sensor_size_y: Optional[int] = Field(alias="sensorSizeY", default=None)

    class Meta:
        document = "mutation CreateCamera($serialNumber: String!, $name: String, $pixelSizeX: Micrometers, $pixelSizeY: Micrometers, $sensorSizeX: Int, $sensorSizeY: Int) {\n  createCamera(\n    input: {name: $name, pixelSizeX: $pixelSizeX, serialNumber: $serialNumber, pixelSizeY: $pixelSizeY, sensorSizeX: $sensorSizeX, sensorSizeY: $sensorSizeY}\n  ) {\n    id\n    name\n  }\n}"


class EnsureCameraMutationEnsurecamera(BaseModel):
    typename: Optional[Literal["Camera"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class EnsureCameraMutation(BaseModel):
    ensure_camera: EnsureCameraMutationEnsurecamera = Field(alias="ensureCamera")

    class Arguments(BaseModel):
        serial_number: str = Field(alias="serialNumber")
        name: Optional[str] = Field(default=None)
        pixel_size_x: Optional[Micrometers] = Field(alias="pixelSizeX", default=None)
        pixel_size_y: Optional[Micrometers] = Field(alias="pixelSizeY", default=None)
        sensor_size_x: Optional[int] = Field(alias="sensorSizeX", default=None)
        sensor_size_y: Optional[int] = Field(alias="sensorSizeY", default=None)

    class Meta:
        document = "mutation EnsureCamera($serialNumber: String!, $name: String, $pixelSizeX: Micrometers, $pixelSizeY: Micrometers, $sensorSizeX: Int, $sensorSizeY: Int) {\n  ensureCamera(\n    input: {name: $name, pixelSizeX: $pixelSizeX, serialNumber: $serialNumber, pixelSizeY: $pixelSizeY, sensorSizeX: $sensorSizeX, sensorSizeY: $sensorSizeY}\n  ) {\n    id\n    name\n  }\n}"


class CreateRenderTreeMutationCreaterendertree(BaseModel):
    typename: Optional[Literal["RenderTree"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class CreateRenderTreeMutation(BaseModel):
    create_render_tree: CreateRenderTreeMutationCreaterendertree = Field(
        alias="createRenderTree"
    )

    class Arguments(BaseModel):
        name: str
        tree: TreeInput

    class Meta:
        document = "mutation CreateRenderTree($name: String!, $tree: TreeInput!) {\n  createRenderTree(input: {name: $name, tree: $tree}) {\n    id\n  }\n}"


class From_parquet_likeMutation(BaseModel):
    from_parquet_like: Table = Field(alias="fromParquetLike")

    class Arguments(BaseModel):
        dataframe: ParquetLike
        name: str
        origins: Optional[List[ID]] = Field(default=None)
        dataset: Optional[ID] = Field(default=None)

    class Meta:
        document = "fragment ParquetStore on ParquetStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment Table on Table {\n  origins {\n    id\n  }\n  id\n  name\n  store {\n    ...ParquetStore\n  }\n}\n\nmutation from_parquet_like($dataframe: ParquetLike!, $name: String!, $origins: [ID!], $dataset: ID) {\n  fromParquetLike(\n    input: {dataframe: $dataframe, name: $name, origins: $origins, dataset: $dataset}\n  ) {\n    ...Table\n  }\n}"


class RequestTableUploadMutation(BaseModel):
    request_table_upload: Credentials = Field(alias="requestTableUpload")

    class Arguments(BaseModel):
        key: str
        datalayer: str

    class Meta:
        document = "fragment Credentials on Credentials {\n  accessKey\n  status\n  secretKey\n  bucket\n  key\n  sessionToken\n  store\n}\n\nmutation RequestTableUpload($key: String!, $datalayer: String!) {\n  requestTableUpload(input: {key: $key, datalayer: $datalayer}) {\n    ...Credentials\n  }\n}"


class RequestTableAccessMutation(BaseModel):
    request_table_access: AccessCredentials = Field(alias="requestTableAccess")

    class Arguments(BaseModel):
        store: ID
        duration: Optional[int] = Field(default=None)

    class Meta:
        document = "fragment AccessCredentials on AccessCredentials {\n  accessKey\n  secretKey\n  bucket\n  key\n  sessionToken\n  path\n}\n\nmutation RequestTableAccess($store: ID!, $duration: Int) {\n  requestTableAccess(input: {store: $store, duration: $duration}) {\n    ...AccessCredentials\n  }\n}"


class From_file_likeMutation(BaseModel):
    from_file_like: File = Field(alias="fromFileLike")

    class Arguments(BaseModel):
        file: FileLike
        name: str
        origins: Optional[List[ID]] = Field(default=None)
        dataset: Optional[ID] = Field(default=None)

    class Meta:
        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n}\n\nfragment File on File {\n  origins {\n    id\n  }\n  id\n  name\n  store {\n    ...BigFileStore\n  }\n}\n\nmutation from_file_like($file: FileLike!, $name: String!, $origins: [ID!], $dataset: ID) {\n  fromFileLike(\n    input: {file: $file, name: $name, origins: $origins, dataset: $dataset}\n  ) {\n    ...File\n  }\n}"


class RequestFileUploadMutation(BaseModel):
    request_file_upload: Credentials = Field(alias="requestFileUpload")

    class Arguments(BaseModel):
        key: str
        datalayer: str

    class Meta:
        document = "fragment Credentials on Credentials {\n  accessKey\n  status\n  secretKey\n  bucket\n  key\n  sessionToken\n  store\n}\n\nmutation RequestFileUpload($key: String!, $datalayer: String!) {\n  requestFileUpload(input: {key: $key, datalayer: $datalayer}) {\n    ...Credentials\n  }\n}"


class RequestFileAccessMutation(BaseModel):
    request_file_access: AccessCredentials = Field(alias="requestFileAccess")

    class Arguments(BaseModel):
        store: ID
        duration: Optional[int] = Field(default=None)

    class Meta:
        document = "fragment AccessCredentials on AccessCredentials {\n  accessKey\n  secretKey\n  bucket\n  key\n  sessionToken\n  path\n}\n\nmutation RequestFileAccess($store: ID!, $duration: Int) {\n  requestFileAccess(input: {store: $store, duration: $duration}) {\n    ...AccessCredentials\n  }\n}"


class CreateStageMutation(BaseModel):
    create_stage: Stage = Field(alias="createStage")

    class Arguments(BaseModel):
        name: str

    class Meta:
        document = "fragment Stage on Stage {\n  id\n  name\n}\n\nmutation CreateStage($name: String!) {\n  createStage(input: {name: $name}) {\n    ...Stage\n  }\n}"


class CreateRoiMutation(BaseModel):
    create_roi: ROI = Field(alias="createRoi")

    class Arguments(BaseModel):
        image: ID
        vectors: List[FiveDVector]
        kind: RoiKind

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  image {\n    id\n  }\n  vectors\n  kind\n}\n\nmutation CreateRoi($image: ID!, $vectors: [FiveDVector!]!, $kind: RoiKind!) {\n  createRoi(input: {image: $image, vectors: $vectors, kind: $kind}) {\n    ...ROI\n  }\n}"


class DeleteRoiMutation(BaseModel):
    delete_roi: ID = Field(alias="deleteRoi")

    class Arguments(BaseModel):
        roi: ID

    class Meta:
        document = "mutation DeleteRoi($roi: ID!) {\n  deleteRoi(input: {id: $roi})\n}"


class CreateObjectiveMutationCreateobjective(BaseModel):
    typename: Optional[Literal["Objective"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class CreateObjectiveMutation(BaseModel):
    create_objective: CreateObjectiveMutationCreateobjective = Field(
        alias="createObjective"
    )

    class Arguments(BaseModel):
        serial_number: str = Field(alias="serialNumber")
        name: Optional[str] = Field(default=None)
        na: Optional[float] = Field(default=None)
        magnification: Optional[float] = Field(default=None)

    class Meta:
        document = "mutation CreateObjective($serialNumber: String!, $name: String, $na: Float, $magnification: Float) {\n  createObjective(\n    input: {name: $name, na: $na, serialNumber: $serialNumber, magnification: $magnification}\n  ) {\n    id\n    name\n  }\n}"


class EnsureObjectiveMutationEnsureobjective(BaseModel):
    typename: Optional[Literal["Objective"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class EnsureObjectiveMutation(BaseModel):
    ensure_objective: EnsureObjectiveMutationEnsureobjective = Field(
        alias="ensureObjective"
    )

    class Arguments(BaseModel):
        serial_number: str = Field(alias="serialNumber")
        name: Optional[str] = Field(default=None)
        na: Optional[float] = Field(default=None)
        magnification: Optional[float] = Field(default=None)

    class Meta:
        document = "mutation EnsureObjective($serialNumber: String!, $name: String, $na: Float, $magnification: Float) {\n  ensureObjective(\n    input: {name: $name, na: $na, serialNumber: $serialNumber, magnification: $magnification}\n  ) {\n    id\n    name\n  }\n}"


class CreateDatasetMutationCreatedataset(BaseModel):
    typename: Optional[Literal["Dataset"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class CreateDatasetMutation(BaseModel):
    create_dataset: CreateDatasetMutationCreatedataset = Field(alias="createDataset")

    class Arguments(BaseModel):
        name: str

    class Meta:
        document = "mutation CreateDataset($name: String!) {\n  createDataset(input: {name: $name}) {\n    id\n    name\n  }\n}"


class UpdateDatasetMutationUpdatedataset(BaseModel):
    typename: Optional[Literal["Dataset"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class UpdateDatasetMutation(BaseModel):
    update_dataset: UpdateDatasetMutationUpdatedataset = Field(alias="updateDataset")

    class Arguments(BaseModel):
        id: ID
        name: str

    class Meta:
        document = "mutation UpdateDataset($id: ID!, $name: String!) {\n  updateDataset(input: {id: $id, name: $name}) {\n    id\n    name\n  }\n}"


class RevertDatasetMutationRevertdataset(BaseModel):
    typename: Optional[Literal["Dataset"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    description: Optional[str]

    class Config:
        """A config class"""

        frozen = True


class RevertDatasetMutation(BaseModel):
    revert_dataset: RevertDatasetMutationRevertdataset = Field(alias="revertDataset")

    class Arguments(BaseModel):
        dataset: ID
        history: ID

    class Meta:
        document = "mutation RevertDataset($dataset: ID!, $history: ID!) {\n  revertDataset(input: {id: $dataset, historyId: $history}) {\n    id\n    name\n    description\n  }\n}"


class CreateInstrumentMutationCreateinstrument(BaseModel):
    typename: Optional[Literal["Instrument"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class CreateInstrumentMutation(BaseModel):
    create_instrument: CreateInstrumentMutationCreateinstrument = Field(
        alias="createInstrument"
    )

    class Arguments(BaseModel):
        serial_number: str = Field(alias="serialNumber")
        name: Optional[str] = Field(default=None)
        model: Optional[str] = Field(default=None)

    class Meta:
        document = "mutation CreateInstrument($serialNumber: String!, $name: String, $model: String) {\n  createInstrument(\n    input: {name: $name, model: $model, serialNumber: $serialNumber}\n  ) {\n    id\n    name\n  }\n}"


class EnsureInstrumentMutationEnsureinstrument(BaseModel):
    typename: Optional[Literal["Instrument"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class EnsureInstrumentMutation(BaseModel):
    ensure_instrument: EnsureInstrumentMutationEnsureinstrument = Field(
        alias="ensureInstrument"
    )

    class Arguments(BaseModel):
        serial_number: str = Field(alias="serialNumber")
        name: Optional[str] = Field(default=None)
        model: Optional[str] = Field(default=None)

    class Meta:
        document = "mutation EnsureInstrument($serialNumber: String!, $name: String, $model: String) {\n  ensureInstrument(\n    input: {name: $name, model: $model, serialNumber: $serialNumber}\n  ) {\n    id\n    name\n  }\n}"


class CreateAntibodyMutationCreateantibody(BaseModel):
    typename: Optional[Literal["Antibody"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class CreateAntibodyMutation(BaseModel):
    create_antibody: CreateAntibodyMutationCreateantibody = Field(
        alias="createAntibody"
    )

    class Arguments(BaseModel):
        name: str
        epitope: Optional[str] = Field(default=None)

    class Meta:
        document = "mutation CreateAntibody($name: String!, $epitope: String) {\n  createAntibody(input: {name: $name, epitope: $epitope}) {\n    id\n    name\n  }\n}"


class EnsureAntibodyMutationEnsureantibody(BaseModel):
    typename: Optional[Literal["Antibody"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class EnsureAntibodyMutation(BaseModel):
    ensure_antibody: EnsureAntibodyMutationEnsureantibody = Field(
        alias="ensureAntibody"
    )

    class Arguments(BaseModel):
        name: str
        epitope: Optional[str] = Field(default=None)

    class Meta:
        document = "mutation EnsureAntibody($name: String!, $epitope: String) {\n  ensureAntibody(input: {name: $name, epitope: $epitope}) {\n    id\n    name\n  }\n}"


class CreateFluorophoreMutationCreatefluorophore(BaseModel):
    typename: Optional[Literal["Fluorophore"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class CreateFluorophoreMutation(BaseModel):
    create_fluorophore: CreateFluorophoreMutationCreatefluorophore = Field(
        alias="createFluorophore"
    )

    class Arguments(BaseModel):
        name: str
        excitation_wavelength: Optional[Micrometers] = Field(
            alias="excitationWavelength", default=None
        )
        emission_wavelength: Optional[Micrometers] = Field(
            alias="emissionWavelength", default=None
        )

    class Meta:
        document = "mutation CreateFluorophore($name: String!, $excitationWavelength: Micrometers, $emissionWavelength: Micrometers) {\n  createFluorophore(\n    input: {name: $name, excitationWavelength: $excitationWavelength, emissionWavelength: $emissionWavelength}\n  ) {\n    id\n    name\n  }\n}"


class EnsureFluorophoreMutationEnsurefluorophore(BaseModel):
    typename: Optional[Literal["Fluorophore"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class EnsureFluorophoreMutation(BaseModel):
    ensure_fluorophore: EnsureFluorophoreMutationEnsurefluorophore = Field(
        alias="ensureFluorophore"
    )

    class Arguments(BaseModel):
        name: str
        excitation_wavelength: Optional[Micrometers] = Field(
            alias="excitationWavelength", default=None
        )
        emission_wavelength: Optional[Micrometers] = Field(
            alias="emissionWavelength", default=None
        )

    class Meta:
        document = "mutation EnsureFluorophore($name: String!, $excitationWavelength: Micrometers, $emissionWavelength: Micrometers) {\n  ensureFluorophore(\n    input: {name: $name, excitationWavelength: $excitationWavelength, emissionWavelength: $emissionWavelength}\n  ) {\n    id\n    name\n  }\n}"


class From_array_likeMutation(BaseModel):
    from_array_like: Image = Field(alias="fromArrayLike")

    class Arguments(BaseModel):
        array: ArrayLike
        name: str
        origins: Optional[List[ID]] = Field(default=None)
        channel_views: Optional[List[PartialChannelViewInput]] = Field(
            alias="channelViews", default=None
        )
        transformation_views: Optional[
            List[PartialAffineTransformationViewInput]
        ] = Field(alias="transformationViews", default=None)
        label_views: Optional[List[PartialLabelViewInput]] = Field(
            alias="labelViews", default=None
        )
        rgb_views: Optional[List[PartialRGBViewInput]] = Field(
            alias="rgbViews", default=None
        )
        acquisition_views: Optional[List[PartialAcquisitionViewInput]] = Field(
            alias="acquisitionViews", default=None
        )
        timepoint_views: Optional[List[PartialTimepointViewInput]] = Field(
            alias="timepointViews", default=None
        )
        optics_views: Optional[List[PartialOpticsViewInput]] = Field(
            alias="opticsViews", default=None
        )
        tags: Optional[List[str]] = Field(default=None)
        file_origins: Optional[List[ID]] = Field(alias="fileOrigins", default=None)
        roi_origins: Optional[List[ID]] = Field(alias="roiOrigins", default=None)

    class Meta:
        document = "fragment Channel on Channel {\n  id\n  name\n  excitationWavelength\n}\n\nfragment Era on Era {\n  id\n  begin\n  name\n}\n\nfragment View on View {\n  zMin\n  zMax\n}\n\nfragment Antibody on Antibody {\n  name\n  epitope\n}\n\nfragment Fluorophore on Fluorophore {\n  id\n  name\n  emissionWavelength\n  excitationWavelength\n}\n\nfragment OpticsView on OpticsView {\n  ...View\n  objective {\n    id\n    name\n    serialNumber\n  }\n  camera {\n    id\n    name\n    serialNumber\n  }\n  instrument {\n    id\n    name\n    serialNumber\n  }\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment ChannelView on ChannelView {\n  ...View\n  id\n  channel {\n    ...Channel\n  }\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  cMin\n  cMax\n  fullColour\n  baseColor\n}\n\nfragment LabelView on LabelView {\n  ...View\n  id\n  fluorophore {\n    ...Fluorophore\n  }\n  primaryAntibody {\n    ...Antibody\n  }\n  secondaryAntibody {\n    ...Antibody\n  }\n}\n\nfragment TimepointView on TimepointView {\n  ...View\n  id\n  msSinceStart\n  indexSinceStart\n  era {\n    ...Era\n  }\n}\n\nfragment AffineTransformationView on AffineTransformationView {\n  ...View\n  id\n  affineMatrix\n  stage {\n    id\n  }\n}\n\nfragment Image on Image {\n  origins {\n    id\n  }\n  id\n  name\n  store {\n    ...ZarrStore\n  }\n  views {\n    ...ChannelView\n    ...AffineTransformationView\n    ...LabelView\n    ...TimepointView\n    ...OpticsView\n  }\n  rgbContexts {\n    id\n    name\n    views {\n      ...RGBView\n    }\n  }\n}\n\nmutation from_array_like($array: ArrayLike!, $name: String!, $origins: [ID!], $channelViews: [PartialChannelViewInput!], $transformationViews: [PartialAffineTransformationViewInput!], $labelViews: [PartialLabelViewInput!], $rgbViews: [PartialRGBViewInput!], $acquisitionViews: [PartialAcquisitionViewInput!], $timepointViews: [PartialTimepointViewInput!], $opticsViews: [PartialOpticsViewInput!], $tags: [String!], $fileOrigins: [ID!], $roiOrigins: [ID!]) {\n  fromArrayLike(\n    input: {array: $array, name: $name, origins: $origins, channelViews: $channelViews, transformationViews: $transformationViews, acquisitionViews: $acquisitionViews, labelViews: $labelViews, timepointViews: $timepointViews, opticsViews: $opticsViews, rgbViews: $rgbViews, tags: $tags, fileOrigins: $fileOrigins, roiOrigins: $roiOrigins}\n  ) {\n    ...Image\n  }\n}"


class RequestUploadMutation(BaseModel):
    request_upload: Credentials = Field(alias="requestUpload")

    class Arguments(BaseModel):
        key: str
        datalayer: str

    class Meta:
        document = "fragment Credentials on Credentials {\n  accessKey\n  status\n  secretKey\n  bucket\n  key\n  sessionToken\n  store\n}\n\nmutation RequestUpload($key: String!, $datalayer: String!) {\n  requestUpload(input: {key: $key, datalayer: $datalayer}) {\n    ...Credentials\n  }\n}"


class RequestAccessMutation(BaseModel):
    request_access: AccessCredentials = Field(alias="requestAccess")
    "Request upload credentials for a given key"

    class Arguments(BaseModel):
        store: ID
        duration: Optional[int] = Field(default=None)

    class Meta:
        document = "fragment AccessCredentials on AccessCredentials {\n  accessKey\n  secretKey\n  bucket\n  key\n  sessionToken\n  path\n}\n\nmutation RequestAccess($store: ID!, $duration: Int) {\n  requestAccess(input: {store: $store, duration: $duration}) {\n    ...AccessCredentials\n  }\n}"


class CreateEraMutationCreateera(BaseModel):
    typename: Optional[Literal["Era"]] = Field(alias="__typename", exclude=True)
    id: ID
    begin: Optional[datetime]

    class Config:
        """A config class"""

        frozen = True


class CreateEraMutation(BaseModel):
    create_era: CreateEraMutationCreateera = Field(alias="createEra")

    class Arguments(BaseModel):
        name: str
        begin: Optional[datetime] = Field(default=None)

    class Meta:
        document = "mutation CreateEra($name: String!, $begin: DateTime) {\n  createEra(input: {name: $name, begin: $begin}) {\n    id\n    begin\n  }\n}"


class CreateSnapshotMutation(BaseModel):
    create_snapshot: Snapshot = Field(alias="createSnapshot")

    class Arguments(BaseModel):
        image: ID
        file: Upload

    class Meta:
        document = "fragment Snapshot on Snapshot {\n  id\n  store {\n    key\n    presignedUrl\n  }\n  name\n}\n\nmutation CreateSnapshot($image: ID!, $file: Upload!) {\n  createSnapshot(input: {file: $file, image: $image}) {\n    ...Snapshot\n  }\n}"


class CreateRgbViewMutationCreatergbview(BaseModel):
    typename: Optional[Literal["RGBView"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class CreateRgbViewMutation(BaseModel):
    create_rgb_view: CreateRgbViewMutationCreatergbview = Field(alias="createRgbView")

    class Arguments(BaseModel):
        image: ID
        context: ID
        gamma: Optional[float] = Field(default=None)
        contrast_limit_max: Optional[float] = Field(
            alias="contrastLimitMax", default=None
        )
        contrast_limit_min: Optional[float] = Field(
            alias="contrastLimitMin", default=None
        )
        rescale: Optional[bool] = Field(default=None)
        active: Optional[bool] = Field(default=None)
        color_map: Optional[ColorMap] = Field(alias="colorMap", default=None)
        base_color: Optional[List[float]] = Field(alias="baseColor", default=None)

    class Meta:
        document = "mutation CreateRgbView($image: ID!, $context: ID!, $gamma: Float, $contrastLimitMax: Float, $contrastLimitMin: Float, $rescale: Boolean, $active: Boolean, $colorMap: ColorMap, $baseColor: [Float!]) {\n  createRgbView(\n    input: {image: $image, context: $context, gamma: $gamma, contrastLimitMax: $contrastLimitMax, contrastLimitMin: $contrastLimitMin, rescale: $rescale, active: $active, colorMap: $colorMap, baseColor: $baseColor}\n  ) {\n    id\n  }\n}"


class CreateRGBContextMutation(BaseModel):
    create_rgb_context: RGBContext = Field(alias="createRgbContext")

    class Arguments(BaseModel):
        input: CreateRGBContextInput

    class Meta:
        document = "fragment View on View {\n  zMin\n  zMax\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  cMin\n  cMax\n  fullColour\n  baseColor\n}\n\nfragment RGBContext on RGBContext {\n  id\n  views {\n    ...RGBView\n  }\n  image {\n    id\n    store {\n      ...ZarrStore\n    }\n  }\n  pinned\n  name\n  z\n  t\n  c\n  blending\n}\n\nmutation CreateRGBContext($input: CreateRGBContextInput!) {\n  createRgbContext(input: $input) {\n    ...RGBContext\n  }\n}"


class UpdateRGBContextMutation(BaseModel):
    update_rgb_context: RGBContext = Field(alias="updateRgbContext")
    "Update RGB Context"

    class Arguments(BaseModel):
        input: UpdateRGBContextInput

    class Meta:
        document = "fragment View on View {\n  zMin\n  zMax\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  cMin\n  cMax\n  fullColour\n  baseColor\n}\n\nfragment RGBContext on RGBContext {\n  id\n  views {\n    ...RGBView\n  }\n  image {\n    id\n    store {\n      ...ZarrStore\n    }\n  }\n  pinned\n  name\n  z\n  t\n  c\n  blending\n}\n\nmutation UpdateRGBContext($input: UpdateRGBContextInput!) {\n  updateRgbContext(input: $input) {\n    ...RGBContext\n  }\n}"


class CreateViewCollectionMutationCreateviewcollection(BaseModel):
    typename: Optional[Literal["ViewCollection"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class CreateViewCollectionMutation(BaseModel):
    create_view_collection: CreateViewCollectionMutationCreateviewcollection = Field(
        alias="createViewCollection"
    )

    class Arguments(BaseModel):
        name: str

    class Meta:
        document = "mutation CreateViewCollection($name: String!) {\n  createViewCollection(input: {name: $name}) {\n    id\n    name\n  }\n}"


class CreateChannelMutationCreatechannel(BaseModel):
    typename: Optional[Literal["Channel"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class CreateChannelMutation(BaseModel):
    create_channel: CreateChannelMutationCreatechannel = Field(alias="createChannel")

    class Arguments(BaseModel):
        name: str

    class Meta:
        document = "mutation CreateChannel($name: String!) {\n  createChannel(input: {name: $name}) {\n    id\n    name\n  }\n}"


class EnsureChannelMutationEnsurechannel(BaseModel):
    typename: Optional[Literal["Channel"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class EnsureChannelMutation(BaseModel):
    ensure_channel: EnsureChannelMutationEnsurechannel = Field(alias="ensureChannel")

    class Arguments(BaseModel):
        name: str

    class Meta:
        document = "mutation EnsureChannel($name: String!) {\n  ensureChannel(input: {name: $name}) {\n    id\n    name\n  }\n}"


class GetCameraQuery(BaseModel):
    camera: Camera

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Camera on Camera {\n  sensorSizeX\n  sensorSizeY\n  pixelSizeX\n  pixelSizeY\n  name\n  serialNumber\n}\n\nquery GetCamera($id: ID!) {\n  camera(id: $id) {\n    ...Camera\n  }\n}"


class GetTableQuery(BaseModel):
    table: Table

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment ParquetStore on ParquetStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment Table on Table {\n  origins {\n    id\n  }\n  id\n  name\n  store {\n    ...ParquetStore\n  }\n}\n\nquery GetTable($id: ID!) {\n  table(id: $id) {\n    ...Table\n  }\n}"


class GetFileQuery(BaseModel):
    file: File

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n}\n\nfragment File on File {\n  origins {\n    id\n  }\n  id\n  name\n  store {\n    ...BigFileStore\n  }\n}\n\nquery GetFile($id: ID!) {\n  file(id: $id) {\n    ...File\n  }\n}"


class SearchFilesQueryOptions(BaseModel):
    typename: Optional[Literal["File"]] = Field(alias="__typename", exclude=True)
    value: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchFilesQuery(BaseModel):
    options: Tuple[SearchFilesQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)

    class Meta:
        document = "query SearchFiles($search: String, $values: [ID!], $pagination: OffsetPaginationInput) {\n  options: files(\n    filters: {search: $search, ids: $values}\n    pagination: $pagination\n  ) {\n    value: id\n    label: name\n  }\n}"


class GetStageQuery(BaseModel):
    stage: Stage

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Stage on Stage {\n  id\n  name\n}\n\nquery GetStage($id: ID!) {\n  stage(id: $id) {\n    ...Stage\n  }\n}"


class SearchStagesQueryOptions(BaseModel):
    typename: Optional[Literal["Stage"]] = Field(alias="__typename", exclude=True)
    value: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchStagesQuery(BaseModel):
    options: Tuple[SearchStagesQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)

    class Meta:
        document = "query SearchStages($search: String, $values: [ID!], $pagination: OffsetPaginationInput) {\n  options: stages(\n    filters: {search: $search, ids: $values}\n    pagination: $pagination\n  ) {\n    value: id\n    label: name\n  }\n}"


class GetRoisQuery(BaseModel):
    rois: Tuple[ROI, ...]

    class Arguments(BaseModel):
        image: ID

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  image {\n    id\n  }\n  vectors\n  kind\n}\n\nquery GetRois($image: ID!) {\n  rois(filters: {image: $image}) {\n    ...ROI\n  }\n}"


class GetRoiQuery(BaseModel):
    roi: ROI

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  image {\n    id\n  }\n  vectors\n  kind\n}\n\nquery GetRoi($id: ID!) {\n  roi(id: $id) {\n    ...ROI\n  }\n}"


class GetObjectiveQuery(BaseModel):
    objective: Objective

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Objective on Objective {\n  id\n  na\n  name\n  serialNumber\n}\n\nquery GetObjective($id: ID!) {\n  objective(id: $id) {\n    ...Objective\n  }\n}"


class GetDatasetQuery(BaseModel):
    dataset: Dataset

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment HistoryStuff on History {\n  id\n  app {\n    id\n  }\n}\n\nfragment Dataset on Dataset {\n  name\n  description\n  history {\n    ...HistoryStuff\n  }\n}\n\nquery GetDataset($id: ID!) {\n  dataset(id: $id) {\n    ...Dataset\n  }\n}"


class GetInstrumentQuery(BaseModel):
    instrument: Instrument

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Instrument on Instrument {\n  id\n  model\n  name\n  serialNumber\n}\n\nquery GetInstrument($id: ID!) {\n  instrument(id: $id) {\n    ...Instrument\n  }\n}"


class GetImageQuery(BaseModel):
    image: Image

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Channel on Channel {\n  id\n  name\n  excitationWavelength\n}\n\nfragment Era on Era {\n  id\n  begin\n  name\n}\n\nfragment View on View {\n  zMin\n  zMax\n}\n\nfragment Antibody on Antibody {\n  name\n  epitope\n}\n\nfragment Fluorophore on Fluorophore {\n  id\n  name\n  emissionWavelength\n  excitationWavelength\n}\n\nfragment OpticsView on OpticsView {\n  ...View\n  objective {\n    id\n    name\n    serialNumber\n  }\n  camera {\n    id\n    name\n    serialNumber\n  }\n  instrument {\n    id\n    name\n    serialNumber\n  }\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment ChannelView on ChannelView {\n  ...View\n  id\n  channel {\n    ...Channel\n  }\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  cMin\n  cMax\n  fullColour\n  baseColor\n}\n\nfragment LabelView on LabelView {\n  ...View\n  id\n  fluorophore {\n    ...Fluorophore\n  }\n  primaryAntibody {\n    ...Antibody\n  }\n  secondaryAntibody {\n    ...Antibody\n  }\n}\n\nfragment TimepointView on TimepointView {\n  ...View\n  id\n  msSinceStart\n  indexSinceStart\n  era {\n    ...Era\n  }\n}\n\nfragment AffineTransformationView on AffineTransformationView {\n  ...View\n  id\n  affineMatrix\n  stage {\n    id\n  }\n}\n\nfragment Image on Image {\n  origins {\n    id\n  }\n  id\n  name\n  store {\n    ...ZarrStore\n  }\n  views {\n    ...ChannelView\n    ...AffineTransformationView\n    ...LabelView\n    ...TimepointView\n    ...OpticsView\n  }\n  rgbContexts {\n    id\n    name\n    views {\n      ...RGBView\n    }\n  }\n}\n\nquery GetImage($id: ID!) {\n  image(id: $id) {\n    ...Image\n  }\n}"


class GetRandomImageQuery(BaseModel):
    random_image: Image = Field(alias="randomImage")

    class Arguments(BaseModel):
        pass

    class Meta:
        document = "fragment Channel on Channel {\n  id\n  name\n  excitationWavelength\n}\n\nfragment Era on Era {\n  id\n  begin\n  name\n}\n\nfragment View on View {\n  zMin\n  zMax\n}\n\nfragment Antibody on Antibody {\n  name\n  epitope\n}\n\nfragment Fluorophore on Fluorophore {\n  id\n  name\n  emissionWavelength\n  excitationWavelength\n}\n\nfragment OpticsView on OpticsView {\n  ...View\n  objective {\n    id\n    name\n    serialNumber\n  }\n  camera {\n    id\n    name\n    serialNumber\n  }\n  instrument {\n    id\n    name\n    serialNumber\n  }\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment ChannelView on ChannelView {\n  ...View\n  id\n  channel {\n    ...Channel\n  }\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  cMin\n  cMax\n  fullColour\n  baseColor\n}\n\nfragment LabelView on LabelView {\n  ...View\n  id\n  fluorophore {\n    ...Fluorophore\n  }\n  primaryAntibody {\n    ...Antibody\n  }\n  secondaryAntibody {\n    ...Antibody\n  }\n}\n\nfragment TimepointView on TimepointView {\n  ...View\n  id\n  msSinceStart\n  indexSinceStart\n  era {\n    ...Era\n  }\n}\n\nfragment AffineTransformationView on AffineTransformationView {\n  ...View\n  id\n  affineMatrix\n  stage {\n    id\n  }\n}\n\nfragment Image on Image {\n  origins {\n    id\n  }\n  id\n  name\n  store {\n    ...ZarrStore\n  }\n  views {\n    ...ChannelView\n    ...AffineTransformationView\n    ...LabelView\n    ...TimepointView\n    ...OpticsView\n  }\n  rgbContexts {\n    id\n    name\n    views {\n      ...RGBView\n    }\n  }\n}\n\nquery GetRandomImage {\n  randomImage {\n    ...Image\n  }\n}"


class SearchImagesQueryOptions(HasZarrStoreTrait, BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    value: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchImagesQuery(BaseModel):
    options: Tuple[SearchImagesQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchImages($search: String, $values: [ID!]) {\n  options: images(\n    filters: {name: {contains: $search}, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n  }\n}"


class ImagesQuery(BaseModel):
    images: Tuple[Image, ...]

    class Arguments(BaseModel):
        filter: Optional[ImageFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)

    class Meta:
        document = "fragment Channel on Channel {\n  id\n  name\n  excitationWavelength\n}\n\nfragment Era on Era {\n  id\n  begin\n  name\n}\n\nfragment View on View {\n  zMin\n  zMax\n}\n\nfragment Antibody on Antibody {\n  name\n  epitope\n}\n\nfragment Fluorophore on Fluorophore {\n  id\n  name\n  emissionWavelength\n  excitationWavelength\n}\n\nfragment OpticsView on OpticsView {\n  ...View\n  objective {\n    id\n    name\n    serialNumber\n  }\n  camera {\n    id\n    name\n    serialNumber\n  }\n  instrument {\n    id\n    name\n    serialNumber\n  }\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment ChannelView on ChannelView {\n  ...View\n  id\n  channel {\n    ...Channel\n  }\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  cMin\n  cMax\n  fullColour\n  baseColor\n}\n\nfragment LabelView on LabelView {\n  ...View\n  id\n  fluorophore {\n    ...Fluorophore\n  }\n  primaryAntibody {\n    ...Antibody\n  }\n  secondaryAntibody {\n    ...Antibody\n  }\n}\n\nfragment TimepointView on TimepointView {\n  ...View\n  id\n  msSinceStart\n  indexSinceStart\n  era {\n    ...Era\n  }\n}\n\nfragment AffineTransformationView on AffineTransformationView {\n  ...View\n  id\n  affineMatrix\n  stage {\n    id\n  }\n}\n\nfragment Image on Image {\n  origins {\n    id\n  }\n  id\n  name\n  store {\n    ...ZarrStore\n  }\n  views {\n    ...ChannelView\n    ...AffineTransformationView\n    ...LabelView\n    ...TimepointView\n    ...OpticsView\n  }\n  rgbContexts {\n    id\n    name\n    views {\n      ...RGBView\n    }\n  }\n}\n\nquery Images($filter: ImageFilter, $pagination: OffsetPaginationInput) {\n  images(filters: $filter, pagination: $pagination) {\n    ...Image\n  }\n}"


class GetSnapshotQuery(BaseModel):
    snapshot: Snapshot

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Snapshot on Snapshot {\n  id\n  store {\n    key\n    presignedUrl\n  }\n  name\n}\n\nquery GetSnapshot($id: ID!) {\n  snapshot(id: $id) {\n    ...Snapshot\n  }\n}"


class SearchSnapshotsQueryOptions(BaseModel):
    typename: Optional[Literal["Snapshot"]] = Field(alias="__typename", exclude=True)
    value: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchSnapshotsQuery(BaseModel):
    options: Tuple[SearchSnapshotsQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchSnapshots($search: String, $values: [ID!]) {\n  options: snapshots(\n    filters: {name: {contains: $search}, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n  }\n}"


class GetRGBContextQuery(BaseModel):
    rgbcontext: RGBContext

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment View on View {\n  zMin\n  zMax\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  cMin\n  cMax\n  fullColour\n  baseColor\n}\n\nfragment RGBContext on RGBContext {\n  id\n  views {\n    ...RGBView\n  }\n  image {\n    id\n    store {\n      ...ZarrStore\n    }\n  }\n  pinned\n  name\n  z\n  t\n  c\n  blending\n}\n\nquery GetRGBContext($id: ID!) {\n  rgbcontext(id: $id) {\n    ...RGBContext\n  }\n}"


class WatchRoisSubscriptionRois(BaseModel):
    typename: Optional[Literal["RoiEvent"]] = Field(alias="__typename", exclude=True)
    create: Optional[ROI]
    delete: Optional[ID]
    update: Optional[ROI]

    class Config:
        """A config class"""

        frozen = True


class WatchRoisSubscription(BaseModel):
    rois: WatchRoisSubscriptionRois

    class Arguments(BaseModel):
        image: ID

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  image {\n    id\n  }\n  vectors\n  kind\n}\n\nsubscription WatchRois($image: ID!) {\n  rois(image: $image) {\n    create {\n      ...ROI\n    }\n    delete\n    update {\n      ...ROI\n    }\n  }\n}"


async def acreate_camera(
    serial_number: str,
    name: Optional[str] = None,
    pixel_size_x: Optional[Micrometers] = None,
    pixel_size_y: Optional[Micrometers] = None,
    sensor_size_x: Optional[int] = None,
    sensor_size_y: Optional[int] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateCameraMutationCreatecamera:
    """CreateCamera



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        pixel_size_x (Optional[Micrometers], optional): pixelSizeX.
        pixel_size_y (Optional[Micrometers], optional): pixelSizeY.
        sensor_size_x (Optional[int], optional): sensorSizeX.
        sensor_size_y (Optional[int], optional): sensorSizeY.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateCameraMutationCreatecamera"""
    return (
        await aexecute(
            CreateCameraMutation,
            {
                "serialNumber": serial_number,
                "name": name,
                "pixelSizeX": pixel_size_x,
                "pixelSizeY": pixel_size_y,
                "sensorSizeX": sensor_size_x,
                "sensorSizeY": sensor_size_y,
            },
            rath=rath,
        )
    ).create_camera


def create_camera(
    serial_number: str,
    name: Optional[str] = None,
    pixel_size_x: Optional[Micrometers] = None,
    pixel_size_y: Optional[Micrometers] = None,
    sensor_size_x: Optional[int] = None,
    sensor_size_y: Optional[int] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateCameraMutationCreatecamera:
    """CreateCamera



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        pixel_size_x (Optional[Micrometers], optional): pixelSizeX.
        pixel_size_y (Optional[Micrometers], optional): pixelSizeY.
        sensor_size_x (Optional[int], optional): sensorSizeX.
        sensor_size_y (Optional[int], optional): sensorSizeY.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateCameraMutationCreatecamera"""
    return execute(
        CreateCameraMutation,
        {
            "serialNumber": serial_number,
            "name": name,
            "pixelSizeX": pixel_size_x,
            "pixelSizeY": pixel_size_y,
            "sensorSizeX": sensor_size_x,
            "sensorSizeY": sensor_size_y,
        },
        rath=rath,
    ).create_camera


async def aensure_camera(
    serial_number: str,
    name: Optional[str] = None,
    pixel_size_x: Optional[Micrometers] = None,
    pixel_size_y: Optional[Micrometers] = None,
    sensor_size_x: Optional[int] = None,
    sensor_size_y: Optional[int] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureCameraMutationEnsurecamera:
    """EnsureCamera



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        pixel_size_x (Optional[Micrometers], optional): pixelSizeX.
        pixel_size_y (Optional[Micrometers], optional): pixelSizeY.
        sensor_size_x (Optional[int], optional): sensorSizeX.
        sensor_size_y (Optional[int], optional): sensorSizeY.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureCameraMutationEnsurecamera"""
    return (
        await aexecute(
            EnsureCameraMutation,
            {
                "serialNumber": serial_number,
                "name": name,
                "pixelSizeX": pixel_size_x,
                "pixelSizeY": pixel_size_y,
                "sensorSizeX": sensor_size_x,
                "sensorSizeY": sensor_size_y,
            },
            rath=rath,
        )
    ).ensure_camera


def ensure_camera(
    serial_number: str,
    name: Optional[str] = None,
    pixel_size_x: Optional[Micrometers] = None,
    pixel_size_y: Optional[Micrometers] = None,
    sensor_size_x: Optional[int] = None,
    sensor_size_y: Optional[int] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureCameraMutationEnsurecamera:
    """EnsureCamera



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        pixel_size_x (Optional[Micrometers], optional): pixelSizeX.
        pixel_size_y (Optional[Micrometers], optional): pixelSizeY.
        sensor_size_x (Optional[int], optional): sensorSizeX.
        sensor_size_y (Optional[int], optional): sensorSizeY.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureCameraMutationEnsurecamera"""
    return execute(
        EnsureCameraMutation,
        {
            "serialNumber": serial_number,
            "name": name,
            "pixelSizeX": pixel_size_x,
            "pixelSizeY": pixel_size_y,
            "sensorSizeX": sensor_size_x,
            "sensorSizeY": sensor_size_y,
        },
        rath=rath,
    ).ensure_camera


async def acreate_render_tree(
    name: str, tree: TreeInput, rath: Optional[MikroNextRath] = None
) -> CreateRenderTreeMutationCreaterendertree:
    """CreateRenderTree



    Arguments:
        name (str): name
        tree (TreeInput): tree
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateRenderTreeMutationCreaterendertree"""
    return (
        await aexecute(
            CreateRenderTreeMutation, {"name": name, "tree": tree}, rath=rath
        )
    ).create_render_tree


def create_render_tree(
    name: str, tree: TreeInput, rath: Optional[MikroNextRath] = None
) -> CreateRenderTreeMutationCreaterendertree:
    """CreateRenderTree



    Arguments:
        name (str): name
        tree (TreeInput): tree
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateRenderTreeMutationCreaterendertree"""
    return execute(
        CreateRenderTreeMutation, {"name": name, "tree": tree}, rath=rath
    ).create_render_tree


async def afrom_parquet_like(
    dataframe: ParquetLike,
    name: str,
    origins: Optional[List[ID]] = None,
    dataset: Optional[ID] = None,
    rath: Optional[MikroNextRath] = None,
) -> Table:
    """from_parquet_like



    Arguments:
        dataframe (ParquetLike): dataframe
        name (str): name
        origins (Optional[List[ID]], optional): origins.
        dataset (Optional[ID], optional): dataset.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Table"""
    return (
        await aexecute(
            From_parquet_likeMutation,
            {
                "dataframe": dataframe,
                "name": name,
                "origins": origins,
                "dataset": dataset,
            },
            rath=rath,
        )
    ).from_parquet_like


def from_parquet_like(
    dataframe: ParquetLike,
    name: str,
    origins: Optional[List[ID]] = None,
    dataset: Optional[ID] = None,
    rath: Optional[MikroNextRath] = None,
) -> Table:
    """from_parquet_like



    Arguments:
        dataframe (ParquetLike): dataframe
        name (str): name
        origins (Optional[List[ID]], optional): origins.
        dataset (Optional[ID], optional): dataset.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Table"""
    return execute(
        From_parquet_likeMutation,
        {"dataframe": dataframe, "name": name, "origins": origins, "dataset": dataset},
        rath=rath,
    ).from_parquet_like


async def arequest_table_upload(
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> Credentials:
    """RequestTableUpload


     requestTableUpload: Temporary Credentials for a file upload that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        key (str): key
        datalayer (str): datalayer
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Credentials"""
    return (
        await aexecute(
            RequestTableUploadMutation, {"key": key, "datalayer": datalayer}, rath=rath
        )
    ).request_table_upload


def request_table_upload(
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> Credentials:
    """RequestTableUpload


     requestTableUpload: Temporary Credentials for a file upload that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        key (str): key
        datalayer (str): datalayer
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Credentials"""
    return execute(
        RequestTableUploadMutation, {"key": key, "datalayer": datalayer}, rath=rath
    ).request_table_upload


async def arequest_table_access(
    store: ID, duration: Optional[int] = None, rath: Optional[MikroNextRath] = None
) -> AccessCredentials:
    """RequestTableAccess


     requestTableAccess: Temporary Credentials for a file download that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        store (ID): store
        duration (Optional[int], optional): duration.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        AccessCredentials"""
    return (
        await aexecute(
            RequestTableAccessMutation,
            {"store": store, "duration": duration},
            rath=rath,
        )
    ).request_table_access


def request_table_access(
    store: ID, duration: Optional[int] = None, rath: Optional[MikroNextRath] = None
) -> AccessCredentials:
    """RequestTableAccess


     requestTableAccess: Temporary Credentials for a file download that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        store (ID): store
        duration (Optional[int], optional): duration.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        AccessCredentials"""
    return execute(
        RequestTableAccessMutation, {"store": store, "duration": duration}, rath=rath
    ).request_table_access


async def afrom_file_like(
    file: FileLike,
    name: str,
    origins: Optional[List[ID]] = None,
    dataset: Optional[ID] = None,
    rath: Optional[MikroNextRath] = None,
) -> File:
    """from_file_like



    Arguments:
        file (FileLike): file
        name (str): name
        origins (Optional[List[ID]], optional): origins.
        dataset (Optional[ID], optional): dataset.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        File"""
    return (
        await aexecute(
            From_file_likeMutation,
            {"file": file, "name": name, "origins": origins, "dataset": dataset},
            rath=rath,
        )
    ).from_file_like


def from_file_like(
    file: FileLike,
    name: str,
    origins: Optional[List[ID]] = None,
    dataset: Optional[ID] = None,
    rath: Optional[MikroNextRath] = None,
) -> File:
    """from_file_like



    Arguments:
        file (FileLike): file
        name (str): name
        origins (Optional[List[ID]], optional): origins.
        dataset (Optional[ID], optional): dataset.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        File"""
    return execute(
        From_file_likeMutation,
        {"file": file, "name": name, "origins": origins, "dataset": dataset},
        rath=rath,
    ).from_file_like


async def arequest_file_upload(
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> Credentials:
    """RequestFileUpload


     requestFileUpload: Temporary Credentials for a file upload that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        key (str): key
        datalayer (str): datalayer
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Credentials"""
    return (
        await aexecute(
            RequestFileUploadMutation, {"key": key, "datalayer": datalayer}, rath=rath
        )
    ).request_file_upload


def request_file_upload(
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> Credentials:
    """RequestFileUpload


     requestFileUpload: Temporary Credentials for a file upload that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        key (str): key
        datalayer (str): datalayer
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Credentials"""
    return execute(
        RequestFileUploadMutation, {"key": key, "datalayer": datalayer}, rath=rath
    ).request_file_upload


async def arequest_file_access(
    store: ID, duration: Optional[int] = None, rath: Optional[MikroNextRath] = None
) -> AccessCredentials:
    """RequestFileAccess


     requestFileAccess: Temporary Credentials for a file download that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        store (ID): store
        duration (Optional[int], optional): duration.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        AccessCredentials"""
    return (
        await aexecute(
            RequestFileAccessMutation, {"store": store, "duration": duration}, rath=rath
        )
    ).request_file_access


def request_file_access(
    store: ID, duration: Optional[int] = None, rath: Optional[MikroNextRath] = None
) -> AccessCredentials:
    """RequestFileAccess


     requestFileAccess: Temporary Credentials for a file download that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        store (ID): store
        duration (Optional[int], optional): duration.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        AccessCredentials"""
    return execute(
        RequestFileAccessMutation, {"store": store, "duration": duration}, rath=rath
    ).request_file_access


async def acreate_stage(name: str, rath: Optional[MikroNextRath] = None) -> Stage:
    """CreateStage



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Stage"""
    return (await aexecute(CreateStageMutation, {"name": name}, rath=rath)).create_stage


def create_stage(name: str, rath: Optional[MikroNextRath] = None) -> Stage:
    """CreateStage



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Stage"""
    return execute(CreateStageMutation, {"name": name}, rath=rath).create_stage


async def acreate_roi(
    image: ID,
    vectors: List[FiveDVector],
    kind: RoiKind,
    rath: Optional[MikroNextRath] = None,
) -> ROI:
    """CreateRoi



    Arguments:
        image (ID): image
        vectors (List[FiveDVector]): vectors
        kind (RoiKind): kind
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ROI"""
    return (
        await aexecute(
            CreateRoiMutation,
            {"image": image, "vectors": vectors, "kind": kind},
            rath=rath,
        )
    ).create_roi


def create_roi(
    image: ID,
    vectors: List[FiveDVector],
    kind: RoiKind,
    rath: Optional[MikroNextRath] = None,
) -> ROI:
    """CreateRoi



    Arguments:
        image (ID): image
        vectors (List[FiveDVector]): vectors
        kind (RoiKind): kind
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ROI"""
    return execute(
        CreateRoiMutation, {"image": image, "vectors": vectors, "kind": kind}, rath=rath
    ).create_roi


async def adelete_roi(roi: ID, rath: Optional[MikroNextRath] = None) -> ID:
    """DeleteRoi


     deleteRoi: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.


    Arguments:
        roi (ID): roi
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ID"""
    return (await aexecute(DeleteRoiMutation, {"roi": roi}, rath=rath)).delete_roi


def delete_roi(roi: ID, rath: Optional[MikroNextRath] = None) -> ID:
    """DeleteRoi


     deleteRoi: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.


    Arguments:
        roi (ID): roi
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ID"""
    return execute(DeleteRoiMutation, {"roi": roi}, rath=rath).delete_roi


async def acreate_objective(
    serial_number: str,
    name: Optional[str] = None,
    na: Optional[float] = None,
    magnification: Optional[float] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateObjectiveMutationCreateobjective:
    """CreateObjective



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        na (Optional[float], optional): na.
        magnification (Optional[float], optional): magnification.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateObjectiveMutationCreateobjective"""
    return (
        await aexecute(
            CreateObjectiveMutation,
            {
                "serialNumber": serial_number,
                "name": name,
                "na": na,
                "magnification": magnification,
            },
            rath=rath,
        )
    ).create_objective


def create_objective(
    serial_number: str,
    name: Optional[str] = None,
    na: Optional[float] = None,
    magnification: Optional[float] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateObjectiveMutationCreateobjective:
    """CreateObjective



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        na (Optional[float], optional): na.
        magnification (Optional[float], optional): magnification.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateObjectiveMutationCreateobjective"""
    return execute(
        CreateObjectiveMutation,
        {
            "serialNumber": serial_number,
            "name": name,
            "na": na,
            "magnification": magnification,
        },
        rath=rath,
    ).create_objective


async def aensure_objective(
    serial_number: str,
    name: Optional[str] = None,
    na: Optional[float] = None,
    magnification: Optional[float] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureObjectiveMutationEnsureobjective:
    """EnsureObjective



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        na (Optional[float], optional): na.
        magnification (Optional[float], optional): magnification.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureObjectiveMutationEnsureobjective"""
    return (
        await aexecute(
            EnsureObjectiveMutation,
            {
                "serialNumber": serial_number,
                "name": name,
                "na": na,
                "magnification": magnification,
            },
            rath=rath,
        )
    ).ensure_objective


def ensure_objective(
    serial_number: str,
    name: Optional[str] = None,
    na: Optional[float] = None,
    magnification: Optional[float] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureObjectiveMutationEnsureobjective:
    """EnsureObjective



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        na (Optional[float], optional): na.
        magnification (Optional[float], optional): magnification.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureObjectiveMutationEnsureobjective"""
    return execute(
        EnsureObjectiveMutation,
        {
            "serialNumber": serial_number,
            "name": name,
            "na": na,
            "magnification": magnification,
        },
        rath=rath,
    ).ensure_objective


async def acreate_dataset(
    name: str, rath: Optional[MikroNextRath] = None
) -> CreateDatasetMutationCreatedataset:
    """CreateDataset



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateDatasetMutationCreatedataset"""
    return (
        await aexecute(CreateDatasetMutation, {"name": name}, rath=rath)
    ).create_dataset


def create_dataset(
    name: str, rath: Optional[MikroNextRath] = None
) -> CreateDatasetMutationCreatedataset:
    """CreateDataset



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateDatasetMutationCreatedataset"""
    return execute(CreateDatasetMutation, {"name": name}, rath=rath).create_dataset


async def aupdate_dataset(
    id: ID, name: str, rath: Optional[MikroNextRath] = None
) -> UpdateDatasetMutationUpdatedataset:
    """UpdateDataset



    Arguments:
        id (ID): id
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        UpdateDatasetMutationUpdatedataset"""
    return (
        await aexecute(UpdateDatasetMutation, {"id": id, "name": name}, rath=rath)
    ).update_dataset


def update_dataset(
    id: ID, name: str, rath: Optional[MikroNextRath] = None
) -> UpdateDatasetMutationUpdatedataset:
    """UpdateDataset



    Arguments:
        id (ID): id
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        UpdateDatasetMutationUpdatedataset"""
    return execute(
        UpdateDatasetMutation, {"id": id, "name": name}, rath=rath
    ).update_dataset


async def arevert_dataset(
    dataset: ID, history: ID, rath: Optional[MikroNextRath] = None
) -> RevertDatasetMutationRevertdataset:
    """RevertDataset



    Arguments:
        dataset (ID): dataset
        history (ID): history
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RevertDatasetMutationRevertdataset"""
    return (
        await aexecute(
            RevertDatasetMutation, {"dataset": dataset, "history": history}, rath=rath
        )
    ).revert_dataset


def revert_dataset(
    dataset: ID, history: ID, rath: Optional[MikroNextRath] = None
) -> RevertDatasetMutationRevertdataset:
    """RevertDataset



    Arguments:
        dataset (ID): dataset
        history (ID): history
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RevertDatasetMutationRevertdataset"""
    return execute(
        RevertDatasetMutation, {"dataset": dataset, "history": history}, rath=rath
    ).revert_dataset


async def acreate_instrument(
    serial_number: str,
    name: Optional[str] = None,
    model: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateInstrumentMutationCreateinstrument:
    """CreateInstrument



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        model (Optional[str], optional): model.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateInstrumentMutationCreateinstrument"""
    return (
        await aexecute(
            CreateInstrumentMutation,
            {"serialNumber": serial_number, "name": name, "model": model},
            rath=rath,
        )
    ).create_instrument


def create_instrument(
    serial_number: str,
    name: Optional[str] = None,
    model: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateInstrumentMutationCreateinstrument:
    """CreateInstrument



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        model (Optional[str], optional): model.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateInstrumentMutationCreateinstrument"""
    return execute(
        CreateInstrumentMutation,
        {"serialNumber": serial_number, "name": name, "model": model},
        rath=rath,
    ).create_instrument


async def aensure_instrument(
    serial_number: str,
    name: Optional[str] = None,
    model: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureInstrumentMutationEnsureinstrument:
    """EnsureInstrument



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        model (Optional[str], optional): model.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureInstrumentMutationEnsureinstrument"""
    return (
        await aexecute(
            EnsureInstrumentMutation,
            {"serialNumber": serial_number, "name": name, "model": model},
            rath=rath,
        )
    ).ensure_instrument


def ensure_instrument(
    serial_number: str,
    name: Optional[str] = None,
    model: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureInstrumentMutationEnsureinstrument:
    """EnsureInstrument



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        model (Optional[str], optional): model.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureInstrumentMutationEnsureinstrument"""
    return execute(
        EnsureInstrumentMutation,
        {"serialNumber": serial_number, "name": name, "model": model},
        rath=rath,
    ).ensure_instrument


async def acreate_antibody(
    name: str, epitope: Optional[str] = None, rath: Optional[MikroNextRath] = None
) -> CreateAntibodyMutationCreateantibody:
    """CreateAntibody



    Arguments:
        name (str): name
        epitope (Optional[str], optional): epitope.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateAntibodyMutationCreateantibody"""
    return (
        await aexecute(
            CreateAntibodyMutation, {"name": name, "epitope": epitope}, rath=rath
        )
    ).create_antibody


def create_antibody(
    name: str, epitope: Optional[str] = None, rath: Optional[MikroNextRath] = None
) -> CreateAntibodyMutationCreateantibody:
    """CreateAntibody



    Arguments:
        name (str): name
        epitope (Optional[str], optional): epitope.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateAntibodyMutationCreateantibody"""
    return execute(
        CreateAntibodyMutation, {"name": name, "epitope": epitope}, rath=rath
    ).create_antibody


async def aensure_antibody(
    name: str, epitope: Optional[str] = None, rath: Optional[MikroNextRath] = None
) -> EnsureAntibodyMutationEnsureantibody:
    """EnsureAntibody



    Arguments:
        name (str): name
        epitope (Optional[str], optional): epitope.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureAntibodyMutationEnsureantibody"""
    return (
        await aexecute(
            EnsureAntibodyMutation, {"name": name, "epitope": epitope}, rath=rath
        )
    ).ensure_antibody


def ensure_antibody(
    name: str, epitope: Optional[str] = None, rath: Optional[MikroNextRath] = None
) -> EnsureAntibodyMutationEnsureantibody:
    """EnsureAntibody



    Arguments:
        name (str): name
        epitope (Optional[str], optional): epitope.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureAntibodyMutationEnsureantibody"""
    return execute(
        EnsureAntibodyMutation, {"name": name, "epitope": epitope}, rath=rath
    ).ensure_antibody


async def acreate_fluorophore(
    name: str,
    excitation_wavelength: Optional[Micrometers] = None,
    emission_wavelength: Optional[Micrometers] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateFluorophoreMutationCreatefluorophore:
    """CreateFluorophore



    Arguments:
        name (str): name
        excitation_wavelength (Optional[Micrometers], optional): excitationWavelength.
        emission_wavelength (Optional[Micrometers], optional): emissionWavelength.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateFluorophoreMutationCreatefluorophore"""
    return (
        await aexecute(
            CreateFluorophoreMutation,
            {
                "name": name,
                "excitationWavelength": excitation_wavelength,
                "emissionWavelength": emission_wavelength,
            },
            rath=rath,
        )
    ).create_fluorophore


def create_fluorophore(
    name: str,
    excitation_wavelength: Optional[Micrometers] = None,
    emission_wavelength: Optional[Micrometers] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateFluorophoreMutationCreatefluorophore:
    """CreateFluorophore



    Arguments:
        name (str): name
        excitation_wavelength (Optional[Micrometers], optional): excitationWavelength.
        emission_wavelength (Optional[Micrometers], optional): emissionWavelength.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateFluorophoreMutationCreatefluorophore"""
    return execute(
        CreateFluorophoreMutation,
        {
            "name": name,
            "excitationWavelength": excitation_wavelength,
            "emissionWavelength": emission_wavelength,
        },
        rath=rath,
    ).create_fluorophore


async def aensure_fluorophore(
    name: str,
    excitation_wavelength: Optional[Micrometers] = None,
    emission_wavelength: Optional[Micrometers] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureFluorophoreMutationEnsurefluorophore:
    """EnsureFluorophore



    Arguments:
        name (str): name
        excitation_wavelength (Optional[Micrometers], optional): excitationWavelength.
        emission_wavelength (Optional[Micrometers], optional): emissionWavelength.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureFluorophoreMutationEnsurefluorophore"""
    return (
        await aexecute(
            EnsureFluorophoreMutation,
            {
                "name": name,
                "excitationWavelength": excitation_wavelength,
                "emissionWavelength": emission_wavelength,
            },
            rath=rath,
        )
    ).ensure_fluorophore


def ensure_fluorophore(
    name: str,
    excitation_wavelength: Optional[Micrometers] = None,
    emission_wavelength: Optional[Micrometers] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureFluorophoreMutationEnsurefluorophore:
    """EnsureFluorophore



    Arguments:
        name (str): name
        excitation_wavelength (Optional[Micrometers], optional): excitationWavelength.
        emission_wavelength (Optional[Micrometers], optional): emissionWavelength.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureFluorophoreMutationEnsurefluorophore"""
    return execute(
        EnsureFluorophoreMutation,
        {
            "name": name,
            "excitationWavelength": excitation_wavelength,
            "emissionWavelength": emission_wavelength,
        },
        rath=rath,
    ).ensure_fluorophore


async def afrom_array_like(
    array: ArrayLike,
    name: str,
    origins: Optional[List[ID]] = None,
    channel_views: Optional[List[PartialChannelViewInput]] = None,
    transformation_views: Optional[List[PartialAffineTransformationViewInput]] = None,
    label_views: Optional[List[PartialLabelViewInput]] = None,
    rgb_views: Optional[List[PartialRGBViewInput]] = None,
    acquisition_views: Optional[List[PartialAcquisitionViewInput]] = None,
    timepoint_views: Optional[List[PartialTimepointViewInput]] = None,
    optics_views: Optional[List[PartialOpticsViewInput]] = None,
    tags: Optional[List[str]] = None,
    file_origins: Optional[List[ID]] = None,
    roi_origins: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Image:
    """from_array_like



    Arguments:
        array (ArrayLike): array
        name (str): name
        origins (Optional[List[ID]], optional): origins.
        channel_views (Optional[List[PartialChannelViewInput]], optional): channelViews.
        transformation_views (Optional[List[PartialAffineTransformationViewInput]], optional): transformationViews.
        label_views (Optional[List[PartialLabelViewInput]], optional): labelViews.
        rgb_views (Optional[List[PartialRGBViewInput]], optional): rgbViews.
        acquisition_views (Optional[List[PartialAcquisitionViewInput]], optional): acquisitionViews.
        timepoint_views (Optional[List[PartialTimepointViewInput]], optional): timepointViews.
        optics_views (Optional[List[PartialOpticsViewInput]], optional): opticsViews.
        tags (Optional[List[str]], optional): tags.
        file_origins (Optional[List[ID]], optional): fileOrigins.
        roi_origins (Optional[List[ID]], optional): roiOrigins.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Image"""
    return (
        await aexecute(
            From_array_likeMutation,
            {
                "array": array,
                "name": name,
                "origins": origins,
                "channelViews": channel_views,
                "transformationViews": transformation_views,
                "labelViews": label_views,
                "rgbViews": rgb_views,
                "acquisitionViews": acquisition_views,
                "timepointViews": timepoint_views,
                "opticsViews": optics_views,
                "tags": tags,
                "fileOrigins": file_origins,
                "roiOrigins": roi_origins,
            },
            rath=rath,
        )
    ).from_array_like


def from_array_like(
    array: ArrayLike,
    name: str,
    origins: Optional[List[ID]] = None,
    channel_views: Optional[List[PartialChannelViewInput]] = None,
    transformation_views: Optional[List[PartialAffineTransformationViewInput]] = None,
    label_views: Optional[List[PartialLabelViewInput]] = None,
    rgb_views: Optional[List[PartialRGBViewInput]] = None,
    acquisition_views: Optional[List[PartialAcquisitionViewInput]] = None,
    timepoint_views: Optional[List[PartialTimepointViewInput]] = None,
    optics_views: Optional[List[PartialOpticsViewInput]] = None,
    tags: Optional[List[str]] = None,
    file_origins: Optional[List[ID]] = None,
    roi_origins: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Image:
    """from_array_like



    Arguments:
        array (ArrayLike): array
        name (str): name
        origins (Optional[List[ID]], optional): origins.
        channel_views (Optional[List[PartialChannelViewInput]], optional): channelViews.
        transformation_views (Optional[List[PartialAffineTransformationViewInput]], optional): transformationViews.
        label_views (Optional[List[PartialLabelViewInput]], optional): labelViews.
        rgb_views (Optional[List[PartialRGBViewInput]], optional): rgbViews.
        acquisition_views (Optional[List[PartialAcquisitionViewInput]], optional): acquisitionViews.
        timepoint_views (Optional[List[PartialTimepointViewInput]], optional): timepointViews.
        optics_views (Optional[List[PartialOpticsViewInput]], optional): opticsViews.
        tags (Optional[List[str]], optional): tags.
        file_origins (Optional[List[ID]], optional): fileOrigins.
        roi_origins (Optional[List[ID]], optional): roiOrigins.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Image"""
    return execute(
        From_array_likeMutation,
        {
            "array": array,
            "name": name,
            "origins": origins,
            "channelViews": channel_views,
            "transformationViews": transformation_views,
            "labelViews": label_views,
            "rgbViews": rgb_views,
            "acquisitionViews": acquisition_views,
            "timepointViews": timepoint_views,
            "opticsViews": optics_views,
            "tags": tags,
            "fileOrigins": file_origins,
            "roiOrigins": roi_origins,
        },
        rath=rath,
    ).from_array_like


async def arequest_upload(
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> Credentials:
    """RequestUpload


     requestUpload: Temporary Credentials for a file upload that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        key (str): key
        datalayer (str): datalayer
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Credentials"""
    return (
        await aexecute(
            RequestUploadMutation, {"key": key, "datalayer": datalayer}, rath=rath
        )
    ).request_upload


def request_upload(
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> Credentials:
    """RequestUpload


     requestUpload: Temporary Credentials for a file upload that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        key (str): key
        datalayer (str): datalayer
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Credentials"""
    return execute(
        RequestUploadMutation, {"key": key, "datalayer": datalayer}, rath=rath
    ).request_upload


async def arequest_access(
    store: ID, duration: Optional[int] = None, rath: Optional[MikroNextRath] = None
) -> AccessCredentials:
    """RequestAccess


     requestAccess: Temporary Credentials for a file download that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        store (ID): store
        duration (Optional[int], optional): duration.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        AccessCredentials"""
    return (
        await aexecute(
            RequestAccessMutation, {"store": store, "duration": duration}, rath=rath
        )
    ).request_access


def request_access(
    store: ID, duration: Optional[int] = None, rath: Optional[MikroNextRath] = None
) -> AccessCredentials:
    """RequestAccess


     requestAccess: Temporary Credentials for a file download that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        store (ID): store
        duration (Optional[int], optional): duration.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        AccessCredentials"""
    return execute(
        RequestAccessMutation, {"store": store, "duration": duration}, rath=rath
    ).request_access


async def acreate_era(
    name: str, begin: Optional[datetime] = None, rath: Optional[MikroNextRath] = None
) -> CreateEraMutationCreateera:
    """CreateEra



    Arguments:
        name (str): name
        begin (Optional[datetime], optional): begin.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateEraMutationCreateera"""
    return (
        await aexecute(CreateEraMutation, {"name": name, "begin": begin}, rath=rath)
    ).create_era


def create_era(
    name: str, begin: Optional[datetime] = None, rath: Optional[MikroNextRath] = None
) -> CreateEraMutationCreateera:
    """CreateEra



    Arguments:
        name (str): name
        begin (Optional[datetime], optional): begin.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateEraMutationCreateera"""
    return execute(
        CreateEraMutation, {"name": name, "begin": begin}, rath=rath
    ).create_era


async def acreate_snapshot(
    image: ID, file: Upload, rath: Optional[MikroNextRath] = None
) -> Snapshot:
    """CreateSnapshot



    Arguments:
        image (ID): image
        file (Upload): file
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Snapshot"""
    return (
        await aexecute(
            CreateSnapshotMutation, {"image": image, "file": file}, rath=rath
        )
    ).create_snapshot


def create_snapshot(
    image: ID, file: Upload, rath: Optional[MikroNextRath] = None
) -> Snapshot:
    """CreateSnapshot



    Arguments:
        image (ID): image
        file (Upload): file
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Snapshot"""
    return execute(
        CreateSnapshotMutation, {"image": image, "file": file}, rath=rath
    ).create_snapshot


async def acreate_rgb_view(
    image: ID,
    context: ID,
    gamma: Optional[float] = None,
    contrast_limit_max: Optional[float] = None,
    contrast_limit_min: Optional[float] = None,
    rescale: Optional[bool] = None,
    active: Optional[bool] = None,
    color_map: Optional[ColorMap] = None,
    base_color: Optional[List[float]] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateRgbViewMutationCreatergbview:
    """CreateRgbView



    Arguments:
        image (ID): image
        context (ID): context
        gamma (Optional[float], optional): gamma.
        contrast_limit_max (Optional[float], optional): contrastLimitMax.
        contrast_limit_min (Optional[float], optional): contrastLimitMin.
        rescale (Optional[bool], optional): rescale.
        active (Optional[bool], optional): active.
        color_map (Optional[ColorMap], optional): colorMap.
        base_color (Optional[List[float]], optional): baseColor.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateRgbViewMutationCreatergbview"""
    return (
        await aexecute(
            CreateRgbViewMutation,
            {
                "image": image,
                "context": context,
                "gamma": gamma,
                "contrastLimitMax": contrast_limit_max,
                "contrastLimitMin": contrast_limit_min,
                "rescale": rescale,
                "active": active,
                "colorMap": color_map,
                "baseColor": base_color,
            },
            rath=rath,
        )
    ).create_rgb_view


def create_rgb_view(
    image: ID,
    context: ID,
    gamma: Optional[float] = None,
    contrast_limit_max: Optional[float] = None,
    contrast_limit_min: Optional[float] = None,
    rescale: Optional[bool] = None,
    active: Optional[bool] = None,
    color_map: Optional[ColorMap] = None,
    base_color: Optional[List[float]] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateRgbViewMutationCreatergbview:
    """CreateRgbView



    Arguments:
        image (ID): image
        context (ID): context
        gamma (Optional[float], optional): gamma.
        contrast_limit_max (Optional[float], optional): contrastLimitMax.
        contrast_limit_min (Optional[float], optional): contrastLimitMin.
        rescale (Optional[bool], optional): rescale.
        active (Optional[bool], optional): active.
        color_map (Optional[ColorMap], optional): colorMap.
        base_color (Optional[List[float]], optional): baseColor.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateRgbViewMutationCreatergbview"""
    return execute(
        CreateRgbViewMutation,
        {
            "image": image,
            "context": context,
            "gamma": gamma,
            "contrastLimitMax": contrast_limit_max,
            "contrastLimitMin": contrast_limit_min,
            "rescale": rescale,
            "active": active,
            "colorMap": color_map,
            "baseColor": base_color,
        },
        rath=rath,
    ).create_rgb_view


async def acreate_rgb_context(
    input: CreateRGBContextInput, rath: Optional[MikroNextRath] = None
) -> RGBContext:
    """CreateRGBContext



    Arguments:
        input (CreateRGBContextInput): input
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RGBContext"""
    return (
        await aexecute(CreateRGBContextMutation, {"input": input}, rath=rath)
    ).create_rgb_context


def create_rgb_context(
    input: CreateRGBContextInput, rath: Optional[MikroNextRath] = None
) -> RGBContext:
    """CreateRGBContext



    Arguments:
        input (CreateRGBContextInput): input
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RGBContext"""
    return execute(
        CreateRGBContextMutation, {"input": input}, rath=rath
    ).create_rgb_context


async def aupdate_rgb_context(
    input: UpdateRGBContextInput, rath: Optional[MikroNextRath] = None
) -> RGBContext:
    """UpdateRGBContext



    Arguments:
        input (UpdateRGBContextInput): input
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RGBContext"""
    return (
        await aexecute(UpdateRGBContextMutation, {"input": input}, rath=rath)
    ).update_rgb_context


def update_rgb_context(
    input: UpdateRGBContextInput, rath: Optional[MikroNextRath] = None
) -> RGBContext:
    """UpdateRGBContext



    Arguments:
        input (UpdateRGBContextInput): input
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RGBContext"""
    return execute(
        UpdateRGBContextMutation, {"input": input}, rath=rath
    ).update_rgb_context


async def acreate_view_collection(
    name: str, rath: Optional[MikroNextRath] = None
) -> CreateViewCollectionMutationCreateviewcollection:
    """CreateViewCollection



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateViewCollectionMutationCreateviewcollection"""
    return (
        await aexecute(CreateViewCollectionMutation, {"name": name}, rath=rath)
    ).create_view_collection


def create_view_collection(
    name: str, rath: Optional[MikroNextRath] = None
) -> CreateViewCollectionMutationCreateviewcollection:
    """CreateViewCollection



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateViewCollectionMutationCreateviewcollection"""
    return execute(
        CreateViewCollectionMutation, {"name": name}, rath=rath
    ).create_view_collection


async def acreate_channel(
    name: str, rath: Optional[MikroNextRath] = None
) -> CreateChannelMutationCreatechannel:
    """CreateChannel



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateChannelMutationCreatechannel"""
    return (
        await aexecute(CreateChannelMutation, {"name": name}, rath=rath)
    ).create_channel


def create_channel(
    name: str, rath: Optional[MikroNextRath] = None
) -> CreateChannelMutationCreatechannel:
    """CreateChannel



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateChannelMutationCreatechannel"""
    return execute(CreateChannelMutation, {"name": name}, rath=rath).create_channel


async def aensure_channel(
    name: str, rath: Optional[MikroNextRath] = None
) -> EnsureChannelMutationEnsurechannel:
    """EnsureChannel



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureChannelMutationEnsurechannel"""
    return (
        await aexecute(EnsureChannelMutation, {"name": name}, rath=rath)
    ).ensure_channel


def ensure_channel(
    name: str, rath: Optional[MikroNextRath] = None
) -> EnsureChannelMutationEnsurechannel:
    """EnsureChannel



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureChannelMutationEnsurechannel"""
    return execute(EnsureChannelMutation, {"name": name}, rath=rath).ensure_channel


async def aget_camera(id: ID, rath: Optional[MikroNextRath] = None) -> Camera:
    """GetCamera



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Camera"""
    return (await aexecute(GetCameraQuery, {"id": id}, rath=rath)).camera


def get_camera(id: ID, rath: Optional[MikroNextRath] = None) -> Camera:
    """GetCamera



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Camera"""
    return execute(GetCameraQuery, {"id": id}, rath=rath).camera


async def aget_table(id: ID, rath: Optional[MikroNextRath] = None) -> Table:
    """GetTable



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Table"""
    return (await aexecute(GetTableQuery, {"id": id}, rath=rath)).table


def get_table(id: ID, rath: Optional[MikroNextRath] = None) -> Table:
    """GetTable



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Table"""
    return execute(GetTableQuery, {"id": id}, rath=rath).table


async def aget_file(id: ID, rath: Optional[MikroNextRath] = None) -> File:
    """GetFile



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        File"""
    return (await aexecute(GetFileQuery, {"id": id}, rath=rath)).file


def get_file(id: ID, rath: Optional[MikroNextRath] = None) -> File:
    """GetFile



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        File"""
    return execute(GetFileQuery, {"id": id}, rath=rath).file


async def asearch_files(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchFilesQueryOptions]:
    """SearchFiles



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        pagination (Optional[OffsetPaginationInput], optional): pagination.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchFilesQueryFiles]"""
    return (
        await aexecute(
            SearchFilesQuery,
            {"search": search, "values": values, "pagination": pagination},
            rath=rath,
        )
    ).options


def search_files(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchFilesQueryOptions]:
    """SearchFiles



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        pagination (Optional[OffsetPaginationInput], optional): pagination.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchFilesQueryFiles]"""
    return execute(
        SearchFilesQuery,
        {"search": search, "values": values, "pagination": pagination},
        rath=rath,
    ).options


async def aget_stage(id: ID, rath: Optional[MikroNextRath] = None) -> Stage:
    """GetStage



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Stage"""
    return (await aexecute(GetStageQuery, {"id": id}, rath=rath)).stage


def get_stage(id: ID, rath: Optional[MikroNextRath] = None) -> Stage:
    """GetStage



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Stage"""
    return execute(GetStageQuery, {"id": id}, rath=rath).stage


async def asearch_stages(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchStagesQueryOptions]:
    """SearchStages



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        pagination (Optional[OffsetPaginationInput], optional): pagination.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchStagesQueryStages]"""
    return (
        await aexecute(
            SearchStagesQuery,
            {"search": search, "values": values, "pagination": pagination},
            rath=rath,
        )
    ).options


def search_stages(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchStagesQueryOptions]:
    """SearchStages



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        pagination (Optional[OffsetPaginationInput], optional): pagination.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchStagesQueryStages]"""
    return execute(
        SearchStagesQuery,
        {"search": search, "values": values, "pagination": pagination},
        rath=rath,
    ).options


async def aget_rois(image: ID, rath: Optional[MikroNextRath] = None) -> List[ROI]:
    """GetRois



    Arguments:
        image (ID): image
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[ROI]"""
    return (await aexecute(GetRoisQuery, {"image": image}, rath=rath)).rois


def get_rois(image: ID, rath: Optional[MikroNextRath] = None) -> List[ROI]:
    """GetRois



    Arguments:
        image (ID): image
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[ROI]"""
    return execute(GetRoisQuery, {"image": image}, rath=rath).rois


async def aget_roi(id: ID, rath: Optional[MikroNextRath] = None) -> ROI:
    """GetRoi



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ROI"""
    return (await aexecute(GetRoiQuery, {"id": id}, rath=rath)).roi


def get_roi(id: ID, rath: Optional[MikroNextRath] = None) -> ROI:
    """GetRoi



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ROI"""
    return execute(GetRoiQuery, {"id": id}, rath=rath).roi


async def aget_objective(id: ID, rath: Optional[MikroNextRath] = None) -> Objective:
    """GetObjective



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Objective"""
    return (await aexecute(GetObjectiveQuery, {"id": id}, rath=rath)).objective


def get_objective(id: ID, rath: Optional[MikroNextRath] = None) -> Objective:
    """GetObjective



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Objective"""
    return execute(GetObjectiveQuery, {"id": id}, rath=rath).objective


async def aget_dataset(id: ID, rath: Optional[MikroNextRath] = None) -> Dataset:
    """GetDataset



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Dataset"""
    return (await aexecute(GetDatasetQuery, {"id": id}, rath=rath)).dataset


def get_dataset(id: ID, rath: Optional[MikroNextRath] = None) -> Dataset:
    """GetDataset



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Dataset"""
    return execute(GetDatasetQuery, {"id": id}, rath=rath).dataset


async def aget_instrument(id: ID, rath: Optional[MikroNextRath] = None) -> Instrument:
    """GetInstrument



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Instrument"""
    return (await aexecute(GetInstrumentQuery, {"id": id}, rath=rath)).instrument


def get_instrument(id: ID, rath: Optional[MikroNextRath] = None) -> Instrument:
    """GetInstrument



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Instrument"""
    return execute(GetInstrumentQuery, {"id": id}, rath=rath).instrument


async def aget_image(id: ID, rath: Optional[MikroNextRath] = None) -> Image:
    """GetImage



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Image"""
    return (await aexecute(GetImageQuery, {"id": id}, rath=rath)).image


def get_image(id: ID, rath: Optional[MikroNextRath] = None) -> Image:
    """GetImage



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Image"""
    return execute(GetImageQuery, {"id": id}, rath=rath).image


async def aget_random_image(rath: Optional[MikroNextRath] = None) -> Image:
    """GetRandomImage



    Arguments:
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Image"""
    return (await aexecute(GetRandomImageQuery, {}, rath=rath)).random_image


def get_random_image(rath: Optional[MikroNextRath] = None) -> Image:
    """GetRandomImage



    Arguments:
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Image"""
    return execute(GetRandomImageQuery, {}, rath=rath).random_image


async def asearch_images(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchImagesQueryOptions]:
    """SearchImages



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchImagesQueryImages]"""
    return (
        await aexecute(
            SearchImagesQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_images(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchImagesQueryOptions]:
    """SearchImages



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchImagesQueryImages]"""
    return execute(
        SearchImagesQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aimages(
    filter: Optional[ImageFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[Image]:
    """Images



    Arguments:
        filter (Optional[ImageFilter], optional): filter.
        pagination (Optional[OffsetPaginationInput], optional): pagination.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[Image]"""
    return (
        await aexecute(
            ImagesQuery, {"filter": filter, "pagination": pagination}, rath=rath
        )
    ).images


def images(
    filter: Optional[ImageFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[Image]:
    """Images



    Arguments:
        filter (Optional[ImageFilter], optional): filter.
        pagination (Optional[OffsetPaginationInput], optional): pagination.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[Image]"""
    return execute(
        ImagesQuery, {"filter": filter, "pagination": pagination}, rath=rath
    ).images


async def aget_snapshot(id: ID, rath: Optional[MikroNextRath] = None) -> Snapshot:
    """GetSnapshot



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Snapshot"""
    return (await aexecute(GetSnapshotQuery, {"id": id}, rath=rath)).snapshot


def get_snapshot(id: ID, rath: Optional[MikroNextRath] = None) -> Snapshot:
    """GetSnapshot



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Snapshot"""
    return execute(GetSnapshotQuery, {"id": id}, rath=rath).snapshot


async def asearch_snapshots(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchSnapshotsQueryOptions]:
    """SearchSnapshots



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchSnapshotsQuerySnapshots]"""
    return (
        await aexecute(
            SearchSnapshotsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_snapshots(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchSnapshotsQueryOptions]:
    """SearchSnapshots



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchSnapshotsQuerySnapshots]"""
    return execute(
        SearchSnapshotsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_rgb_context(id: ID, rath: Optional[MikroNextRath] = None) -> RGBContext:
    """GetRGBContext



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RGBContext"""
    return (await aexecute(GetRGBContextQuery, {"id": id}, rath=rath)).rgbcontext


def get_rgb_context(id: ID, rath: Optional[MikroNextRath] = None) -> RGBContext:
    """GetRGBContext



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RGBContext"""
    return execute(GetRGBContextQuery, {"id": id}, rath=rath).rgbcontext


async def awatch_rois(
    image: ID, rath: Optional[MikroNextRath] = None
) -> AsyncIterator[WatchRoisSubscriptionRois]:
    """WatchRois



    Arguments:
        image (ID): image
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        WatchRoisSubscriptionRois"""
    async for event in asubscribe(WatchRoisSubscription, {"image": image}, rath=rath):
        yield event.rois


def watch_rois(
    image: ID, rath: Optional[MikroNextRath] = None
) -> Iterator[WatchRoisSubscriptionRois]:
    """WatchRois



    Arguments:
        image (ID): image
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        WatchRoisSubscriptionRois"""
    for event in subscribe(WatchRoisSubscription, {"image": image}, rath=rath):
        yield event.rois


AffineTransformationViewFilter.update_forward_refs()
ChannelView.update_forward_refs()
DatasetFilter.update_forward_refs()
EraFilter.update_forward_refs()
File.update_forward_refs()
Image.update_forward_refs()
ImageFilter.update_forward_refs()
LabelView.update_forward_refs()
ProvenanceFilter.update_forward_refs()
RGBContextImage.update_forward_refs()
StageFilter.update_forward_refs()
Table.update_forward_refs()
TimepointView.update_forward_refs()
TimepointViewFilter.update_forward_refs()
TreeInput.update_forward_refs()
TreeNodeInput.update_forward_refs()
ZarrStoreFilter.update_forward_refs()
