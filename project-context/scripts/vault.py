#!/usr/bin/env python3
"""Mechanical helper for the optional project-context remote vault.

Local-only project-context work must not call this script.
Only invoke it when the current user request explicitly asks for a
project memory vault / remote context store / pull / push / import.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


SECRET_PATTERNS = [
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github_pat", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b")),
    ("github_fine_grained_pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("private_key", re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----")),
    ("openai_like_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("assignment_secret", re.compile(
        r"(?i)\b(?:api[_-]?key|secret|token|password|passwd|private[_-]?key)\b\s*[:=]\s*['\"][^'\"]{8,}['\"]"
    )),
]

SKIP_SCAN_NAMES = {".git"}


def xdg_config_home() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))


def xdg_data_home() -> Path:
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))


def xdg_state_home() -> Path:
    return Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))


def default_config_path() -> Path:
    return xdg_config_home() / "opencode" / "project-context" / "config.yaml"


def default_vault_path() -> Path:
    return xdg_data_home() / "opencode" / "project-context" / "vault"


def default_state_path() -> Path:
    return xdg_state_home() / "opencode" / "project-context" / "state.yaml"


def eprint(*args) -> None:
    print(*args, file=sys.stderr)


def die(message: str, code: int = 1) -> None:
    eprint(message)
    raise SystemExit(code)


def run_git(args: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    result = subprocess.run(
        ["git", *args],
        cwd=str(cwd) if cwd else None,
        env=env,
        text=True,
        capture_output=True,
    )
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        die(f"git {' '.join(args)} 失败: {detail}")
    return result


def parse_simple_yaml(text: str) -> dict:
    root: dict = {}
    section: str | None = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" ") and line.endswith(":"):
            section = line[:-1].strip()
            root[section] = {}
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if section and line.startswith(" "):
            root[section][key] = value
        else:
            root[key] = value
            section = None
    return root


def dump_simple_yaml(data: dict) -> str:
    lines: list[str] = []
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for inner_key, inner_value in value.items():
                rendered = "" if inner_value is None else str(inner_value)
                lines.append(f"  {inner_key}: {rendered}")
        else:
            rendered = "" if value is None else str(value)
            lines.append(f"{key}: {rendered}")
    return "\n".join(lines) + "\n"


def load_yaml_file(path: Path) -> dict:
    if not path.exists():
        return {}
    return parse_simple_yaml(path.read_text(encoding="utf-8"))


def write_yaml_file(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_simple_yaml(data), encoding="utf-8")


def expand_path(value: str) -> Path:
    return Path(os.path.expanduser(value)).resolve()


def load_config(config_path: Path | None = None) -> dict:
    path = config_path or default_config_path()
    if not path.exists():
        die(
            "未找到远程记忆库配置。"
            "仅在用户显式要求远程记忆库时才应创建；"
            f"预期路径: {path}",
            4,
        )
    data = load_yaml_file(path)
    store = data.get("store") or {}
    if not isinstance(store, dict) or not store.get("remote"):
        die(f"配置无效：缺少 store.remote: {path}", 4)
    store.setdefault("type", "git")
    store.setdefault("local_path", str(default_vault_path()))
    store.setdefault("projects_prefix", "projects")
    sync = data.get("sync") or {}
    if not isinstance(sync, dict):
        sync = {}
    sync.setdefault("pull", "explicit")
    sync.setdefault("push", "explicit")
    sync.setdefault("conflict", "stop")
    data["store"] = store
    data["sync"] = sync
    data["_path"] = str(path)
    return data


def vault_path_from_config(config: dict) -> Path:
    return expand_path(config["store"]["local_path"])


def projects_prefix(config: dict) -> str:
    return str(config["store"].get("projects_prefix") or "projects").strip("/")


def normalize_remote_url(url: str) -> str:
    value = url.strip()
    if value.endswith(".git"):
        value = value[:-4]
    ssh_match = re.match(r"^git@([^:]+):(.+)$", value)
    if ssh_match:
        host, path = ssh_match.group(1), ssh_match.group(2)
        return f"{host.lower()}/{path.strip('/')}"
    ssh_scheme = re.match(r"^ssh://git@([^/]+)/(.+)$", value)
    if ssh_scheme:
        host, path = ssh_scheme.group(1), ssh_scheme.group(2)
        return f"{host.lower()}/{path.strip('/')}"
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"} and parsed.netloc and parsed.path:
        return f"{parsed.netloc.lower()}{parsed.path.rstrip('/')}"
    die(f"无法从 Git remote 推导项目 ID: {url}")
    raise AssertionError("unreachable")


def detect_project_id(project_root: Path) -> str:
    result = run_git(["remote", "get-url", "origin"], cwd=project_root, check=False)
    if result.returncode != 0:
        die(
            f"{project_root} 没有 origin remote。"
            "无 Git remote 的项目需要用户指定稳定 project_id。",
            4,
        )
    return normalize_remote_url(result.stdout.strip())


def project_context_src(project_root: Path) -> Path:
    return project_root / ".agent-context"


def project_vault_dir(config: dict, project_id: str) -> Path:
    return vault_path_from_config(config) / projects_prefix(config) / project_id / ".agent-context"


def iter_context_files(root: Path):
    if not root.exists():
        return
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_SCAN_NAMES for part in rel.parts):
            continue
        yield path, rel.as_posix()


def file_digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def manifest(root: Path) -> dict[str, str]:
    return {rel: file_digest(path) for path, rel in iter_context_files(root) or []}


def copy_context(src: Path, dst: Path) -> None:
    if not src.exists():
        die(f"源目录不存在: {src}")
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git"))


def scan_path(root: Path) -> list[tuple[str, str, int]]:
    hits: list[tuple[str, str, int]] = []
    for path, rel in iter_context_files(root) or []:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            die(f"拒绝同步二进制或非 UTF-8 文件: {rel}", 3)
        for line_no, line in enumerate(text.splitlines(), 1):
            for name, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    hits.append((rel, name, line_no))
    return hits


def print_scan_hits(hits: list[tuple[str, str, int]]) -> None:
    for rel, name, line_no in hits:
        print(f"{rel}:{line_no}: {name}")


def ensure_config(remote: str, config_path: Path | None = None, local_path: str | None = None) -> Path:
    path = config_path or default_config_path()
    if path.exists():
        existing = load_yaml_file(path)
        store = existing.get("store") or {}
        current_remote = store.get("remote")
        if current_remote and current_remote.rstrip("/") != remote.rstrip("/"):
            die(
                f"已存在配置 {path}，远程为 {current_remote}。"
                "不会覆盖；如需改用新仓库，请用户明确要求重配。",
                4,
            )
        print(f"已使用现有配置: {path}")
        return path
    data = {
        "store": {
            "type": "git",
            "remote": remote,
            "local_path": local_path or "~/.local/share/opencode/project-context/vault",
            "projects_prefix": "projects",
        },
        "sync": {
            "pull": "explicit",
            "push": "explicit",
            "conflict": "stop",
        },
    }
    write_yaml_file(path, data)
    print(f"已创建配置: {path}")
    return path


def vault_has_commits(vault: Path) -> bool:
    result = run_git(["rev-parse", "--verify", "HEAD"], cwd=vault, check=False)
    return result.returncode == 0


def ensure_vault(config: dict) -> Path:
    vault = vault_path_from_config(config)
    remote = config["store"]["remote"]
    if not vault.exists():
        vault.parent.mkdir(parents=True, exist_ok=True)
        run_git(["clone", remote, str(vault)])
        print(f"已克隆记忆库: {vault}")
    else:
        git_dir = vault / ".git"
        if not git_dir.exists():
            die(f"Vault 路径已存在但不是 Git 仓库: {vault}")
        run_git(["remote", "set-url", "origin", remote], cwd=vault, check=False)
        run_git(["fetch", "origin"], cwd=vault, check=False)
        print(f"已使用现有记忆库克隆: {vault}")
    if not vault_has_commits(vault):
        run_git(["checkout", "-B", "main"], cwd=vault, check=False)
    return vault


def default_vault_readme() -> str:
    return """# Agent Context Vault

