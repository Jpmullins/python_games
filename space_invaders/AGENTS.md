# Repository Guidelines

## Project Structure & Module Organization
- `src/` gameplay: game loop, entities, rendering, input; keep modules small.
- `assets/` sprites, audio, fonts; use `assets/raw/` for sources and `assets/build/` for optimized exports.
- `tests/` mirrors `src/` for unit/integration specs; name tests after the module.
- `scripts/` helper tooling (asset pipeline, lint wrappers, release helpers); keep scripts idempotent.
- `docs/` design notes and diagrams (.png/.md) close to the related feature.

## Build, Test, and Development Commands
- `npm install` installs dependencies (target Node 18+).
- `npm run dev` starts a hot-reload dev server (default `http://localhost:5173`).
- `npm test` runs the automated suite; keep it green before commits.
- `npm run lint` enforces style and correctness checks.
- `npm run build` creates the production bundle in `dist/`.
- If you prefer Make or another stack, add equivalent scripts and note them in `README.md`.

## Coding Style & Naming Conventions
- TypeScript by default; 2-space indent; ~100 columns; semicolons on; single quotes.
- camelCase for variables/functions, PascalCase for classes/components, SCREAMING_SNAKE_CASE for constants.
- Keep game logic pure; separate rendering from state updates to simplify testing.
- Run `npm run lint` (and `npm run format` if available) before pushing; avoid committing lint noise.

## Testing Guidelines
- Use Jest/Vitest; place specs in `tests/**` named `*.test.ts`.
- Target >80% coverage on collision, scoring, and level progression; prefer deterministic seeds for randomness.
- Mock timers and the render loop to keep tests fast; avoid canvas dependencies in unit tests.
- Include an integration test that boots the game loop without throwing; run `npm test` before opening a PR.

## Commit & Pull Request Guidelines
- Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`); subjects ≤72 characters.
- One logical change per commit; add a short rationale when tweaking gameplay balance or physics.
- PRs: brief summary, linked issue, test evidence, and clips/gifs for visual changes.
- Ensure build/lint/tests pass; note new asset licenses in the PR description.

## Security & Asset Hygiene
- Do not commit secrets; load config from `.env` and document required vars in `.env.example`.
- Prefer PNG/WebP sprites and OGG audio; avoid large binaries—store sources in `assets/raw/` and generate optimized assets in `scripts/` or CI.
- Check third-party assets for license compatibility; attribute in `docs/` when required.
