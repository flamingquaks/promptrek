#!/usr/bin/env python3
"""Test and validate generated schemas against example files."""

import json
import sys
from pathlib import Path

import yaml
from jsonschema import ValidationError, validate


def test_schema(schema_file: Path, yaml_files: list[Path]):
    """Test a schema against a list of YAML files."""
    print(f"\nTesting schema: {schema_file.name}")
    print("=" * 60)
    
    # Load schema
    with open(schema_file) as f:
        schema = json.load(f)
    
    passed = 0
    failed = 0
    
    for yaml_file in yaml_files:
        try:
            # Load YAML
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
            
            # Validate
            validate(instance=data, schema=schema)
            print(f"✓ {yaml_file.name}")
            passed += 1
        except ValidationError as e:
            print(f"✗ {yaml_file.name}: {e.message}")
            failed += 1
        except Exception as e:
            print(f"✗ {yaml_file.name}: {type(e).__name__}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def main():
    """Run all schema tests."""
    repo_root = Path(__file__).parent.parent
    schema_dir = repo_root / "gh-pages" / "schema"
    
    # Test v3.0 schema with project file
    v3_files = [
        repo_root / "project.promptrek.yaml",
    ]
    test_v3 = test_schema(schema_dir / "v3.0.json", v3_files)
    
    # Test v2.1 schema with v21-plugins examples
    v21_dir = repo_root / "examples" / "v21-plugins"
    v21_files = list(v21_dir.glob("*.yaml")) if v21_dir.exists() else []
    test_v21 = test_schema(schema_dir / "v2.1.json", v21_files) if v21_files else True
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"v3.0 schema: {'PASS' if test_v3 else 'FAIL'}")
    print(f"v2.1 schema: {'PASS' if test_v21 else 'FAIL'}")
    
    return 0 if (test_v3 and test_v21) else 1


if __name__ == "__main__":
    sys.exit(main())
