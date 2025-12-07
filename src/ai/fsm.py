"""
Advanced Finite State Machine (FSM) for AI behavior in the Turn-Based Fighter Game.
Implements sophisticated multi-factor decision-making with context-aware transitions,
threat assessment, momentum tracking, and predictive behavior analysis.
"""

from src.utils import config
import math


class FSMState:
    """Represents a state in the FSM."""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"FSMState('{self.name}')"


# Define all FSM states
STATES = {
    'AGGRESSIVE': FSMState('Aggressive', 'AI confident, healthy, focuses on offense'),
    'DEFENSIVE': FSMState('Defensive', 'AI anticipates danger, focuses on defense'),
    'COUNTER': FSMState('Counter', 'AI reacts to player patterns'),
    'WOUNDED': FSMState('Wounded', 'AI low HP, plays safe'),
    'DESPERATION': FSMState('Desperation', 'AI very low HP, high risk moves'),
    'EXHAUSTED': FSMState('Exhausted', 'AI low stamina, focuses on recovery'),
    'FINISHER': FSMState('Finisher', 'AI attempts finishing move on low HP opponent')
}

# Default starting state
DEFAULT_STATE = STATES['AGGRESSIVE']


def get_state(state_name):
    """
    Get a state object by name.
    
    Args:
        state_name: Name of the state (case-insensitive)
        
    Returns:
        FSMState object or None if not found
    """
    state_name = state_name.upper()
    return STATES.get(state_name)


def calculate_health_percentage(character):
    """
    Calculate character's health as a percentage.
    
    Args:
        character: Character object
        
    Returns:
        float: Health percentage (0.0 to 1.0)
    """
    if character.max_hp == 0:
        return 0.0
    return character.hp / character.max_hp


def calculate_stamina_percentage(character):
    """
    Calculate character's stamina as a percentage.
    
    Args:
        character: Character object
        
    Returns:
        float: Stamina percentage (0.0 to 1.0)
    """
    if character.max_stamina == 0:
        return 0.0
    return character.stamina / character.max_stamina


def calculate_health_differential(ai_character, opponent_character):
    """
    Calculate health differential between AI and opponent.
    
    Args:
        ai_character: AI character object
        opponent_character: Opponent character object
        
    Returns:
        float: Health differential (positive = AI advantage, negative = disadvantage)
    """
    ai_hp_pct = calculate_health_percentage(ai_character)
    opp_hp_pct = calculate_health_percentage(opponent_character)
    return ai_hp_pct - opp_hp_pct


def calculate_threat_level(ai_character, opponent_character, last_player_move):
    """
    Calculate threat level from opponent based on multiple factors.
    
    Args:
        ai_character: AI character object
        opponent_character: Opponent character object
        last_player_move: Last move player performed
        
    Returns:
        float: Threat level (0.0 to 1.0, higher = more threatening)
    """
    threat = 0.0
    
    # Opponent HP advantage increases threat
    hp_diff = calculate_health_differential(ai_character, opponent_character)
    if hp_diff < -0.2:  # AI significantly behind
        threat += 0.3
    elif hp_diff < -0.1:  # AI slightly behind
        threat += 0.15
    
    # Opponent stamina (high stamina = can use special moves)
    opp_stam_pct = calculate_stamina_percentage(opponent_character)
    if opp_stam_pct > 0.7:
        threat += 0.2
    elif opp_stam_pct > 0.5:
        threat += 0.1
    
    # Last move was special (high threat)
    if last_player_move == 'special':
        threat += 0.25
    
    # Opponent has status effects that could be dangerous
    if opponent_character.status_effects:
        # If opponent has buffs or dangerous effects
        threat += 0.1
    
    return min(1.0, threat)


