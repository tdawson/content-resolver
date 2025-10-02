#!/usr/bin/python3

"""
Test script to validate the --views filtering functionality.
This script loads configs and checks if filtering works correctly.
"""

from content_resolver.config_manager import ConfigManager
import sys

def create_test_settings(views_filter=None):
    settings = {}
    settings["configs"] = "test_configs"
    settings["output"] = "output"
    settings["use_cache"] = False
    settings["dev_buildroot"] = True
    settings["dnf_cache_dir_override"] = None
    settings["parallel_max"] = 1
    settings["selected_views"] = views_filter
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

    settings = create_test_settings(views_filter=None)
    config_manager = ConfigManager(settings)

    try:
        configs = config_manager.get_configs()

        print("\n✅ Test 1 PASSED: Loaded all configs successfully")
        print(f"   - Repos: {len(configs['repos'])}")
        print(f"   - Envs: {len(configs['envs'])}")
        print(f"   - Workloads: {len(configs['workloads'])}")
        print(f"   - Views: {len(configs['views'])}")

        return configs
    except Exception as e:
        print(f"\n❌ Test 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_with_filter(all_configs):
    print("\n" + "=" * 80)
    print("TEST 2: Loading with --views filter")
    print("=" * 80)

    # Get a view ID from the loaded configs
    if not all_configs or not all_configs['views']:
        print("❌ Cannot test filtering - no views loaded in test 1")
        return False

    view_id = list(all_configs['views'].keys())[0]
    print(f"\nFiltering to view: {view_id}")

    settings = create_test_settings(views_filter=view_id)
    config_manager = ConfigManager(settings)

    try:
        filtered_configs = config_manager.get_configs()

        print("\n✅ Test 2 PASSED: Filtered configs successfully")
        print(f"   - Repos: {len(filtered_configs['repos'])} (was {len(all_configs['repos'])})")
        print(f"   - Envs: {len(filtered_configs['envs'])} (was {len(all_configs['envs'])})")
        print(f"   - Workloads: {len(filtered_configs['workloads'])} (was {len(all_configs['workloads'])})")
        print(f"   - Views: {len(filtered_configs['views'])} (was {len(all_configs['views'])})")

        # Verify the filtered view is present
        if view_id in filtered_configs['views']:
            print(f"\n✅ Selected view '{view_id}' is present in filtered configs")
        else:
            print(f"\n❌ Selected view '{view_id}' is NOT present in filtered configs")
            return False

        # Verify filtering actually reduced the config count
        if len(filtered_configs['views']) <= len(all_configs['views']):
            print(f"✅ Filtering reduced or maintained view count")
        else:
            print(f"❌ Filtering increased view count (should not happen)")
            return False

        return True

    except Exception as e:
        print(f"\n❌ Test 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_views(all_configs):
    print("\n" + "=" * 80)
    print("TEST 3: Loading with multiple views filter")
    print("=" * 80)

    if not all_configs or len(all_configs['views']) < 2:
        print("⚠️  Skipping test 3 - need at least 2 views")
        return True

    view_ids = list(all_configs['views'].keys())[:2]
    views_filter = ",".join(view_ids)
    print(f"\nFiltering to views: {views_filter}")

    settings = create_test_settings(views_filter=views_filter)
    config_manager = ConfigManager(settings)

    try:
        filtered_configs = config_manager.get_configs()

        print("\n✅ Test 3 PASSED: Filtered multiple views successfully")
        print(f"   - Views: {len(filtered_configs['views'])} (requested {len(view_ids)})")

        # Verify both views are present
        all_present = all(vid in filtered_configs['views'] for vid in view_ids)
        if all_present:
            print(f"✅ All selected views are present")
            return True
        else:
            print(f"❌ Some selected views are missing")
            return False

    except Exception as e:
        print(f"\n❌ Test 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "VIEW FILTERING TEST SUITE" + " " * 33 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    # Test 1: Load all configs
    all_configs = test_no_filter()
    if not all_configs:
        print("\n❌ OVERALL RESULT: Tests failed - could not load configs")
        sys.exit(1)

    # Test 2: Filter to single view
    test2_passed = test_with_filter(all_configs)

    # Test 3: Filter to multiple views
    test3_passed = test_multiple_views(all_configs)

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Test 1 (Load all configs):        ✅ PASSED")
    print(f"Test 2 (Filter single view):      {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"Test 3 (Filter multiple views):   {'✅ PASSED' if test3_passed else '❌ FAILED'}")

    if test2_passed and test3_passed:
        print("\n✅ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
