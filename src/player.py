"""
Automated player that simulates swipe gestures on the Word Hunt board.
Works with iPhone Mirroring on macOS or any screen mirror app.

Uses Quartz CoreGraphics directly for drag events, since pyautogui's
moveTo() only generates mouseMoved events (not mouseDragged), which
iPhone Mirroring ignores.
"""

import time
import sys

try:
    import pyautogui

    pyautogui.PAUSE = 0
    pyautogui.FAILSAFE = True
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

if sys.platform == "darwin":
    import Quartz


def _smooth_drag(from_x, from_y, to_x, to_y, duration=0.1, steps=20):
    """
    Generate proper kCGEventLeftMouseDragged events so macOS (and iPhone
    Mirroring) registers the movement as a touch drag, not just a hover.
    """
    for i in range(1, steps + 1):
        t = i / steps
        ix = from_x + (to_x - from_x) * t
        iy = from_y + (to_y - from_y) * t
        drag_event = Quartz.CGEventCreateMouseEvent(
            None,
            Quartz.kCGEventLeftMouseDragged,
            (ix, iy),
            Quartz.kCGMouseButtonLeft,
        )
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, drag_event)
        time.sleep(duration / steps)


def _mouse_down(x, y):
    """Send a proper mouse-down event at (x, y)."""
    event = Quartz.CGEventCreateMouseEvent(
        None, Quartz.kCGEventLeftMouseDown, (x, y), Quartz.kCGMouseButtonLeft
    )
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)


def _mouse_up(x, y):
    """Send a proper mouse-up event at (x, y)."""
    event = Quartz.CGEventCreateMouseEvent(
        None, Quartz.kCGEventLeftMouseUp, (x, y), Quartz.kCGMouseButtonLeft
    )
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)


class BoardPlayer:
    """Automates Word Hunt gameplay by simulating swipe gestures."""

    def __init__(
        self,
        board_origin: tuple[int, int],
        cell_size: int,
        swipe_delay: float = 0.02,
        word_delay: float = 0.08,
    ):
        """
        board_origin: (x, y) pixel coordinates of the CENTER of cell (0,0) on screen.
        cell_size: pixel distance between cell centers.
        swipe_delay: seconds between moving to each letter in a word.
        word_delay: seconds to pause between words.
        """
        if not PYAUTOGUI_AVAILABLE:
            raise ImportError("pyautogui is required for automation. Install with: pip install pyautogui")

        self.origin_x, self.origin_y = board_origin
        self.cell_size = cell_size
        self.swipe_delay = swipe_delay
        self.word_delay = word_delay

    def cell_to_screen(self, row: int, col: int) -> tuple[int, int]:
        """Convert grid (row, col) to screen pixel coordinates."""
        x = self.origin_x + col * self.cell_size
        y = self.origin_y + row * self.cell_size
        return x, y

    def play_word(self, path: list[tuple[int, int]]):
        """Swipe through a word path on screen via click-and-drag."""
        if not path:
            return

        # Move to first cell and press down
        cur_x, cur_y = self.cell_to_screen(*path[0])
        pyautogui.moveTo(cur_x, cur_y)
        _mouse_down(cur_x, cur_y)

        # Drag through remaining cells with proper drag events
        for row, col in path[1:]:
            next_x, next_y = self.cell_to_screen(row, col)
            _smooth_drag(cur_x, cur_y, next_x, next_y, duration=self.swipe_delay)
            cur_x, cur_y = next_x, next_y

        # Release to submit the word
        _mouse_up(cur_x, cur_y)
        time.sleep(self.word_delay)

    def play_words(
        self,
        results: list[tuple[str, list[tuple[int, int]], int]],
        max_words: int = 0,
        time_limit: float = 75.0,
    ) -> tuple[int, int]:
        """
        Play all found words automatically.

        max_words: stop after N words (0 = no limit).
        time_limit: stop after N seconds (default 75s to leave buffer from 80s game).

        Returns (words_played, estimated_score).
        """
        start_time = time.time()
        words_played = 0
        total_score = 0

        for word, path, score in results:
            elapsed = time.time() - start_time
            if elapsed >= time_limit:
                print(f"\nTime limit reached ({time_limit}s). Stopping.")
                break
            if max_words > 0 and words_played >= max_words:
                break

            self.play_word(path)
            words_played += 1
            total_score += score

        return words_played, total_score


