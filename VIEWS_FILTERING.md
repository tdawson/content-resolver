# Selective View Processing with --views

This branch implements Option 1 from the design discussion: filtering configs at load time to enable selective view processing.

## Overview

When working with large configuration sets, you may only want to process specific views rather than analyzing everything. The `--views` option allows you to specify which views to process, and Content Resolver will automatically determine and include only the necessary dependencies (workloads, environments, and repositories).

## Usage

### Basic Usage - Single View

```bash
./content_resolver.py --views view-eln test_configs output
```

This will process only the `view-eln` view and its dependencies.

### Multiple Views

```bash
./content_resolver.py --views view-eln,view-eln-extras test_configs output
```

Process multiple views by separating them with commas.

### Combined with Other Options

```bash
./content_resolver.py --dev-buildroot --views view-eln-extras test_configs output
```

The `--views` option works with all other command-line options.

### View All Available Views

Without the `--views` option, Content Resolver processes all views (default behavior):

```bash
./content_resolver.py test_configs output
```

## How It Works

The filtering happens in `ConfigManager.get_configs()` after all YAML files are loaded but before analysis begins:

1. **Views**: Filters to only the specified view IDs
   - Automatically includes base views if filtering an addon view

2. **Labels**: Collects labels from the selected views

3. **Workloads**: Keeps only workloads that match the collected labels

4. **Environments**: Keeps only environments that match labels from the filtered workloads

5. **Repositories**: Keeps only repositories referenced by views or environments

6. **Labels**: Keeps only labels that are actually used

This dependency-aware filtering ensures that all required configs are included while excluding everything else.

## Benefits

- **Performance**: Significantly faster when you only need specific views
- **Resource Usage**: Reduces memory consumption by not loading/analyzing unnecessary data
- **Development**: Iterate faster when working on specific views
- **Backwards Compatible**: No `--views` argument means process everything (existing behavior)

## Example Output

When using `--views`, you'll see filtering information in the logs:

```
Filtering configs to process only selected views...
Selected views: view-eln-extras

  Including base view 'view-eln' (required by addon view 'view-eln-extras')
  Filtered to 2 views (from 3)
  Found 2 labels from views: eln, eln-extras
  Filtered to 7 workloads (from 8)
  Filtered to 3 environments (from 3)
  Filtered to 3 repositories (from 3)
  Filtered to 2 labels (from 2)

Config filtering complete!

Summary:
--------

Standard yaml configs:
  - 3 repositories
  - 3 environments
  - 7 workloads
  - 2 views
  - 0 exclusion lists
```

## Testing

A test script is included to validate the filtering functionality:

```bash
./test_view_filtering.py
```

This runs three test scenarios:
1. Loading all configs (no filtering)
2. Filtering to a single view
3. Filtering to multiple views

All tests should pass with the test_configs directory.

## Implementation Details

### Code Changes

**File**: `content_resolver/config_manager.py`

- Added `--views` CLI argument in `load_settings()`
- Added `filter_configs_by_views()` method (120 lines)
- Called filtering in `get_configs()` after config loading

**File**: `test_view_filtering.py` (new)

- Test script to validate filtering behavior
- Compares filtered vs unfiltered config counts
- Validates dependency relationships

### Design Rationale

This implementation was chosen (Option 1: Filter at Config Load Time) because:

1. **Minimal Code Changes**: Only changes in config_manager.py, no modifications to analyzer.py
2. **Performance**: Filtering happens once, before expensive DNF operations
3. **Maintainability**: Clear separation between config selection and analysis
4. **Backwards Compatible**: Preserves existing behavior when --views is not specified

### Dependency Resolution

The filtering correctly handles:

- **Addon views**: Automatically includes base views
- **Labels**: Transitively includes all necessary labels
- **Workloads**: Includes all workloads matching view labels
- **Environments**: Includes all environments needed by workloads
- **Repositories**: Includes all repos referenced by views or environments

### Edge Cases Handled

- Non-existent view IDs: Warning logged, processing continues with valid IDs
- Addon views: Base view automatically included even if not specified
- Empty view list: Processes all views (same as not specifying --views)
- Whitespace in view IDs: Automatically trimmed

## Future Enhancements

Potential improvements for future iterations:

1. **Architecture Filtering**: Add `--arches` to filter specific architectures
2. **Workload Filtering**: Add `--workloads` to process specific workloads directly
3. **Dry Run**: Add `--dry-run` to show what would be processed without running analysis
4. **Config Validation**: Warn if filtering results in zero views to process
5. **Performance Metrics**: Report time/memory saved by filtering

## Git Branch

Branch: `feature/filter-views-at-config-load`

```bash
# To use this feature:
git checkout feature/filter-views-at-config-load

# To merge into your working branch:
git checkout your-branch
git merge feature/filter-views-at-config-load
```

## Questions or Issues?

If you encounter any problems or have questions about this feature, please open an issue on the repository.
