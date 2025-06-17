# ISI-Core/run_tests.py

"""
Test runner for ISI-Core test suite.
Handles proper module path setup for running tests.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path for relative imports
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def run_demo():
    """Run the demo integration test."""
    print("Running demo integration...")
    try:
        from tests.demo_integration import main

        main()
        print("✅ Demo integration completed successfully")
        return True
    except Exception as e:
        print(f"❌ Demo integration failed: {e}")
        return False


def run_experiment_workflow_test():
    """Run the experiment workflow test."""
    print("Running experiment workflow test...")
    try:
        from tests.test_experiment_workflow import main

        main()
        print("✅ Experiment workflow test completed successfully")
        return True
    except Exception as e:
        print(f"❌ Experiment workflow test failed: {e}")
        return False


def run_integration_test():
    """Run the integration test."""
    print("Running integration test...")
    try:
        from tests.integration_test import main

        result = main()
        if result == 0:
            print("✅ Integration test completed successfully")
            return True
        else:
            print("❌ Integration test failed")
            return False
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("ISI-CORE TEST SUITE")
    print("=" * 60)

    results = []

    # Run individual tests
    results.append(run_demo())
    results.append(run_experiment_workflow_test())
    results.append(run_integration_test())

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