这是私有的项目上下文记忆库，用来跨设备保存各项目被 gitignore 的 `.agent-context/` 工作副本。

- 这里不是业务代码仓库。
- 布局：`projects/<git-host>/<owner>/<repo>/.agent-context/`
- 不要写入令牌、私钥、密码或 `.env` 内容。
- 本机路径和同步状态不放进各个项目的 `.agent-context/`。
"""


def ensure_vault_readme(vault: Path) -> None:
    readme = vault / "README.md"
    if not readme.exists():
        readme.write_text(default_vault_readme(), encoding="utf-8")


def load_state_projects() -> dict[str, dict]:
    path = default_state_path()
    raw = load_yaml_file(path)
    projects: dict[str, dict] = {}
    for key, value in raw.items():
        if not key.startswith("project.") or not isinstance(value, dict):
            continue
        projects[key[len("project."):]] = value
    return projects


def update_project_state(project_id: str, commit: str, direction: str) -> None:
    path = default_state_path()
    raw = load_yaml_file(path)
    raw[f"project.{project_id}"] = {
        "last_sync_commit": commit,
        "last_sync_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "direction": direction,
    }
    write_yaml_file(path, raw)


def current_commit(vault: Path) -> str:
    result = run_git(["rev-parse", "HEAD"], cwd=vault)
    return result.stdout.strip()


def changed_files(left: dict[str, str], right: dict[str, str]) -> dict[str, str]:
    names = set(left) | set(right)
    diff: dict[str, str] = {}
    for name in sorted(names):
        lhash = left.get(name)
        rhash = right.get(name)
        if lhash == rhash:
            continue
        if lhash is None:
            diff[name] = "only_remote"
        elif rhash is None:
            diff[name] = "only_local"
        else:
            diff[name] = "both_changed"
    return diff


def print_diff(diff: dict[str, str]) -> None:
    if not diff:
        print("无差异")
        return
    for name, status in diff.items():
        print(f"{status}\t{name}")


def write_registry(config: dict, project_id: str, source_remote: str) -> None:
    vault = vault_path_from_config(config)
    registry_path = vault / "registry.yaml"
    existing = load_yaml_file(registry_path)
    existing[f"project.{project_id}"] = {
        "id": project_id,
        "source_remote": source_remote,
        "path": f"{projects_prefix(config)}/{project_id}/.agent-context",
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }
    write_yaml_file(registry_path, existing)


def source_remote_of(project_root: Path) -> str:
    result = run_git(["remote", "get-url", "origin"], cwd=project_root, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def ff_pull_vault(vault: Path) -> None:
    if not vault_has_commits(vault):
        return
    remote_head = run_git(["rev-parse", "--verify", "origin/HEAD"], cwd=vault, check=False)
    if remote_head.returncode != 0:
        # Try common branch names.
        for branch in ("main", "master"):
            probe = run_git(["rev-parse", "--verify", f"origin/{branch}"], cwd=vault, check=False)
            if probe.returncode == 0:
                run_git(["pull", "--ff-only", "origin", branch], cwd=vault)
                return
        return
    run_git(["pull", "--ff-only"], cwd=vault, check=False)


def cmd_ensure_config(args: argparse.Namespace) -> int:
    if not args.remote:
        die("ensure-config 需要 --remote", 4)
    ensure_config(args.remote, Path(args.config) if args.config else None, args.local_path)
    return 0


def cmd_ensure_vault(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config) if args.config else None)
    vault = ensure_vault(config)
    ensure_vault_readme(vault)
    print(vault)
    return 0


def cmd_project_id(args: argparse.Namespace) -> int:
    project_root = Path(args.project_root).resolve()
    print(detect_project_id(project_root))
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    hits = scan_path(root)
    if hits:
        print_scan_hits(hits)
        return 3
    print("未发现可识别的秘密凭据")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config) if args.config else None)
    ensure_vault(config)
    project_root = Path(args.project_root).resolve()
    project_id = args.project_id or detect_project_id(project_root)
    local = manifest(project_context_src(project_root))
    remote = manifest(project_vault_dir(config, project_id))
    diff = changed_files(local, remote)
    print(f"project_id: {project_id}")
    print_diff(diff)
    return 0 if not diff else 2


def cmd_status(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config) if args.config else None)
    vault = ensure_vault(config)
    project_root = Path(args.project_root).resolve()
    project_id = args.project_id or detect_project_id(project_root)
    local_dir = project_context_src(project_root)
    remote_dir = project_vault_dir(config, project_id)
    local = manifest(local_dir)
    remote = manifest(remote_dir)
    diff = changed_files(local, remote)
    state = load_state_projects().get(project_id, {})
    print(f"config: {config['_path']}")
    print(f"vault_remote: {config['store']['remote']}")
    print(f"vault_local: {vault}")
    print(f"project_id: {project_id}")
    print(f"local_context: {local_dir} ({'exists' if local_dir.exists() else 'missing'}, {len(local)} files)")
    print(f"vault_context: {remote_dir} ({'exists' if remote_dir.exists() else 'missing'}, {len(remote)} files)")
    print(f"last_sync_commit: {state.get('last_sync_commit') or '(none)'}")
    print(f"last_sync_at: {state.get('last_sync_at') or '(none)'}")
    print("diff:")
    print_diff(diff)
    return 0


def cmd_push(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config) if args.config else None)
    vault = ensure_vault(config)
    ensure_vault_readme(vault)
    ff_pull_vault(vault)
    project_root = Path(args.project_root).resolve()
    src = project_context_src(project_root)
    if not src.exists():
        die(f"当前项目没有 .agent-context/: {src}")
    project_id = args.project_id or detect_project_id(project_root)
    dst = project_vault_dir(config, project_id)
    hits = scan_path(src)
    if hits:
        print_scan_hits(hits)
        die("发现疑似秘密凭据，已拒绝推送。", 3)
    local = manifest(src)
    remote = manifest(dst)
    if local == remote and vault_has_commits(vault):
        print("远程已是当前项目上下文，无需推送")
        return 0
    copy_context(src, dst)
    write_registry(config, project_id, source_remote_of(project_root))
    rel_dir = f"{projects_prefix(config)}/{project_id}/.agent-context"
    run_git(["add", "--", rel_dir, "registry.yaml", "README.md"], cwd=vault)
    staged = run_git(["diff", "--cached", "--quiet"], cwd=vault, check=False)
    if staged.returncode == 0:
        print("没有可提交的上下文变化")
        return 0
    message = args.message or f"chore: import {project_id} agent context"
    run_git(["commit", "-m", message], cwd=vault)
    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=vault).stdout.strip() or "main"
    push = run_git(["push", "-u", "origin", branch], cwd=vault, check=False)
    if push.returncode != 0:
        die((push.stderr or push.stdout or "push 失败").strip())
    commit = current_commit(vault)
    update_project_state(project_id, commit, "push")
    print(f"已推送 {project_id}")
    print(f"vault_path: {rel_dir}")
    print(f"commit: {commit}")
    return 0


def cmd_pull(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config) if args.config else None)
    vault = ensure_vault(config)
    ff_pull_vault(vault)
    project_root = Path(args.project_root).resolve()
    project_id = args.project_id or detect_project_id(project_root)
    src = project_vault_dir(config, project_id)
    dst = project_context_src(project_root)
    if not src.exists():
        die(f"记忆库中没有该项目上下文: {project_id}", 4)
    local = manifest(dst)
    remote = manifest(src)
    if local and local != remote and not args.force:
        print("本地与记忆库不一致，已停止。差异：")
        print_diff(changed_files(local, remote))
        return 2
    hits = scan_path(src)
    if hits:
        print_scan_hits(hits)
        die("记忆库内容含疑似秘密凭据，已拒绝写入项目。", 3)
    copy_context(src, dst)
    if vault_has_commits(vault):
        update_project_state(project_id, current_commit(vault), "pull")
    print(f"已拉取 {project_id} 到 {dst}")
    return 0


def cmd_self_check(_args: argparse.Namespace) -> int:
    cases = {
        "https://github.com/KomeijiReimu/Komei-Agent.git": "github.com/KomeijiReimu/Komei-Agent",
        "git@github.com:KomeijiReimu/Komei-Agent.git": "github.com/KomeijiReimu/Komei-Agent",
        "ssh://git@github.com/KomeijiReimu/Komei-Agent.git": "github.com/KomeijiReimu/Komei-Agent",
        "https://gitlab.com/group/sub/repo": "gitlab.com/group/sub/repo",
    }
    failed = 0
    for url, expected in cases.items():
        got = normalize_remote_url(url)
        if got != expected:
            eprint(f"FAIL {url} -> {got} (expected {expected})")
            failed += 1
    sample = "token = \"not-a-real-secret-value-123\"\n不要记录 token、密码或用户数据。\n"
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "note.md"
        path.write_text(sample, encoding="utf-8")
        hits = scan_path(Path(tmp))
        names = {name for _, name, _ in hits}
        if "assignment_secret" not in names:
            eprint("FAIL expected assignment_secret hit")
            failed += 1
        if any(name != "assignment_secret" for name in names):
            eprint(f"FAIL unexpected scan hits: {names}")
            failed += 1
    if failed:
        die(f"self-check 失败: {failed}", 1)
    print("self-check ok")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Optional remote vault helper for project-context")
    parser.add_argument("--config", help="config.yaml path")
    sub = parser.add_subparsers(dest="command", required=True)

    ensure_config_p = sub.add_parser("ensure-config")
    ensure_config_p.add_argument("--remote", required=True)
    ensure_config_p.add_argument("--local-path")
    ensure_config_p.set_defaults(func=cmd_ensure_config)

    ensure_vault_p = sub.add_parser("ensure-vault")
    ensure_vault_p.set_defaults(func=cmd_ensure_vault)

    project_id_p = sub.add_parser("project-id")
    project_id_p.add_argument("--project-root", default=".")
    project_id_p.set_defaults(func=cmd_project_id)

    scan_p = sub.add_parser("scan")
    scan_p.add_argument("--path", required=True)
    scan_p.set_defaults(func=cmd_scan)

    diff_p = sub.add_parser("diff")
    diff_p.add_argument("--project-root", default=".")
    diff_p.add_argument("--project-id")
    diff_p.set_defaults(func=cmd_diff)

    status_p = sub.add_parser("status")
    status_p.add_argument("--project-root", default=".")
    status_p.add_argument("--project-id")
    status_p.set_defaults(func=cmd_status)

    push_p = sub.add_parser("push")
    push_p.add_argument("--project-root", default=".")
    push_p.add_argument("--project-id")
    push_p.add_argument("--message")
    push_p.set_defaults(func=cmd_push)

    pull_p = sub.add_parser("pull")
    pull_p.add_argument("--project-root", default=".")
    pull_p.add_argument("--project-id")
    pull_p.add_argument("--force", action="store_true")
    pull_p.set_defaults(func=cmd_pull)

    self_check_p = sub.add_parser("self-check")
    self_check_p.set_defaults(func=cmd_self_check)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
