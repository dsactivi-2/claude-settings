#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import pathlib
import re
import socket
import subprocess
import sys
import uuid


HOME = pathlib.Path("/Users/dsselmanovic")
CONFIG_PATH = HOME / ".claude" / "workflow" / "config.json"


def load_config():
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def ensure_dir(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def iso_now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def run_git(args, cwd):
    try:
        cp = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return ""
    if cp.returncode != 0:
        return ""
    return cp.stdout.strip()


def detect_repo_info(cwd):
    cwd = pathlib.Path(cwd)
    repo_root = run_git(["rev-parse", "--show-toplevel"], cwd)
    if not repo_root:
        return {
            "cwd": str(cwd),
            "repo_root": "",
            "repo_name": "",
            "branch": "",
            "ticket_id": detect_ticket_id("", os.environ),
            "changed_files": [],
        }
    repo_root_path = pathlib.Path(repo_root)
    branch = run_git(["branch", "--show-current"], repo_root_path)
    changed = run_git(["status", "--short"], repo_root_path).splitlines()
    changed_files = []
    for line in changed:
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            changed_files.append(parts[1])
    return {
        "cwd": str(cwd),
        "repo_root": repo_root,
        "repo_name": repo_root_path.name,
        "branch": branch,
        "ticket_id": detect_ticket_id(branch, os.environ),
        "changed_files": changed_files[:20],
    }


def detect_ticket_id(branch, env):
    for key in ("WORKFLOW_TICKET_ID", "LINEAR_TICKET_ID"):
        value = env.get(key, "").strip()
        if value:
            return value
    match = re.search(r"\b([A-Z][A-Z0-9]+-\d+)\b", branch or "")
    return match.group(1) if match else ""


def write_json(path, payload):
    with pathlib.Path(path).open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")


def append_jsonl(path, payload):
    with pathlib.Path(path).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=True) + "\n")


def load_state(config):
    state_path = pathlib.Path(config["state_dir"]) / "current-session.json"
    if not state_path.exists():
        return {}
    with state_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_state(config, payload):
    ensure_dir(config["state_dir"])
    write_json(pathlib.Path(config["state_dir"]) / "current-session.json", payload)


def daily_note_path(config, day=None):
    day = day or dt.date.today().isoformat()
    return pathlib.Path(config["vault_dir"]) / config["daily_dir_name"] / f"{day}.md"


def ticket_note_path(config, ticket_id):
    safe = ticket_id if ticket_id else "UNASSIGNED"
    return pathlib.Path(config["vault_dir"]) / config["tickets_dir_name"] / f"{safe}.md"


def ensure_vault(config):
    vault = pathlib.Path(config["vault_dir"])
    ensure_dir(vault)
    for key in (
        "daily_dir_name",
        "tickets_dir_name",
        "projects_dir_name",
        "decisions_dir_name",
        "logs_dir_name",
    ):
        ensure_dir(vault / config[key])
    ensure_dir(config["events_dir"])
    ensure_dir(config["state_dir"])


def append_unique_line(path, line):
    path = pathlib.Path(path)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if line in existing:
        return
    with path.open("a", encoding="utf-8") as fh:
        if existing and not existing.endswith("\n"):
            fh.write("\n")
        fh.write(line + "\n")


def create_daily_if_missing(config, session):
    path = daily_note_path(config)
    if path.exists():
        return path
    repo_name = session.get("repo_name") or config["default_project"]
    content = [
        f"# {dt.date.today().isoformat()}",
        "",
        "## Focus",
        "",
        "## Tickets",
        f"- {session.get('ticket_id') or 'UNASSIGNED'}",
        "",
        "## Sessions",
        "",
        "## Notes",
        "",
    ]
    path.write_text("\n".join(content) + "\n", encoding="utf-8")
    append_unique_line(
        path,
        f"- project: `{repo_name}` | branch: `{session.get('branch') or 'n/a'}`",
    )
    return path


