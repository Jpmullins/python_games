# Repository Guidelines

## Project Structure & Module Organization
- `src/`: Core gameplay logic, entity behaviors, input handling, and any shared helpers. Keep files small and prefer feature-focused subfolders (e.g., `src/enemies/`, `src/player/`, `src/ui/`).
- `assets/`: Art, audio, fonts, and VFX. Name assets with kebab-case and descriptive variants (e.g., `enemy-imp-run-01.png`). Consider Git LFS for large binaries.
- `tests/`: Automated checks; mirror the `src/` layout (e.g., `tests/enemies/imp.spec.ts`).
- `docs/`: Design notes, tuning sheets, and architecture decisions. Update when systems change.
- `scripts/`: Development scripts (build, export, asset pipelines). Keep them idempotent and POSIX-sh compatible.

## Build, Test, and Development Commands
- `make dev`: Run the local game with live reload. Ensure dependencies are installed first (e.g., `npm ci` or engine-specific modules).
- `make test`: Execute automated tests in `tests/`; add `CI=true make test` for deterministic runs.
- `make lint`: Run linting/formatting across `src/`, `tests/`, and `scripts/`.
- `make build`: Produce an optimized export into `build/` (platform targets belong under `build/<platform>/`).
Expose equivalent commands via `package.json` or engine CLI if `make` is unavailable in your environment.

## Coding Style & Naming Conventions
- Indentation: 2 spaces for JavaScript/TypeScript/JSON; 4 spaces for shell scripts only when readability benefits.
- Naming: PascalCase for classes/components, camelCase for variables/functions, SCREAMING_SNAKE for constants. Asset files stay kebab-case.
- Formatting: Use Prettier for JS/TS/JSON/Markdown and ESLint for logic checks. Run `make lint` before committing.
- Comments: Prefer brief intent-focused comments; avoid explaining obvious control flow.

## Testing Guidelines
- Place unit/integration specs in `tests/` with filenames ending in `.spec.ts` or `.test.ts` aligned with the module under test.
- Favor deterministic tests; seed randomness and avoid real timers where possible.
- Aim for high coverage on gameplay rules, collision logic, and input handling; add regression tests for reported bugs.

## Commit & Pull Request Guidelines
- Commit messages: Follow Conventional Commits (`feat:`, `fix:`, `chore:`, `refactor:`) to keep history searchable. Squash local WIP before pushing.
- Pull requests: Include a concise summary, linked issue/feature ticket, test results (`make test` output), and screenshots/GIFs for gameplay or UI changes.
- Keep PRs small and focused; note any follow-up tasks in the description. Update `docs/` and `CHANGELOG` entries when behavior changes.

## Security & Configuration Tips
- Keep secrets out of the repo; use `.env` (gitignored) and document required variables in `docs/config.md` or similar.
- Validate third-party assets for licensing; attribute where required and avoid unvetted binaries. Add checksums for downloaded build tools when practical.
