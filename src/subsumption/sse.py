"""Structured Subsumption Engine for fast numeric pre-filtering.

This module implements the SSE which evaluates structured conditions
(numeric comparisons) before expensive SHACL validation.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.models.signifier import StructuredCondition, ValueCondition

logger = logging.getLogger(__name__)


@dataclass
class SSEViolation:
    """SSE violation details.

    Args:
        artifact: Artifact URI that failed
        property_affordance: Property URI that failed
        operator: Operator that was used
        expected_value: Expected value
        actual_value: Actual value from context
        message: Human-readable violation message
    """

    artifact: str
    property_affordance: str
    operator: str
    expected_value: Any
    actual_value: Optional[Any]
    message: str


@dataclass
class SSEResult:
    """Result of SSE evaluation.

    Args:
        sse_pass: Whether all conditions passed
        violations: List of violations if any failed
        conditions_checked: Number of conditions checked
        missing_properties: List of missing (artifact, property) pairs
    """

    sse_pass: bool
    violations: List[SSEViolation] = field(default_factory=list)
    conditions_checked: int = 0
    missing_properties: List[tuple[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary representation
        """
        return {
            "sse_pass": self.sse_pass,
            "violations": [
                {
                    "artifact": v.artifact,
                    "property_affordance": v.property_affordance,
                    "operator": v.operator,
                    "expected_value": v.expected_value,
                    "actual_value": v.actual_value,
                    "message": v.message,
                }
                for v in self.violations
            ],
            "conditions_checked": self.conditions_checked,
            "missing_properties": [
                {"artifact": a, "property": p} for a, p in self.missing_properties
            ],
        }


class SSE:
    """Structured Subsumption Engine for fast numeric pre-filtering.

    This engine evaluates structured conditions using numeric operators
    before running expensive SHACL validation. It provides fast rejection
    of candidates that don't meet basic numeric constraints.
    """

    def __init__(
        self,
        missing_value_policy: str = "fail",
        enable_type_coercion: bool = True,
    ):
        """Initialize the SSE.

        Args:
            missing_value_policy: How to handle missing values
                - 'fail': Treat missing as violation
                - 'ignore': Skip conditions with missing values
                - 'pass': Treat missing as passing
            enable_type_coercion: Whether to coerce types for comparison
        """
        self.missing_value_policy = missing_value_policy
        self.enable_type_coercion = enable_type_coercion

        logger.info(
            f"Initialized SSE (missing_policy={missing_value_policy}, "
            f"coercion={enable_type_coercion})"
        )

    def evaluate(
        self,
        structured_conditions: List[StructuredCondition],
        context_features: Dict[str, Dict[str, Any]],
    ) -> SSEResult:
        """Evaluate structured conditions against context features.

        Args:
            structured_conditions: List of conditions from signifier
            context_features: Context as {artifact_uri: {property_uri: value}}

        Returns:
            SSEResult with pass/fail and violations
        """
        if not structured_conditions:
            return SSEResult(sse_pass=True, conditions_checked=0)

        violations = []
        missing_properties = []
        conditions_checked = 0

        for condition in structured_conditions:
            artifact = condition.artifact
            property_affordance = condition.property_affordance

            artifact_data = context_features.get(artifact, {})
            if property_affordance not in artifact_data:
                missing_properties.append((artifact, property_affordance))

                if self.missing_value_policy == "fail":
                    violations.append(
                        SSEViolation(
                            artifact=artifact,
                            property_affordance=property_affordance,
                            operator="missing",
                            expected_value="<present>",
                            actual_value=None,
                            message=f"Missing property {property_affordance} "
                            f"on artifact {artifact}",
                        )
                    )
                elif self.missing_value_policy == "ignore":
                    continue
                continue

            actual_value = artifact_data[property_affordance]

            for value_condition in condition.value_conditions:
                conditions_checked += 1

                passed = self._evaluate_condition(
                    value_condition, actual_value
                )

                if not passed:
                    violations.append(
                        SSEViolation(
                            artifact=artifact,
                            property_affordance=property_affordance,
                            operator=value_condition.operator,
                            expected_value=value_condition.value,
                            actual_value=actual_value,
                            message=self._format_violation_message(
                                value_condition, actual_value
                            ),
                        )
                    )

        sse_pass = len(violations) == 0

        logger.debug(
            f"SSE evaluation: {conditions_checked} conditions checked, "
            f"pass={sse_pass}, violations={len(violations)}"
        )

        return SSEResult(
            sse_pass=sse_pass,
            violations=violations,
            conditions_checked=conditions_checked,
            missing_properties=missing_properties,
        )

    def _evaluate_condition(
        self, condition: ValueCondition, actual_value: Any
    ) -> bool:
        """Evaluate a single value condition.

        Args:
            condition: The value condition to check
            actual_value: The actual value from context

        Returns:
            True if condition passes, False otherwise
        """
        expected_value = condition.value
        operator = condition.operator

        if self.enable_type_coercion:
            try:
                if isinstance(expected_value, (int, float)) and not isinstance(
                    actual_value, (int, float)
                ):
                    actual_value = float(actual_value)
                elif isinstance(expected_value, str) and not isinstance(
                    actual_value, str
                ):
                    actual_value = str(actual_value)
            except (ValueError, TypeError):
                logger.warning(
                    f"Type coercion failed for {actual_value} "
                    f"to {type(expected_value)}"
                )

        try:
            if operator == "greaterThan":
                return actual_value > expected_value
            elif operator == "lessThan":
                return actual_value < expected_value
            elif operator == "greaterEqual":
                return actual_value >= expected_value
            elif operator == "lessEqual":
                return actual_value <= expected_value
            elif operator == "equals":
                return actual_value == expected_value
            elif operator == "notEquals":
                return actual_value != expected_value
            else:
                logger.warning(f"Unknown operator: {operator}")
                return False
        except TypeError as e:
            logger.warning(
                f"Comparison failed: {actual_value} {operator} "
                f"{expected_value}: {e}"
            )
            return False

    def _format_violation_message(
        self, condition: ValueCondition, actual_value: Any
    ) -> str:
        """Format a human-readable violation message.

        Args:
            condition: The failed condition
            actual_value: The actual value

        Returns:
            Formatted message
        """
        operator_text = {
            "greaterThan": "greater than",
            "lessThan": "less than",
            "greaterEqual": "greater than or equal to",
            "lessEqual": "less than or equal to",
            "equals": "equal to",
            "notEquals": "not equal to",
        }.get(condition.operator, condition.operator)

        return (
            f"Expected value to be {operator_text} {condition.value}, "
            f"but got {actual_value}"
        )
