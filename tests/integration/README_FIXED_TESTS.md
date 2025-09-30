# Fixed Test Files

## Overview

The integration test suite contains both original and "fixed" versions of some test files:

- `test_adapter_workflows.py` / `test_adapter_workflows_fixed.py`
- `test_cli_comprehensive.py` / `test_cli_comprehensive_fixed.py`
- `test_core_workflows.py` / `test_core_workflows_fixed.py`

## Purpose

These "fixed" versions were created during development to address:
1. Instabilities in test execution
2. Issues with mock configurations
3. Timing or dependency-related failures

## Current Status (v0.0.1)

- ✅ **All tests now pass reliably** (442 passing tests, 82% coverage)
- Both versions are kept for comparison and verification
- Tests run successfully across platforms (Linux, macOS, Windows)

## Recommendations for Future Cleanup

### Option 1: Consolidate (Recommended for v0.1.0)
- Compare the two versions of each file
- Merge the best implementations into the original files
- Remove the "_fixed" versions
- Verify all tests still pass

### Option 2: Document and Keep
- Add clear comments explaining differences
- Use "_fixed" as the canonical version if it's superior
- Rename to indicate purpose (e.g., `_stable` instead of `_fixed`)

## Testing Commands

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific test files
pytest tests/integration/test_adapter_workflows.py -v
pytest tests/integration/test_adapter_workflows_fixed.py -v

# Compare test coverage
pytest tests/integration/test_adapter_workflows.py --cov=src/promptrek --cov-report=term-missing
pytest tests/integration/test_adapter_workflows_fixed.py --cov=src/promptrek --cov-report=term-missing
```

## File Sizes

- `test_adapter_workflows.py`: ~30KB
- `test_adapter_workflows_fixed.py`: ~25KB (more focused)
- `test_cli_comprehensive.py`: ~22KB
- `test_cli_comprehensive_fixed.py`: ~20KB (cleaner mocks)
- `test_core_workflows.py`: ~23KB
- `test_core_workflows_fixed.py`: ~23KB (similar size)

## Action Items for v0.1.0

- [ ] Compare implementations line-by-line
- [ ] Identify which version is superior for each file
- [ ] Consolidate into single version
- [ ] Run full test suite to verify
- [ ] Update CI/CD if needed
- [ ] Remove duplicate files

## Notes

The presence of both versions is acceptable for v0.0.1 as it ensures test reliability during initial release. Future versions should consolidate to reduce maintenance burden.