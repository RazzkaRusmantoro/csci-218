"""
Utility functions for the Turn-Based Fighter Game.
Contains helper functions for formatting, logging, weighted choices, and display.
"""

import random
from src.utils import config


def weighted_choice(choices):
    """
    Select an item from a dictionary of choices based on weights.
    
    Args:
        choices: Dictionary of {choice: weight} where weights are probabilities
        
    Returns:
        str: Selected choice
    """
    if not choices:
        return None
    
    items = list(choices.items())
    choices_list = [item[0] for item in items]
    weights = [item[1] for item in items]
    
    # Normalize weights to sum to 1.0
    total_weight = sum(weights)
    if total_weight == 0:
        # If all weights are 0, return random choice
        return random.choice(choices_list)
    
    normalized_weights = [w / total_weight for w in weights]
    
    # Use random.choices for weighted selection
    return random.choices(choices_list, weights=normalized_weights, k=1)[0]


def create_bar(current, maximum, length, filled_char='█', empty_char='░'):
    """
    Create a visual bar representation of a value.
    
    Args:
        current: Current value
        maximum: Maximum value
        length: Length of the bar in characters
        filled_char: Character to use for filled portion
        empty_char: Character to use for empty portion
        
    Returns:
        str: Bar representation
    """
    if maximum == 0:
        return empty_char * length
    
    filled_length = int((current / maximum) * length)
    filled_length = max(0, min(filled_length, length))  # Clamp between 0 and length
    
    bar = filled_char * filled_length + empty_char * (length - filled_length)
    return bar


def format_hp_bar(character):
    """
    Format HP bar for a character.
    
    Args:
        character: Character object
        
    Returns:
        str: Formatted HP bar string
    """
    bar = create_bar(character.hp, character.max_hp, config.HP_BAR_LENGTH)
    return f"HP: [{bar}] {character.hp}/{character.max_hp}"


def format_stamina_bar(character):
    """
    Format stamina bar for a character.
    
    Args:
        character: Character object
        
    Returns:
        str: Formatted stamina bar string
    """
    bar = create_bar(character.stamina, character.max_stamina, config.STAMINA_BAR_LENGTH)
    return f"Stamina: [{bar}] {character.stamina}/{character.max_stamina}"


def format_character_status(character):
    """
    Format complete character status (HP and stamina bars).
    
    Args:
        character: Character object
        
    Returns:
        str: Formatted character status
    """
    hp_bar = format_hp_bar(character)
    stamina_bar = format_stamina_bar(character)
    
    status = f"{character.name}:\n  {hp_bar}\n  {stamina_bar}"
    
    # Add status effects if any
    if character.status_effects:
        effects = ", ".join(character.status_effects.keys())
        status += f"\n  Status Effects: {effects}"
    
    return status


def print_turn_separator():
    """Print a separator line for turn display."""
    print(config.TURN_SEPARATOR)


def print_action_separator():
    """Print a separator line for action display."""
    print(config.ACTION_SEPARATOR)


def format_move_result(result):
    """
    Format a move result for display.
    
    Args:
        result: Dictionary containing move result information
        
    Returns:
        str: Formatted move result message
    """
    message = result.get('message', '')
    
    if config.SHOW_DETAILED_CALCULATIONS:
        details = []
        if 'damage' in result:
            details.append(f"Damage: {result['damage']}")
        if 'stamina_cost' in result:
            details.append(f"Stamina Cost: {result['stamina_cost']}")
        if 'critical' in result and result['critical']:
            details.append("CRITICAL HIT!")
        
        if details:
            message += f" ({', '.join(details)})"
    
    return message


def log_message(message, level='INFO'):
    """
    Log a message (simple console logging).
    
    Args:
        message: Message to log
        level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
    """
    if not config.DEBUG_MODE and level == 'DEBUG':
        return
    
    # Check if we should show this log level
    levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    current_level_index = levels.index(config.LOG_LEVEL)
    message_level_index = levels.index(level)
    
    if message_level_index >= current_level_index:
        prefix = f"[{level}]" if config.DEBUG_MODE else ""
        print(f"{prefix} {message}")


