# Source of this skill

- Upstream: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill (MIT, see LICENSE), folder `.claude/skills/ui-ux-pro-max`
- Pinned at upstream commit `2de1134` ("fix(projects): precompile sample styles so they render offline"), copied 21.11.2026
- Changes: upstream `scripts/tests/` left out. Nothing else edited.
- Reviewed before adding: guidance files plus local search scripts (Python standard library only, no network calls,
  no subprocess). Added at Rashed's request for UI work on `app/` (task R7).
- Rules: it never overrides `AGENTS.md`, `docs/traps.md` or the `trap-guard` skill. Update only by a new pinned copy in a PR.
