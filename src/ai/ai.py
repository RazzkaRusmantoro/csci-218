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
        self.player_move_history = []  
        self.consecutive_heavy_attacks = 0  
        self.last_player_move = None
        self.turn_count = 0
        self.recent_damage_dealt = 0  
        self.recent_damage_taken = 0  
        self.current_state = fsm.DEFAULT_STATE  
        
    def update_state(self, opponent_character):
        """
        Update AI behavioral state using Finite State Machine.
        Tracks the AI's current strategic mindset (Aggressive, Defensive, etc.)
        while Fuzzy Logic handles the actual move selection.
        
        Args:
            opponent_character: Opponent (player) character object
        """
        
        
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
            
            pass
    
    def record_player_move(self, move_type):
        """
        Record the player's move for pattern detection.
        
        Args:
            move_type: Type of move player performed
        """
        self.last_player_move = move_type
        
        
        self.player_move_history.append(move_type)
        if len(self.player_move_history) > 5:
            self.player_move_history.pop(0)
        
        
        self.pattern_recognizer.record_move(move_type)
        
        
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
        
        threat_level = self._calculate_threat_level(opponent_character)
        
        
        pattern_info = self.pattern_recognizer.get_pattern_info()
        pattern_strength = pattern_info['pattern_strength']
        
        
        max_cooldown = 4  
        cooldown_ratio = 1.0 - (self.ai_character.special_move_cooldown / max_cooldown) if max_cooldown > 0 else 1.0
        cooldown_ratio = max(0.0, min(1.0, cooldown_ratio))
        
        
        action_probs = self.fuzzy_system.compute_action_probabilities(
            self.ai_character,
            opponent_character,
            threat_level=threat_level,
            last_player_move=self.last_player_move,
            pattern_strength=pattern_strength,
            cooldown_ratio=cooldown_ratio
        )
        
        
        if pattern_info['predicted_move']:
            predicted = pattern_info['predicted_move']
            if pattern_strength > 0.6:  
                
                if predicted in ['punch', 'kick'] and pattern_strength > 0.7:
                    action_probs['block'] = min(1.0, action_probs['block'] * 1.5)
                elif predicted == 'special' and pattern_strength > 0.7:
                    action_probs['evade'] = min(1.0, action_probs['evade'] * 1.4)
                elif predicted == 'block':
                    action_probs['special'] = min(1.0, action_probs['special'] * 1.3)  
        
        
        action_probs = self._apply_difficulty_modifiers_to_fuzzy(action_probs)
        
        
        available_actions = {}
        for action, prob in action_probs.items():
            if action == 'special':
                
                if self.ai_character.can_use_special():
                    
                    char_name = self.ai_character.name.lower()
                    required_stamina = config.SPECIAL_STAMINA_COSTS.get(char_name, 30)  
                    if self.ai_character.stamina >= required_stamina:
                        available_actions[action] = prob
                    
            elif action == 'rest':
                
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
        
        
        if not available_actions:
            return 'rest'
        
        
        if len(available_actions) == 1 and 'rest' in available_actions:
            return 'rest'
        
        
        total = sum(available_actions.values())
        if total > 0:
            for action in available_actions:
                available_actions[action] = available_actions[action] / total
        else:
            
            for action in available_actions:
                available_actions[action] = 1.0 / len(available_actions)
        
        
        selected_action = utils.weighted_choice(available_actions)
        
        
        
        if selected_action != 'rest':
            if selected_action == 'special':
                
                char_name = self.ai_character.name.lower()
                required_stamina = config.SPECIAL_STAMINA_COSTS.get(char_name, 30)
                if not self.ai_character.can_use_special() or self.ai_character.stamina < required_stamina:
                    return 'rest'
            else:
                
                can_perform, _ = moves.can_perform_move(self.ai_character, selected_action)
                if not can_perform:
                    return 'rest'
        
        
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
        
        
        opp_health_pct = fsm.calculate_health_percentage(opponent_character)
        opp_stam_pct = fsm.calculate_stamina_percentage(opponent_character)
        
        
        health_threat = (1.0 - opp_health_pct) * 0.4  
        stamina_threat = opp_stam_pct * 0.4  
        
        
        action_threat = 0.2
        if self.last_player_move == 'special':
            action_threat = 0.8  
        elif self.last_player_move in ['punch', 'kick']:
            action_threat = 0.4  
        elif self.last_player_move == 'rest':
            action_threat = 0.1  
        
        
        threat = health_threat + stamina_threat + action_threat
        
        
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
            
            if not result.get('success', False) and 'stamina' in result.get('message', '').lower():
                result = moves.rest(self.ai_character)
                result['message'] = f"{self.ai_character.name} rests (insufficient stamina for special move)"
        else:
            result = {
                'success': False,
                'message': f"Unknown action: {action}",
                'damage': 0
            }
        
        
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
        
        
        opponent_hp_before = opponent_character.hp
        
        
        action = self.select_action(opponent_character)
        
        
        result = self.execute_action(action, opponent_character)
        
        
        damage_dealt = opponent_hp_before - opponent_character.hp
        if damage_dealt > 0:
            self.recent_damage_dealt = damage_dealt
        else:
            
            self.recent_damage_dealt = max(0, self.recent_damage_dealt - 5)
        
        
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
            
            self.recent_damage_taken = max(0, self.recent_damage_taken - 5)
    
    def get_state_info(self):
        """
        Get information about current AI state.
        
        Returns:
            dict: State information
        """
        
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
        
        self.update_state(opponent_character)
        
        
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

