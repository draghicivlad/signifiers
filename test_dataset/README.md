# RD4 Signifier System - Test Dataset

This directory contains a comprehensive test dataset for validating the RD4 Signifier System across all phases (Storage, SHACL Validation, Intent Matching).

## Dataset Structure

```
test_dataset/
├── signifiers/          # Signifier definitions in Turtle format
│   ├── smart_home/     # Smart home automation signifiers
│   ├── office/         # Office automation signifiers
│   └── energy/         # Energy management signifiers
├── contexts/           # Context snapshots for testing
├── scenarios/          # Test scenario definitions
└── scripts/            # Automated test scripts
```

## Signifier Categories

### 1. Smart Home - Lighting (3 signifiers)
- **turn-light-on**: Turn on lights when dark and people present
- **turn-light-off**: Turn off lights when bright or no people
- **dim-lights**: Dim lights to comfortable level

### 2. Smart Home - Climate (3 signifiers)
- **heat-room**: Turn on heating when cold
- **cool-room**: Turn on AC when hot
- **open-window**: Open window for ventilation

### 3. Smart Home - Blinds (3 signifiers)
- **raise-blinds**: Raise blinds when bright outside
- **lower-blinds**: Lower blinds when too bright
- **tilt-blinds**: Adjust blinds for optimal light

### 4. Office Automation (2 signifiers)
- **start-meeting-mode**: Configure room for meeting
- **end-workday**: Turn off all devices at end of day

### 5. Energy Management (2 signifiers)
- **reduce-consumption**: Reduce power when high usage
- **night-mode**: Enter low-power mode at night

## Test Scenarios

### Scenario 1: Perfect Match
Intent matches AND context satisfies SHACL constraints
- Query: "make room brighter"
- Expected: turn-light-on or raise-blinds

### Scenario 2: Intent Match but Context Fails
Intent matches BUT context violates SHACL
- Query: "increase brightness"
- Context: luminosity already high
- Expected: No matches (SHACL validation fails)

### Scenario 3: Multiple Matches
Multiple signifiers match, test ranking
- Query: "increase light in room"
- Expected: Multiple matches ranked by similarity

### Scenario 4: Semantic Similarity
Test embedding matcher vs string matcher
- Query: "make it brighter in here"
- Expected: v1 matcher performs better than v0

### Scenario 5: Edge Cases
Boundary value testing
- Luminosity exactly at threshold (10000)
- Temperature exactly at threshold (25)

### Scenario 6: No Matches
Query doesn't match any signifier
- Query: "brew coffee"
- Expected: Empty results

## Usage

### 1. Load Signifiers
```bash
python test_dataset/scripts/load_signifiers.py
```

### 2. Run Test Scenarios
```bash
python test_dataset/scripts/run_scenarios.py
```

### 3. Generate Report
```bash
python test_dataset/scripts/generate_report.py
```

## Validation Criteria

- All signifiers load successfully
- Round-trip RDF fidelity maintained
- SHACL validation works correctly
- Intent matching v0 and v1 produce results
- End-to-end pipeline completes within latency budget
