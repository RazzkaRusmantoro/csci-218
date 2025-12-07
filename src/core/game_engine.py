"""
Game engine for the Turn-Based Fighter Game.
Handles game loop, turn resolution, HP/stamina updates, and win/loss conditions.
"""

from src.core import characters, moves
from src.ai import ai
from src.utils import utils, config
import time


class GameEngine:
    """Main game engine that manages the game loop and turn resolution."""
    
    def __init__(self, player_character, ai_character, difficulty='medium'):
        """
        Initialize the game engine.
        
        Args:
            player_character: Player's character object
            ai_character: AI's character object
            difficulty: Difficulty level ('easy', 'medium', 'hard')
        """
        self.player = player_character
        self.ai_char = ai_character
        self.difficulty = difficulty.lower()
        self.ai_controller = ai.AIController(ai_character, self.difficulty)
        
        self.turn_number = 0
        self.game_over = False
        self.winner = None
        
    def start_game(self):
        """Start the game and display initial state."""
        print("\n" + "=" * 70)
        print(" " * 25 + "BATTLE BEGINS!")
        print("=" * 70)
        time.sleep(1.0)
        
    def display_battle_status_with_moves(self):
        """Display battle status and move selection in one simple block."""
        print("\n" + "=" * 70)
        print(f"TURN {self.turn_number}")
        print("=" * 70)
        
        # Player stats
        player_hp_bar = utils.create_bar(self.player.hp, self.player.max_hp, 30)
        player_stam_bar = utils.create_bar(self.player.stamina, self.player.max_stamina, 25)
        print(f"\n{self.player.name.upper()}")
        print(f"  HP:  [{player_hp_bar}] {self.player.hp}/{self.player.max_hp}")
        print(f"  ST:  [{player_stam_bar}] {self.player.stamina}/{self.player.max_stamina}")
        
        # Player status effects
        player_effects = utils.format_status_effects(self.player)
        if player_effects != "None":
            print(f"  Effects: {player_effects}")
        if self.player.special_move_cooldown > 0:
            print(f"  Special Cooldown: {self.player.special_move_cooldown} turns")
        
        # AI stats
        ai_hp_bar = utils.create_bar(self.ai_char.hp, self.ai_char.max_hp, 30)
        ai_stam_bar = utils.create_bar(self.ai_char.stamina, self.ai_char.max_stamina, 25)
        print(f"\n{self.ai_char.name.upper()}")
        print(f"  HP:  [{ai_hp_bar}] {self.ai_char.hp}/{self.ai_char.max_hp}")
        print(f"  ST:  [{ai_stam_bar}] {self.ai_char.stamina}/{self.ai_char.max_stamina}")
        
        # AI status effects
        ai_effects = utils.format_status_effects(self.ai_char)
        if ai_effects != "None":
            print(f"  Effects: {ai_effects}")
        if self.ai_char.special_move_cooldown > 0:
            print(f"  Special Cooldown: {self.ai_char.special_move_cooldown} turns")
        
        # AI State
        if config.SHOW_AI_DECISIONS:
            state_info = self.ai_controller.get_state_info()
            print(f"  AI State: {state_info['state']}")
        
        print("\n" + "-" * 70)
        print("YOUR MOVES:")
        print("-" * 70)
        
        # Show moves
        available_moves = moves.get_available_moves(self.player)
        move_options = []
        for i, move in enumerate(available_moves, 1):
            move_info = moves.get_move_info(move)
            can_perform, reason = moves.can_perform_move(self.player, move)
            
            if move == 'special':
                move_name = f"{move_info['name']} ({self.player.special_move_name})"
                if self.player.special_move_cooldown > 0:
                    status = f"[Cooldown: {self.player.special_move_cooldown} turns]"
                elif not can_perform:
                    status = f"[{reason}]"
                else:
                    status = "[Ready]"
            elif move == 'rest':
                move_name = move_info['name']
                status = "[Available]"
            else:
                move_name = move_info['name']
                status = "[Available]" if can_perform else f"[{reason}]"
            
            print(f"  {i}. {move_name} {status}")
            move_options.append((str(i), move))
        
        print("-" * 70)
    
    def process_status_effects(self):
        """Process status effects for both characters at the start of turn."""
        status_messages = []
        
        # Process player status effects
        player_effects = self.player.process_status_effects()
        if player_effects['damage'] > 0:
            status_messages.append(f"{self.player.name} takes {player_effects['damage']} damage from status effects!")
            if player_effects['expired_effects']:
                status_messages.append(f"  {self.player.name}'s effects expired: {', '.join(player_effects['expired_effects'])}")
        
        # Process AI status effects
        ai_effects = self.ai_char.process_status_effects()
        if ai_effects['damage'] > 0:
            status_messages.append(f"{self.ai_char.name} takes {ai_effects['damage']} damage from status effects!")
            if ai_effects['expired_effects']:
                status_messages.append(f"  {self.ai_char.name}'s effects expired: {', '.join(ai_effects['expired_effects'])}")
        
        if status_messages:
            for msg in status_messages:
                print(msg)
                time.sleep(0.5)
        
        # Check if anyone died from status effects
        if not self.player.is_alive():
            self.game_over = True
            self.winner = self.ai_char
        elif not self.ai_char.is_alive():
            self.game_over = True
            self.winner = self.player
    
    def reset_turn_status(self):
        """Reset status effects (block/evade) for both characters."""
        # Decay momentum if same move repeated
        if self.player.last_move and self.player.last_move in ['punch', 'kick']:
            self.player.move_variety_bonus = max(0.0, self.player.move_variety_bonus - config.MOMENTUM_DECAY)
        if self.ai_char.last_move and self.ai_char.last_move in ['punch', 'kick']:
            self.ai_char.move_variety_bonus = max(0.0, self.ai_char.move_variety_bonus - config.MOMENTUM_DECAY)
        
        self.player.reset_status()
        self.ai_char.reset_status()
    
    def tick_cooldowns(self):
        """Decrease cooldowns for both characters each turn."""
        self.player.tick_cooldowns()
        self.ai_char.tick_cooldowns()
    
    def player_turn(self):
        """Handle player's turn."""
        # Display battle status with moves
        self.display_battle_status_with_moves()
        
        # Get player input
        available_moves = moves.get_available_moves(self.player)
        move_options = []
        for i, move in enumerate(available_moves, 1):
            move_options.append((str(i), move))
        
        valid_inputs = [opt[0] for opt in move_options] + [opt[1] for opt in move_options]
        choice = utils.get_user_input(
            f"\nYour move: ",
            valid_options=valid_inputs,
            case_sensitive=False
        )
        
        # Convert input to move name
        player_move = None
        for num, move in move_options:
            if choice == num or choice.lower() == move.lower():
                player_move = move
                break
        
        if player_move is None:
            player_move = choice.lower()
        
        # Track AI HP before player move
        ai_hp_before = self.ai_char.hp
        
        # Execute player move
        result = moves.execute_move(player_move, self.player, self.ai_char)
        
        # Track damage dealt to AI
        damage_to_ai = ai_hp_before - self.ai_char.hp
        if damage_to_ai > 0:
            self.ai_controller.record_damage_taken(damage_to_ai)
        
        # Display result
        print(f"\n{self.player.name}: {result.get('message', '')}")
        time.sleep(1.0)
        
        # Record move for AI pattern detection
        # Normalize punch/kick to 'attack' for pattern recognition, or keep specific for counter logic
        if player_move == 'special':
            self.ai_controller.record_player_move('special')
        elif player_move in ['punch', 'kick']:
            self.ai_controller.record_player_move(player_move)  # Keep specific for counter logic
        else:
            self.ai_controller.record_player_move(player_move)
        
        # Check if AI is defeated
        if not self.ai_char.is_alive():
            self.game_over = True
            self.winner = self.player
            return
        
        return result
    
    def ai_turn(self):
        """Handle AI's turn."""
        # AI makes move
        result = self.ai_controller.make_move(self.player)
        
        # Display result
        print(f"{self.ai_char.name}: {result.get('message', '')}")
        time.sleep(1.0)
        
        # Check if player is defeated
        if not self.player.is_alive():
            self.game_over = True
            self.winner = self.ai_char
            return
        
        return result
    
    def execute_turn(self):
        """Execute a complete turn (player + AI)."""
        self.turn_number += 1
        
        
        # Process status effects at start of turn
        self.process_status_effects()
        if self.game_over:
            return
        
        # Tick cooldowns (decrease cooldown counters)
        self.tick_cooldowns()
        
        # Reset turn status (block/evade)
        self.reset_turn_status()
        
        # Player goes first (configurable)
        if config.PLAYER_TURN_FIRST:
            self.player_turn()
            if self.game_over:
                return
            
            self.ai_turn()
        else:
            self.ai_turn()
            if self.game_over:
                return
            
            self.player_turn()
        
        # Brief pause before next turn
        if not self.game_over:
            time.sleep(0.5)
    
    def check_game_over(self):
        """
        Check if game is over.
        
        Returns:
            bool: True if game is over
        """
        if not self.player.is_alive():
            self.game_over = True
            self.winner = self.ai_char
            return True
        
        if not self.ai_char.is_alive():
            self.game_over = True
            self.winner = self.player
            return True
        
        return False
    
    def display_winner(self):
        """Display the winner and game statistics."""
        if self.winner is None:
            return
        
        player_won = (self.winner == self.player)
        
        print("\n" + "=" * 70)
        print(" " * 30 + "GAME OVER!")
        print("=" * 70)
        print(f"\n{self.winner.name.upper()} WINS!")
        print(f"\nTotal Turns: {self.turn_number}")
        print(f"Difficulty: {self.difficulty.upper()}")
        
        print("\n" + "=" * 70)
        print("Final Status:")
        print("-" * 70)
        print(f"{self.player.name}: {self.player.hp}/{self.player.max_hp} HP, {self.player.stamina}/{self.player.max_stamina} ST")
        print(f"{self.ai_char.name}: {self.ai_char.hp}/{self.ai_char.max_hp} HP, {self.ai_char.stamina}/{self.ai_char.max_stamina} ST")
        print("=" * 70)
    
    def run_game(self):
        """Run the main game loop."""
        self.start_game()
        
        while not self.game_over:
            self.execute_turn()
            
            # Check game over condition
            if self.check_game_over():
                break
        
        self.display_winner()
        return self.winner


