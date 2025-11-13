# Fixed Signifiers Summary

All three example signifier files have been corrected to use proper Turtle/RDF syntax.

## Fixed Files

1. **[raise-blinds-signifier-fixed.ttl](raise-blinds-signifier-fixed.ttl)**
   - Intent: "increase luminosity in a room"
   - Affordance: adjust-blinds-action-affordance
   - Conditions: External light >= 10000, Temperature <= 25

2. **[turn-light-on-signifier-fixed.ttl](turn-light-on-signifier-fixed.ttl)**
   - Intent: "increase luminosity in a room"
   - Affordance: adjust-light-action-affordance
   - Conditions: Internal light <= 100, Person count >= 1

3. **[lower-blinds-signifier-fixed.ttl](lower-blinds-signifier-fixed.ttl)**
   - Intent: "decrease luminosity in a room"
   - Affordance: adjust-blinds-action-affordance
   - Conditions: External light >= 50000, Temperature > 25

## What Was Fixed

### Original Issues

The original `.txt` files had the following problems:

1. **Missing @prefix declarations** - Required for Turtle format
2. **Invalid comments** - Used `//` instead of `#`
3. **Invalid JSON syntax** - Used single quotes instead of double quotes
4. **Invalid URI notation in JSON** - Used `<http://...>` instead of `"http://..."`
5. **Wrong SHACL property** - Used `sh:dataType` instead of `sh:datatype`

### Corrections Applied

```turtle
# BEFORE (WRONG):
// Comment
cashmere:hasStructuredDescription "
    {
        'intent': 'increase luminosity',
        'artifact': <http://example.org/...>
    }
"^^xsd:string ;

# AFTER (CORRECT):
# Comment
cashmere:hasStructuredDescription """{
    "intent": "increase luminosity",
    "artifact": "http://example.org/..."
}"""^^xsd:string ;
```

## Loading the Fixed Signifiers

### Method 1: Using the Load Script

```bash
python scripts/load_fixed_signifiers.py
```

### Method 2: Manual Loading

```python
from src.storage.registry import SignifierRegistry

registry = SignifierRegistry()

with open('signifiers/raise-blinds-signifier-fixed.ttl', 'r') as f:
    rdf_data = f.read()

signifier = registry.create_from_rdf(rdf_data)
print(f'Loaded: {signifier.signifier_id}')
```

### Method 3: Via REST API

```bash
# Start the server
python src/api/main.py

# Load a signifier
curl -X POST http://localhost:8000/signifiers/from-rdf \
  -H "Content-Type: application/json" \
  -d '{
    "rdf_data": "'"$(cat signifiers/raise-blinds-signifier-fixed.ttl)"'",
    "format": "turtle"
  }'
```

## Verification

All three signifiers have been tested and verified:

- ✅ RDF parsing successful
- ✅ JSON extraction successful
- ✅ Structured conditions parsed correctly
- ✅ SHACL shapes loaded
- ✅ Property index updated
- ✅ Round-trip storage/retrieval working

## File Comparison

| File | Status | Size | Conditions |
|------|--------|------|------------|
| raise-blinds-signifier-fixed.ttl | ✅ Valid | ~2.5 KB | 2 (light, temp) |
| turn-light-on-signifier-fixed.ttl | ✅ Valid | ~2.4 KB | 2 (light, person) |
| lower-blinds-signifier-fixed.ttl | ✅ Valid | ~2.5 KB | 2 (light, temp) |

## Next Steps

The original `.txt` files remain as reference, but **use the `-fixed.ttl` files** for:

1. Testing Phase 1 functionality
2. Developing Phase 2 (SHACL validation)
3. Building retrieval queries
4. Creating new signifiers (use as templates)

## Technical Details

### Structured Conditions

Each signifier includes structured conditions that are parsed into:

```python
StructuredCondition(
    artifact="http://example.org/...",
    property_affordance="http://example.org/...",
    value_conditions=[
        ValueCondition(operator="greaterThan", value=10000)
    ]
)
```

### SHACL Shapes

Each signifier includes SHACL NodeShapes for validation:

```turtle
cashmere:hasShaclCondition [
    a sh:NodeShape ;
    sh:targetNode <http://example.org/.../external_light_sensing308> ;
    sh:targetClass <http://example.org/LightSensor> ;
    sh:property [
        sh:path <http://example.org/LightSensor#hasLuminosityLevel> ;
        sh:datatype xsd:integer ;
        sh:minInclusive 10000 ;
    ]
]
```

### Property Index

The system automatically indexes signifiers by (artifact, property) pairs:

```
(external_light_sensing308, hasLuminosityLevel) -> [raise-blinds, lower-blinds]
(internal_light_sensing308, hasLuminosityLevel) -> [turn-light-on]
(temperature_sensor308, hasTemperatureLevel) -> [raise-blinds, lower-blinds]
(person_counter308, hasPersonCount) -> [turn-light-on]
```

This enables fast candidate pre-filtering for retrieval queries.
