"""Agent workspaces must not reach the gold commit or any task branch."""
import subprocess
from pathlib import Path

from scbench import harness


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)


def make_fork(tmp: Path) -> tuple[Path, str, str]:
    """A fork with base on main and the gold fix on fix/task, like oss-workbench/<lib>/src."""
    repo = tmp / "lib" / "src"
    repo.mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@t")
    git(repo, "config", "user.name", "t")
    (repo / "lib.cpp").write_text("int f() { return 1; }\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD").stdout.strip()
    git(repo, "switch", "-q", "-c", "fix/task")
    (repo / "lib.cpp").write_text("int f() { return 2; }  // the answer\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "t.cpp").write_text("hidden test\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fix: the answer")
    gold = git(repo, "rev-parse", "HEAD").stdout.strip()
    git(repo, "switch", "-q", "main")
    return repo, base, gold


def test_workspace_cannot_reach_gold(tmp_path):
    repo, base, gold = make_fork(tmp_path)
    snap, head = harness.snapshot_repo(repo, base, tmp_path / "wt" / "_snapshots")
    wt = tmp_path / "wt" / "run"
    harness.make_worktree(snap, head, wt)
    # same files as the base commit
    assert (wt / "lib.cpp").read_text() == "int f() { return 1; }\n"
    assert not (wt / "tests").exists()
    # one commit, no task branch, no gold object, no remote
    log = git(wt, "log", "--all", "--oneline").stdout.strip().splitlines()
    assert len(log) == 1 and "answer" not in log[0]
    assert git(wt, "cat-file", "-e", gold).returncode != 0
    assert git(wt, "cat-file", "-e", base).returncode != 0      # not even the fork's base id
    refs = git(wt, "for-each-ref", "--format=%(refname)").stdout
    assert "fix/" not in refs and "remotes" not in refs
    assert git(wt, "remote").stdout.strip() == ""
    assert "the answer" not in git(wt, "log", "--all", "-p").stdout
    harness.drop_worktree(snap, wt)
    assert not wt.exists()


def test_snapshot_is_reused(tmp_path):
    repo, base, _ = make_fork(tmp_path)
    a = harness.snapshot_repo(repo, base, tmp_path / "s")
    b = harness.snapshot_repo(repo, base, tmp_path / "s")
    assert a == b
