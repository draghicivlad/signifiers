# Test Scenarios for RD4 Signifier System

This document defines comprehensive test scenarios to validate all phases of the system.

## Phase 1: Storage Tests

### T1.1: Load Signifiers from RDF
**Objective**: Verify signifiers can be loaded from Turtle files
- Load all 7 signifiers from test_dataset/signifiers/
- Verify round-trip RDF fidelity
- Check all fields are correctly parsed

**Expected**: All signifiers load successfully, no data loss

### T1.2: CRUD Operations
**Objective**: Verify create, read, update, delete operations
- Create new signifier programmatically
- Retrieve by ID
- Update and verify version increment
- Delete and verify removal

**Expected**: All operations succeed, versioning works

### T1.3: Listing and Filtering
**Objective**: Verify signifier listing and filtering
- List all signifiers
- Filter by status (active/deprecated)
- Filter by affordance URI

**Expected**: Correct filtering results

## Phase 2: SHACL Validation Tests

### T2.1: Conforming Context (raise-blinds)
**Query**: "increase luminosity"
**Context**: scenario1_bright_warm.json (luminosity=15000, temp=22)
**Expected**: SHACL validation PASSES for raise-blinds-signifier
- Luminosity 15000 >= 10000 (min)
- Temperature 22 <= 25 (max)

### T2.2: Non-Conforming Context (luminosity too low)
**Query**: "increase brightness"
**Context**: luminosity=5000, temp=22
**Expected**: SHACL validation FAILS
- Luminosity 5000 < 10000 (violated minInclusive constraint)

### T2.3: Edge Case - Exact Threshold
**Context**: scenario7_edge_luminosity.json (luminosity=10000 exactly)
**Expected**: Validation PASSES (minInclusive allows equality)

### T2.4: Multiple Constraints Validation
**Query**: "turn on light"
**Context**: scenario2_dark_people.json
**Expected**: SHACL validation PASSES for turn-light-on-signifier
- Luminosity 50 <= 100 (max)
- Person count 3 >= 1 (min)

### T2.5: Authoring Validation
**Objective**: Verify signifier structure validation at ingest
- Load signifier with missing required fields
- Load signifier with invalid SHACL shapes

**Expected**: Validation errors caught (when enabled)

## Phase 3: Intent Matching Tests

### T3.1: String Matcher (v0) - Exact Match
**Query**: "increase luminosity"
**Expected**: High similarity for raise-blinds and turn-light-on
- Both contain "increase" and "luminosity"

### T3.2: String Matcher (v0) - Partial Match
**Query**: "make brighter"
**Expected**: Lower similarity, may not match
- No exact token overlap

### T3.3: Embedding Matcher (v1) - Semantic Match
**Query**: "make room brighter"
**Expected**: Matches raise-blinds and turn-light-on via semantic similarity
- Semantic meaning captured despite different words

### T3.4: Embedding Matcher (v1) - Better than String
**Query**: "it's too dark in here"
**Expected**: v1 performs better than v0
- v1 understands "dark" relates to "luminosity"
- v0 has no token overlap

### T3.5: Version Comparison (A/B Test)
**Query**: "increase light level"
**Expected**: Both versions return results, compare similarity scores
- Document performance difference

### T3.6: Top-K Limiting
**Query**: "increase luminosity" with k=2
**Expected**: Returns top 2 matches only

### T3.7: No Matches
**Query**: "brew coffee"
**Expected**: Empty results (no signifier matches this intent)

## End-to-End Integration Tests

### T4.1: Full Pipeline - Perfect Match
**Query**: "increase luminosity"
**Context**: scenario1_bright_warm.json
**Steps**:
1. Intent matching (both v0 and v1)
2. Context normalization
3. SHACL validation for candidates
4. Filter non-conforming

**Expected**: raise-blinds-signifier returned (passes both intent AND SHACL)

### T4.2: Full Pipeline - Intent Match, Context Fails
**Query**: "increase brightness"
**Context**: luminosity=5000 (too low)
**Expected**: Intent matches but SHACL filters out => No results

### T4.3: Multiple Candidates Ranking
**Query**: "make room brighter"
**Context**: scenario2_dark_people.json
**Expected**: Multiple signifiers match, ranked by similarity

### T4.4: Temperature Control Scenarios
**Query**: "warm up the room"
**Context**: scenario3_cold_people.json (temp=18, people=2)
**Expected**: heat-room-signifier matches and validates

**Query**: "cool down"
**Context**: scenario4_hot.json (temp=28)
**Expected**: cool-room-signifier matches and validates

### T4.5: Meeting Scenario
**Query**: "prepare for meeting"
**Context**: scenario5_meeting.json (people=5)
**Expected**: start-meeting-mode-signifier matches

### T4.6: No Action Needed
**Query**: "adjust lighting"
**Context**: scenario6_no_match.json (optimal conditions, no people)
**Expected**: No matches (context doesn't satisfy any signifier)

## Performance Tests

### T5.1: Latency Budget - Storage
**Objective**: Verify CRUD operations within budget
- Measure: Create, Read, Update, Delete times

**Expected**: Each operation < 50ms

### T5.2: Latency Budget - String Matching
**Objective**: Verify IM v0 within budget (30ms)
- Match query against 10 signifiers

**Expected**: < 30ms

### T5.3: Latency Budget - Embedding Matching
**Objective**: Verify IM v1 within budget (30ms)
- Match query against 10 signifiers (with cache)

**Expected**: < 30ms (first call may be slower due to model load)

### T5.4: Latency Budget - SHACL Validation
**Objective**: Verify validation within budget (80ms)
- Validate context against signifier shapes

**Expected**: < 80ms per validation

## Data Quality Tests

### T6.1: Round-Trip Fidelity
**Objective**: Verify no data loss in RDF <-> JSON conversion
- Load signifier from RDF
- Convert to JSON
- Convert back to RDF
- Compare original vs result

**Expected**: Identical RDF graphs

### T6.2: Encoding Handling
**Objective**: Verify special characters handled correctly
- Signifier with unicode in NL text
- URIs with special characters

**Expected**: Correct encoding/decoding

### T6.3: Large Signifier Sets
**Objective**: Verify system handles many signifiers
- Load 50+ signifiers
- Query and filter

**Expected**: Consistent performance

## Test Execution Order

1. Run Phase 1 tests (Storage foundation)
2. Run Phase 2 tests (SHACL validation)
3. Run Phase 3 tests (Intent matching)
4. Run Integration tests (End-to-end)
5. Run Performance tests
6. Run Data Quality tests

## Success Criteria

- All storage tests pass (100%)
- All SHACL validation tests pass (100%)
- All intent matching tests pass (100%)
- End-to-end integration tests pass (100%)
- Performance within budgets (>95% of requests)
- No data loss in round-trip tests (100%)