def calculate_momentum(ai_character, opponent_character, recent_damage_dealt=0, recent_damage_taken=0):
    """
    Calculate momentum score (positive = AI advantage, negative = disadvantage).
    
    Args:
        ai_character: AI character object
        opponent_character: Opponent character object
        recent_damage_dealt: Recent damage AI dealt
        recent_damage_taken: Recent damage AI took
        
    Returns:
        float: Momentum score (-1.0 to 1.0)
    """
    momentum = 0.0
    
    # Health differential
    hp_diff = calculate_health_differential(ai_character, opponent_character)
    momentum += hp_diff * 0.4
    
    # Recent damage dealt vs taken
    if recent_damage_dealt > 0 or recent_damage_taken > 0:
        damage_ratio = recent_damage_dealt / (recent_damage_taken + recent_damage_dealt + 1)
        momentum += (damage_ratio - 0.5) * 0.3
    
    # Stamina advantage
    ai_stam = calculate_stamina_percentage(ai_character)
    opp_stam = calculate_stamina_percentage(opponent_character)
    stam_diff = ai_stam - opp_stam
    momentum += stam_diff * 0.3
    
    return max(-1.0, min(1.0, momentum))


def should_transition_to_exhausted(ai_character, opponent_character=None, threat_level=0.0):
    """
    Advanced check if AI should transition to Exhausted state.
    Considers stamina, threat level, and opponent state.
    
    Args:
        ai_character: AI character object
        opponent_character: Opponent character object (optional)
        threat_level: Current threat level from opponent
        
    Returns:
        tuple: (should_transition: bool, urgency: float)
    """
    stamina_pct = calculate_stamina_percentage(ai_character)
    base_threshold = config.AI_STAMINA_THRESHOLDS['EXHAUSTED']
    
    # Adjust threshold based on threat (if high threat, exhaust earlier)
    adjusted_threshold = base_threshold + (threat_level * 0.1)
    
    should_transition = stamina_pct < adjusted_threshold
    
    # Calculate urgency (0.0 to 1.0)
    if should_transition:
        urgency = 1.0 - (stamina_pct / adjusted_threshold)
        urgency = max(0.0, min(1.0, urgency))
    else:
        urgency = 0.0
    
    return should_transition, urgency


def should_transition_to_wounded(ai_character, opponent_character=None, threat_level=0.0, momentum=0.0):
    """
    Advanced check if AI should transition to Wounded state.
    Considers HP, threat, momentum, and opponent state.
    
    Args:
        ai_character: AI character object
        opponent_character: Opponent character object (optional)
        threat_level: Current threat level
        momentum: Current momentum score
        
    Returns:
        tuple: (should_transition: bool, severity: float)
    """
    health_pct = calculate_health_percentage(ai_character)
    base_threshold = config.AI_HEALTH_THRESHOLDS['WOUNDED']
    
    # Adjust threshold based on threat and momentum
    # High threat or negative momentum = transition earlier
    threshold_adjustment = (threat_level * 0.1) - (momentum * 0.05)
    adjusted_threshold = base_threshold + threshold_adjustment
    
    should_transition = health_pct < adjusted_threshold
    
    # Calculate severity (0.0 to 1.0)
    if should_transition:
        severity = 1.0 - (health_pct / adjusted_threshold)
        severity = max(0.0, min(1.0, severity))
    else:
        severity = 0.0
    
    return should_transition, severity


def should_transition_to_desperation(ai_character, opponent_character=None, threat_level=0.0, momentum=0.0):
    """
    Advanced check if AI should transition to Desperation state.
    Considers critical HP, opponent state, and last resort scenarios.
    
    Args:
        ai_character: AI character object
        opponent_character: Opponent character object (optional)
        threat_level: Current threat level
        momentum: Current momentum score
        
    Returns:
        tuple: (should_transition: bool, desperation_level: float)
    """
    health_pct = calculate_health_percentage(ai_character)
    base_threshold = config.AI_HEALTH_THRESHOLDS['DESPERATION']
    
    # In desperation, threshold is more strict (only very low HP)
    # But high threat can trigger it slightly earlier
    adjusted_threshold = base_threshold - (threat_level * 0.05)
    
    should_transition = health_pct < adjusted_threshold
    
    # Calculate desperation level (0.0 to 1.0)
    if should_transition:
        desperation = 1.0 - (health_pct / adjusted_threshold)
        # Boost desperation if momentum is very negative
        if momentum < -0.5:
            desperation = min(1.0, desperation + 0.2)
        desperation = max(0.0, min(1.0, desperation))
    else:
        desperation = 0.0
    
    return should_transition, desperation


