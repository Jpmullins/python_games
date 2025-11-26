# Kpop Demon Hunters: Rumi vs The Streets

Python/Pygame brawler prototype inspired by classic Street Fighter pacing. Play as Rumi, keep demons off the neon block, and clear the wave.

## Quick start
1) Install deps: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
2) Launch: `python src/main.py`

## Controls
- Move: `A/D` or `Left/Right`
- Jump: `W`, `Up`, or `Space`
- Light attack: `J` (fast jab)
- Heavy attack: `K` (harder, longer cooldown)
- Quit: `Esc` — Retry after defeat: `R`

## Gameplay notes
- Defeat 10 demons to clear the block; max 3 spawn at once.
- Rumi and demons exchange simple hitboxes; watch for retaliation after you whiff.
- Use jump arcs to bypass rushes and land heavy strikes.

## Folder layout
- `src/main.py` — Game loop, characters, drawing, and hitbox logic.
- `requirements.txt` — Pygame dependency pin.
- `AGENTS.md` — Contributor guidelines for extending the game.
