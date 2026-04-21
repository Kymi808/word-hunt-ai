# Word Hunt AI

Automated solver and player for GamePigeon Word Hunt. Finds every possible word on the 4x4 board and can auto-play them via simulated swipes on a mirrored iPhone screen.

## Features

- **Trie-based solver** — finds all valid words using DFS with prefix pruning
- **Score-optimized** — plays highest-scoring words first for maximum points
- **Auto-play** — simulates swipe gestures on iPhone Mirroring (macOS)
- **OCR capture** — reads the board directly from a screenshot (optional)
- **Fast** — solves a board in ~1 second, typically finds 150-300+ words

## Quick Start

### 1. Setup

```bash
chmod +x setup.sh
./setup.sh
source venv/bin/activate
```

Or manually:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Minimum install** (solver only, no OCR or auto-play):

```bash
pip install pyyaml
```

### 2. Solve a Board

Enter the 16 letters left-to-right, top-to-bottom:

```
┌───┬───┬───┬───┐
│ T │ H │ E │ R │
├───┼───┼───┼───┤
│ A │ I │ N │ S │
├───┼───┼───┼───┤
│ P │ A │ I │ N │
├───┼───┼───┼───┤
│ F │ A │ L │ L │
└───┴───┴───┴───┘
```

```bash
python -m src.main solve "therainspainfall"
```

Or interactively:

```bash
python -m src.main solve
# Enter 16 letters: therainspainfall
```

### 3. Auto-Play (Full E2E)

This mode solves the board and automatically swipes words on your screen.

**Prerequisites:**
- iPhone Mirroring enabled on macOS (macOS Sequoia+), or any screen mirror app
- Accessibility permissions for your terminal (System Settings > Privacy & Security > Accessibility)

**Steps:**

1. **Calibrate** your screen coordinates (one-time setup):

```bash
python -m src.main calibrate
```

The mouse will move to where it thinks each cell center is. Adjust `config.yaml` values until alignment is correct:

```yaml
board_origin_x: 200   # x pixel of cell (0,0) center
board_origin_y: 400   # y pixel of cell (0,0) center
cell_size: 90          # pixels between cell centers
```

2. **Start a Word Hunt game** on your iPhone (via iPhone Mirroring)

3. **Run the player:**

```bash
python -m src.main play "abcdefghijklmnop"
```

You get a 3-second countdown to switch focus to the game window. The bot will then swipe through all words automatically.

### 4. OCR Capture (Optional)

Reads the board directly from a screenshot instead of manual letter input:

```bash
# Capture live from screen region
python -m src.main capture

# Or from an existing screenshot
python -m src.main capture --image screenshot.png
```

Requires `tesseract` and `opencv-python`:

```bash
brew install tesseract
pip install opencv-python pytesseract
```

## Configuration

Edit `config.yaml` to customize behavior:

| Setting | Default | Description |
|---------|---------|-------------|
| `dictionary_path` | `/usr/share/dict/words` | Word list file (one word per line) |
| `min_word_length` | `3` | Minimum word length to search for |
| `board_origin_x` | `200` | X pixel of cell (0,0) center on screen |
| `board_origin_y` | `400` | Y pixel of cell (0,0) center on screen |
| `cell_size` | `90` | Pixel distance between cell centers |
| `swipe_delay` | `0.02` | Seconds between letters in a swipe |
| `word_delay` | `0.08` | Seconds between words |
| `time_limit` | `75.0` | Stop after N seconds (game gives 80s) |
| `max_words` | `0` | Max words to play (0 = unlimited) |
| `top_display` | `0` | Max words to show in output (0 = all) |

### Tuning for Speed

For maximum score, lower the delays:

```yaml
swipe_delay: 0.01
word_delay: 0.05
```

If the game misses inputs, increase them slightly.

### Custom Dictionary

The macOS system dictionary works well but includes some words Word Hunt doesn't accept. For better accuracy, use a Scrabble dictionary (TWL or SOWPODS):

```yaml
dictionary_path: "dictionary/custom_words.txt"
```

Place your word list in `dictionary/` with one word per line.

## Scoring

| Word Length | Points |
|-------------|--------|
| 3 letters | 100 |
| 4 letters | 400 |
| 5 letters | 800 |
| 6 letters | 1,400 |
| 7 letters | 1,800 |
| 8+ letters | 2,200 + 400/letter |

The solver prioritizes longer/higher-scoring words first.

## How It Works

1. **Dictionary** is loaded into a Trie (prefix tree) for O(1) prefix lookups
2. **DFS** explores all paths on the 4x4 grid, pruning branches with no valid prefix
3. Words are **sorted by score** (descending) so highest-value words are played first
4. **Auto-play** simulates mouse-down → drag → mouse-up gestures matching each word's path on the grid

## Testing

```bash
python -m pytest tests/ -v
```

Tip: run the solver-only path first before enabling OCR or auto-play so board parsing and dictionary loading are verified independently.

## Project Structure

```
word_hunt_ai/
├── config.yaml          # Runtime configuration
├── requirements.txt     # Python dependencies
├── setup.sh             # One-command setup
├── src/
│   ├── solver.py        # Trie + DFS word finder
│   ├── board.py         # Board parsing and display
│   ├── capture.py       # Screen capture + OCR
│   ├── player.py        # Automated swipe simulation
│   └── main.py          # CLI entry point
└── tests/
    └── test_solver.py   # Solver tests
```
