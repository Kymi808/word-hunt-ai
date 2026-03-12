"""
Word Hunt AI - Main entry point.

Modes:
  solve     - Solve a board and display results (manual letter input)
  capture   - Capture board from screen via OCR, then solve
  play      - Solve + automatically play words via simulated swipes
  calibrate - Calibrate screen coordinates for the game board
"""

import argparse
import sys
import os
import yaml

from src.solver import solve, load_dictionary
from src.board import parse_board, display_board, display_results
from src.player import BoardPlayer, calibrate


DEFAULT_CONFIG = {
    "dictionary_path": "/usr/share/dict/words",
    "min_word_length": 3,
    "board_origin_x": 200,
    "board_origin_y": 400,
    "cell_size": 90,
    "swipe_delay": 0.02,
    "word_delay": 0.08,
    "time_limit": 75.0,
    "max_words": 0,
    "top_display": 0,
}


def load_config(config_path: str | None = None) -> dict:
    config = dict(DEFAULT_CONFIG)
    if config_path and os.path.exists(config_path):
        with open(config_path) as f:
            user_config = yaml.safe_load(f) or {}
            config.update(user_config)
    elif os.path.exists("config.yaml"):
        with open("config.yaml") as f:
            user_config = yaml.safe_load(f) or {}
            config.update(user_config)
    return config


def cmd_solve(args, config):
    """Solve a board from manual letter input."""
    if args.letters:
        letters = args.letters
    else:
        print("Enter 16 letters (left-to-right, top-to-bottom):")
        letters = input("> ").strip()

    board = parse_board(letters)
    display_board(board)

    print("\nLoading dictionary...")
    trie = load_dictionary(config["dictionary_path"], min_length=config["min_word_length"])

    print("Solving...")
    results = solve(board, trie, min_length=config["min_word_length"])
    display_results(results, top_n=config["top_display"])
    return results, board


def cmd_capture(args, config):
    """Capture board from screen and solve."""
    from src.capture import capture_screen_region, ocr_board_from_image

    if args.image:
        image_path = args.image
    else:
        print("Capturing screen region...")
        x = config["board_origin_x"] - config["cell_size"]
        y = config["board_origin_y"] - config["cell_size"]
        w = config["cell_size"] * 6
        h = config["cell_size"] * 6
        image_path = capture_screen_region(x, y, w, h)
        print(f"Screenshot saved: {image_path}")

    print("Running OCR...")
    letters = ocr_board_from_image(image_path)
    print(f"Detected letters: {letters}")

    confirm = input("Correct? (y/n or type corrected letters): ").strip()
    if confirm.lower() != "y" and len(confirm) == 16:
        letters = confirm

    board = parse_board(letters)
    display_board(board)

    trie = load_dictionary(config["dictionary_path"], min_length=config["min_word_length"])
    results = solve(board, trie, min_length=config["min_word_length"])
    display_results(results, top_n=config["top_display"])
    return results, board


def cmd_play(args, config):
    """Solve and automatically play."""
    results, board = cmd_solve(args, config)

    if not results:
        print("No words found!")
        return

    player = BoardPlayer(
        board_origin=(config["board_origin_x"], config["board_origin_y"]),
        cell_size=config["cell_size"],
        swipe_delay=config["swipe_delay"],
        word_delay=config["word_delay"],
    )

    print(f"\nReady to play {len(results)} words.")
    print("Switch to the game window. Starting in 3 seconds...")
    print("(Move mouse to top-left corner to abort - pyautogui failsafe)")

    import time

    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)

    words_played, score = player.play_words(
        results,
        max_words=config["max_words"],
        time_limit=config["time_limit"],
    )
    print(f"\nDone! Played {words_played} words for ~{score} points.")


def cmd_calibrate(args, config):
    """Run calibration to verify screen coordinates."""
    print("Move your game window into position, then press Enter.")
    input()
    calibrate(
        board_origin=(config["board_origin_x"], config["board_origin_y"]),
        cell_size=config["cell_size"],
    )


def main():
    parser = argparse.ArgumentParser(
        description="Word Hunt AI - Automated solver and player for GamePigeon Word Hunt"
    )
    parser.add_argument("-c", "--config", help="Path to config.yaml")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # solve
    solve_parser = subparsers.add_parser("solve", help="Solve a board (manual input)")
    solve_parser.add_argument("letters", nargs="?", help="16 letters (e.g., 'abcdefghijklmnop')")

    # capture
    cap_parser = subparsers.add_parser("capture", help="Capture board from screen via OCR")
    cap_parser.add_argument("--image", help="Path to existing screenshot instead of live capture")

    # play
    play_parser = subparsers.add_parser("play", help="Solve + auto-play words")
    play_parser.add_argument("letters", nargs="?", help="16 letters")

    # calibrate
    subparsers.add_parser("calibrate", help="Calibrate screen coordinates")

    args = parser.parse_args()
    config = load_config(args.config)

    if args.command == "solve":
        cmd_solve(args, config)
    elif args.command == "capture":
        cmd_capture(args, config)
    elif args.command == "play":
        cmd_play(args, config)
    elif args.command == "calibrate":
        cmd_calibrate(args, config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
