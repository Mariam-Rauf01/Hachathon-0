# AI Employee Test Suite

## Overview
This test suite validates the Silver Tier AI Employee system functionality, including all watchers, reasoning loops, approval workflows, and action handlers.

## Prerequisites

Install required packages:
```bash
pip install pytest
```

Or if you prefer unittest (built into Python):
```bash
# No additional installation needed for unittest
```

## Test Structure

The test suite includes:

### 1. Unit Tests
- **Watcher Tests**: Verify watchers create .md files from inputs
- **Reasoning Tests**: Validate plan generation with checkboxes
- **Approval Tests**: Test pending approval workflows
- **Action Tests**: Verify action handlers trigger correctly
- **Dashboard Tests**: Confirm dashboard updates

### 2. Integration Tests
- **End-to-End Workflow**: Complete pipeline from input to action
- **File System Operations**: Directory management and file movement
- **Component Coordination**: Cross-component interactions

### 3. Functional Tests
- **File Existence**: Verify files are created/moved correctly
- **Content Validation**: Check file contents meet expectations
- **Workflow Integrity**: Ensure approval processes work

## Running Tests

### Option 1: Using pytest (Recommended)
```bash
# Run all tests
pytest test_suite.py -v

# Run with coverage
pytest test_suite.py --cov=AI_Employee_Vault -v

# Run specific test class
pytest test_suite.py::TestAIOrchestrator::test_end_to_end_workflow -v

# Run with detailed output
pytest test_suite.py -v -s
```

### Option 2: Using unittest
```bash
# Run all tests
python -m unittest test_suite.py -v

# Run specific test
python -m unittest test_suite.py.TestAIOrchestrator.test_end_to_end_workflow -v
```

## Test Coverage

### Core Components Tested:
1. **Watchers** (Gmail, WhatsApp, LinkedIn)
2. **Reasoning Loop** (Plan generation)
3. **Approval Workflow** (Pending → Approved → Done)
4. **Action Handlers** (Email, LinkedIn posting)
5. **Dashboard Updates** (Status tracking)
6. **File System Operations** (Directory management)

### Test Scenarios:
- ✅ Watcher creates .md from mock input
- ✅ Reasoning loop generates Plan.md with checkboxes  
- ✅ Pending approval file creation for sensitive actions
- ✅ Approved files trigger action handlers
- ✅ Dashboard.md updates with status
- ✅ End-to-end workflow simulation
- ✅ File existence and content validation
- ✅ Error handling and recovery

## Test Reports

### Default Output
- Console output shows test results
- Individual test status (PASS/FAIL)
- Error details for failed tests

### Logging
- Test logs are stored in `Logs/test_suite.log`
- Detailed execution trace
- Performance metrics

## Running in Different Environments

### Development
```bash
# Quick run
pytest test_suite.py

# Verbose with output
pytest test_suite.py -v -s
```

### Continuous Integration
```bash
# Run with coverage and exit codes
pytest test_suite.py --cov=AI_Employee_Vault --cov-report=html --junitxml=test-results.xml
```

### Production Validation
```bash
# Run comprehensive test suite
pytest test_suite.py -k "not slow" --tb=short
```

## Expected Results

All tests should pass with:
- 100% file operation success
- Valid plan generation with checkboxes
- Proper approval workflow execution
- Correct dashboard updates
- No file corruption or loss

## Troubleshooting

### Common Issues:
- **Permission Errors**: Ensure write access to test directories
- **Missing Dependencies**: Install required packages
- **Path Issues**: Run tests from AI_Employee_Vault directory

### Debug Mode:
```bash
pytest test_suite.py -v -s --tb=long
```

## Maintenance

### Adding New Tests:
1. Add test methods to `TestAIOrchestrator` class
2. Follow existing naming convention (`test_*`)
3. Use appropriate assertions
4. Clean up test files in `tearDown`

### Updating Tests:
- Modify test data as system evolves
- Update expected values
- Add new validation checks

## Quality Gates

- All tests must pass before deployment
- Code coverage should be >80%
- No critical failures in end-to-end tests
- Performance within acceptable limits