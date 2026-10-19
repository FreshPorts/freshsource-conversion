# freshsource-conversion

The scripts that convert the FreshSource Subversion repository, `freshsource`
(r273, 2024-07-02), to git: one repository per project, with full history,
branches and tags. Adapted from the freshports-1 conversion in
`~/src/freshports/git-conversion`.

| Repository | From Subversion | Notes |
|---|---|---|
| `freshsource` | `www` | `branches/git` is `main`; pre-2017 `/configuration` history grafted in |
| `freshsource-phorum` | `phorum` | dormant since 2003 |

Each has a README describing its conversion, in `readmes/`.

## Requirements

- The Subversion repository itself at `~/src/freshsource-svn-repo/freshsource`.
- git, git-svn, git-filter-repo, Subversion, Python 3 and gh, in
  `/opt/homebrew/bin`.

## Running it

```sh
./run-all.sh                # everything, including the README commits
./run-all.sh --no-readmes   # stop after verification
```

Output goes to `repos/`, logs to `logs/`. It takes under a minute.

| Script | What it does |
|---|---|
| `convert.sh` | git-svn conversion of each project in `projects.txt`, with `authors.txt`; `branches/git` becomes `main` |
| `prune-deleted-tags.sh` | (called by `convert.sh`) drops tags deleted in SVN (`freshsource-git-2.0.0`) |
| `retarget-tags.py` | points `freshsource-2.1.1` back at r218, before r220 nested a second copy in it |
| `graft-configuration.sh` | converts `/configuration` (r4-r174) and makes the r175 commit a merge of it |
| `verify.py` | compares every commit, branch and tag with `svn export`, executable bit included |
| `add-readmes.sh` | commits `readmes/<repo>/README.md` |

## Publishing

```sh
./push-to-github.sh
```

Creates `FreshPorts/freshsource` and `FreshPorts/freshsource-phorum` as
private repositories and pushes every branch and tag. It skips any repository
that already exists on GitHub, or that already has an `origin`.