def create_game(player_character_name, ai_character_name=None, difficulty='medium'):
    """
    Create a new game instance.
    
    Args:
        player_character_name: Name of player's character
        ai_character_name: Name of AI's character (None for random)
        difficulty: Difficulty level ('easy', 'medium', 'hard')
        
    Returns:
        GameEngine instance
    """
    # Create player character
    player_char = characters.get_character(player_character_name)
    if player_char is None:
        raise ValueError(f"Invalid player character: {player_character_name}")
    
    # Create AI character
    if ai_character_name is None:
        import random
        available_chars = characters.list_all_characters()
        # Don't let AI use same character as player
        available_chars = [c for c in available_chars if c != player_character_name.lower()]
        ai_character_name = random.choice(available_chars)
    
    ai_char = characters.get_character(ai_character_name)
    if ai_char is None:
        raise ValueError(f"Invalid AI character: {ai_character_name}")
    
    return GameEngine(player_char, ai_char, difficulty)


def display_character_selection():
    """
    Display character selection menu and get player's choice.
    
    Returns:
        str: Selected character name
    """
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "CHARACTER SELECTION" + " " * 29 + "║")
    print("╚" + "═" * 68 + "╝")
    
    char_list = characters.list_all_characters()
    
    # Display in a clean table
    print(f"\n{'─' * 70}")
    print(f"{'#':<4} {'Character':<18} {'Special Move':<22} {'HP':<6} {'Stam':<6} {'Dmg':<4}")
    print(f"{'─' * 70}")
    
    for i, char_name in enumerate(char_list, 1):
        char = characters.get_character(char_name)
        if char:
            print(f"{i:<4} {char.name:<18} {char.special_move_name:<22} {char.max_hp:<6} {char.max_stamina:<6} {char.base_damage:<4}")
    
    print(f"{'─' * 70}")
    
    while True:
        try:
            choice = input(f"\n🎮 Select a character (1-{len(char_list)} or name): ").strip()
            
            # Try as number
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(char_list):
                    selected_char = characters.get_character(char_list[choice_num - 1])
                    print(f"\n  ✅ You selected: {selected_char.name}")
                    print(f"     Special Move: {selected_char.special_move_name}")
                    return char_list[choice_num - 1]
                else:
                    print(f"  ❌ Please enter a number between 1 and {len(char_list)}")
                    continue
            
            # Try as name
            choice_lower = choice.lower()
            if choice_lower in char_list:
                selected_char = characters.get_character(choice_lower)
                print(f"\n  ✅ You selected: {selected_char.name}")
                print(f"     Special Move: {selected_char.special_move_name}")
                return choice_lower
            
            print(f"  ❌ Invalid choice. Please enter a number (1-{len(char_list)}) or character name.")
        
        except (ValueError, KeyboardInterrupt):
            print("  ❌ Invalid input. Please try again.")


