"""
Main entry point for the Turn-Based Fighter Game.
Handles game start and character selection.
"""

from src.core import game_engine


def main():
    """Main entry point for the game."""
    print("=" * 60)
    print("TURN-BASED FIGHTER GAME")
    print("With FSM AI")
    print("=" * 60)
    
    game_engine.main_game_loop()


if __name__ == "__main__":
    main()

