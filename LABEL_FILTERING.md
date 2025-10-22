# Selective Processing with --labels

This feature implements label-based filtering at config load time to enable selective processing of workloads, environments, and views.

## Overview

When working with large configuration sets, you may only want to process configs with specific labels rather than analyzing everything. The `--labels` option allows you to specify which labels to process, and Content Resolver will automatically include only the configs (workloads, environments, views, and repositories) that match those labels.

## Usage

### Basic Usage - Single Label

```bash
./content_resolver.py --labels eln test_configs output
```

This will process only configs with the `eln` label and their dependencies.

### Multiple Labels

```bash
./content_resolver.py --labels eln,eln-extras test_configs output
```

Process multiple labels by separating them with commas.

### Combined with Other Options

```bash
./content_resolver.py --dev-buildroot --labels eln test_configs output
```

The `--labels` option works with all other command-line options.

### Process All Labels

Without the `--labels` option, Content Resolver processes all configs (default behavior):

```bash
./content_resolver.py test_configs output
```

## How It Works

The filtering happens in `ConfigManager.get_configs()` after all YAML files are loaded but before analysis begins:

1. **Workloads**: Filters to only workloads that have matching labels

2. **Environments**: Keeps only environments that have matching labels

3. **Views**: Keeps only views that have matching labels
   - Automatically includes base views if filtering includes an addon view

4. **Repositories**: Keeps only repositories referenced by filtered views or environments

This label-based filtering ensures that all required configs are included while excluding everything else.

## Benefits

- **Performance**: Significantly faster when you only need specific label subsets
- **Resource Usage**: Reduces memory consumption by not loading/analyzing unnecessary data
- **Development**: Iterate faster when working on specific labels
- **Backwards Compatible**: No `--labels` argument means process everything (existing behavior)
- **More Flexible**: Unlike the previous `--views` option, `--labels` allows filtering at a more fundamental level
- **Simpler Logic**: Labels are the core architectural concept that connects configs together

## Example Output

When using `--labels`, you'll see filtering information in the logs:

```
Filtering configs to process only selected labels...
Selected labels: eln, eln-extras

  Filtered to 7 workloads (from 8)
  Filtered to 3 environments (from 3)
  Including base view 'view-eln' (required by addon view)
  Filtered to 2 views (from 3)
  Filtered to 3 repositories (from 3)

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
./test_label_filtering.py
```

This runs three test scenarios:
1. Loading all configs (no filtering)
2. Filtering to a single label
3. Filtering to multiple labels

All tests should pass with the test_configs directory.

## Implementation Details

### Code Changes

**File**: `content_resolver/config_manager.py`

- Added `--labels` CLI argument in `load_settings()` (replaces `--views`)
- Added `filter_configs_by_labels()` method
- Called filtering in `get_configs()` after config loading

**File**: `test_label_filtering.py` (renamed from `test_view_filtering.py`)

- Test script to validate filtering behavior
- Compares filtered vs unfiltered config counts
- Validates label-based filtering logic

### Design Rationale

This implementation uses label-based filtering (rather than view-based) because:

1. **Architectural Alignment**: Labels are the fundamental connecting mechanism in the system
2. **Simpler Logic**: Directly filters by labels instead of extracting labels from views
3. **More Flexible**: Can filter workloads/environments even if no view references them yet
4. **Performance**: Filtering happens once, before expensive DNF operations
5. **Maintainability**: Clear separation between config selection and analysis
6. **Backwards Compatible**: Preserves existing behavior when --labels is not specified

### Dependency Resolution

The filtering correctly handles:

- **Addon views**: Automatically includes base views when an addon view's labels match
- **Labels**: Uses specified labels directly for filtering
- **Workloads**: Includes all workloads matching selected labels
- **Environments**: Includes all environments matching selected labels
- **Views**: Includes all views matching selected labels
- **Repositories**: Includes all repos referenced by filtered views or environments

### Edge Cases Handled

- Non-existent label IDs: Warning logged, processing continues
- Addon views: Base view automatically included if addon view's labels match
- Empty label list: Processes all configs (same as not specifying --labels)
- Whitespace in label IDs: Automatically trimmed

## Comparison to Previous --views Option

The `--labels` option is superior to the previous `--views` option because:

1. **Labels are more fundamental**: They're the actual mechanism that connects configs
2. **Simpler implementation**: No need to extract labels from views first
3. **More powerful**: Can filter configs before they're organized into views
4. **Better developer experience**: Labels are what developers work with directly in configs

## Future Enhancements

Potential improvements for future iterations:

1. **Architecture Filtering**: Add `--arches` to filter specific architectures
2. **Workload Filtering**: Add `--workloads` to process specific workloads directly
3. **Dry Run**: Add `--dry-run` to show what would be processed without running analysis
4. **Config Validation**: Warn if filtering results in zero configs to process
5. **Performance Metrics**: Report time/memory saved by filtering

## Git Branch

Branch: `feature/filter-by-labels`

```bash
# To use this feature:
git checkout feature/filter-by-labels

# To merge into your working branch:
git checkout your-branch
git merge feature/filter-by-labels
```

## Questions or Issues?

If you encounter any problems or have questions about this feature, please open an issue on the repository.