def should_transition_to_finisher(opponent_character, ai_character=None, ai_stamina_pct=0.0):
    """
    Advanced check if AI should transition to Finisher state.
    Considers opponent HP, AI stamina, and kill potential.
    
    Args:
        opponent_character: Opponent (player) character object
        ai_character: AI character object (optional)
        ai_stamina_pct: AI stamina percentage
        
    Returns:
        tuple: (should_transition: bool, kill_potential: float)
    """
    opp_health_pct = calculate_health_percentage(opponent_character)
    base_threshold = config.AI_HEALTH_THRESHOLDS['FINISHER']
    
    # Adjust threshold based on AI stamina (need stamina to finish)
    # If AI has low stamina, be more aggressive about finishing
    stamina_factor = 1.0 - (ai_stamina_pct * 0.3)  # Lower stamina = lower threshold needed
    adjusted_threshold = base_threshold * stamina_factor
    
    should_transition = opp_health_pct < adjusted_threshold
    
    # Calculate kill potential (0.0 to 1.0)
    if should_transition:
        kill_potential = 1.0 - (opp_health_pct / adjusted_threshold)
        # Boost if AI has good stamina for special move
        if ai_stamina_pct > 0.5:
            kill_potential = min(1.0, kill_potential + 0.2)
        kill_potential = max(0.0, min(1.0, kill_potential))
    else:
        kill_potential = 0.0
    
    return should_transition, kill_potential


def should_transition_to_defensive(last_player_move, consecutive_heavy_attacks=0, threat_level=0.0, 
                                   player_move_history=None, ai_health_pct=1.0):
    """
    Advanced check if AI should transition to Defensive state.
    Considers threat level, player patterns, and AI health.
    
    Args:
        last_player_move: Last move the player performed
        consecutive_heavy_attacks: Number of consecutive heavy attacks
        threat_level: Current threat level
        player_move_history: Recent player move history
        ai_health_pct: AI health percentage
        
    Returns:
        tuple: (should_transition: bool, defensive_urgency: float)
    """
    defensive_score = 0.0
    
    # High threat level increases defensive need
    defensive_score += threat_level * 0.4
    
    # Player used special move (high threat)
    if last_player_move == 'special':
        defensive_score += 0.3
    
    # Multiple consecutive heavy attacks
    if consecutive_heavy_attacks >= 2:
        defensive_score += 0.2
    elif consecutive_heavy_attacks >= 1:
        defensive_score += 0.1
    
    # Low AI health increases defensive need
    if ai_health_pct < 0.4:
        defensive_score += 0.2
    elif ai_health_pct < 0.6:
        defensive_score += 0.1
    
    # Player pattern: aggressive sequence (punch, punch, special)
    if player_move_history is None:
        player_move_history = []
    # Convert to list if needed
    if not isinstance(player_move_history, list):
        player_move_history = list(player_move_history)
    
    if player_move_history and len(player_move_history) >= 3:
        recent = player_move_history[-3:]
        if recent.count('punch') >= 2 and 'special' in recent:
            defensive_score += 0.15
    
    should_transition = defensive_score >= 0.5
    defensive_urgency = min(1.0, defensive_score)
    
    return should_transition, defensive_urgency


