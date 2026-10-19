# freshsource-phorum

Phorum 3.3.2c, as used by FreshSource in 2003, with the FreshSource headers,
footers and colours (`maestra0618/`). Dormant since 2003-06-17; kept for its
history.

## Conversion from Subversion

This repository was converted from `phorum` in the `freshsource` Subversion
repository (`svn+ssh://svn.int.unixathome.org/usr/local/svn/repos/freshsource`)
in October 2026, with git-svn. The conversion scripts are in
`~/src/freshsource-conversion/` (`run-all.sh` rebuilds everything).

| git | Subversion |
|---|---|
| `main` | `phorum/trunk` |
| `phorum_3_3_2c` | `phorum/tags/phorum_3_3_2c`, the vendor import (r105) |

Seven commits, 2003-04-28 to 2003-06-17 (r104-r120). Every commit keeps a
`git-svn-id:` trailer giving its Subversion path and revision; `dan` is mapped
to Dan Langille.

The site's Phorum configuration lived elsewhere, in
`configuration/trunk/phorum/` of the
[freshsource](https://github.com/FreshPorts/freshsource) repository.

### Verification

Every commit, `main` and the tag were compared file by file, executable bit
included, with an `svn export` of the matching SVN path and revision. All
matched. Empty directories were ignored.
