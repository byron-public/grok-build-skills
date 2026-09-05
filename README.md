# Grok Build Skills

**Grok Build’s own agent skills and platform references**, collected directly from the Grok Build app-builder environment and preserved here for browsing and study. The collection contains **18 skills**, their supporting references, and five Python tools for game-asset processing.

The collection brings platform-specific implementation details together in a browsable library: design rules, game-control checks, sprite pipelines, authentication, database wiring, deployment behavior, and more.

**Start with:** [Design & UI](skills/design-ui/SKILL.md) · [Building Games](skills/building-games/SKILL.md) · [Controls](skills/controls/SKILL.md) · [Game Asset Core](skills/game-asset-core/SKILL.md)

## Behind the platform

These are detailed instructions aimed at an app-building agent operating inside a particular Grok template. They expose the working assumptions behind that environment, including preview bridges, injected configuration, authentication flows, and deployment contracts.

The skills come from Grok Build; this repository is a mirror maintained by `byron-public`. The bundle also includes third-party material used by Grok Build, with its original source and license notices preserved.

These platform instructions are normally encountered inside Grok-generated projects. This repository brings them together as a focused, browsable skill library. A September 5, 2026 comparison confirmed that all 85 original skill and platform-reference files match an existing public `.grok` snapshot byte for byte.

See [provenance and public-source evidence](docs/provenance.md) for the exact snapshot and comparison method.

## What is worth exploring

- **Interface design:** `design-ui` connects typography, surfaces, layout, motion, and performance into a coherent design workflow. It is a useful starting point for dashboards and application screens.
- **Browser games:** `building-games` covers timing, physics, cameras, audio, persistence, and genre-specific implementation. Pair it with `controls` for movement, steering, flight, and inverted-input checks.
- **Game art:** `game-asset-core` and its specialists describe dimensions, visual consistency, transparency, animation, and inspection. The sprite and map packages add executable post-processing tools.
- **Platform implementation:** `auth`, `neon`, `xai-api`, `og`, and `multiplayer-p2p` document how applications fit the Grok-hosted environment. Their assumptions need checking before reuse elsewhere.

## Skill index

| Area | Skills | Focus |
| --- | --- | --- |
| Interface design | [design-ui](skills/design-ui/SKILL.md) | Design systems, typography, surfaces, motion, and layout |
| Browser games and 3D | [building-games](skills/building-games/SKILL.md), [controls](skills/controls/SKILL.md), [threejs](skills/threejs/SKILL.md) | Game loops, physics, cameras, movement checks, engines, and Three.js/TSL |
| Game-art direction | [game-asset-core](skills/game-asset-core/SKILL.md), [game-character-consistency](skills/game-character-consistency/SKILL.md), [game-animation-frames](skills/game-animation-frames/SKILL.md), [game-tilesets](skills/game-tilesets/SKILL.md), [game-ui-icons](skills/game-ui-icons/SKILL.md) | Asset specifications, character identity, animation, terrain, and UI art |
| Asset-generation pipelines | [imagine](skills/imagine/SKILL.md), [generate2dsprite](skills/generate2dsprite/SKILL.md), [generate2dmap](skills/generate2dmap/SKILL.md), [video2dsprite](skills/video2dsprite/SKILL.md) | Image/video tools, sprite processing, layered maps, and prop extraction |
| Application services | [auth](skills/auth/SKILL.md), [neon](skills/neon/SKILL.md), [xai-api](skills/xai-api/SKILL.md), [multiplayer-p2p](skills/multiplayer-p2p/SKILL.md) | Sign-in, sessions, per-user data, Postgres, Grok APIs, and WebRTC |
| App identity and sharing | [og](skills/og/SKILL.md) | Share cards, favicons, PWA icons, and Grok metadata |

## Repository layout

| Folder | Contents |
| --- | --- |
| [skills/](skills/) | The 18 original skill packages, including their references, tools, and notices |
| [references/](references/) | Original platform guidance for scaffolding, browser QA, generated art, data/auth, deployment, and workspace revival |
| [docs/](docs/index.md) | Provenance, verification, and supplementary guides |
| [examples/](examples/) | Non-secret configuration examples |
| [scripts/](scripts/) | Archive integrity and local smoke checks |

Additional write-ups, including the consolidated Better Auth guide, are listed in the [documentation index](docs/index.md).

## Read and use the collection

```bash
git clone https://github.com/byron-public/grok-build-skills.git
cd grok-build-skills
```

Open the relevant `SKILL.md`, then follow its supporting references. For an agent that can read your checkout, a starting prompt is:

> Read `skills/design-ui/SKILL.md` and its relevant references. Use the design guidance for this task, checking its framework assumptions against this project first.

Select the skills needed for the task. Loading all 18 adds overlapping instructions and platform assumptions.

The archived instructions target **TanStack Start, React, Tailwind v4, and shadcn/Radix**, with Grok-specific tooling. References to `.grok/`, `/workspace`, template `AGENTS.md`, `src/lib/auth/`, preview scripts, or Imagine tools describe the original host. This archive does not include that host, the complete app scaffold, or service credentials. Preserved `user-invocable: false` metadata and tool names may need adaptation for other agents.

[`examples/app-env.example.json`](examples/app-env.example.json) contains only the documented, non-secret auth-disabled default. It is an example, not configuration to overwrite in a working application.

## Python tools and verification

Reading the skills requires no installation. To use the local image-processing scripts or run the archive checks with the pinned dependencies, use Python 3.12 or later:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/validate_archive.py
.venv/bin/python skills/generate2dsprite/scripts/generate2dsprite.py --help
```

Pillow and NumPy support the asset tools; PyYAML validates skill metadata. Video frame extraction also requires `ffmpeg` on `PATH`. Image/video generation itself requires the original host tools or an adaptation with your own authorized provider access. Cloning and validating this archive makes no provider API calls.

See [verification and privacy checks](docs/verification.md) for the tested scope. This is a documentation and tool archive, so there is no application build or hosted demo.

## Privacy and licensing

The archive excludes project memory, runtime status, live environment configuration, macOS metadata, and the source folder's local history. Original skill/reference content is preserved, with file hashes recorded in [the manifest](docs/archive-manifest.json).

The three sprite/map packages retain their existing MIT notices and upstream source records. The Three.js reference includes its upstream MIT notice. **There is no blanket open-source license for the entire collection.** Public availability alone does not establish redistribution or relicensing permission for the other material; see [licensing and attribution](LICENSE.md).

For corrections, include a public source or a reproducible example. Never put credentials, session data, private project files, or personal information in an issue or pull request. See [CONTRIBUTING](CONTRIBUTING.md) and [SECURITY](SECURITY.md).