def should_transition_to_counter(player_move_history, min_repeats=2, last_player_move=None):
    """
    Advanced check if AI should transition to Counter state.
    Detects patterns, sequences, and predictable behavior.
    
    Args:
        player_move_history: List of recent player moves
        min_repeats: Minimum number of repeated moves to trigger counter
        last_player_move: Last move player performed
        
    Returns:
        tuple: (should_transition: bool, pattern_strength: float)
    """
    if player_move_history is None:
        player_move_history = []
    
    # Convert to list if it's not already (handles deque, etc.)
    if not isinstance(player_move_history, list):
        player_move_history = list(player_move_history)
    
    if len(player_move_history) < min_repeats:
        return False, 0.0
    
    pattern_strength = 0.0
    
    # Pattern 1: Exact repetition (e.g., punch, punch, punch)
    last_moves = player_move_history[-min_repeats:]
    if len(set(last_moves)) == 1:
        pattern_strength = 0.8
        # Longer patterns = stronger
        if len(player_move_history) >= min_repeats + 1:
            if player_move_history[-(min_repeats + 1)] == last_moves[0]:
                pattern_strength = 1.0
    
    # Pattern 2: Alternating pattern (e.g., punch, block, punch, block)
    if len(player_move_history) >= 4:
        last_four = player_move_history[-4:]
        if last_four[0] == last_four[2] and last_four[1] == last_four[3] and last_four[0] != last_four[1]:
            pattern_strength = max(pattern_strength, 0.7)
    
    # Pattern 3: Sequence pattern (e.g., block, evade, special)
    if len(player_move_history) >= 3:
        last_three = player_move_history[-3:]
        # Defensive sequence
        if set(last_three) == {'block', 'evade'}:
            pattern_strength = max(pattern_strength, 0.6)
        # Aggressive sequence
        if 'punch' in last_three and 'special' in last_three:
            pattern_strength = max(pattern_strength, 0.65)
    
    should_transition = pattern_strength >= 0.6
    return should_transition, pattern_strength


