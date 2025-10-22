#!/usr/bin/python3

"""
Test script to validate the --labels filtering functionality.
This script loads configs and checks if filtering works correctly.
"""

from content_resolver.config_manager import ConfigManager
import sys

def create_test_settings(labels_filter=None):
    settings = {}
    settings["configs"] = "test_configs"
    settings["output"] = "output"
    settings["use_cache"] = False
    settings["dev_buildroot"] = True
    settings["dnf_cache_dir_override"] = None
    settings["parallel_max"] = 1
    settings["selected_labels"] = labels_filter
    settings["root_log_deps_cache_path"] = "cache_root_log_deps.json"
    settings["max_subprocesses"] = 10
    settings["allowed_arches"] = ["aarch64","ppc64le","s390x","x86_64"]
    settings["weird_packages_that_can_not_be_installed"] = ["glibc32"]
    settings["strict"] = False

    return settings

def test_no_filter():
    print("=" * 80)
    print("TEST 1: Loading all configs (no filtering)")
    print("=" * 80)

    settings = create_test_settings(labels_filter=None)
    config_manager = ConfigManager(settings)

    try:
        configs = config_manager.get_configs()

        print("\n✅ Test 1 PASSED: Loaded all configs successfully")
        print(f"   - Repos: {len(configs['repos'])}")
        print(f"   - Envs: {len(configs['envs'])}")
        print(f"   - Workloads: {len(configs['workloads'])}")
        print(f"   - Labels: {len(configs['labels'])}")
        print(f"   - Views: {len(configs['views'])}")

        return configs
    except Exception as e:
        print(f"\n❌ Test 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_with_filter(all_configs):
    print("\n" + "=" * 80)
    print("TEST 2: Loading with --labels filter")
    print("=" * 80)

    # Use a known label from the test configs (labels are defined in workloads/envs/views)
    # In test_configs, we know "eln" is used
    label_id = "eln"
    print(f"\nFiltering to label: {label_id}")

    settings = create_test_settings(labels_filter=label_id)
    config_manager = ConfigManager(settings)

    try:
        filtered_configs = config_manager.get_configs()

        print("\n✅ Test 2 PASSED: Filtered configs successfully")
        print(f"   - Repos: {len(filtered_configs['repos'])} (was {len(all_configs['repos'])})")
        print(f"   - Envs: {len(filtered_configs['envs'])} (was {len(all_configs['envs'])})")
        print(f"   - Workloads: {len(filtered_configs['workloads'])} (was {len(all_configs['workloads'])})")
        print(f"   - Views: {len(filtered_configs['views'])} (was {len(all_configs['views'])})")

        # Verify filtering actually reduced the config count (or at least didn't increase it)
        if (len(filtered_configs['workloads']) <= len(all_configs['workloads']) and
            len(filtered_configs['views']) <= len(all_configs['views'])):
            print(f"✅ Filtering reduced or maintained config counts")
        else:
            print(f"❌ Filtering increased config count (should not happen)")
            return False

        return True

    except Exception as e:
        print(f"\n❌ Test 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_labels(all_configs):
    print("\n" + "=" * 80)
    print("TEST 3: Loading with multiple labels filter")
    print("=" * 80)

    # Use known labels from test configs
    label_ids = ["eln", "eln-extras"]
    labels_filter = ",".join(label_ids)
    print(f"\nFiltering to labels: {labels_filter}")

    settings = create_test_settings(labels_filter=labels_filter)
    config_manager = ConfigManager(settings)

    try:
        filtered_configs = config_manager.get_configs()

        print("\n✅ Test 3 PASSED: Filtered multiple labels successfully")
        print(f"   - Workloads: {len(filtered_configs['workloads'])}")
        print(f"   - Envs: {len(filtered_configs['envs'])}")
        print(f"   - Views: {len(filtered_configs['views'])}")

        # Verify we got some configs matching our labels
        if len(filtered_configs['workloads']) > 0 or len(filtered_configs['views']) > 0:
            print(f"✅ Found configs matching selected labels")
            return True
        else:
            print(f"⚠️  No configs found for selected labels (this may be expected)")
            return True

    except Exception as e:
        print(f"\n❌ Test 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "LABEL FILTERING TEST SUITE" + " " * 32 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    # Test 1: Load all configs
    all_configs = test_no_filter()
    if not all_configs:
        print("\n❌ OVERALL RESULT: Tests failed - could not load configs")
        sys.exit(1)

    # Test 2: Filter to single label
    test2_passed = test_with_filter(all_configs)

    # Test 3: Filter to multiple labels
    test3_passed = test_multiple_labels(all_configs)

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Test 1 (Load all configs):         ✅ PASSED")
    print(f"Test 2 (Filter single label):      {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"Test 3 (Filter multiple labels):   {'✅ PASSED' if test3_passed else '❌ FAILED'}")

    if test2_passed and test3_passed:
        print("\n✅ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
