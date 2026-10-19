# freshsource

The FreshSource website (www.freshsource.org).

## Conversion from Subversion

This repository was converted from `www` in the `freshsource` Subversion
repository (`svn+ssh://svn.int.unixathome.org/usr/local/svn/repos/freshsource`)
in October 2026, with git-svn. The conversion scripts are in
`~/src/freshsource-conversion/` (`run-all.sh` rebuilds everything).

### Layout

| git | Subversion |
|---|---|
| `main` | `www/branches/git`, where all work since January 2021 happened |
| `trunk` | `www/trunk`, last changed 2021-04-01 (r225) |
| tags | `www/tags/*` |

History starts on 2002-06-19 (via cvs2svn) and runs to r273 (2024-07-02).

Every converted commit keeps a `git-svn-id:` trailer giving its Subversion
path and revision, so `r1234` references still resolve. SVN usernames are
mapped to names and email addresses (`dan`/`dvl` → Dan Langille). Each tag is
annotated with the author, date and message of the SVN revision that created
it, and points at the commit it was copied from.

### configuration/

Until r175 (2017-11-03), `configuration` was a project of its own at the top
of the SVN repository. r175 copied it into `www/trunk/configuration` and r176
flattened it. git-svn does not follow a copy into a subdirectory, so its
earlier history (21 commits, 2002-2012, r4-r170) was converted separately and
joined in: the r175 commit is a merge whose second parent is that history,
with its files under `configuration/trunk/` as r175 had them. `git log --
configuration/vhosts.conf.sample` goes back to 2002.

### Tags

- `freshsource-git-2.0.0` is not here: it was renamed to `freshsource-2.0.0`
  in r208.
- `freshsource-2.1.1` points at r218, where it was created. r220 accidentally
  copied `branches/git` into it a second time, as `tags/freshsource-2.1.1/git/`;
  that copy is not in the tag.

### Verification

Every commit was compared file by file, executable bit included, with an
`svn export` of the path and revision in its `git-svn-id`; every tag with its
SVN tag as created; and `main` and `trunk` with `www/branches/git` and
`www/trunk` at HEAD. All matched. Empty directories, which git cannot store,
were ignored.

### Not converted

- `svn:ignore` properties (only `include/`, ignoring `.cvsignore` and
  `common.php`); there is no `.gitignore`.
- The 2003 `phorum` project, which is in
  [freshsource-phorum](https://github.com/FreshPorts/freshsource-phorum).
