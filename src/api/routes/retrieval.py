"""Retrieval API routes for Phase 4 orchestration.

This module provides the retrieval endpoint that uses the
Retrieval Orchestrator to execute configurable pipelines.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.config import get_settings
from src.orchestrator import RetrievalOrchestrator, RetrievalRequest
from src.ranking.ranker import Ranker
from src.storage.registry import SignifierRegistry

logger = logging.getLogger(__name__)

router = APIRouter(tags=["retrieval"], prefix="/retrieve")

settings = get_settings()
registry = SignifierRegistry(
    storage_dir=settings.storage_dir,
    enable_authoring_validation=False,
)
orchestrator = RetrievalOrchestrator(registry=registry, ranker=Ranker())


class MatchRequest(BaseModel):
    """Request for signifier matching via orchestrator.

    Args:
        intent_query: Natural language intent query
        context_input: Context data as nested dict
        pipeline: Pipeline modules to execute
        matcher_version: Intent matcher version
        k: Number of top candidates
        ranking_weights: Custom ranking weights
    """

    intent_query: str = Field(
        ..., min_length=1, description="Natural language intent query"
    )
    context_input: Dict[str, Dict[str, Any]] = Field(
        default={},
        description="Context as nested dict: {artifact_uri: {property_uri: value}}",
    )
    pipeline: List[str] = Field(
        default=["IM", "SSE", "SV", "RP"],
        description="Pipeline modules to execute (IM, SSE, SV, RP)",
    )
    matcher_version: Optional[str] = Field(
        None, description="Intent matcher version (v0, v1)"
    )
    k: int = Field(default=10, ge=1, le=100, description="Top K candidates")
    ranking_weights: Optional[Dict[str, float]] = Field(
        None, description="Custom ranking weights"
    )
    enable_sse: bool = Field(
        default=True, description="Enable Structured Subsumption Engine"
    )


class SignalInfo(BaseModel):
    """Signal information.

    Args:
        name: Signal name
        value: Signal value
        weight: Signal weight
        is_gate: Whether this is a hard gate
    """

    name: str
    value: Any
    weight: float
    is_gate: bool


class MatchResultItem(BaseModel):
    """Single match result.

    Args:
        signifier_id: Signifier identifier
        final_score: Final combined score
        passed_gates: Whether all hard gates passed
        signals: List of signals
        explanation: Human-readable explanation
        metadata: Additional metadata
    """

    signifier_id: str
    final_score: float
    passed_gates: bool
    signals: List[SignalInfo]
    explanation: List[str]
    metadata: Dict[str, Any]


class ModuleResultItem(BaseModel):
    """Per-module execution result.

    Args:
        module: Module name
        latency_ms: Execution time in milliseconds
        candidate_count: Number of candidates after this module
        metadata: Module-specific metadata
    """

    module: str
    latency_ms: float
    candidate_count: int
    metadata: Dict[str, Any]


class MatchResponse(BaseModel):
    """Response for match request.

    Args:
        results: List of ranked results
        module_results: Per-module execution results
        total_latency_ms: Total pipeline latency
        summary: Summary information
    """

    results: List[MatchResultItem]
    module_results: List[ModuleResultItem]
    total_latency_ms: float
    summary: Dict[str, Any]


@router.post("/match", response_model=MatchResponse)
async def retrieve_match(request: MatchRequest) -> MatchResponse:
    """Match signifiers using the retrieval orchestrator.

    This endpoint executes a configurable retrieval pipeline with
    multiple stages (Intent Matching, SHACL Validation, Ranking)
    and returns ranked results with explanations and metrics.

    Args:
        request: Match request with intent, context, and configuration

    Returns:
        Ranked results with signals, explanations, and metrics
    """
    try:
        retrieval_request = RetrievalRequest(
            intent_query=request.intent_query,
            context_input=request.context_input,
            pipeline=request.pipeline,
            matcher_version=request.matcher_version,
            k=request.k,
            ranking_weights=request.ranking_weights,
            enable_sse=request.enable_sse,
        )

        logger.info(
            f"Processing retrieval request: intent='{request.intent_query}', "
            f"pipeline={request.pipeline}"
        )

        response = orchestrator.retrieve(retrieval_request)

        results = [
            MatchResultItem(
                signifier_id=r.signifier_id,
                final_score=r.final_score,
                passed_gates=r.passed_gates,
                signals=[
                    SignalInfo(
                        name=s.name,
                        value=s.value,
                        weight=s.weight,
                        is_gate=s.is_gate,
                    )
                    for s in r.signals
                ],
                explanation=r.explanation,
                metadata=r.metadata,
            )
            for r in response.results
        ]

        module_results = [
            ModuleResultItem(
                module=m.module_name,
                latency_ms=m.latency_ms,
                candidate_count=m.candidate_count,
                metadata=m.metadata,
            )
            for m in response.module_results
        ]

        passed_gates_count = sum(1 for r in response.results if r.passed_gates)

        summary = {
            "total_results": len(response.results),
            "passed_gates": passed_gates_count,
            "failed_gates": len(response.results) - passed_gates_count,
            "pipeline": request.pipeline,
            "intent_query": request.intent_query,
        }

        logger.info(
            f"Retrieval complete: {len(results)} results, "
            f"{passed_gates_count} passed gates, "
            f"{response.total_latency_ms:.2f}ms total"
        )

        return MatchResponse(
            results=results,
            module_results=module_results,
            total_latency_ms=response.total_latency_ms,
            summary=summary,
        )

    except Exception as e:
        logger.error(f"Error during retrieval: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retrieval failed: {str(e)}",
        )
