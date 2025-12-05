# Phase 4 - Retrieval Orchestrator

## Overview

Phase 4 implements a complete retrieval pipeline orchestrator that coordinates multiple modules to match signifiers against user queries with explainability and performance tracking.

## Architecture

The retrieval pipeline consists of three main modules:

1. **Intent Matcher (IM)**: Matches user intent using semantic similarity
2. **SHACL Validator (SV)**: Validates context against signifier constraints
3. **Ranker & Policy (RP)**: Combines signals and enforces hard gates

## Components

### Ranker & Policy Module

Location: [src/ranking/ranker.py](../src/ranking/ranker.py)

The Ranker combines multiple signals into a final score with explainability:

- Weighted scoring: `intent_similarity=0.7, shacl=0.2, sse=0.1`
- Hard gate enforcement for SHACL validation
- Specificity boost for tie-breaking
- Per-signal contribution explanations

### Retrieval Orchestrator

Location: [src/orchestrator/orchestrator.py](../src/orchestrator/orchestrator.py)

The Orchestrator executes the pipeline and tracks performance:

- Configurable pipeline: `[IM, SV, RP]` by default
- Per-module latency tracking
- Signal aggregation across modules
- Pipeline configuration overrides

### Retrieval API Endpoint

Location: [src/api/routes/retrieval.py](../src/api/routes/retrieval.py)

New endpoint: `POST /retrieve/match`

Request format:
```json
{
  "intent_query": "make the room more comfortable",
  "context_input": {
    "http://example.org/artifacts/temperature_sensor": {
      "http://example.org/TemperatureSensor#hasTemperatureLevel": 18
    }
  },
  "pipeline": ["IM", "SV", "RP"],
  "k": 10
}
```

Response format:
```json
{
  "results": [
    {
      "signifier_id": "heat-room-occupied-signifier",
      "final_score": 0.8065,
      "passed_gates": true,
      "signals": [
        {
          "name": "intent_similarity",
          "value": 0.7865,
          "weight": 0.7,
          "is_gate": false
        },
        {
          "name": "shacl_conforms",
          "value": true,
          "weight": 0.2,
          "is_gate": true
        }
      ],
      "explanation": [
        "Intent similarity: 0.7865 (weight: 0.7)",
        "SHACL validation: PASS (weight: 0.2)"
      ]
    }
  ],
  "module_results": [
    {
      "module": "IM",
      "latency_ms": 21.35,
      "candidate_count": 10
    },
    {
      "module": "SV",
      "latency_ms": 45.82,
      "candidate_count": 10
    },
    {
      "module": "RP",
      "latency_ms": 0.50,
      "candidate_count": 10
    }
  ],
  "total_latency_ms": 67.67,
  "summary": {
    "total_results": 10,
    "passed_gates": 3,
    "failed_gates": 7
  }
}
```

## Testing

### Enhanced Test Runner

Location: [scripts/run_scenario_orchestrator.py](../scripts/run_scenario_orchestrator.py)

Usage:
```bash
# Run with existing server
python scripts/run_scenario_orchestrator.py test_scenario/4

# Run with auto server start
python scripts/run_scenario_orchestrator.py test_scenario/4 --start-server

# Run with custom API URL
python scripts/run_scenario_orchestrator.py test_scenario/4 --api-url http://localhost:8000
```

The test runner:
- Loads signifiers from TTL files
- Executes queries from queries.json
- Uses the new `/retrieve/match` endpoint
- Displays pipeline execution metrics
- Shows ranked results with signal details
- Saves detailed JSON results

### Test Results

All scenarios tested successfully:

- **Scenario 1**: 2 signifiers, 2 queries - PASSED
- **Scenario 2**: 4 signifiers, 6 queries - PASSED
- **Scenario 3**: 8 signifiers, 8 queries - PASSED
- **Scenario 4**: 23 signifiers, 15 queries - PASSED

Performance metrics:
- Pipeline latency: 40-130ms (after model load)
- First query: 5-22s (includes embedding model loading)
- Intent Matching (IM): 5-20ms
- SHACL Validation (SV): 15-50ms
- Ranking & Policy (RP): 0-1ms

## Key Features

### 1. Weighted Scoring

The ranker combines signals using configurable weights:
- Intent similarity: 70%
- SHACL validation: 20%
- SSE (future): 10%

### 2. Hard Gate Enforcement

When SHACL shapes are present and hard gates are enabled:
- Signifiers that fail SHACL validation receive a score of 0
- They appear in results but are marked as `passed_gates=false`

### 3. Explainability

Each result includes:
- Per-signal values and weights
- Human-readable explanation bullets
- Gate status indicators
- Constraint counts and metadata

### 4. Performance Tracking

Per-module metrics include:
- Execution latency in milliseconds
- Candidate count after each stage
- Module-specific metadata
- Total pipeline latency

## Configuration

### Pipeline Configuration

Configure the pipeline in the request:
```json
{
  "pipeline": ["IM", "SV", "RP"]
}
```

### Ranking Weights

Customize ranking weights:
```json
{
  "ranking_weights": {
    "intent_similarity": 0.6,
    "shacl": 0.3,
    "sse": 0.1
  }
}
```

### Matcher Version

Select intent matcher version:
```json
{
  "matcher_version": "v1"
}
```

## API Endpoints

### Legacy Endpoint

`GET /signifiers/match` - Simple matching (Phase 3)

### New Orchestrator Endpoint

`POST /retrieve/match` - Full pipeline with explainability (Phase 4)

## Future Enhancements

Phase 5 will add the Structured Subsumption Engine (SSE):
- Fast numeric pre-filtering
- Positioned before SHACL validation
- Reduces candidates for expensive validation

## Files Modified

New files:
- `src/ranking/__init__.py`
- `src/ranking/ranker.py`
- `src/orchestrator/__init__.py`
- `src/orchestrator/orchestrator.py`
- `src/api/routes/retrieval.py`
- `scripts/run_scenario_orchestrator.py`

Updated files:
- `src/api/main.py` - Added retrieval router
- `requirements.txt` - Added requests library

## Dependencies

New dependency: `requests>=2.31.0` (for test scripts)

All other dependencies from Phase 3 are reused.
