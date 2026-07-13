import argparse
import sys
from collections.abc import Sequence

from app.api.scan import build_scan_result
from app.cli_format import exit_code_for_action, render_prompt_result, render_repository_result
from app.genai.safe_rewriter import rewrite_safe
from app.services.github_service import scan_repository
from app.services.policy_engine import apply_policy


POLICY_CHOICES = ("student", "developer", "company", "strict")


def scan_prompt_for_cli(text: str, policy_mode: str = "developer") -> dict:
    result = build_scan_result(text, "cli")
    decision = apply_policy(result, policy_mode)
    safe_text = ""
    if decision["requires_rewrite"]:
        safe_text = rewrite_safe(text, result["entities"])["safe_text"]
    return {
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "category": result["category"],
        "entities": result["entities"],
        "injection_detected": result["injection_detected"],
        "explanation": result["explanation"],
        "safe_text": safe_text,
        "policy_decision": decision,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shadowai",
        description="Local-first prompt, repository, and secret leak protection.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("info", help="Show local capabilities and commands")

    prompt = subparsers.add_parser("prompt", help="Inspect text for secrets and injection")
    prompt.add_argument("text")
    prompt.add_argument("--policy", choices=POLICY_CHOICES, default="developer")
    prompt.add_argument("--json", action="store_true")

    repository = subparsers.add_parser("repo", help="Scan a public GitHub repository")
    repository.add_argument("url")
    repository.add_argument("--json", action="store_true")

    watch = subparsers.add_parser("watch", help="Monitor an explicitly mounted folder")
    watch.add_argument("path")

    hooks = subparsers.add_parser("install-hooks", help="Protect a mounted Git repository")
    hooks.add_argument("path")

    monitor = subparsers.add_parser("monitor-repo", help="Periodically rescan a public GitHub repository")
    monitor.add_argument("url")
    monitor.add_argument("--interval", type=int, default=300)

    git_check = subparsers.add_parser("git-check", help=argparse.SUPPRESS)
    git_check.add_argument("mode", choices=("staged", "push"))
    git_check.add_argument("--repo", required=True)
    git_check.add_argument("--remote", default="origin")
    return parser


def print_info() -> None:
    print(
        """ShadowAI Guardian - Local AI and secret leak protection

Commands:
  info                              Show this information
  prompt TEXT [--policy MODE]       Scan prompt/text locally
  repo GITHUB_URL                   Scan a public GitHub repository
  watch PATH                        Monitor an explicitly mounted folder
  install-hooks PATH                Add pre-commit/pre-push protection
  monitor-repo URL [--interval N]   Rescan an approved public repository

Policy modes: student, developer, company, strict
Core scanning works locally. Optional NVIDIA enhancement is disabled without a key.
Only redacted secret findings are printed."""
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    command = args.command or "info"
    try:
        if command == "info":
            print_info()
            return 0
        if command == "prompt":
            result = scan_prompt_for_cli(args.text, args.policy)
            print(render_prompt_result(result, as_json=args.json))
            return exit_code_for_action(result["policy_decision"]["action"])
        if command == "repo":
            result = scan_repository(args.url)
            print(render_repository_result(result, as_json=args.json))
            return 2 if result["risk_level"] in {"High", "Critical"} else 1 if result["risk_score"] else 0
        if command == "watch":
            from app.live_guard import watch_directory

            return watch_directory(args.path)
        if command == "install-hooks":
            from app.git_guard import install_hooks

            result = install_hooks(args.path)
            print(result["message"])
            return 0
        if command == "monitor-repo":
            from app.repo_monitor import monitor_repository

            return monitor_repository(args.url, args.interval)
        if command == "git-check":
            from app.git_guard import render_git_findings, scan_outgoing, scan_staged

            if args.mode == "staged":
                findings = scan_staged(args.repo)
            else:
                findings = []
                for line in sys.stdin:
                    fields = line.split()
                    if len(fields) >= 4:
                        findings.extend(
                            scan_outgoing(args.repo, args.remote, fields[3], fields[1])
                        )
            print(render_git_findings(findings))
            return 2 if any(item["blocking"] for item in findings) else 0
        parser.error(f"Unknown command: {command}")
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ShadowAI error: {exc}", file=sys.stderr)
        return 3
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
