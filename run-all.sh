#!/bin/sh
# Rebuild every repo in repos/ from ~/src/freshsource-svn-repo/freshsource.
#   usage: run-all.sh [--no-readmes]	(stop before committing the READMEs)
set -eu
cd "$(dirname "$0")"
mkdir -p logs
xargs -P 2 -n 2 ./convert.sh < projects.txt
# Point freshsource-2.1.1 back at r218, before r220 nested a second copy in it.
./retarget-tags.py --apply freshsource:www/tags: freshsource-phorum:phorum/tags:
./graft-configuration.sh	# /configuration history (2002-2012) into freshsource
# Compare every commit, branch and tag with SVN before adding commits of our own.
if ! ./verify.py > logs/verify.log 2>&1; then
	echo "verify: refs differ from SVN; see logs/verify.log" >&2
	exit 1
fi
cat logs/verify.log
[ "${1:-}" = --no-readmes ] && exit 0
./add-readmes.sh		# README.md for each conversion
