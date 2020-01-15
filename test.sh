#!/bin/bash

# Populate the 'expected' folder.
mkdir -p test/expected
cp -rf test/source/* test/expected
cp -rf test/patch/* test/expected

# Mount the filesystem.
mkdir -p test/mount
python patchfs.py test/source test/patch test/mount &
fs_pid="$!"

sleep 0.5

# Check that mount and expected are identical.
diff -r test/mount test/expected

rm -rf test/expected

kill "$fs_pid"