def debug_print(message):
    """
    Print debug message if debug mode is enabled.
    
    Args:
        message: Debug message to print
    """
    if config.DEBUG_MODE:
        print(f"[DEBUG] {message}")


def format_percentage(value, maximum, decimals=1):
    """
    Format a value as a percentage.
    
    Args:
        value: Current value
        maximum: Maximum value
        decimals: Number of decimal places
        
    Returns:
        str: Formatted percentage string
    """
    if maximum == 0:
        return "0.0%"
    
    percentage = (value / maximum) * 100
    return f"{percentage:.{decimals}f}%"


def clamp(value, min_value, max_value):
    """
    Clamp a value between min and max.
    
    Args:
        value: Value to clamp
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Clamped value
    """
    return max(min_value, min(value, max_value))


def validate_move(move_type):
    """
    Validate that a move type is valid.
    
    Args:
        move_type: Move type to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return move_type.lower() in config.VALID_MOVES


def validate_character(character_name):
    """
    Validate that a character name is valid.
    
    Args:
        character_name: Character name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return character_name.lower() in config.VALID_CHARACTER_NAMES


def format_battle_summary(player, ai, ai_controller):
    """
    Format a summary of the current battle state.
    
    Args:
        player: Player character object
        ai: AI character object
        ai_controller: AIController object
        
    Returns:
        str: Formatted battle summary
    """
    summary = []
    summary.append("\n" + "=" * 60)
    summary.append("BATTLE STATUS")
    summary.append("=" * 60)
    summary.append(f"\n{format_character_status(player)}")
    summary.append(f"\n{format_character_status(ai)}")
    
    if config.SHOW_AI_DECISIONS:
        state_info = ai_controller.get_state_info()
        summary.append(f"\nAI State: {state_info['state']}")
        summary.append(f"  {state_info['state_description']}")
        summary.append(f"  Health: {format_percentage(ai.hp, ai.max_hp)}")
        summary.append(f"  Stamina: {format_percentage(ai.stamina, ai.max_stamina)}")
    
    summary.append("=" * 60)
    
    return "\n".join(summary)


def clear_screen():
    """Clear the console screen (cross-platform)."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def print_centered(text, width=60):
    """
    Print centered text.
    
    Args:
        text: Text to center
        width: Width to center within
    """
    padding = (width - len(text)) // 2
    print(" " * padding + text)


def format_status_effects(character):
    """
    Format status effects for display.
    
    Args:
        character: Character object
        
    Returns:
        str: Formatted status effects string
    """
    if not character.status_effects:
        return "None"
    
    effects = []
    for effect_type, effect_data in character.status_effects.items():
        turns = effect_data.get('turns', 0)
        damage = effect_data.get('damage', 0)
        
        effect_str = effect_type.capitalize()
        if turns > 0:
            effect_str += f" ({turns} turns)"
        if damage > 0:
            effect_str += f" [{damage} dmg/turn]"
        
        effects.append(effect_str)
    
    return ", ".join(effects)


def get_user_input(prompt, valid_options=None, case_sensitive=False):
    """
    Get user input with validation.
    
    Args:
        prompt: Prompt to display
        valid_options: List of valid options (None for any input)
        case_sensitive: Whether to check case
        
    Returns:
        str: User input
    """
    while True:
        user_input = input(prompt).strip()
        
        if not user_input:
            print("Please enter a value.")
            continue
        
        if valid_options is None:
            return user_input
        
        if not case_sensitive:
            user_input = user_input.lower()
            valid_options = [opt.lower() for opt in valid_options]
        
        if user_input in valid_options:
            return user_input
        
        print(f"Invalid input. Please choose from: {', '.join(valid_options)}")

