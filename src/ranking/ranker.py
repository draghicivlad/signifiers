"""Ranker & Policy module for combining multiple signals.

This module implements the ranking and policy enforcement logic
for combining intent similarity, SHACL validation, and other signals
into final scores with explainability.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class RankingSignal:
    """Individual ranking signal.

    Args:
        name: Signal name (e.g., 'intent_similarity', 'shacl_conforms')
        value: Signal value (0.0 to 1.0 for scores, True/False for boolean gates)
        weight: Weight for this signal in final score
        is_gate: Whether this is a hard gate (must pass)
    """

    name: str
    value: Any
    weight: float = 0.0
    is_gate: bool = False


@dataclass
class RankedResult:
    """Ranked signifier result with score and explanation.

    Args:
        signifier_id: Signifier identifier
        final_score: Final combined score (0.0 to 1.0)
        signals: List of signals that contributed to the score
        passed_gates: Whether all hard gates passed
        explanation: Human-readable explanation of the score
        metadata: Additional metadata
    """

    signifier_id: str
    final_score: float
    signals: List[RankingSignal]
    passed_gates: bool
    explanation: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary representation
        """
        return {
            "signifier_id": self.signifier_id,
            "final_score": round(self.final_score, 4),
            "passed_gates": self.passed_gates,
            "signals": [
                {
                    "name": s.name,
                    "value": s.value,
                    "weight": s.weight,
                    "is_gate": s.is_gate,
                }
                for s in self.signals
            ],
            "explanation": self.explanation,
            "metadata": self.metadata,
        }


class Ranker:
    """Ranker & Policy implementation for combining signals.

    This ranker combines multiple signals (intent similarity, SHACL validation,
    SSE, etc.) into a final score using configurable weights. It enforces
    hard gates (e.g., SHACL must pass) and provides explainability.
    """

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        enable_shacl_gate: bool = True,
        enable_sse_gate: bool = False,
        specificity_boost: float = 0.01,
    ):
        """Initialize the ranker.

        Args:
            weights: Signal weights (default: similarity=0.7, shacl=0.2, sse=0.1)
            enable_shacl_gate: If True, reject signifiers that fail SHACL
            enable_sse_gate: If True, reject signifiers that fail SSE
            specificity_boost: Score boost per constraint (for tie-breaking)
        """
        self.weights = weights or {
            "intent_similarity": 0.7,
            "shacl": 0.2,
            "sse": 0.1,
        }
        self.enable_shacl_gate = enable_shacl_gate
        self.enable_sse_gate = enable_sse_gate
        self.specificity_boost = specificity_boost

        logger.info(
            f"Initialized Ranker (weights={self.weights}, "
            f"shacl_gate={enable_shacl_gate}, sse_gate={enable_sse_gate})"
        )

    def rank(
        self,
        candidates: List[Dict[str, Any]],
    ) -> List[RankedResult]:
        """Rank candidates by combining multiple signals.

        Args:
            candidates: List of candidate dictionaries with signals

        Returns:
            List of RankedResult objects sorted by final_score (descending)
        """
        ranked_results = []

        for candidate in candidates:
            signifier_id = candidate.get("signifier_id")
            intent_similarity = candidate.get("intent_similarity", 0.0)
            shacl_conforms = candidate.get("shacl_conforms", True)
            shacl_has_shapes = candidate.get("shacl_has_shapes", False)
            sse_pass = candidate.get("sse_pass", True)
            constraint_count = candidate.get("constraint_count", 0)

            signals = []
            explanation = []

            intent_signal = RankingSignal(
                name="intent_similarity",
                value=intent_similarity,
                weight=self.weights.get("intent_similarity", 0.7),
                is_gate=False,
            )
            signals.append(intent_signal)
            explanation.append(
                f"Intent similarity: {intent_similarity:.4f} "
                f"(weight: {intent_signal.weight})"
            )

            passed_gates = True

            if shacl_has_shapes:
                shacl_signal = RankingSignal(
                    name="shacl_conforms",
                    value=shacl_conforms,
                    weight=self.weights.get("shacl", 0.2),
                    is_gate=self.enable_shacl_gate,
                )
                signals.append(shacl_signal)

                if shacl_conforms:
                    explanation.append(
                        f"SHACL validation: PASS (weight: {shacl_signal.weight})"
                    )
                else:
                    explanation.append("SHACL validation: FAIL (hard gate)")
                    if self.enable_shacl_gate:
                        passed_gates = False

            if "sse_pass" in candidate:
                sse_signal = RankingSignal(
                    name="sse_pass",
                    value=sse_pass,
                    weight=self.weights.get("sse", 0.1),
                    is_gate=self.enable_sse_gate,
                )
                signals.append(sse_signal)

                if sse_pass:
                    explanation.append(
                        f"SSE check: PASS (weight: {sse_signal.weight})"
                    )
                else:
                    explanation.append("SSE check: FAIL")
                    if self.enable_sse_gate:
                        passed_gates = False

            final_score = 0.0
            if passed_gates:
                final_score = self._calculate_weighted_score(signals)

                if constraint_count > 0:
                    boost = constraint_count * self.specificity_boost
                    final_score = min(1.0, final_score + boost)
                    explanation.append(
                        f"Specificity boost: +{boost:.4f} "
                        f"({constraint_count} constraints)"
                    )
            else:
                explanation.append("Final score: 0.0 (failed hard gates)")

            ranked_result = RankedResult(
                signifier_id=signifier_id,
                final_score=final_score,
                signals=signals,
                passed_gates=passed_gates,
                explanation=explanation,
                metadata={
                    "constraint_count": constraint_count,
                    "shacl_has_shapes": shacl_has_shapes,
                },
            )
            ranked_results.append(ranked_result)

        ranked_results.sort(key=lambda r: r.final_score, reverse=True)

        logger.info(
            f"Ranked {len(ranked_results)} candidates, "
            f"{sum(1 for r in ranked_results if r.passed_gates)} passed gates"
        )

        return ranked_results

    def _calculate_weighted_score(self, signals: List[RankingSignal]) -> float:
        """Calculate weighted score from signals.

        Args:
            signals: List of ranking signals

        Returns:
            Weighted score (0.0 to 1.0)
        """
        total_weight = 0.0
        weighted_sum = 0.0

        for signal in signals:
            if signal.is_gate:
                continue

            if isinstance(signal.value, bool):
                signal_value = 1.0 if signal.value else 0.0
            else:
                signal_value = float(signal.value)

            weighted_sum += signal_value * signal.weight
            total_weight += signal.weight

        if total_weight == 0:
            return 0.0

        return weighted_sum / total_weight
