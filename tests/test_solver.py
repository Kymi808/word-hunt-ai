"""Tests for the Word Hunt solver."""

import pytest
from src.solver import Trie, solve, word_score, load_dictionary
from src.board import parse_board


@pytest.fixture
def small_trie():
    trie = Trie()
    words = ["cat", "car", "card", "care", "cart", "ace", "act", "arc",
             "rat", "tar", "tare", "race", "trace", "crate", "the", "hat"]
    for w in words:
        trie.insert(w)
    return trie


class TestTrie:
    def test_insert_and_lookup(self):
        trie = Trie()
        trie.insert("hello")
        assert trie.starts_with("hel")
        assert trie.starts_with("hello")
        assert not trie.starts_with("xyz")

    def test_is_word(self):
        trie = Trie()
        trie.insert("cat")
        node = trie.root
        for ch in "cat":
            node = node.children[ch]
        assert node.is_word

    def test_prefix_not_word(self):
        trie = Trie()
        trie.insert("cats")
        node = trie.root
        for ch in "cat":
            node = node.children[ch]
        assert not node.is_word


class TestScoring:
    def test_three_letter(self):
        assert word_score("cat") == 100

    def test_four_letter(self):
        assert word_score("cats") == 400

    def test_five_letter(self):
        assert word_score("crate") == 800

    def test_six_letter(self):
        assert word_score("cranes") == 1400

    def test_seven_letter(self):
        assert word_score("craters") == 1800

    def test_eight_letter(self):
        assert word_score("creators") == 2200

    def test_nine_letter(self):
        assert word_score("creatures") == 2600


class TestSolver:
    def test_finds_words(self, small_trie):
        # Board:
        # C A R D
        # T H E _
        # _ _ _ _
        # _ _ _ _
        board = parse_board("cardthe_________")
        # Replace underscores with z (unused letter)
        board = [
            ["c", "a", "r", "d"],
            ["t", "h", "e", "z"],
            ["z", "z", "z", "z"],
            ["z", "z", "z", "z"],
        ]
        results = solve(board, small_trie)
        words_found = {r[0] for r in results}
        assert "car" in words_found
        assert "card" in words_found
        assert "the" in words_found
        assert "cat" in words_found
        assert "care" in words_found
        assert "hat" in words_found
        assert "act" in words_found

    def test_no_reuse_of_cells(self, small_trie):
        # Even if letters allow it, can't reuse same cell
        board = [
            ["c", "a", "t", "z"],
            ["z", "z", "z", "z"],
            ["z", "z", "z", "z"],
            ["z", "z", "z", "z"],
        ]
        results = solve(board, small_trie)
        words_found = {r[0] for r in results}
        assert "cat" in words_found
        # "act" needs a, c, t - a(0,1) is adjacent to c(0,0) and t(0,2) is adjacent to c(0,0)
        # But for "act": a(0,1)->c(0,0)->t(0,2)... c and t are adjacent? (0,0) and (0,2) differ by 2 cols, NOT adjacent
        # So "act" should NOT be found here
        assert "act" not in words_found

    def test_adjacency_diagonal(self, small_trie):
        board = [
            ["a", "z", "z", "z"],
            ["z", "c", "z", "z"],
            ["z", "z", "t", "z"],
            ["z", "z", "z", "z"],
        ]
        results = solve(board, small_trie)
        words_found = {r[0] for r in results}
        assert "act" in words_found

    def test_sorted_by_score(self, small_trie):
        board = [
            ["c", "a", "r", "d"],
            ["t", "h", "e", "z"],
            ["z", "z", "z", "z"],
            ["z", "z", "z", "z"],
        ]
        results = solve(board, small_trie)
        scores = [r[2] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_path_is_valid(self, small_trie):
        board = [
            ["c", "a", "r", "d"],
            ["t", "h", "e", "z"],
            ["z", "z", "z", "z"],
            ["z", "z", "z", "z"],
        ]
        results = solve(board, small_trie)
        for word, path, score in results:
            # Each position in path should be adjacent to the next
            for i in range(len(path) - 1):
                r1, c1 = path[i]
                r2, c2 = path[i + 1]
                assert abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1
            # Letters in path should spell the word
            spelled = "".join(board[r][c] for r, c in path)
            assert spelled == word


class TestBoard:
    def test_parse_board(self):
        board = parse_board("abcdefghijklmnop")
        assert board[0] == ["a", "b", "c", "d"]
        assert board[3] == ["m", "n", "o", "p"]

    def test_parse_board_with_spaces(self):
        board = parse_board("a b c d e f g h i j k l m n o p")
        assert board[0] == ["a", "b", "c", "d"]

    def test_parse_board_wrong_length(self):
        with pytest.raises(ValueError):
            parse_board("abc")


class TestDictionary:
    def test_load_system_dictionary(self):
        trie = load_dictionary("/usr/share/dict/words")
        # Should contain common words
        assert trie.starts_with("hel")
        assert trie.starts_with("cat")

    def test_full_solve_with_real_dictionary(self):
        trie = load_dictionary("/usr/share/dict/words")
        board = parse_board("therainspainfall")
        results = solve(board, trie)
        assert len(results) > 0
        words = {r[0] for r in results}
        assert "rain" in words or "the" in words or "pain" in words
