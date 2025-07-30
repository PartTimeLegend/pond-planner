#!/usr/bin/env python3
"""
Setup verification script for Pond Planner application.

This script verifies that all dependencies are installed and the application
is working correctly.
"""

import os
import sys


def check_python_version() -> bool:
    """Check if Python version is 3.11 or higher."""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 11):
        print(f"❌ Python 3.11+ required, found {sys.version}")
        return False
    print(
        f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    return True


def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    print("\n📦 Checking dependencies...")

    try:
        import importlib.util

        if importlib.util.find_spec("yaml") is not None:
            print("✅ PyYAML installed")
        else:
            print("❌ PyYAML not found. Run: pip install PyYAML>=6.0")
            return False
    except ImportError:
        print("❌ PyYAML not found. Run: pip install PyYAML>=6.0")
        return False

    return True


def check_data_files() -> bool:
    """Check if required data files exist."""
    print("\n📄 Checking data files...")

    required_files = [
        "fish_database.yaml",
        "pond_shapes.yaml",
        "PondPlanner.py",
        "main.py",
    ]

    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} not found")
            return False

    return True


def test_pond_planner() -> bool:
    """Test basic PondPlanner functionality."""
    print("\n🧪 Testing PondPlanner functionality...")

    try:
        from PondPlanner import PondPlanner

        print("✅ PondPlanner import successful")

        planner = PondPlanner()
        print("✅ PondPlanner instance created")

        planner.set_dimensions(3.0, 2.0, 1.0, "rectangular")
        volume = planner.calculate_volume_liters()
        print(f"✅ Volume calculation: {volume:.0f}L")

        # Test fish database access
        fish_repo = planner._fish_repository
        fish_count = len(fish_repo.get_all_fish())
        print(f"✅ Fish database loaded: {fish_count} species")

        return True

    except Exception as e:
        print(f"❌ Error testing PondPlanner: {e}")
        return False


def test_persistence() -> bool:
    """Test save/load functionality."""
    print("\n💾 Testing persistence functionality...")

    try:
        from PondPlanner import PondPlanner

        # Create and save a test pond
        planner = PondPlanner()
        planner.set_dimensions(4.0, 3.0, 1.5, "oval")

        filename = planner.save_pond("Setup_Test", "Verification test pond")
        print(f"✅ Pond saved: {filename}")

        # Load the test pond
        planner2 = PondPlanner()
        planner2.load_pond("Setup_Test")
        print(f"✅ Pond loaded: {planner2.dimensions.shape}")

        # Clean up
        planner.delete_saved_pond("Setup_Test")
        print("✅ Test pond cleaned up")

        return True

    except Exception as e:
        print(f"❌ Error testing persistence: {e}")
        return False


def main() -> int:
    """Run all verification checks."""
    print("🔍 Pond Planner Setup Verification")
    print("=" * 40)

    checks = [
        check_python_version(),
        check_dependencies(),
        check_data_files(),
        test_pond_planner(),
        test_persistence(),
    ]

    print("\n" + "=" * 40)

    if all(checks):
        print("🎉 All checks passed! Pond Planner is ready to use.")
        print("\nTo get started, run: python main.py")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nFor help, see the README.md file or the troubleshooting section.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
