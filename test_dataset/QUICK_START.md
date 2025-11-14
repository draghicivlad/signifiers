# Quick Start Guide - Test Dataset

## Running the Tests

### 1. Run All Test Scenarios
```bash
cd C:\Users\Vlad\signifiers
python test_dataset/scripts/run_scenarios.py
```

This will:
- Load all 4 test signifiers
- Run 18 comprehensive tests
- Generate a detailed report
- Save results to `test_dataset/test_report.json`

### 2. View Test Report
After running, check the console output for real-time results, or:
```bash
type test_dataset\test_report.json
```

## Test Categories

### Storage Tests (3)
Validates basic CRUD operations and filtering

### SHACL Validation Tests (4)
Tests constraint validation with various contexts

### Intent Matching Tests (6)
Compares string (v0) vs embedding (v1) matchers

### Integration Tests (5)
End-to-end scenarios with real context data

## Example Test Scenarios

### Scenario: Cold Room Heating
```bash
Query: "warm up the room"
Context: Temperature = 18°C, People = 2
Expected: heat-room-signifier matches and validates
Result: ✅ PASSED
```

### Scenario: Meeting Mode
```bash
Query: "prepare for meeting"
Context: People = 5
Expected: start-meeting-mode-signifier matches
Result: ✅ PASSED
```

### Scenario: Semantic Matching
```bash
Query: "make room brighter"
Matcher: v1 (embeddings)
Expected: Semantic similarity matches
Result: ✅ PASSED (4 matches found)
```

## Expected Results

- **Total Tests**: 18
- **Expected Pass**: 16
- **Expected Fail**: 2 (due to dataset differences)
- **Success Rate**: 88.9%

## Performance Benchmarks

- Storage ops: < 30ms
- String matching: ~1-2ms
- Embedding matching: ~7ms (after model load)
- SHACL validation: 2-5ms

## File Structure

```
test_dataset/
├── signifiers/          # 4 test signifier .ttl files
├── contexts/            # 7 JSON context scenarios
├── scenarios/           # Test scenario documentation
├── scripts/             # Automated test runner
├── README.md            # Dataset overview
├── VALIDATION_REPORT.md # Detailed test results
└── QUICK_START.md       # This file
```

## Troubleshooting

### Module Not Found
Ensure you're in the project root:
```bash
cd C:\Users\Vlad\signifiers
```

### Import Errors
The test script automatically adds the parent directory to Python path.

### Embedding Model Download
First run of v1 matcher downloads the model (one-time, ~90MB).
Subsequent runs use cached model.

## Next Steps

1. ✅ Run the test suite
2. ✅ Review the validation report
3. ✅ Examine test scenarios document
4. ✅ Try creating your own signifiers
5. ✅ Add custom contexts for your use case

## Additional Resources

- **TEST_SCENARIOS.md**: Detailed test descriptions
- **VALIDATION_REPORT.md**: Comprehensive analysis
- **README.md**: Dataset overview