def create_ticket_if_missing(config, session):
    ticket_id = session.get("ticket_id") or "UNASSIGNED"
    path = ticket_note_path(config, ticket_id)
    if path.exists():
        return path
    content = [
        "---",
        f"ticket_id: {ticket_id}",
        f"status: {'active' if ticket_id != 'UNASSIGNED' else 'unassigned'}",
        f"repo: {session.get('repo_name') or config['default_project']}",
        f"branch: {session.get('branch') or ''}",
        f"updated_at: {dt.date.today().isoformat()}",
        "---",
        "",
        f"# {ticket_id}",
        "",
        "## Ziel",
        "",
        "## Akzeptanzkriterien",
        "",
        "## Arbeitslog",
        "",
    ]
    path.write_text("\n".join(content) + "\n", encoding="utf-8")
    return path


def record_event(config, kind, payload):
    ensure_dir(config["events_dir"])
    append_jsonl(
        pathlib.Path(config["events_dir"]) / "events.jsonl",
        {
            "ts": iso_now(),
            "kind": kind,
            "host": socket.gethostname(),
            **payload,
        },
    )


def cmd_init(args):
    config = load_config()
    ensure_vault(config)
    state = {
        "session_id": "",
        "started_at": "",
        **detect_repo_info(os.getcwd()),
    }
    save_state(config, state)
    create_daily_if_missing(config, state)
    print(json.dumps({"status": "ok", "vault_dir": config["vault_dir"]}, indent=2))


def cmd_session_start(args):
    config = load_config()
    ensure_vault(config)
    repo = detect_repo_info(os.getcwd())
    session = {
        "session_id": str(uuid.uuid4()),
        "started_at": iso_now(),
        "last_seen_at": iso_now(),
        **repo,
    }
    save_state(config, session)
    create_daily_if_missing(config, session)
    create_ticket_if_missing(config, session)
    record_event(config, "session_start", session)
    append_unique_line(
        daily_note_path(config),
        f"- {dt.datetime.now().strftime('%H:%M')} start `{session['repo_name'] or 'no-repo'}` ticket `{session['ticket_id'] or 'UNASSIGNED'}`",
    )
    print(json.dumps(session, indent=2))


def cmd_snapshot(args):
    config = load_config()
    ensure_vault(config)
    current = load_state(config)
    repo = detect_repo_info(os.getcwd())
    merged = {**current, **repo, "last_seen_at": iso_now()}
    if not merged.get("session_id"):
        merged["session_id"] = str(uuid.uuid4())
        merged["started_at"] = iso_now()
    save_state(config, merged)
    record_event(config, "snapshot", {"reason": args.reason, **merged})
    print(json.dumps(merged, indent=2))


def cmd_session_stop(args):
    config = load_config()
    ensure_vault(config)
    current = load_state(config)
    if not current:
        print(json.dumps({"status": "no-active-session"}, indent=2))
        return
    current["stopped_at"] = iso_now()
    record_event(config, "session_stop", current)
    append_unique_line(
        daily_note_path(config),
        f"- {dt.datetime.now().strftime('%H:%M')} stop `{current.get('repo_name') or 'no-repo'}` files `{len(current.get('changed_files') or [])}`",
    )
    save_state(config, {})
    print(json.dumps(current, indent=2))


def cmd_daily(args):
    config = load_config()
    ensure_vault(config)
    state = load_state(config) or detect_repo_info(os.getcwd())
    path = create_daily_if_missing(config, state)
    create_ticket_if_missing(config, state)
    print(str(path))


def cmd_status(args):
    config = load_config()
    ensure_vault(config)
    state = load_state(config)
    if not state:
        state = detect_repo_info(os.getcwd())
    payload = {
        "config": config,
        "state": state,
        "today_note": str(daily_note_path(config)),
    }
    print(json.dumps(payload, indent=2))


def build_parser():
    parser = argparse.ArgumentParser(description="Local workflow sync agent")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init")
    sub.add_parser("session-start")

    snapshot = sub.add_parser("snapshot")
    snapshot.add_argument("--reason", default="manual")

    sub.add_parser("session-stop")
    sub.add_parser("daily")
    sub.add_parser("status")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    dispatch = {
        "init": cmd_init,
        "session-start": cmd_session_start,
        "snapshot": cmd_snapshot,
        "session-stop": cmd_session_stop,
        "daily": cmd_daily,
        "status": cmd_status,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