def display_difficulty_selection():
    """
    Display difficulty selection menu and get player's choice.
    
    Returns:
        str: Selected difficulty level
    """
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 22 + "DIFFICULTY SELECTION" + " " * 27 + "║")
    print("╚" + "═" * 68 + "╝")
    
    print(f"\n{'─' * 70}")
    print(f"{'#':<4} {'Difficulty':<20} {'Description':<45}")
    print(f"{'─' * 70}")
    print(f"{'1':<4} {'Easy':<20} {'AI is more defensive, makes suboptimal moves'}")
    print(f"{'2':<4} {'Medium':<20} {'Balanced AI behavior (default)'}")
    print(f"{'3':<4} {'Hard':<20} {'AI is more aggressive and strategic'}")
    print(f"{'─' * 70}")
    
    while True:
        try:
            choice = input(f"\n🎮 Select difficulty (1-3 or name): ").strip().lower()
            
            difficulty_map = {
                '1': config.DIFFICULTY_EASY,
                '2': config.DIFFICULTY_MEDIUM,
                '3': config.DIFFICULTY_HARD,
                'easy': config.DIFFICULTY_EASY,
                'medium': config.DIFFICULTY_MEDIUM,
                'hard': config.DIFFICULTY_HARD
            }
            
            if choice in difficulty_map:
                selected = difficulty_map[choice]
                print(f"\n  ✅ Difficulty set to: {selected.upper()}")
                return selected
            
            print(f"  ❌ Invalid choice. Please enter 1-3 or difficulty name.")
        
        except (ValueError, KeyboardInterrupt):
            print("  ❌ Invalid input. Please try again.")


def main_game_loop():
    """Main game loop for running the game."""
    try:
        # Difficulty selection
        difficulty = display_difficulty_selection()
        
        # Character selection
        player_char_name = display_character_selection()
        
        # Create and run game
        game = create_game(player_char_name, difficulty=difficulty)
        winner = game.run_game()
        
        # Ask if player wants to play again
        while True:
            play_again = input("\nPlay again? (y/n): ").strip().lower()
            if play_again in ['y', 'yes']:
                # Ask if they want to change difficulty
                change_diff = input("Change difficulty? (y/n): ").strip().lower()
                if change_diff in ['y', 'yes']:
                    difficulty = display_difficulty_selection()
                
                player_char_name = display_character_selection()
                game = create_game(player_char_name, difficulty=difficulty)
                winner = game.run_game()
            elif play_again in ['n', 'no']:
                print("\nThanks for playing!")
                break
            else:
                print("Please enter 'y' or 'n'")
    
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        if config.DEBUG_MODE:
            import traceback
            traceback.print_exc()

