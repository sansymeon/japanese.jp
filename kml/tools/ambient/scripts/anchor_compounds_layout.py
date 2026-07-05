"""Shared compound-word layout — scale long anchor strings to one line."""

from __future__ import annotations


def anchor_word_length(word: str) -> int:
    return len(word)


def anchor_word_scale(word: str) -> float:
    n = anchor_word_length(word)
    if n <= 2:
        return 1.0
    if n == 3:
        return 0.74
    if n == 4:
        return 0.56
    return 0.48
