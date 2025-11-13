# RD4 Signifier System - Phase 1: Storage (MVP)

Phase 1 implements the foundation for persisting signifiers with dual representation (NL + structured).

## Features

Phase 1 provides:

- **Signifier Registry (SR)** - CRUD operations, versioning, status management, provenance tracking
- **Memory Store (MS)** - Dual storage with RDF named graphs and JSON documents
- **Representation Service (RS)** - Normalize NL and structured fields, convert between RDF and JSON
- **Storage APIs** - RESTful endpoints for managing signifiers
- **Property Index Catalog** - Fast candidate prefiltering by (artifact, property) pairs

## Installation

1. Set up Python virtual environment (Python 3.10+):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Starting the API Server

```bash
python src/api/main.py
```

The server will start at http://localhost:8000

API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Loading Example Signifiers

Load the three example signifiers from the `signifiers/` directory:

```bash
python scripts/load_example_signifiers.py
```

### Running Tests

Run the Phase 1 test suite:

```bash
pytest tests/test_phase1.py -v
```

Run all tests with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

## API Endpoints

### Create Signifier

```bash
POST /signifiers
```

Create a new signifier from JSON data.

### Create Signifier from RDF

```bash
POST /signifiers/from-rdf
Content-Type: application/json

{
  "rdf_data": "<signifier RDF in Turtle format>",
  "format": "turtle"
}
```

### Get Signifier

```bash
GET /signifiers/{signifier_id}
```

Retrieve a signifier by ID.

### Get Signifier RDF

```bash
GET /signifiers/{signifier_id}/rdf?version=1
```

Retrieve RDF representation of a signifier.

### Update Signifier

```bash
PUT /signifiers/{signifier_id}
Content-Type: application/json

{
  "signifier": { ... },
  "create_new_version": false
}
```

### Delete Signifier

```bash
DELETE /signifiers/{signifier_id}
```

### List Signifiers

```bash
GET /signifiers?status=active&limit=100&offset=0
```

Query parameters:
- `status` - Filter by status (active or deprecated)
- `affordance_uri` - Filter by affordance URI
- `limit` - Maximum number of results (default: 100)
- `offset` - Number of results to skip (default: 0)

### Update Status

```bash
PATCH /signifiers/{signifier_id}/status?status=deprecated
```

## Example: Using the API with curl

### Load a signifier from RDF

```bash
curl -X POST http://localhost:8000/signifiers/from-rdf \
  -H "Content-Type: application/json" \
  -d '{
    "rdf_data": "'"$(cat signifiers/raise-blinds-signifier.txt)"'",
    "format": "turtle"
  }'
```

### List all signifiers

```bash
curl http://localhost:8000/signifiers
```

### Get a specific signifier

```bash
curl http://localhost:8000/signifiers/raise-blinds-signifier
```

### Get RDF representation

```bash
curl http://localhost:8000/signifiers/raise-blinds-signifier/rdf
```

## Storage Structure

The storage system uses a file-based approach:

```
storage/
  rdf/
    {signifier_id}_v{version}.ttl  # RDF named graphs
  json/
    {signifier_id}.json            # JSON documents
  indexes/
    property_index.json            # Property catalog
```

## Data Model

### Signifier

A signifier consists of:

- `signifier_id` - Unique identifier
- `version` - Version number
- `status` - Status (active or deprecated)
- `intent` - Intent description (NL + structured)
- `context` - Context requirements (structured conditions + SHACL shapes)
- `affordance_uri` - URI of the signified affordance
- `provenance` - Creation and source information
- `indexes` - System-generated indexes

### Intent Description

- `nl_text` - Natural language description
- `structured` - Structured JSON representation

### Intent Context

- `structured_conditions` - List of structured conditions (artifact, property, value conditions)
- `shacl_shapes` - RDF/Turtle representation of SHACL shapes
- `nl_description` - Optional natural language description

## Example Signifiers

Three example signifiers are provided in the `signifiers/` directory:

1. **raise-blinds-signifier.txt** - Increase luminosity by raising blinds
   - Intent: "increase luminosity in a room"
   - Conditions: External light >= 10000, Temperature <= 25

2. **turn-light-on-signifier.txt** - Increase luminosity by turning on light
   - Intent: "increase luminosity in a room"
   - Conditions: Internal light <= 100, Person count >= 1

3. **lower-blinds-signifier.txt** - Decrease luminosity by lowering blinds
   - Intent: "decrease luminosity in a room"
   - Conditions: External light >= 50000, Temperature > 25

## Property Index

The property index enables fast candidate prefiltering. For example:

```python
from src.storage.registry import SignifierRegistry

registry = SignifierRegistry()

# Find all signifiers that reference the external light sensor
results = registry.find_by_property(
    artifact_uri="http://example.org/precis/workspaces/lab308/artifacts/external_light_sensing308",
    property_uri="http://example.org/LightSensor#hasLuminosityLevel"
)
```

## Phase 1 Acceptance Criteria

- [x] CRUD operations work correctly
- [x] Round-trip fidelity for signifier data
- [x] Listing filters by status and affordance_uri
- [x] Index catalog functional
- [x] Idempotent ingest on repeated payloads (creates ValueError on duplicate)
- [x] RDF and JSON storage with named graphs
- [x] Property index catalog for fast lookups
- [x] Versioning support

## Next Steps

Phase 2 will add SHACL validation capabilities:
- Authoring SHACL for signifier object validation
- Runtime SHACL for context graph validation
- Batch validation endpoints
- Validation result caching

## Configuration

Configuration is managed via environment variables or `.env` file:

```bash
STORAGE_DIR=./storage
RDF_FORMAT=turtle
ENABLE_AUTHORING_VALIDATION=false
LOG_LEVEL=INFO
```

See [src/config/settings.py](src/config/settings.py) for all configuration options.