def determine_next_state(current_state, ai_character, opponent_character, 
                         last_player_move=None, player_move_history=None, 
                         consecutive_heavy_attacks=0, state_persistence=0):
    """
    Advanced state determination using multi-factor analysis.
    Implements sophisticated decision-making with context awareness,
    threat assessment, momentum tracking, and state persistence.
    
    Args:
        current_state: Current FSMState object
        ai_character: AI character object
        opponent_character: Opponent (player) character object
        last_player_move: Last move the player performed
        player_move_history: List of recent player moves (for pattern detection)
        consecutive_heavy_attacks: Number of consecutive heavy attacks by player
        state_persistence: Number of turns in current state (for hysteresis)
        
    Returns:
        FSMState: Next state to transition to
    """
    if player_move_history is None:
        player_move_history = []
    
    # Calculate context factors
    ai_hp_pct = calculate_health_percentage(ai_character)
    ai_stam_pct = calculate_stamina_percentage(ai_character)
    opp_hp_pct = calculate_health_percentage(opponent_character)
    opp_stam_pct = calculate_stamina_percentage(opponent_character)
    
    threat_level = calculate_threat_level(ai_character, opponent_character, last_player_move)
    momentum = calculate_momentum(ai_character, opponent_character)
    hp_differential = calculate_health_differential(ai_character, opponent_character)
    
    # State transition scores (higher = more urgent to transition)
    transition_scores = {}
    
    # Priority 1: Exhausted (stamina-based, critical for survival)
    exhausted_check, exhausted_urgency = should_transition_to_exhausted(
        ai_character, opponent_character, threat_level
    )
    if exhausted_check:
        transition_scores['EXHAUSTED'] = exhausted_urgency * 10.0  # High priority
    
    # Priority 2: Desperation (critical HP, last resort)
    desperation_check, desperation_level = should_transition_to_desperation(
        ai_character, opponent_character, threat_level, momentum
    )
    if desperation_check:
        transition_scores['DESPERATION'] = desperation_level * 9.0  # Very high priority
    
    # Priority 3: Finisher (opponent vulnerable, go for kill)
    finisher_check, kill_potential = should_transition_to_finisher(
        opponent_character, ai_character, ai_stam_pct
    )
    if finisher_check:
        # Only transition if AI has enough stamina and special is off cooldown
        if ai_stam_pct > 0.3 and ai_character.can_use_special():
            # Boost score if AI is also healthy (can afford to be aggressive)
            finisher_score = kill_potential * 8.0
            if ai_hp_pct > 0.5:
                finisher_score *= 1.3  # 30% boost if AI is healthy
            transition_scores['FINISHER'] = finisher_score
    
    # Priority 4: Wounded (low HP, defensive play needed)
    wounded_check, wound_severity = should_transition_to_wounded(
        ai_character, opponent_character, threat_level, momentum
    )
    if wounded_check:
        transition_scores['WOUNDED'] = wound_severity * 7.0
    
    # Priority 5: Counter (player pattern detected)
    counter_check, pattern_strength = should_transition_to_counter(
        player_move_history, min_repeats=2, last_player_move=last_player_move
    )
    if counter_check:
        # Counter is more valuable if AI is healthy and can capitalize
        if ai_hp_pct > 0.4 and ai_stam_pct > 0.3:
            counter_score = pattern_strength * 6.0
            # Boost if player is being predictable with attacks
            if last_player_move in ['punch', 'special']:
                counter_score *= 1.2
            transition_scores['COUNTER'] = counter_score
    
    # Priority 6: Defensive (anticipate danger)
    defensive_check, defensive_urgency = should_transition_to_defensive(
        last_player_move, consecutive_heavy_attacks, threat_level,
        player_move_history, ai_hp_pct
    )
    if defensive_check:
        defensive_score = defensive_urgency * 5.0
        # Boost defensive if AI is low on HP (more urgent)
        if ai_hp_pct < 0.4:
            defensive_score *= 1.4
        # Boost if opponent has high stamina (can use special)
        if opp_stam_pct > 0.6:
            defensive_score *= 1.2
        transition_scores['DEFENSIVE'] = defensive_score
    
    # Priority 7: Aggressive (default, healthy state)
    # Score based on health, stamina, advantage, and momentum
    if ai_hp_pct > 0.5 and ai_stam_pct > 0.3:
        aggressive_score = (ai_hp_pct * 0.3) + (ai_stam_pct * 0.25) + (max(0, hp_differential) * 0.25) + (max(0, momentum) * 0.2)
        # Boost if AI has advantage
        if hp_differential > 0.1:
            aggressive_score *= 1.3
        # Boost if opponent is low on stamina (can't defend well)
        if opp_stam_pct < 0.3:
            aggressive_score *= 1.2
        transition_scores['AGGRESSIVE'] = aggressive_score * 4.0
    
    # State persistence (hysteresis) - prevent rapid state switching
    # If in a state for multiple turns, require higher score to leave
    if state_persistence > 0:
        persistence_factor = 1.0 + (state_persistence * 0.1)  # 10% bonus per turn
        current_state_name = current_state.name
        if current_state_name in transition_scores:
            transition_scores[current_state_name] *= persistence_factor
    
    # Select state with highest score
    if transition_scores:
        best_state = max(transition_scores.items(), key=lambda x: x[1])
        state_name = best_state[0]
        
        # Only transition if new state score is significantly better
        current_score = transition_scores.get(current_state.name, 0.0)
        new_score = best_state[1]
        
        # Require at least 20% improvement to switch (hysteresis)
        if new_score > current_score * 1.2 or current_state.name not in transition_scores:
            return STATES[state_name]
    
    # Stay in current state if conditions still apply
    # Check if current state conditions are still met
    if current_state == STATES['EXHAUSTED']:
        exhausted_check, _ = should_transition_to_exhausted(ai_character, opponent_character, threat_level)
        if not exhausted_check and ai_stam_pct > 0.4:
            return STATES['AGGRESSIVE']
        return STATES['EXHAUSTED']
    
    if current_state == STATES['DESPERATION']:
        desperation_check, _ = should_transition_to_desperation(ai_character, opponent_character, threat_level, momentum)
        if not desperation_check and ai_hp_pct > config.AI_HEALTH_THRESHOLDS['DESPERATION'] * 1.5:
            return STATES['WOUNDED']
        return STATES['DESPERATION']
    
    if current_state == STATES['WOUNDED']:
        wounded_check, _ = should_transition_to_wounded(ai_character, opponent_character, threat_level, momentum)
        if not wounded_check and ai_hp_pct > config.AI_HEALTH_THRESHOLDS['WOUNDED'] * 1.2:
            return STATES['AGGRESSIVE']
        return STATES['WOUNDED']
    
    if current_state == STATES['FINISHER']:
        finisher_check, _ = should_transition_to_finisher(opponent_character, ai_character, ai_stam_pct)
        if not finisher_check or opp_hp_pct > config.AI_HEALTH_THRESHOLDS['FINISHER'] * 1.2:
            return STATES['AGGRESSIVE']
        return STATES['FINISHER']
    
    if current_state == STATES['DEFENSIVE']:
        defensive_check, _ = should_transition_to_defensive(
            last_player_move, consecutive_heavy_attacks, threat_level, player_move_history, ai_hp_pct
        )
        if not defensive_check and threat_level < 0.3:
            return STATES['AGGRESSIVE']
        return STATES['DEFENSIVE']
    
    if current_state == STATES['COUNTER']:
        counter_check, _ = should_transition_to_counter(player_move_history, min_repeats=2, last_player_move=last_player_move)
        if not counter_check:
            return STATES['AGGRESSIVE']
        return STATES['COUNTER']
    
    # Default to aggressive
    return STATES['AGGRESSIVE']


