# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running Content Resolver
```bash
# Main execution - analyze package dependencies and generate static website
./content_resolver.py <config_dir> <output_dir>

# Example with test configs for development
./content_resolver.py test_configs output

# Use cached data (faster for development, requires existing cache files)
./content_resolver.py --use-cache test_configs output

# Development mode with fake buildroot (faster analysis)
./content_resolver.py --dev-buildroot test_configs output

# Override DNF cache directory
./content_resolver.py --dnf-cache-dir /path/to/cache test_configs output

# Enable parallel root.log processing (faster, uses more memory/CPU)
./content_resolver.py --parallel-root-logs test_configs output
```

### Container-based Development
```bash
# Build container environment
podman build . -t content-resolver-env

# Run in container (Fedora/Linux)
podman run --rm -it --cap-add CAP_SYS_CHROOT --tmpfs /dnf_cachedir -v $(pwd):/workspace:z content-resolver-env bash

# Run in container (macOS with Docker)
docker run --rm -it --tmpfs /dnf_cachedir -v $(pwd):/workspace content-resolver-env bash

# Inside container - create output directory and run
mkdir -p output/history
./content_resolver.py --dev-buildroot --dnf-cache-dir /dnf_cachedir test_configs output

# With parallel root.log processing enabled
./content_resolver.py --dev-buildroot --parallel-root-logs --dnf-cache-dir /dnf_cachedir test_configs output
```

### Testing
```bash
# Test configuration file validation
python3 test_config_files.py

# Run basic functionality test
python3 test.py

# Test feedback pipeline
python3 test_feedback_pipeline.py

# Test root log functionality
python3 test_root_log_function.py
```

## Architecture

Content Resolver is a Python-based tool that analyzes RPM package dependencies for Linux distributions, particularly focused on Fedora and RHEL ecosystems.

### Core Components

**Main Entry Point**: `content_resolver.py` - Orchestrates the entire analysis pipeline:
1. **Data Collection Stage**: Uses `Analyzer` to resolve package dependencies via DNF
2. **Page Generation Stage**: Uses `Query` and page generation modules to create static HTML output

**Core Modules** (in `content_resolver/` package):
- **`analyzer.py`**: Heart of dependency resolution using DNF, handles multiprocessing and async analysis
- **`config_manager.py`**: Parses command-line arguments and loads YAML configuration files  
- **`query.py`**: Query interface for accessing resolved data during page generation
- **`page_generation.py`**: Generates static HTML pages using Jinja2 templates
- **`data_generation.py`**: Creates JSON data files for consumption by other tools
- **`historia_data.py`**: Manages historical data tracking across builds

### Key Concepts

**Workloads**: Package sets with specific purposes (applications, runtimes, dependencies)
- Required Packages: User-defined
- Dependencies: Resolved by Content Resolver via DNF

**Environments**: Base environments where workloads run (container images, cloud images)
- Similar structure to workloads (required packages + resolved dependencies)
- Workloads are resolved on top of environments

**Views**: Advanced concept combining multiple workloads, primarily used for Fedora ELN
- Can resolve build dependencies
- Show detailed package presence reasons
- Track unwanted packages
- Provide maintainer recommendations

**Labels**: Connect workloads to environments and repositories with matching labels

**Repositories**: Package sources used for dependency resolution

### Data Flow

1. **Configuration Loading**: YAML files define repos, environments, workloads, labels, and views
2. **Dependency Analysis**: DNF-based resolution using temporary installroots and cache directories
3. **Multiprocessing**: Async processing with configurable subprocess limits
4. **Static Generation**: HTML pages and JSON data files output to specified directory

### Dependencies

Runtime dependencies (installed via DNF in container):
- `python3-jinja2` - Template engine for HTML generation
- `python3-koji` - Koji build system integration  
- `python3-yaml` - YAML configuration file parsing
- `python3-dnf` - Package dependency resolution

The tool is designed to run in a Fedora container environment with proper DNF and repository access.