def calibrate(board_origin: tuple[int, int], cell_size: int):
    """
    Visual calibration helper. Moves the mouse to each cell center
    so you can verify alignment with current config values.
    """
    if not PYAUTOGUI_AVAILABLE:
        raise ImportError("pyautogui is required. Install with: pip install pyautogui")

    print("Calibration mode: mouse will drag through each cell center.")
    print("Press Ctrl+C to abort.\n")

    # Move to first cell and press down
    cur_x = board_origin[0]
    cur_y = board_origin[1]
    pyautogui.moveTo(cur_x, cur_y)
    _mouse_down(cur_x, cur_y)
    print(f"  Cell (0,0) -> screen ({cur_x},{cur_y})")

    for row in range(4):
        for col in range(4):
            if row == 0 and col == 0:
                continue
            next_x = board_origin[0] + col * cell_size
            next_y = board_origin[1] + row * cell_size
            _smooth_drag(cur_x, cur_y, next_x, next_y, duration=0.3)
            cur_x, cur_y = next_x, next_y
            print(f"  Cell ({row},{col}) -> screen ({cur_x},{cur_y})")
            time.sleep(0.3)

    _mouse_up(cur_x, cur_y)
    print("\nCalibration complete. Adjust board_origin and cell_size if positions are off.")


def calibrate_by_clicking() -> dict:
    """
    Interactive calibration. User positions their mouse on the center of
    each of the 4 corner cells and presses Enter to record the position.
    The origin and cell_size are computed automatically.
    Returns dict with board_origin_x, board_origin_y, cell_size.
    """
    if not PYAUTOGUI_AVAILABLE:
        raise ImportError("pyautogui is required. Install with: pip install pyautogui")

    corners = [
        ("top-left", 0, 0),
        ("top-right", 0, 3),
        ("bottom-left", 3, 0),
        ("bottom-right", 3, 3),
    ]

    print("\n=== Click Calibration ===")
    print("Position your iPhone Mirroring window at the top of the screen.")
    print("For each corner cell, move your mouse to its CENTER,")
    print("then come back here and press Enter to record the position.\n")

    recorded = {}
    for label, row, col in corners:
        input(f"  Move mouse to the center of the {label} cell ({row},{col}), then press Enter...")
        pos = pyautogui.position()
        recorded[(row, col)] = (pos.x, pos.y)
        print(f"    Recorded: ({pos.x}, {pos.y})")

    # Compute origin and cell_size from the 4 corner clicks
    tl = recorded[(0, 0)]
    tr = recorded[(0, 3)]
    bl = recorded[(3, 0)]
    br = recorded[(3, 3)]

    # cell_size = average spacing across 3 cells in each direction
    cell_size_x = ((tr[0] - tl[0]) + (br[0] - bl[0])) / 2 / 3
    cell_size_y = ((bl[1] - tl[1]) + (br[1] - tr[1])) / 2 / 3
    cell_size = round((cell_size_x + cell_size_y) / 2)

    origin_x = round((tl[0] + bl[0]) / 2)
    origin_y = round((tl[1] + tr[1]) / 2)

    print(f"\nComputed calibration:")
    print(f"  board_origin_x: {origin_x}")
    print(f"  board_origin_y: {origin_y}")
    print(f"  cell_size: {cell_size}")

    return {
        "board_origin_x": origin_x,
        "board_origin_y": origin_y,
        "cell_size": cell_size,
    }