def get_state_description(state):
    """
    Get a description of a state.
    
    Args:
        state: FSMState object or state name
        
    Returns:
        str: Description of the state
    """
    if isinstance(state, str):
        state = get_state(state)
    
    if state is None:
        return "Unknown state"
    
    return state.description


def get_state_action_weights(state):
    """
    Get action weights for a given state.
    
    Args:
        state: FSMState object or state name
        
    Returns:
        dict: Action weights for the state
    """
    if isinstance(state, FSMState):
        state_name = state.name.lower()
    else:
        state_name = str(state).lower()
    
    return config.AI_ACTION_WEIGHTS.get(state_name, config.AI_ACTION_WEIGHTS['aggressive'])


def list_all_states():
    """
    Get a list of all available states.
    
    Returns:
        list: List of FSMState objects
    """
    return list(STATES.values())


def get_state_priority(state):
    """
    Get priority of a state (for transition ordering).
    Lower number = higher priority.
    
    Args:
        state: FSMState object or state name
        
    Returns:
        int: Priority value
    """
    if isinstance(state, FSMState):
        state_name = state.name
    else:
        state_name = str(state).upper()
    
    priorities = {
        'EXHAUSTED': 1,
        'DESPERATION': 2,
        'FINISHER': 3,
        'WOUNDED': 4,
        'COUNTER': 5,
        'DEFENSIVE': 6,
        'AGGRESSIVE': 7
    }
    
    return priorities.get(state_name, 7)


def state_to_dict(state):
    """
    Convert FSMState object to dictionary for JSON serialization.
    
    Args:
        state: FSMState object or state name
        
    Returns:
        dict: Dictionary representation of the state
    """
    if isinstance(state, str):
        state = get_state(state)
    
    if state is None:
        return {
            'state': 'Unknown',
            'state_description': 'Unknown state',
            'state_name': 'UNKNOWN'
        }
    
    return {
        'state': state.name,
        'state_description': state.description,
        'state_name': state.name.upper()
    }


def get_state_info_dict(state, ai_character=None, opponent_character=None):
    """
    Get comprehensive state information as a dictionary for API responses.
    
    Args:
        state: FSMState object or state name
        ai_character: AI character object (optional, for additional context)
        opponent_character: Opponent character object (optional, for additional context)
        
    Returns:
        dict: Complete state information dictionary
    """
    state_dict = state_to_dict(state)
    
    # Add additional context if characters are provided
    if ai_character is not None:
        state_dict['health_percentage'] = calculate_health_percentage(ai_character)
        state_dict['stamina_percentage'] = calculate_stamina_percentage(ai_character)
    
    if opponent_character is not None and ai_character is not None:
        state_dict['health_differential'] = calculate_health_differential(ai_character, opponent_character)
        state_dict['threat_level'] = calculate_threat_level(ai_character, opponent_character, None)
    
    return state_dict

