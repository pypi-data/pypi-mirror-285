#!/usr/bin/env python3
# -*- coding:utf-8 -*-


from brain_games.engine import play
from brain_games.games import brain_gcd


def main():
    """Run game."""
    play(brain_gcd)


if __name__ == "__main__":
    main()
