# Space Invaders (Python)

A minimal Pygame-based Space Invaders clone that launches with one command after dependencies are installed—no external assets required.

## Quick Start
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Controls
- Left/Right or A/D: Move
- Space: Shoot
- R: Restart after game over
- Esc: Quit

## Gameplay Notes
- Enemies march horizontally and drop when hitting screen edges; they speed up as you clear them.
- You have three lives; enemy lasers or invaders reaching the bottom end the run.
- Score increases by 10 for each invader destroyed.

If you change the window size or speeds, update the constants at the top of `main.py` to keep balance sensible.
