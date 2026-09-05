# Verification and privacy checks

This is a static skill/documentation archive with five existing Python asset tools. It has no application build, hosted UI, or included Grok runtime.

## Reproduce the archive checks

From a clean checkout, with Python 3.12 or later:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/validate_archive.py
.venv/bin/python scripts/smoke_assets.py
```

The validator checks payload SHA-256 hashes, the public snapshot's Git blob identifiers, all 18 skill frontmatter records, Python syntax, local Markdown link destinations, the absence of excluded file types, and the non-secret environment example. It does not execute Markdown code samples or contact a provider. URL fragment anchors and external link availability are not covered by its local-link check.

In a Git checkout, it checks tracked and unignored candidate files. Ignored local artifacts such as a virtual environment or Finder metadata are not publication candidates; force-tracking an excluded file makes it visible to the validator.

The smoke check starts all five archived CLIs and uses synthetic images to verify layout dimensions, sprite frame extraction and alpha, prop extraction, and map composition. Its temporary inputs and outputs are removed on completion. Video extraction is not exercised; `video2dsprite` receives an entry-point check only.

## Secret and history scanning

With Gitleaks installed, scan both the working tree and the full reachable history:

```bash
gitleaks dir . --redact --no-banner
gitleaks git . --log-opts="--all" --redact --no-banner
```

Review findings rather than automatically allowlisting matches. The manifest and validator are integrity checks, not secret detectors. Also inspect Git commit identity, filenames, symlinks, binary files, absolute personal paths, contact details, embedded credentials, and all refs before publishing.

The public payload excludes project memory, runtime status, live configuration, macOS metadata, source history, and generated output. Environment variable names such as `XAI_API_KEY` and `DATABASE_URL`, generic `/workspace` paths, localhost URLs, and public platform endpoints are intentional technical documentation; they are not credential values or personal paths.

The archive's original platform instructions have not been validated against a live Grok-hosted app. Their security, provider, browser, authentication, and deployment claims remain dependent on the matching platform version. Provider image/video generation is outside the local verification scope.

## Preparation results

Checked September 5, 2026, using Python 3.12.8 and the pinned dependencies:

- 88 payload hashes verified, including 85 exact matches to the public source snapshot.
- All 18 skill metadata records parsed successfully.
- Seven Python files passed syntax parsing: five archived tools and two archive checks.
- All 64 relative Markdown link destinations resolved.
- All five archived Python command-line entry points accepted `--help`.
- Synthetic layout, sprite alpha/frame extraction, prop extraction, and map composition checks passed.
- Gitleaks 8.30.1 reported zero credential findings in the candidate tree.
- Additional candidate inspection found no personal home-directory paths, private contact details, credential-bearing URLs, unrelated personal project identifiers, or symlinks.

These are bounded checks, not a guarantee that an automated scanner can recognize every possible secret. A fresh Git history is used for publication, with a public GitHub noreply commit identity. Reachable-history and clean-clone checks are required for the final candidate as described above.
