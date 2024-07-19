from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from onecontext.pipeline import Chunk

METRICS_LIST: list[str] = [
    "true_positives",
    "false_positives",
    "precision",
    "recall",
    "exact_match",
]


@dataclass
class EvaluationRequest:
    override_args_map: Dict
    dataset: List[Dict]
    pipeline_yaml: Optional[str] = None
    pipeline_dict: Optional[Dict[str, Any]] = None
    labels_column: str = "label"
    target_metadata_key: str = "label"
    metrics: List[str] = field(default=METRICS_LIST)
    eval_run_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    eval_run_id: str
    eval_set: Dict
    base_pipeline: Dict
    date_created: datetime
    pipelines: List[Dict] = field(default_factory=list)
    pipeline_outputs: List[List[Chunk]] = field(default_factory=list)
    eval_run_metadata: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, List[Union[int, float]]] = field(default_factory=dict)
