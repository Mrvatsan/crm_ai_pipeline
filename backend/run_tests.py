import sys
import os

# Add backend directory to system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from compiler_tests.test_validation import (
    test_full_pipeline_compilation,
    test_static_analysis_validator_detects_errors,
    test_repair_engine_self_healing
)

if __name__ == "__main__":
    print("=" * 60)
    print("      AI-NATIVE COMPILER PIPELINE - INTEGRATION TESTS")
    print("=" * 60)
    
    tests = [
        ("Full compiler pipeline compilation and DB seed loading", test_full_pipeline_compilation),
        ("Static analysis validation & constraint error detection", test_static_analysis_validator_detects_errors),
        ("Compiler target Self-Repair & dynamic role healing", test_repair_engine_self_healing)
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"Running: {name}...", end="", flush=True)
        try:
            test_func()
            print(" [PASS]")
            passed += 1
        except Exception as e:
            print(" [FAIL]")
            import traceback
            traceback.print_exc()
            
    print("=" * 60)
    print(f"Test Summary: {passed}/{len(tests)} passed.")
    print("=" * 60)
    
    if passed == len(tests):
        sys.exit(0)
    else:
        sys.exit(1)
