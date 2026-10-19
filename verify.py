#!/usr/bin/env python3
"""Compare every commit, branch and tag of the converted repos with SVN.

Each commit is checked against an `svn export` of the path and revision in its
git-svn-id trailer; each annotated tag against the SVN tag as it was when
created (from the git-svn-id in its annotation); each branch tip against its
SVN path at HEAD. The commits grafted in from /configuration hold their files
under configuration/trunk/, so only that subdirectory is compared for them.
Files and their contents must match, and so must the executable bit
(svn:executable). Empty directories, which git cannot store, are ignored.

usage: verify.py		exits 1 if anything differs
"""
import os, re, shutil, subprocess, sys, tempfile

GIT = '/opt/homebrew/bin/git'
SVN = '/opt/homebrew/bin/svn'
HERE = os.path.dirname(os.path.abspath(__file__))
SVNREPO = 'file://' + os.path.expanduser('~/src/freshsource-svn-repo/freshsource')
# git repo -> {branch: SVN path}
REPOS = {
    'freshsource': {'main': 'www/branches/git', 'trunk': 'www/trunk'},
    'freshsource-phorum': {'main': 'phorum/trunk'},
}
SVNID = re.compile(r'^git-svn-id: \S+/freshsource/(\S+)@(\d+) ', re.M)

def run(*args, **kw):
    return subprocess.run(args, check=True, capture_output=True, **kw).stdout

def git(repo, *args):
    return run(GIT, '-C', repo, *args, text=True)

def svn_tree(path, rev, dest):
    url = f'{SVNREPO}/{path}@{rev}'
    run(SVN, 'export', '-q', '--ignore-keywords', '--force', url, dest)
    execs = set()
    out = subprocess.run([SVN, 'propget', '-R', 'svn:executable', url],
                         capture_output=True, text=True).stdout
    prefix = f'{SVNREPO}/{path}/'
    for line in out.splitlines():
        m = re.match(r'(\S+) - ', line)
        if m and m.group(1).startswith(prefix):
            execs.add(m.group(1)[len(prefix):])
    return execs

def git_tree(repo, ref, sub, dest):
    os.makedirs(dest)
    if sub and subprocess.run([GIT, '-C', repo, 'rev-parse', '-q', '--verify', f'{ref}:{sub}'],
                              capture_output=True).returncode:
        return dest, set()		# r4: cvs2svn's empty trunk
    archive = subprocess.run([GIT, '-C', repo, 'archive', ref] + ([sub] if sub else []),
                             check=True, capture_output=True).stdout
    subprocess.run(['tar', '-x', '-C', dest], input=archive, check=True)
    execs = set()
    for line in git(repo, 'ls-tree', '-r', ref, *([sub] if sub else [])).splitlines():
        mode, _, _, name = line.split(None, 3)
        if mode == '100755':
            execs.add(name[len(sub) + 1:] if sub else name)
    return (os.path.join(dest, sub) if sub else dest), execs

def same(repo, ref, path, rev, sub=''):
    work = tempfile.mkdtemp(prefix='fs-verify.')
    try:
        s, g = os.path.join(work, 'svn'), os.path.join(work, 'git')
        sx = svn_tree(path, rev, s)
        os.makedirs(s, exist_ok=True)
        gdir, gx = git_tree(repo, ref, sub, g)
        os.makedirs(gdir, exist_ok=True)
        for d in (s, gdir):
            subprocess.run(['find', d, '-type', 'd', '-empty', '-delete'])
            os.makedirs(d, exist_ok=True)
        d = subprocess.run(['diff', '-rq', s, gdir], capture_output=True, text=True).stdout
        if sx != gx:
            d += f'executable: svn only {sorted(sx - gx)}, git only {sorted(gx - sx)}\n'
        return d.replace(work + '/', '')
    finally:
        shutil.rmtree(work)

bad = 0
for name, branches in REPOS.items():
    repo = os.path.join(HERE, 'repos', name)
    checks = []
    for line in git(repo, 'log', '--all', '--format=%H%x00%B%x01').split('\x01'):
        if not line.strip():
            continue
        h, body = line.strip().split('\x00', 1)
        m = SVNID.findall(body)
        if not m:
            if 'git-svn-id' not in body and 'README' in body:
                continue		# added after the conversion
            checks.append((f'commit {h[:9]}', None, None, None))
            continue
        path, rev = m[-1]
        sub = 'configuration/trunk' if path == 'configuration/trunk' else ''
        checks.append((f'commit {h[:9]} {path}@{rev}', h, path, rev, sub))
    for b, path in branches.items():
        checks.append((f'branch {b}', 'refs/heads/' + b, path, 'HEAD', ''))
    for t in git(repo, 'tag').split():
        m = SVNID.findall(git(repo, 'for-each-ref', '--format=%(contents)', 'refs/tags/' + t))
        if not m:
            checks.append((f'tag {t}', None, None, None))
            continue
        checks.append((f'tag {t} {m[-1][0]}@{m[-1][1]}', 'refs/tags/' + t, m[-1][0], m[-1][1], ''))
    ok = 0
    for what, ref, path, rev, *sub in checks:
        if ref is None:
            print(f'{name}: {what}: no git-svn-id'); bad += 1; continue
        d = same(repo, ref, path, rev, *sub)
        if d:
            print(f'{name}: {what} differs:\n  ' + d.strip().replace('\n', '\n  ')); bad += 1
        else:
            ok += 1
    print(f'{name}: {ok} ok of {len(checks)} '
          f'({sum(c[0].startswith("commit") for c in checks)} commits, '
          f'{len(branches)} branches, {sum(c[0].startswith("tag") for c in checks)} tags)')
sys.exit(1 if bad else 0)
