# Provenance

Review date: September 5, 2026.

## Source and repository maintenance

The maintainer supplied this collection directly from Grok Build's app-builder environment. These are Grok Build's platform skills and references, including the third-party packages bundled with them. `byron-public` maintains this mirror; xAI does not maintain this GitHub repository.

The earlier research examined the source collection's platform contracts, its overlap with Grok's locally distributed skills, and matching `.grok` bundles in public Grok-generated projects. Its finding that no standalone xAI source repository or bundle-wide license had been identified concerned distribution and licensing. It did not mean that these were community-written replacements for Grok Build's skills.

The public snapshot below corroborates the original files' byte identity and public availability. It is a comparison source, not the claimed origin of the collection.

## Verified public snapshot

The archived `skills/` and `references/` content was compared with the public `.grok` tree in [DHYEYPATL/SafeBuy---Razorpay-build](https://github.com/DHYEYPATL/SafeBuy---Razorpay-build/tree/ff621ac0313da095028e91f9ccb3ddb75aaf761c/.grok):

- Commit: `ff621ac0313da095028e91f9ccb3ddb75aaf761c`.
- `.grok` tree: `690e69379cad7637be7a3aaecaa23c0a812bfb7b`.
- Compared files: **85** original skill and platform-reference files.
- Exact Git blob matches: **85**.
- Different original skill/reference files: **0**.

The comparison uses `SHA-1("blob " + byte_length + NUL + file_bytes)`, the Git blob object identifier. The [manifest](archive-manifest.json) also records SHA-256 checksums for the published archive payload. The added Three.js license notice is classified separately and is not counted among those 85 files.

The earlier August 2026 research compared 87 source-bundle files: the same 85 files, a non-secret environment flag file, and runtime status. It found 86 exact matches; status differed only in its runtime timestamp. The current archive omits status and presents the flag as an example, explaining the different comparison count.

These results establish that the substantive collection was already publicly accessible. They do not establish a first publication date, confidentiality status, or rarity. The source of the skills, the publisher of this mirror, and permission to redistribute the material are separate questions; licensing is recorded in [LICENSE.md](../LICENSE.md).

## Third-party sources

`generate2dmap`, `generate2dsprite`, and `video2dsprite` retain source notices pointing to [agent-sprite-forge at commit 53dce605](https://github.com/0x0funky/agent-sprite-forge/tree/53dce6055984c610d833e77887939cbd0fb1c92b). Its public repository reports an MIT license. Each package's original notice is preserved.

`threejs/references/llms-full.txt` identifies the official Three.js documentation. The included upstream license was retrieved from [mrdoob/three.js](https://github.com/mrdoob/three.js/blob/dev/LICENSE), Git blob `8ada2a5f982916b0ba4b7a0aa7de347587e745d7`. This is an attribution addition; it does not authenticate the Grok-specific wrapper or date every statement in the reference.

## Supplementary and editorial files

- [`docs/guides/better-auth.md`](guides/better-auth.md): supplementary consolidation supplied alongside the collection, dated August 25, 2026. It is absent from the verified snapshot and is separate from the original Grok Build skills. Moved from `BETTER-AUTH-INSTRUCTIONS.md` without changing its contents.
- [`examples/app-env.example.json`](../examples/app-env.example.json): normalized example containing only `VITE_AUTH_ENABLED: "false"`; it contains no credentials. Moved from the repository root without changing its contents.
- README, documentation, archive validator, requirements, and repository hygiene files: added for this archive.
- `skills/threejs/references/LICENSE.threejs`: upstream attribution added during preparation.

## Preservation and exclusions

The original 85 skill/reference files and the supplementary Better Auth guide are preserved byte for byte. No source installation or personal history is included. Project memory, runtime status, original live configuration, `.DS_Store`, caches, generated outputs, and credentials are excluded.

Instructions inside the archive describe their source environment. They are reference material, not instructions to modify the machine or repository merely while reviewing the archive. Missing host files and platform services are documented limitations, not included dependencies.

Licensing is recorded separately in [LICENSE.md](../LICENSE.md). A matching public blob is not itself a license grant.
