"""Signifier data models for RD4 system.

This module defines the core data structures for storing and managing
signifiers with dual representation (NL + structured).
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger(__name__)


class SignifierStatus(str, Enum):
    """Status of a signifier."""

    ACTIVE = "active"
    DEPRECATED = "deprecated"


class Provenance(BaseModel):
    """Provenance information for a signifier.

    Args:
        created_at: Timestamp when signifier was created
        created_by: Identifier of creator
        source: Source of the signifier (e.g., "manual", "imported")
    """

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = Field(..., min_length=1)
    source: str = Field(default="manual")


class ValueCondition(BaseModel):
    """Value condition for structured context.

    Args:
        operator: Comparison operator (greaterThan, lessThan, greaterEqual, etc.)
        value: The value to compare against
        datatype: Optional XSD datatype (e.g., "xsd:integer")
    """

    operator: str = Field(..., min_length=1)
    value: Any
    datatype: Optional[str] = None

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v: str) -> str:
        """Validate operator is one of the allowed types.

        Args:
            v: The operator value

        Returns:
            The validated operator

        Raises:
            ValueError: If operator is not valid
        """
        allowed_operators = {
            "greaterThan",
            "lessThan",
            "greaterEqual",
            "lessEqual",
            "equals",
            "notEquals",
        }
        if v not in allowed_operators:
            raise ValueError(
                f"Operator must be one of {allowed_operators}, got: {v}"
            )
        return v


class StructuredCondition(BaseModel):
    """Structured condition for context matching.

    Args:
        artifact: URI of the artifact
        property_affordance: URI of the property
        value_conditions: List of value conditions to check
    """

    artifact: str = Field(..., min_length=1)
    property_affordance: str = Field(..., min_length=1)
    value_conditions: List[ValueCondition] = Field(default_factory=list)


class IntentionDescription(BaseModel):
    """Natural language and structured intent description.

    Args:
        nl_text: Natural language description of intent
        structured: Optional structured JSON representation
    """

    nl_text: str = Field(..., min_length=1)
    structured: Optional[Dict[str, Any]] = None

    @field_validator("structured", mode="before")
    @classmethod
    def parse_structured(cls, v: Any) -> Optional[Dict[str, Any]]:
        """Parse structured field if it's a string.

        Args:
            v: The structured value (could be dict or JSON string)

        Returns:
            Parsed dictionary or None
        """
        if v is None:
            return None
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            import json

            try:
                return json.loads(v)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse structured intent: {e}")
                return None
        return None


class IntentContext(BaseModel):
    """Context requirements for signifier applicability.

    Args:
        structured_conditions: List of structured conditions
        shacl_shapes: RDF/Turtle representation of SHACL shapes
        nl_description: Optional natural language description
    """

    structured_conditions: List[StructuredCondition] = Field(default_factory=list)
    shacl_shapes: Optional[str] = None
    nl_description: Optional[str] = None


class Signifier(BaseModel):
    """Canonical signifier with dual representation.

    Args:
        signifier_id: Unique identifier for the signifier
        version: Version number (incremented on breaking changes)
        status: Current status (active or deprecated)
        intent: Intent description (NL + structured)
        context: Context requirements (structured + SHACL)
        affordance_uri: URI of the signified affordance
        provenance: Creation and source information
        indexes: System-generated indexes for fast lookup
    """

    signifier_id: str = Field(..., min_length=1)
    version: int = Field(default=1, ge=1)
    status: SignifierStatus = Field(default=SignifierStatus.ACTIVE)

    intent: IntentionDescription
    context: IntentContext
    affordance_uri: str = Field(..., min_length=1)

    provenance: Provenance

    indexes: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "signifier_id": "raise-blinds-signifier",
                "version": 1,
                "status": "active",
                "intent": {
                    "nl_text": "increase luminosity in a room",
                    "structured": {"verb": "increase", "object": "luminosity"},
                },
                "context": {
                    "structured_conditions": [
                        {
                            "artifact": "http://example.org/artifacts/light_sensor",
                            "property_affordance": "http://example.org/LightSensor#hasLuminosityLevel",
                            "value_conditions": [
                                {"operator": "greaterThan", "value": 10000}
                            ],
                        }
                    ],
                    "shacl_shapes": "# SHACL shapes in Turtle format",
                },
                "affordance_uri": "http://example.org/affordances/adjust-blinds",
                "provenance": {
                    "created_at": "2025-11-11T12:00:00Z",
                    "created_by": "admin",
                    "source": "manual",
                },
            }
        }
    )

    def get_property_keys(self) -> List[tuple[str, str]]:
        """Extract (artifact, property) pairs from structured conditions.

        Returns:
            List of (artifact_uri, property_uri) tuples
        """
        keys = []
        for condition in self.context.structured_conditions:
            keys.append((condition.artifact, condition.property_affordance))
        return keys

    def to_json_doc(self) -> Dict[str, Any]:
        """Convert to JSON document for document store.

        Returns:
            Dictionary representation suitable for JSON storage
        """
        return {
            "signifier_id": self.signifier_id,
            "version": self.version,
            "status": self.status.value,
            "intent": {
                "nl_text": self.intent.nl_text,
                "structured": self.intent.structured,
            },
            "context": {
                "structured_conditions": [
                    {
                        "artifact": cond.artifact,
                        "property_affordance": cond.property_affordance,
                        "value_conditions": [
                            {
                                "operator": vc.operator,
                                "value": vc.value,
                                "datatype": vc.datatype,
                            }
                            for vc in cond.value_conditions
                        ],
                    }
                    for cond in self.context.structured_conditions
                ],
                "shacl_shapes": self.context.shacl_shapes,
                "nl_description": self.context.nl_description,
            },
            "affordance_uri": self.affordance_uri,
            "provenance": {
                "created_at": self.provenance.created_at.isoformat(),
                "created_by": self.provenance.created_by,
                "source": self.provenance.source,
            },
            "indexes": self.indexes,
        }
