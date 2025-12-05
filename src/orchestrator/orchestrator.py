"""Retrieval Orchestrator for executing retrieval pipelines.

This module implements the orchestration layer that executes configurable
retrieval pipelines with multiple stages (IM -> SV -> RP) and tracks
per-module performance metrics.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.matching.registry import IntentMatcherRegistry
from src.ranking.ranker import Ranker, RankedResult
from src.storage.registry import SignifierRegistry
from src.subsumption.sse import SSE
from src.validation.context_builder import ContextGraphBuilder
from src.validation.shacl_validator import SHACLValidator

logger = logging.getLogger(__name__)


@dataclass
class RetrievalRequest:
    """Request for signifier retrieval.

    Args:
        intent_query: Natural language intent query
        context_input: Context data as nested dict
        pipeline: Pipeline modules to execute (default: ['IM', 'SV', 'RP'])
        matcher_version: Intent matcher version to use
        k: Number of top candidates to retrieve
        ranking_weights: Custom ranking weights
    """

    intent_query: str
    context_input: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    pipeline: List[str] = field(default_factory=lambda: ["IM", "SSE", "SV", "RP"])
    matcher_version: Optional[str] = None
    k: int = 10
    ranking_weights: Optional[Dict[str, float]] = None
    enable_sse: bool = True


@dataclass
class ModuleResult:
    """Result from a single pipeline module.

    Args:
        module_name: Module identifier (IM, SV, RP)
        latency_ms: Execution time in milliseconds
        candidate_count: Number of candidates after this module
        metadata: Additional module-specific data
    """

    module_name: str
    latency_ms: float
    candidate_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary representation
        """
        return {
            "module": self.module_name,
            "latency_ms": round(self.latency_ms, 2),
            "candidate_count": self.candidate_count,
            "metadata": self.metadata,
        }


