#!/usr/bin/env python3
"""Check the archive payload, skill metadata, Python syntax, and local links."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".audit"}
FORBIDDEN_NAMES = {".DS_Store", "project_memory.md", "status", "app-env.json"}


def candidate_files() -> list[Path]:
    if (ROOT / ".git").exists():
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=ROOT, capture_output=True, check=True,
        )
        return [ROOT / path for path in sorted(set(result.stdout.decode().split("\0"))) if path]
    return [
        path for path in sorted(ROOT.rglob("*"))
        if (path.is_file() or path.is_symlink())
        and not any(part in EXCLUDED_DIRS for part in path.relative_to(ROOT).parts)
    ]


def main() -> int:
    errors: list[str] = []
    manifest = json.loads((ROOT / "docs/archive-manifest.json").read_text())
    records = manifest["files"]
    paths = [row["path"] for row in records]
    if len(paths) != len(set(paths)):
        errors.append("Duplicate payload paths in manifest")
    expected = set(paths)
    candidates = candidate_files()
    actual = {
        p.relative_to(ROOT).as_posix() for p in candidates
        if p.relative_to(ROOT).parts[0] in {"skills", "references"}
    } | {"docs/guides/better-auth.md", "examples/app-env.example.json"}
    for path in sorted(actual ^ expected):
        errors.append(f"Payload/manifest mismatch: {path}")
    for row in records:
        path = ROOT / row["path"]
        if not path.is_file() or path.is_symlink():
            errors.append(f"Missing file or symlink: {row['path']}")
            continue
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != row["sha256"]:
            errors.append(f"Changed payload: {row['path']}")
        if row.get("public_git_blob"):
            blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            if blob != row["public_git_blob"]:
                errors.append(f"Public blob mismatch: {row['path']}")

    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if len(skills) != manifest["skill_count"]:
        errors.append("Skill count does not match manifest")
    for path in skills:
        text = path.read_text()
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            errors.append(f"Missing YAML frontmatter: {path.relative_to(ROOT)}")
            continue
        try:
            metadata = yaml.safe_load(text.split("---", 2)[1])
            valid = (
                isinstance(metadata, dict)
                and metadata.get("name") == path.parent.name
                and isinstance(metadata.get("description"), str)
                and bool(metadata["description"].strip())
            )
            if not valid:
                errors.append(f"Invalid skill metadata: {path.relative_to(ROOT)}")
        except yaml.YAMLError:
            errors.append(f"Invalid YAML: {path.relative_to(ROOT)}")

    python_count = 0
    link_count = 0
    file_count = 0
    for path in candidates:
        relative = path.relative_to(ROOT)
        if path.is_symlink():
            errors.append(f"Unexpected symlink: {relative}")
            continue
        if not path.is_file():
            continue
        file_count += 1
        if path.name in FORBIDDEN_NAMES or path.name.startswith((".env", "._")):
            errors.append(f"Excluded file present: {relative}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"Unexpected binary file: {relative}")
            continue
        if path.suffix == ".py":
            python_count += 1
            try:
                ast.parse(text, filename=str(relative))
            except SyntaxError:
                errors.append(f"Python syntax error: {relative}")
        if path.suffix != ".md":
            continue
        # Ignore code examples; host paths mentioned in code are not archive links.
        prose = re.sub(r"(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1[^\n]*$", "", text)
        for match in re.finditer(r"\[[^\]\n]+\]\(([^\s)]+)(?:\s+[^)]*)?\)", prose):
            target = match.group(1).strip("<>")
            url = urlsplit(target)
            if url.scheme or url.netloc or not url.path or url.path.startswith("/"):
                continue
            destination = (path.parent / unquote(url.path)).resolve()
            link_count += 1
            if not destination.is_relative_to(ROOT) or not destination.exists():
                errors.append(f"Broken relative link: {relative} -> {target}")

    example = json.loads((ROOT / "examples/app-env.example.json").read_text())
    if example != {"VITE_AUTH_ENABLED": "false"}:
        errors.append("Environment example differs from reviewed non-secret default")
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(
        f"PASS: {len(records)} payload hashes; {len(skills)} skills; "
        f"{python_count} Python files; {link_count} relative links; {file_count} text files."
    )
    print("Archive checks do not replace secret scanning or host runtime testing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
