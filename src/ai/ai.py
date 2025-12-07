"""
AI controller for the Turn-Based Fighter Game.
Uses Fuzzy Logic for intelligent decision-making with uncertainty handling.
"""

import random
from src.ai import fsm, fuzzy_logic, pattern_recognition
from src.core import moves
from src.utils import utils, config


class AIController:
    """AI controller that uses Fuzzy Logic for intelligent decision-making."""
    
    def __init__(self, ai_character, difficulty='medium'):
        """
        Initialize AI controller.
        
        Args:
            ai_character: Character object controlled by AI
            difficulty: Difficulty level ('easy', 'medium', 'hard')
        """
        self.ai_character = ai_character
        self.difficulty = difficulty.lower()
        self.fuzzy_system = fuzzy_logic.get_fuzzy_system()
        self.pattern_recognizer = pattern_recognition.PatternRecognizer(history_size=5)
        self.player_move_history = []  # Track last few player moves
        self.consecutive_heavy_attacks = 0  # Track consecutive heavy attacks
        self.last_player_move = None
        self.turn_count = 0
        self.recent_damage_dealt = 0  # Track recent damage for momentum
        self.recent_damage_taken = 0  # Track recent damage taken
        self.current_state = fsm.DEFAULT_STATE  # Track AI behavioral state (FSM)
        
    def update_state(self, opponent_character):
        """
        Update AI behavioral state using Finite State Machine.
        Tracks the AI's current strategic mindset (Aggressive, Defensive, etc.)
        while Fuzzy Logic handles the actual move selection.
        
        Args:
            opponent_character: Opponent (player) character object
        """
        # Update FSM state to reflect current AI behavioral state
        # FSM provides strategic context; Fuzzy Logic handles action selection
        try:
            new_state = fsm.determine_next_state(
                current_state=self.current_state,
                ai_character=self.ai_character,
                opponent_character=opponent_character,
                last_player_move=self.last_player_move,
                player_move_history=self.player_move_history,
                consecutive_heavy_attacks=self.consecutive_heavy_attacks,
                state_persistence=0
            )
            self.current_state = new_state
        except:
            # If FSM fails, keep current state
            pass
    
    def record_player_move(self, move_type):
        """
        Record the player's move for pattern detection.
        
        Args:
            move_type: Type of move player performed
        """
        self.last_player_move = move_type
        
        # Add to history (keep last 5 moves)
        self.player_move_history.append(move_type)
        if len(self.player_move_history) > 5:
            self.player_move_history.pop(0)
        
        # Record in pattern recognizer
        self.pattern_recognizer.record_move(move_type)
        
        # Track consecutive heavy attacks
        if move_type in ['special', 'kick']:
            self.consecutive_heavy_attacks += 1
        else:
            self.consecutive_heavy_attacks = 0
    
    def select_action(self, opponent_character):
        """
        Intelligently select an action using Fuzzy Logic.
        Handles uncertainty and approximate reasoning for better decision-making.
        
        Args:
            opponent_character: Opponent (player) character object
            
        Returns:
            str: Selected action type ('punch', 'block', 'evade', 'special', 'rest')
        """
        # Calculate threat level based on opponent's state
        threat_level = self._calculate_threat_level(opponent_character)
        
        # Get pattern recognition info
        pattern_info = self.pattern_recognizer.get_pattern_info()
        pattern_strength = pattern_info['pattern_strength']
        
        # Calculate cooldown ratio (1.0 = ready, 0.0 = just used)
        max_cooldown = 4  # From config
        cooldown_ratio = 1.0 - (self.ai_character.special_move_cooldown / max_cooldown) if max_cooldown > 0 else 1.0
        cooldown_ratio = max(0.0, min(1.0, cooldown_ratio))
        
        # Get fuzzy logic action probabilities (now with pattern and cooldown)
        action_probs = self.fuzzy_system.compute_action_probabilities(
            self.ai_character,
            opponent_character,
            threat_level=threat_level,
            last_player_move=self.last_player_move,
            pattern_strength=pattern_strength,
            cooldown_ratio=cooldown_ratio
        )
        
        # Apply pattern-based adjustments
        if pattern_info['predicted_move']:
            predicted = pattern_info['predicted_move']
            if pattern_strength > 0.6:  # Strong pattern detected
                # Boost counter moves
                if predicted in ['punch', 'kick'] and pattern_strength > 0.7:
                    action_probs['block'] = min(1.0, action_probs['block'] * 1.5)
                elif predicted == 'special' and pattern_strength > 0.7:
                    action_probs['evade'] = min(1.0, action_probs['evade'] * 1.4)
                elif predicted == 'block':
                    action_probs['special'] = min(1.0, action_probs['special'] * 1.3)  # Special ignores block
        
        # Apply difficulty modifiers to probabilities
        action_probs = self._apply_difficulty_modifiers_to_fuzzy(action_probs)
        
        # Filter out actions that can't be performed and adjust probabilities
        available_actions = {}
        for action, prob in action_probs.items():
            if action == 'special':
                # Check if special move is available (cooldown AND stamina)
                if self.ai_character.can_use_special():
                    # Also check if we have enough stamina for the special move
                    char_name = self.ai_character.name.lower()
                    required_stamina = config.SPECIAL_STAMINA_COSTS.get(char_name, 30)  # Default to 30 if not found
                    if self.ai_character.stamina >= required_stamina:
                        available_actions[action] = prob
                    # If not enough stamina, don't include it at all (will default to rest)
            elif action == 'rest':
                # Rest is always available
                available_actions[action] = prob
            elif action == 'punch':
                can_perform, _ = moves.can_perform_move(self.ai_character, 'punch')
                if can_perform:
                    available_actions[action] = prob
            elif action == 'kick':
                can_perform, _ = moves.can_perform_move(self.ai_character, 'kick')
                if can_perform:
                    available_actions[action] = prob
            elif action == 'block':
                can_perform, _ = moves.can_perform_move(self.ai_character, 'block')
                if can_perform:
                    available_actions[action] = prob
            elif action == 'evade':
                can_perform, _ = moves.can_perform_move(self.ai_character, 'evade')
                if can_perform:
                    available_actions[action] = prob
        
        # If no actions available (except rest), default to rest
        if not available_actions:
            return 'rest'
        
        # If only rest is available, just return rest immediately
        if len(available_actions) == 1 and 'rest' in available_actions:
            return 'rest'
        
        # Normalize probabilities
        total = sum(available_actions.values())
        if total > 0:
            for action in available_actions:
                available_actions[action] = available_actions[action] / total
        else:
            # Fallback: equal probabilities
            for action in available_actions:
                available_actions[action] = 1.0 / len(available_actions)
        
        # Select action based on fuzzy probabilities
        selected_action = utils.weighted_choice(available_actions)
        
        # Final safety check: verify the selected action can actually be performed
        # This prevents any edge cases where an invalid move might slip through
        if selected_action != 'rest':
            if selected_action == 'special':
                # Double-check special move requirements
                char_name = self.ai_character.name.lower()
                required_stamina = config.SPECIAL_STAMINA_COSTS.get(char_name, 30)
                if not self.ai_character.can_use_special() or self.ai_character.stamina < required_stamina:
                    return 'rest'
            else:
                # For other moves, verify they can be performed
                can_perform, _ = moves.can_perform_move(self.ai_character, selected_action)
                if not can_perform:
                    return 'rest'
        
        # Update FSM state to track current behavioral state
        self.update_state(opponent_character)
        
        return selected_action
    
    def _calculate_threat_level(self, opponent_character):
        """
        Calculate threat level based on opponent's state.
        
        Args:
            opponent_character: Opponent character object
            
        Returns:
            float: Threat level (0.0 to 1.0)
        """
        from src.ai import fsm
        
        # Base threat on opponent's health, stamina, and recent actions
        opp_health_pct = fsm.calculate_health_percentage(opponent_character)
        opp_stam_pct = fsm.calculate_stamina_percentage(opponent_character)
        
        # Opponent with high health and stamina is more threatening
        health_threat = (1.0 - opp_health_pct) * 0.4  # Lower health = less threat
        stamina_threat = opp_stam_pct * 0.4  # Higher stamina = more threat
        
        # Recent player actions affect threat
        action_threat = 0.2
        if self.last_player_move == 'special':
            action_threat = 0.8  # Special moves are very threatening
        elif self.last_player_move in ['punch', 'kick']:
            action_threat = 0.4  # Basic attacks are moderately threatening
        elif self.last_player_move == 'rest':
            action_threat = 0.1  # Resting is less threatening
        
        # Combine threats
        threat = health_threat + stamina_threat + action_threat
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, threat))
    
    def _apply_difficulty_modifiers_to_fuzzy(self, action_probs):
        """
        Apply difficulty modifiers to fuzzy logic probabilities.
        
        Args:
            action_probs: Dictionary of action probabilities from fuzzy logic
            
        Returns:
            dict: Modified action probabilities
        """
        if self.difficulty not in config.DIFFICULTY_MODIFIERS:
            return action_probs
        
        # Get base modifiers (use 'aggressive' state as default)
        modifiers = config.DIFFICULTY_MODIFIERS[self.difficulty].get('aggressive', {})
        
        modified_probs = {}
        for action, prob in action_probs.items():
            modifier = modifiers.get(action, 1.0)
            modified_probs[action] = prob * modifier
        
        return modified_probs
    
    
    def set_difficulty(self, difficulty):
        """
        Set the difficulty level.
        
        Args:
            difficulty: Difficulty level ('easy', 'medium', 'hard')
        """
        self.difficulty = difficulty.lower()
    
    def execute_action(self, action, opponent_character):
        """
        Execute the selected action.
        
        Args:
            action: Action type to execute
            opponent_character: Opponent (player) character object
            
        Returns:
            dict: Result of the action execution
        """
        if action == 'punch':
            result = moves.punch(self.ai_character, opponent_character)
        elif action == 'kick':
            result = moves.kick(self.ai_character, opponent_character)
        elif action == 'block':
            result = moves.block(self.ai_character)
        elif action == 'evade':
            result = moves.evade(self.ai_character)
        elif action == 'rest':
            result = moves.rest(self.ai_character)
        elif action == 'special':
            result = self.ai_character.use_special_move_with_cooldown(opponent_character)
            # Safety check: if special move failed due to stamina, fall back to rest
            if not result.get('success', False) and 'stamina' in result.get('message', '').lower():
                result = moves.rest(self.ai_character)
                result['message'] = f"{self.ai_character.name} rests (insufficient stamina for special move)"
        else:
            result = {
                'success': False,
                'message': f"Unknown action: {action}",
                'damage': 0
            }
        
        # Add state information to result
        result['ai_state'] = str(self.current_state)
        result['ai_state_description'] = 'Fuzzy Logic Decision-Making'
        
        return result
    
    def make_move(self, opponent_character):
        """
        Complete AI turn: select and execute an action.
        
        Args:
            opponent_character: Opponent (player) character object
            
        Returns:
            dict: Result of the AI's move
        """
        self.turn_count += 1
        
        # Track damage before move
        opponent_hp_before = opponent_character.hp
        
        # Select action
        action = self.select_action(opponent_character)
        
        # Execute action
        result = self.execute_action(action, opponent_character)
        
        # Track damage dealt
        damage_dealt = opponent_hp_before - opponent_character.hp
        if damage_dealt > 0:
            self.recent_damage_dealt = damage_dealt
        else:
            # Decay recent damage
            self.recent_damage_dealt = max(0, self.recent_damage_dealt - 5)
        
        # Add action type to result
        result['action_type'] = action
        
        return result
    
    def record_damage_taken(self, damage):
        """
        Record damage taken for momentum calculation.
        
        Args:
            damage: Amount of damage taken
        """
        if damage > 0:
            self.recent_damage_taken = damage
        else:
            # Decay recent damage
            self.recent_damage_taken = max(0, self.recent_damage_taken - 5)
    
    def get_state_info(self):
        """
        Get information about current AI state.
        
        Returns:
            dict: State information
        """
        # Use FSM helper function for consistent state serialization
        state_dict = fsm.state_to_dict(self.current_state)
        state_dict['health_percentage'] = fsm.calculate_health_percentage(self.ai_character)
        state_dict['stamina_percentage'] = fsm.calculate_stamina_percentage(self.ai_character)
        state_dict['turn_count'] = self.turn_count
        return state_dict
    
    def reset(self):
        """Reset AI controller to initial state."""
        self.current_state = fsm.DEFAULT_STATE
        self.player_move_history = []
        self.consecutive_heavy_attacks = 0
        self.last_player_move = None
        self.turn_count = 0
    
    def get_debug_info(self, opponent_character):
        """
        Get debug information about AI decision-making using fuzzy logic.
        
        Args:
            opponent_character: Opponent (player) character object
            
        Returns:
            dict: Debug information
        """
        # Update FSM state
        self.update_state(opponent_character)
        
        # Get fuzzy logic probabilities
        threat_level = self._calculate_threat_level(opponent_character)
        action_probs = self.fuzzy_system.compute_action_probabilities(
            self.ai_character,
            opponent_character,
            threat_level=threat_level,
            last_player_move=self.last_player_move
        )
        
        return {
            'current_state': str(self.current_state),
            'state_description': 'Fuzzy Logic Decision-Making',
            'action_probabilities': action_probs,
            'threat_level': threat_level,
            'health_percentage': fsm.calculate_health_percentage(self.ai_character),
            'stamina_percentage': fsm.calculate_stamina_percentage(self.ai_character),
            'opponent_health_percentage': fsm.calculate_health_percentage(opponent_character),
            'player_move_history': self.player_move_history.copy(),
            'consecutive_heavy_attacks': self.consecutive_heavy_attacks,
            'last_player_move': self.last_player_move,
            'ai_type': 'Fuzzy Logic'
        }

