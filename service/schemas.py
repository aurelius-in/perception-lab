from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DatasetSpec(BaseModel):
    """Specification for an input dataset to be evaluated or ingested."""

    dataset_id: str = Field(..., description="Unique dataset identifier")
    uris: List[str] = Field(default_factory=list, description="List of URIs or filepaths")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata for dataset")


class EvalSpec(BaseModel):
    """Specification for an evaluation run request."""

    run_id: Optional[str] = Field(default=None, description="Client-provided run identifier (optional)")
    model_name: str = Field(..., description="Model name")
    model_version: str = Field(..., description="Model version or digest")
    dataset: DatasetSpec = Field(..., description="Dataset specification")
    params: Dict[str, Any] = Field(default_factory=dict, description="Additional evaluation parameters")


class ResultCard(BaseModel):
    """Compact result record with provenance."""

    run_id: str = Field(..., description="Run identifier")
    model_name: str = Field(..., description="Model name")
    model_version: str = Field(..., description="Model version or digest")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Aggregate metrics for the run")
    artifacts: Dict[str, str] = Field(default_factory=dict, description="Key to artifact path mapping")
    doc_hashes: List[str] = Field(default_factory=list, description="Hashes of referenced documents (if any)")
    signature: Optional[str] = Field(default=None, description="Signature placeholder for signed results")


