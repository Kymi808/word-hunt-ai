"""
Automated player that simulates swipe gestures on the Word Hunt board.
Works with iPhone Mirroring on macOS or any screen mirror app.
"""

import time

try:
    import pyautogui

    pyautogui.PAUSE = 0
    pyautogui.FAILSAFE = True
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


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
        """Swipe through a word path on screen."""
        if not path:
            return

        # Move to first cell and press down
        x, y = self.cell_to_screen(*path[0])
        pyautogui.moveTo(x, y)
        pyautogui.mouseDown()

        # Drag through remaining cells
        for row, col in path[1:]:
            x, y = self.cell_to_screen(row, col)
            pyautogui.moveTo(x, y, duration=self.swipe_delay)

        # Release to submit the word
        pyautogui.mouseUp()
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
    so you can verify alignment.
    """
    if not PYAUTOGUI_AVAILABLE:
        raise ImportError("pyautogui is required. Install with: pip install pyautogui")

    print("Calibration mode: mouse will move to each cell center.")
    print("Press Ctrl+C to abort.\n")

    for row in range(4):
        for col in range(4):
            x = board_origin[0] + col * cell_size
            y = board_origin[1] + row * cell_size
            pyautogui.moveTo(x, y)
            print(f"  Cell ({row},{col}) -> screen ({x},{y})")
            time.sleep(0.5)

    print("\nCalibration complete. Adjust board_origin and cell_size if positions are off.")