@dataclass
class RetrievalResponse:
    """Response from retrieval orchestrator.

    Args:
        results: List of ranked results
        module_results: Per-module execution results
        total_latency_ms: Total pipeline latency
        request: Original request
    """

    results: List[RankedResult]
    module_results: List[ModuleResult]
    total_latency_ms: float
    request: RetrievalRequest

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary representation
        """
        return {
            "results": [r.to_dict() for r in self.results],
            "module_results": [m.to_dict() for m in self.module_results],
            "total_latency_ms": round(self.total_latency_ms, 2),
            "request": {
                "intent_query": self.request.intent_query,
                "context_input": self.request.context_input,
                "pipeline": self.request.pipeline,
                "k": self.request.k,
            },
        }


class RetrievalOrchestrator:
    """Orchestrator for executing retrieval pipelines.

    This orchestrator coordinates the execution of multiple modules
    in sequence: Intent Matching (IM), Structured Subsumption Engine (SSE),
    SHACL Validation (SV), and Ranking & Policy (RP).
    """

    def __init__(
        self,
        registry: SignifierRegistry,
        matcher_registry: Optional[IntentMatcherRegistry] = None,
        context_builder: Optional[ContextGraphBuilder] = None,
        sse: Optional[SSE] = None,
        shacl_validator: Optional[SHACLValidator] = None,
        ranker: Optional[Ranker] = None,
        default_pipeline: Optional[List[str]] = None,
    ):
        """Initialize the retrieval orchestrator.

        Args:
            registry: Signifier registry
            matcher_registry: Intent matcher registry
            context_builder: Context graph builder
            sse: Structured subsumption engine
            shacl_validator: SHACL validator
            ranker: Ranker & policy module
            default_pipeline: Default pipeline modules
        """
        self.registry = registry
        self.matcher_registry = matcher_registry or IntentMatcherRegistry(
            default_version="v1"
        )
        self.context_builder = context_builder or ContextGraphBuilder()
        self.sse = sse or SSE(missing_value_policy="fail")
        self.shacl_validator = shacl_validator or SHACLValidator(
            enable_caching=False
        )
        self.ranker = ranker or Ranker()
        self.default_pipeline = default_pipeline or ["IM", "SSE", "SV", "RP"]

        logger.info(
            f"Initialized Retrieval Orchestrator "
            f"(default_pipeline={self.default_pipeline})"
        )

    def retrieve(self, request: RetrievalRequest) -> RetrievalResponse:
        """Execute retrieval pipeline for a request.

        Args:
            request: Retrieval request with intent and context

        Returns:
            Retrieval response with ranked results and metrics
        """
        start_time = time.time()
        pipeline = request.pipeline or self.default_pipeline
        module_results = []

        logger.info(
            f"Starting retrieval pipeline: {pipeline} "
            f"for intent: '{request.intent_query}'"
        )

        candidates = []

        if "IM" in pipeline:
            im_result = self._execute_intent_matching(request)
            module_results.append(im_result)
            candidates = im_result.metadata.get("candidates", [])

        if "SSE" in pipeline and candidates and request.enable_sse:
            sse_result = self._execute_sse(request, candidates)
            module_results.append(sse_result)
            candidates = sse_result.metadata.get("candidates", [])

        if "SV" in pipeline and candidates:
            sv_result = self._execute_shacl_validation(request, candidates)
            module_results.append(sv_result)
            candidates = sv_result.metadata.get("candidates", [])

        if "RP" in pipeline and candidates:
            rp_result = self._execute_ranking(request, candidates)
            module_results.append(rp_result)
            ranked_results = rp_result.metadata.get("ranked_results", [])
        else:
            ranked_results = []

        total_latency_ms = (time.time() - start_time) * 1000

        logger.info(
            f"Pipeline complete: {len(ranked_results)} results, "
            f"{total_latency_ms:.2f}ms total"
        )

        return RetrievalResponse(
            results=ranked_results,
            module_results=module_results,
            total_latency_ms=total_latency_ms,
            request=request,
        )

    def _execute_intent_matching(
        self, request: RetrievalRequest
    ) -> ModuleResult:
        """Execute Intent Matching (IM) module.

        Args:
            request: Retrieval request

        Returns:
            Module result with candidates
        """
        start_time = time.time()

        all_signifiers = self.registry.list_signifiers(limit=10000)
        signifier_dicts = [s.model_dump() for s in all_signifiers]

        match_results = self.matcher_registry.match(
            intent_query=request.intent_query,
            signifiers=signifier_dicts,
            k=request.k,
            version=request.matcher_version,
        )

        candidates = []
        for match in match_results:
            signifier = self.registry.get(match.signifier_id)
            if signifier:
                candidates.append(
                    {
                        "signifier_id": match.signifier_id,
                        "intent_similarity": match.similarity,
                        "signifier": signifier,
                    }
                )

        latency_ms = (time.time() - start_time) * 1000

        logger.info(
            f"IM: {len(candidates)} candidates in {latency_ms:.2f}ms"
        )

        return ModuleResult(
            module_name="IM",
            latency_ms=latency_ms,
            candidate_count=len(candidates),
            metadata={
                "candidates": candidates,
                "matcher_version": request.matcher_version
                or self.matcher_registry.get_default_version(),
            },
        )

    def _execute_sse(
        self, request: RetrievalRequest, candidates: List[Dict[str, Any]]
    ) -> ModuleResult:
        """Execute Structured Subsumption Engine (SSE) module.

        Args:
            request: Retrieval request
            candidates: Candidates from IM module

        Returns:
            Module result with SSE-filtered candidates
        """
        start_time = time.time()

        context_features = request.context_input
        sse_candidates = []

        for candidate in candidates:
            signifier = candidate["signifier"]
            structured_conditions = signifier.context.structured_conditions

            if not structured_conditions:
                sse_candidates.append(
                    {
                        **candidate,
                        "sse_pass": True,
                        "sse_violations": [],
                    }
                )
                continue

            sse_result = self.sse.evaluate(
                structured_conditions, context_features
            )

            sse_candidates.append(
                {
                    **candidate,
                    "sse_pass": sse_result.sse_pass,
                    "sse_violations": [v.message for v in sse_result.violations],
                    "sse_checked": sse_result.conditions_checked,
                }
            )

        latency_ms = (time.time() - start_time) * 1000

        passed_count = sum(1 for c in sse_candidates if c["sse_pass"])

        logger.info(
            f"SSE: {passed_count}/{len(sse_candidates)} passed in "
            f"{latency_ms:.2f}ms"
        )

        return ModuleResult(
            module_name="SSE",
            latency_ms=latency_ms,
            candidate_count=len(sse_candidates),
            metadata={
                "candidates": sse_candidates,
                "passed_count": passed_count,
            },
        )

    def _execute_shacl_validation(
        self, request: RetrievalRequest, candidates: List[Dict[str, Any]]
    ) -> ModuleResult:
        """Execute SHACL Validation (SV) module.

        Args:
            request: Retrieval request
            candidates: Candidates from IM module

        Returns:
            Module result with validated candidates
        """
        start_time = time.time()

        context_graph, _ = self.context_builder.normalize_context(
            request.context_input
        )

        validated_candidates = []
        for candidate in candidates:
            signifier = candidate["signifier"]
            shacl_conforms = True
            shacl_violations = []
            shacl_has_shapes = False
            constraint_count = 0

            if signifier.context.shacl_shapes:
                shacl_has_shapes = True
                validation = self.shacl_validator.validate_signifier_context(
                    context_graph,
                    signifier.context.shacl_shapes,
                    format="turtle",
                )
                shacl_conforms = validation.conforms
                shacl_violations = [v.message for v in validation.violations]

                if signifier.context.shacl_shapes:
                    constraint_count = signifier.context.shacl_shapes.count(
                        "sh:property"
                    ) + signifier.context.shacl_shapes.count("sh:class")

            validated_candidates.append(
                {
                    **candidate,
                    "shacl_conforms": shacl_conforms,
                    "shacl_violations": shacl_violations,
                    "shacl_has_shapes": shacl_has_shapes,
                    "constraint_count": constraint_count,
                }
            )

        latency_ms = (time.time() - start_time) * 1000

        passed_count = sum(
            1 for c in validated_candidates if c["shacl_conforms"]
        )

        logger.info(
            f"SV: {passed_count}/{len(validated_candidates)} passed in "
            f"{latency_ms:.2f}ms"
        )

        return ModuleResult(
            module_name="SV",
            latency_ms=latency_ms,
            candidate_count=len(validated_candidates),
            metadata={
                "candidates": validated_candidates,
                "passed_count": passed_count,
            },
        )

    def _execute_ranking(
        self, request: RetrievalRequest, candidates: List[Dict[str, Any]]
    ) -> ModuleResult:
        """Execute Ranking & Policy (RP) module.

        Args:
            request: Retrieval request
            candidates: Candidates from SV module

        Returns:
            Module result with ranked results
        """
        start_time = time.time()

        if request.ranking_weights:
            ranker = Ranker(weights=request.ranking_weights)
        else:
            ranker = self.ranker

        ranked_results = ranker.rank(candidates)

        latency_ms = (time.time() - start_time) * 1000

        logger.info(
            f"RP: Ranked {len(ranked_results)} candidates in {latency_ms:.2f}ms"
        )

        return ModuleResult(
            module_name="RP",
            latency_ms=latency_ms,
            candidate_count=len(ranked_results),
            metadata={
                "ranked_results": ranked_results,
            },
        )
