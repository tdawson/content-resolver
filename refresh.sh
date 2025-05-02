#!/bin/bash

# This script runs the content_resolvere.py with the right configs and pushes out the results

### NOTE: Before running, create the dockerfile with
# podman build -t localhost/asamalik/fedora-env .

WORK_DIR=$(mktemp -d -t content-resolver-XXXXXXXXXX)
SAVE_DIR="/home/tdawson/tmp/cr"

if [[ ! "$WORK_DIR" || ! -d "$WORK_DIR" ]]; then
  echo "Could not create temp dir"
  exit 1
fi

mkdir -p $SAVE_DIR/{out,cache,history,logs}

cd $WORK_DIR

# Get the latest code repo and configs
#git clone https://github.com/minimization/content-resolver || exit 1
git clone -b package-json git@github.com:tdawson/content-resolver.git || exit 1
cd content-resolver || exit 1
#git clone https://github.com/minimization/content-resolver-input || exit 1

# Local output dir. Includes a dir for the history data, too.
mkdir -p $WORK_DIR/content-resolver/out/history || exit 1

# Get a copy of the historic data
# aws s3 sync s3://tiny.distro.builders/history $WORK_DIR/content-resolver/out/history --exclude "*" --include="historic_data*" || exit 1
# rsync -aH $SAVE_DIR/out/history $WORK_DIR/content-resolver/out/history --exclude "*" --include="historic_data*" || exit 1

# Get the root log cache
# (there's no exit one because that file might not exist)
# aws s3 cp s3://tiny.distro.builders/cache_root_log_deps.json $WORK_DIR/content-resolver/cache_root_log_deps.json
# cp $SAVE_DIR/out/cache_root_log_deps.json $WORK_DIR/content-resolver/cache_root_log_deps.json

# Build the site
build_started=$(date +"%Y-%m-%d-%H%M")
echo ""
echo "Building..."
echo "$build_started"
echo "(Logging into $SAVE_DIR/logs/$build_started.log)"
CMD="./content_resolver.py --dnf-cache-dir /dnf_cachedir test_configs out" || exit 1
podman run --rm -it --tmpfs /dnf_cachedir -v $WORK_DIR/content-resolver:/workspace:z localhost/asamalik/fedora-env $CMD > $SAVE_DIR/logs/$build_started.log || exit 1

# Save the root log cache
cp $WORK_DIR/content-resolver/cache_root_log_deps.json $WORK_DIR/content-resolver/out/cache_root_log_deps.json || exit 1

# Publish the site
# aws s3 sync --delete $WORK_DIR/content-resolver/out s3://tiny.distro.builders || exit 1
rsync -aH $WORK_DIR/content-resolver/out/ $SAVE_DIR/out/
