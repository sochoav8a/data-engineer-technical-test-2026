from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class Quantity(BaseModel):
    value: Optional[float] = None
    unit: Optional[str] = None
    raw: Optional[str] = None


class ProjectMetadata(BaseModel):
    project_name: Optional[str] = None
    company_name: Optional[str] = None
    location_country: Optional[str] = None
    location_region: Optional[str] = None
    report_date: Optional[str] = None
    report_date_raw: Optional[str] = None
    source_pdf: Optional[str] = None


class MineralResource(BaseModel):
    category: Optional[str] = None
    tonnes: Quantity = Field(default_factory=Quantity)
    grade: Quantity = Field(default_factory=Quantity)
    metal: Optional[str] = None
    contained_metal: Quantity = Field(default_factory=Quantity)
    source_pages: Optional[str] = None

    @field_validator("tonnes", "grade", "contained_metal", mode="before")
    @classmethod
    def _coerce_quantity(cls, value):
        if value is None:
            return {}
        return value


class MineralReserve(BaseModel):
    category: Optional[str] = None
    tonnes: Quantity = Field(default_factory=Quantity)
    grade: Quantity = Field(default_factory=Quantity)
    metal: Optional[str] = None
    contained_metal: Quantity = Field(default_factory=Quantity)
    source_pages: Optional[str] = None

    @field_validator("tonnes", "grade", "contained_metal", mode="before")
    @classmethod
    def _coerce_quantity(cls, value):
        if value is None:
            return {}
        return value


class Economics(BaseModel):
    capex: Quantity | None = None
    opex: Quantity | None = None
    npv: Quantity | None = None
    irr: Quantity | None = None
    currency: Optional[str] = None
    source_pages: Optional[str] = None


class MetadataResult(BaseModel):
    metadata: ProjectMetadata = Field(default_factory=ProjectMetadata)


class ResourcesResult(BaseModel):
    resources: List[MineralResource] = Field(default_factory=list)


class ReservesResult(BaseModel):
    reserves: List[MineralReserve] = Field(default_factory=list)


class EconomicsResult(BaseModel):
    economics: Economics = Field(default_factory=Economics)


class ExtractionResult(BaseModel):
    metadata: ProjectMetadata = Field(default_factory=ProjectMetadata)
    resources: List[MineralResource] = Field(default_factory=list)
    reserves: List[MineralReserve] = Field(default_factory=list)
    economics: Economics = Field(default_factory=Economics)
    confidence: Optional[float] = None
    warnings: List[str] = Field(default_factory=list)
