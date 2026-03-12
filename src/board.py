"""
Board representation and input utilities.
"""


def parse_board(letters: str) -> list[list[str]]:
    """
    Parse a 16-character string into a 4x4 board.
    Example: "abcdefghijklmnop" ->
        [['a','b','c','d'],
         ['e','f','g','h'],
         ['i','j','k','l'],
         ['m','n','o','p']]
    """
    letters = letters.lower().replace(" ", "").replace(",", "").replace("\n", "")
    if len(letters) != 16:
        raise ValueError(f"Expected 16 letters, got {len(letters)}")
    return [[letters[r * 4 + c] for c in range(4)] for r in range(4)]


def display_board(board: list[list[str]]):
    """Print the board in a readable format."""
    print("\n┌───┬───┬───┬───┐")
    for i, row in enumerate(board):
        print("│ " + " │ ".join(ch.upper() for ch in row) + " │")
        if i < 3:
            print("├───┼───┼───┼───┤")
    print("└───┴───┴───┴───┘")


def display_results(results: list[tuple[str, list[tuple[int, int]], int]], top_n: int = 0):
    """Print found words with scores."""
    if top_n > 0:
        results = results[:top_n]

    total = sum(score for _, _, score in results)
    print(f"\nFound {len(results)} words (total: {total} pts)\n")
    print(f"{'#':<5} {'Word':<20} {'Length':<8} {'Score':<8} {'Path'}")
    print("─" * 65)
    for i, (word, path, score) in enumerate(results, 1):
        path_str = "→".join(f"({r},{c})" for r, c in path)
        print(f"{i:<5} {word.upper():<20} {len(word):<8} {score:<8} {path_str}")
    print(f"\n{'Total score:':<34}{total}")
