"""Structured Subsumption Engine (SSE) module.

This module provides fast numeric pre-filtering before expensive SHACL validation
by evaluating structured conditions against context features.
"""

from src.subsumption.sse import SSE, SSEResult, SSEViolation

__all__ = ["SSE", "SSEResult", "SSEViolation"]
