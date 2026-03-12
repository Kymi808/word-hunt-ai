"""
Core Word Hunt solver using Trie + DFS.
Finds all valid words on a 4x4 letter grid by traversing adjacent cells.
"""


class TrieNode:
    __slots__ = ("children", "is_word")

    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_word = True

    def starts_with(self, prefix: str) -> bool:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True


# Word Hunt scoring
SCORE_TABLE = {
    3: 100,
    4: 400,
    5: 800,
    6: 1400,
    7: 1800,
    8: 2200,
}


def word_score(word: str) -> int:
    length = len(word)
    if length < 3:
        return 0
    if length <= 8:
        return SCORE_TABLE[length]
    return 2200 + (length - 8) * 400


# 8-directional adjacency on a 4x4 grid
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def solve(board: list[list[str]], trie: Trie, min_length: int = 3) -> list[tuple[str, list[tuple[int, int]], int]]:
    """
    Find all valid words on the board.

    Returns a list of (word, path, score) sorted by score descending, then length descending.
    path is a list of (row, col) positions for each letter.
    """
    rows, cols = len(board), len(board[0])
    found: dict[str, list[tuple[int, int]]] = {}

    def dfs(r: int, c: int, node: TrieNode, path: list[tuple[int, int]], current: list[str]):
        ch = board[r][c].lower()
        if ch not in node.children:
            return
        next_node = node.children[ch]
        current.append(ch)
        path.append((r, c))

        word = "".join(current)
        if next_node.is_word and len(word) >= min_length and word not in found:
            found[word] = list(path)

        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                visited.add((nr, nc))
                dfs(nr, nc, next_node, path, current)
                visited.discard((nr, nc))

        current.pop()
        path.pop()

    visited: set[tuple[int, int]] = set()
    for r in range(rows):
        for c in range(cols):
            visited.add((r, c))
            dfs(r, c, trie.root, [], [])
            visited.discard((r, c))

    results = [(word, path, word_score(word)) for word, path in found.items()]
    results.sort(key=lambda x: (-x[2], -len(x[0])))
    return results


def load_dictionary(path: str, min_length: int = 3, max_length: int = 16) -> Trie:
    """Load words from a dictionary file into a Trie."""
    trie = Trie()
    with open(path) as f:
        for line in f:
            word = line.strip().lower()
            if min_length <= len(word) <= max_length and word.isalpha():
                trie.insert(word)
    return trie
