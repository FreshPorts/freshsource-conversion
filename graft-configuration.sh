#!/bin/sh
# Give freshsource the history of /configuration from before 2017. In r175
# (2017-11-03) the top-level /configuration project was copied, with its own
# trunk/branches/tags, into www/trunk/configuration and then deleted; r176
# flattened configuration/trunk into configuration/. git-svn does not follow a
# copy into a subdirectory, so in freshsource those files first appear at r175.
#
# This converts /configuration (r4-r174) on its own, moves its files under
# configuration/trunk/ as they were at r175, and makes the r175 commit a merge
# of www/trunk and that history. Run after convert.sh and retarget-tags.py;
# the ungrafted repo is kept in repos/.pre-graft/freshsource.
set -eu
PATH=/opt/homebrew/bin:$PATH
HERE=$(cd "$(dirname "$0")" && pwd)
SVNREPO=file://$HOME/src/freshsource-svn-repo/freshsource
REWRITE_ROOT=svn+ssh://svn.int.unixathome.org/usr/local/svn/repos/freshsource
R=$HERE/repos/freshsource
C=$HERE/repos/.configuration
GRAFT_SVN='/www/trunk@175 '

# /configuration, as a repository of its own
rm -rf "$C"
mkdir -p "$C"
git -C "$C" init -q -b main
# /configuration was deleted in r175, so name it at r174 and stop there.
git -C "$C" svn init --prefix=svn/ --rewrite-root="$REWRITE_ROOT" -T trunk "$SVNREPO/configuration" >/dev/null 2>&1
git -C "$C" config svn.authorsfile "$HERE/authors.txt"
git -C "$C" svn fetch -q -r 1:174 >> "$HERE/logs/configuration.fetch.log" 2>&1
git -C "$C" update-ref refs/heads/main refs/remotes/svn/trunk
git -C "$C" for-each-ref --format='%(refname)' refs/remotes | xargs -n1 git -C "$C" update-ref -d
git -C "$C" filter-repo --quiet --force --to-subdirectory-filter configuration/trunk
echo "configuration: $(git -C "$C" rev-list --count main) commits, $(git -C "$C" log -1 --format='%ad %s' --date=short main)"

mkdir -p "$HERE/repos/.pre-graft"
rm -rf "$HERE/repos/.pre-graft/freshsource"
cp -Rp "$R" "$HERE/repos/.pre-graft/freshsource"

git -C "$R" fetch -q --no-tags "$C" "+refs/heads/main:refs/graft/configuration"
conftip=$(git -C "$R" rev-parse refs/graft/configuration)
merge=$(git -C "$R" log --format=%H --grep="freshsource$GRAFT_SVN" -F main | head -1)
[ -n "$merge" ] || { echo "freshsource: r175 commit not found" >&2; exit 1; }
parents=$(git -C "$R" rev-list --parents -n1 "$merge" | cut -d' ' -f2-)
[ "$(echo "$parents" | wc -w)" -eq 1 ] || { echo "freshsource: r175 has parents: $parents" >&2; exit 1; }
# The r175 tree must hold exactly what /configuration had at r174.
[ "$(git -C "$R" rev-parse "$merge:configuration/trunk")" = "$(git -C "$R" rev-parse "$conftip:configuration/trunk")" ] ||
	{ echo "freshsource: configuration/trunk at r175 differs from /configuration/trunk@174" >&2; exit 1; }
git -C "$R" replace --graft "$merge" $parents "$conftip"
git -C "$R" update-ref -d refs/graft/configuration
# filter-repo writes the replacement into real history and drops the replace
# ref; every commit from r175 on gets a new hash, and tags follow.
git -C "$R" filter-repo --quiet --force --replace-refs delete-no-add
git -C "$R" reflog expire --expire=now --all
git -C "$R" gc -q --prune=now
rm -rf "$C"
echo "freshsource: r175 now merges $(git -C "$R" log -1 --format='%h %ad %s' --date=short "$conftip" 2>/dev/null || echo "$conftip")"
