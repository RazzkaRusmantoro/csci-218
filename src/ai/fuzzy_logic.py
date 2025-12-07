"""
Fuzzy Logic System for AI Decision-Making in Turn-Based Fighter Game.
Handles uncertainty and approximate reasoning for intelligent AI behavior.

Uses fuzzy membership functions and rules to determine action probabilities
based on game state variables (health, stamina, threat, etc.).
"""

import math
from src.utils import config


class FuzzyVariable:
    """Represents a fuzzy variable with membership functions."""
    
    def __init__(self, name, min_val, max_val):
        """
        Initialize a fuzzy variable.
        
        Args:
            name: Name of the variable
            min_val: Minimum possible value
            max_val: Maximum possible value
        """
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.membership_functions = {}
    
    def add_membership_function(self, name, func_type, params):
        """
        Add a membership function to this variable.
        
        Args:
            name: Name of the membership function (e.g., 'low', 'medium', 'high')
            func_type: Type of function ('triangular', 'trapezoidal', 'gaussian')
            params: Parameters for the function
        """
        self.membership_functions[name] = {
            'type': func_type,
            'params': params
        }
    
    def get_membership(self, value, func_name):
        """
        Get membership value for a given crisp value.
        
        Args:
            value: Crisp input value
            func_name: Name of the membership function
            
        Returns:
            float: Membership value (0.0 to 1.0)
        """
        if func_name not in self.membership_functions:
            return 0.0
        
        func = self.membership_functions[func_name]
        func_type = func['type']
        params = func['params']
        
        
        value = max(self.min_val, min(self.max_val, value))
        
        if func_type == 'triangular':
            a, b, c = params  
            if value <= a or value >= c:
                return 0.0
            elif value < b:
                return (value - a) / (b - a) if b != a else 1.0
            else:
                return (c - value) / (c - b) if c != b else 1.0
        
        elif func_type == 'trapezoidal':
            a, b, c, d = params  
            if value <= a or value >= d:
                return 0.0
            elif a < value < b:
                return (value - a) / (b - a) if b != a else 1.0
            elif b <= value <= c:
                return 1.0
            else:  
                return (d - value) / (d - c) if d != c else 1.0
        
        elif func_type == 'gaussian':
            center, width = params
            return math.exp(-0.5 * ((value - center) / width) ** 2)
        
        return 0.0
    
    def fuzzify(self, value):
        """
        Convert a crisp value to fuzzy membership values.
        
        Args:
            value: Crisp input value
            
        Returns:
            dict: Dictionary of membership values for each function
        """
        result = {}
        for func_name in self.membership_functions:
            result[func_name] = self.get_membership(value, func_name)
        return result


class FuzzyRule:
    """Represents a fuzzy rule (IF-THEN statement)."""
    
    def __init__(self, conditions, conclusion, weight=1.0):
        """
        Initialize a fuzzy rule.
        
        Args:
            conditions: List of (variable, membership_func) tuples for IF part
            conclusion: (variable, membership_func) tuple for THEN part
            weight: Rule weight (0.0 to 1.0)
        """
        self.conditions = conditions  
        self.conclusion = conclusion  
        self.weight = weight
    
    def evaluate(self, fuzzy_values):
        """
        Evaluate this rule given fuzzy input values.
        
        Args:
            fuzzy_values: Dictionary of {variable_name: {func_name: membership_value}}
            
        Returns:
            float: Firing strength of the rule (0.0 to 1.0)
        """
        if not self.conditions:
            return self.weight
        
        
        firing_strength = 1.0
        for var_name, func_name in self.conditions:
            if var_name in fuzzy_values:
                membership = fuzzy_values[var_name].get(func_name, 0.0)
                firing_strength = min(firing_strength, membership)
            else:
                return 0.0  
        
        return firing_strength * self.weight


class FuzzyLogicSystem:
    """Main fuzzy logic system for AI decision-making."""
    
    def __init__(self):
        """Initialize the fuzzy logic system with variables and rules."""
        self.variables = {}
        self.rules = []
        self._setup_variables()
        self._setup_rules()
    
    def _setup_variables(self):
        """Set up fuzzy variables with membership functions."""
        
        
        health = FuzzyVariable('health', 0.0, 1.0)
        health.add_membership_function('very_low', 'triangular', (0.0, 0.0, 0.2))
        health.add_membership_function('low', 'triangular', (0.1, 0.3, 0.5))
        health.add_membership_function('medium', 'triangular', (0.4, 0.6, 0.8))
        health.add_membership_function('high', 'triangular', (0.7, 0.9, 1.0))
        health.add_membership_function('very_high', 'triangular', (0.8, 1.0, 1.0))
        self.variables['ai_health'] = health
        self.variables['opponent_health'] = health  
        
        
        stamina = FuzzyVariable('stamina', 0.0, 1.0)
        stamina.add_membership_function('very_low', 'triangular', (0.0, 0.0, 0.25))
        stamina.add_membership_function('low', 'triangular', (0.15, 0.35, 0.55))
        stamina.add_membership_function('medium', 'triangular', (0.45, 0.65, 0.85))
        stamina.add_membership_function('high', 'triangular', (0.75, 0.9, 1.0))
        stamina.add_membership_function('very_high', 'triangular', (0.9, 1.0, 1.0))
        self.variables['ai_stamina'] = stamina
        self.variables['opponent_stamina'] = stamina
        
        
        health_diff = FuzzyVariable('health_differential', -1.0, 1.0)
        health_diff.add_membership_function('large_disadvantage', 'triangular', (-1.0, -0.5, 0.0))
        health_diff.add_membership_function('disadvantage', 'triangular', (-0.3, -0.1, 0.1))
        health_diff.add_membership_function('even', 'triangular', (-0.1, 0.0, 0.1))
        health_diff.add_membership_function('advantage', 'triangular', (-0.1, 0.1, 0.3))
        health_diff.add_membership_function('large_advantage', 'triangular', (0.0, 0.5, 1.0))
        self.variables['health_differential'] = health_diff
        
        
        threat = FuzzyVariable('threat', 0.0, 1.0)
        threat.add_membership_function('very_low', 'triangular', (0.0, 0.0, 0.3))
        threat.add_membership_function('low', 'triangular', (0.2, 0.4, 0.6))
        threat.add_membership_function('medium', 'triangular', (0.5, 0.7, 0.9))
        threat.add_membership_function('high', 'triangular', (0.8, 1.0, 1.0))
        self.variables['threat'] = threat
        
        
        pattern = FuzzyVariable('pattern_strength', 0.0, 1.0)
        pattern.add_membership_function('none', 'triangular', (0.0, 0.0, 0.3))
        pattern.add_membership_function('weak', 'triangular', (0.2, 0.4, 0.6))
        pattern.add_membership_function('strong', 'triangular', (0.5, 0.8, 1.0))
        pattern.add_membership_function('very_strong', 'triangular', (0.7, 1.0, 1.0))
        self.variables['pattern_strength'] = pattern
        
        
        cooldown = FuzzyVariable('cooldown_status', 0.0, 1.0)
        cooldown.add_membership_function('not_ready', 'triangular', (0.0, 0.0, 0.5))
        cooldown.add_membership_function('almost_ready', 'triangular', (0.3, 0.6, 0.9))
        cooldown.add_membership_function('ready', 'triangular', (0.7, 1.0, 1.0))
        self.variables['cooldown_status'] = cooldown
        
        
        action_prob = FuzzyVariable('action_probability', 0.0, 1.0)
        action_prob.add_membership_function('very_low', 'triangular', (0.0, 0.0, 0.25))
        action_prob.add_membership_function('low', 'triangular', (0.15, 0.35, 0.55))
        action_prob.add_membership_function('medium', 'triangular', (0.45, 0.65, 0.85))
        action_prob.add_membership_function('high', 'triangular', (0.75, 0.9, 1.0))
        action_prob.add_membership_function('very_high', 'triangular', (0.9, 1.0, 1.0))
        
        self.variables['punch_prob'] = action_prob
        self.variables['kick_prob'] = action_prob
        self.variables['special_prob'] = action_prob
        self.variables['block_prob'] = action_prob
        self.variables['evade_prob'] = action_prob
        self.variables['rest_prob'] = action_prob
    
    def _setup_rules(self):
        """Set up fuzzy rules for decision-making."""
        
        
        self.rules.append(FuzzyRule(
            [('ai_health', 'very_low'), ('ai_stamina', 'high')],
            ('rest_prob', 'very_high'),
            weight=1.0
        ))
        
        
        self.rules.append(FuzzyRule(
            [('ai_stamina', 'very_low')],
            ('rest_prob', 'very_high'),
            weight=1.0
        ))
        
        
        self.rules.append(FuzzyRule(
            [('ai_health', 'high'), ('ai_stamina', 'high'), ('opponent_health', 'low')],
            ('special_prob', 'very_high'),
            weight=1.0
        ))
        
        
        self.rules.append(FuzzyRule(
            [('ai_health', 'high'), ('ai_stamina', 'medium'), ('health_differential', 'advantage')],
            ('punch_prob', 'high'),
            weight=0.9
        ))
        
        
        self.rules.append(FuzzyRule(
            [('ai_health', 'high'), ('ai_stamina', 'high'), ('opponent_health', 'medium')],
            ('kick_prob', 'high'),
            weight=0.8
        ))
        
        
        self.rules.append(FuzzyRule(
            [('threat', 'high'), ('ai_health', 'medium')],
            ('block_prob', 'high'),
            weight=0.9
        ))
        
        
        self.rules.append(FuzzyRule(
            [('threat', 'high'), ('ai_health', 'low')],
            ('evade_prob', 'high'),
            weight=0.9
        ))
        
        
        self.rules.append(FuzzyRule(
            [('health_differential', 'large_advantage'), ('ai_stamina', 'high')],
            ('special_prob', 'high'),
            weight=0.85
        ))
        
        
        self.rules.append(FuzzyRule(
            [('health_differential', 'large_disadvantage'), ('ai_stamina', 'medium')],
            ('block_prob', 'very_high'),
            weight=0.9
        ))
        
        
        self.rules.append(FuzzyRule(
            [('opponent_health', 'very_low'), ('ai_stamina', 'high')],
            ('special_prob', 'very_high'),
            weight=1.0
        ))
        
        
        self.rules.append(FuzzyRule(
            [('ai_health', 'medium'), ('ai_stamina', 'medium'), ('threat', 'low')],
            ('punch_prob', 'medium'),
            weight=0.8
        ))
        
        
        self.rules.append(FuzzyRule(
            [('ai_stamina', 'low'), ('ai_health', 'high')],
            ('rest_prob', 'medium'),
            weight=0.7
        ))
        
        
        self.rules.append(FuzzyRule(
            [('health_differential', 'even'), ('ai_stamina', 'high')],
            ('special_prob', 'medium'),
            weight=0.75
        ))
        
        
        self.rules.append(FuzzyRule(
            [('threat', 'medium'), ('ai_health', 'high')],
            ('punch_prob', 'high'),
            weight=0.85
        ))
        
        
        self.rules.append(FuzzyRule(
            [('ai_health', 'very_low'), ('opponent_health', 'high')],
            ('evade_prob', 'very_high'),
            weight=0.9
        ))
        
        
        self.rules.append(FuzzyRule(
            [('ai_stamina', 'very_high'), ('opponent_health', 'medium')],
            ('punch_prob', 'high'),
            weight=0.8
        ))
        
        
        self.rules.append(FuzzyRule(
            [('pattern_strength', 'strong')],
            ('block_prob', 'high'),
            weight=0.85
        ))
        
        
        self.rules.append(FuzzyRule(
            [('pattern_strength', 'very_strong'), ('threat', 'high')],
            ('evade_prob', 'very_high'),
            weight=0.9
        ))
        
        
        self.rules.append(FuzzyRule(
            [('cooldown_status', 'ready'), ('opponent_health', 'low')],
            ('special_prob', 'very_high'),
            weight=1.0
        ))
        
        
        self.rules.append(FuzzyRule(
            [('cooldown_status', 'not_ready'), ('ai_stamina', 'high')],
            ('punch_prob', 'high'),
            weight=0.75
        ))
        
        
        self.rules.append(FuzzyRule(
            [('pattern_strength', 'strong'), ('health_differential', 'disadvantage')],
            ('block_prob', 'very_high'),
            weight=0.9
        ))
        
        
        self.rules.append(FuzzyRule(
            [('opponent_health', 'very_low'), ('ai_stamina', 'medium')],
            ('punch_prob', 'very_high'),
            weight=1.0
        ))
        self.rules.append(FuzzyRule(
            [('opponent_health', 'very_low'), ('ai_stamina', 'high')],
            ('punch_prob', 'very_high'),
            weight=1.0
        ))
        self.rules.append(FuzzyRule(
            [('opponent_health', 'very_low'), ('ai_stamina', 'very_high')],
            ('punch_prob', 'very_high'),
            weight=1.0
        ))
        
        
        self.rules.append(FuzzyRule(
            [('opponent_health', 'low'), ('ai_stamina', 'high'), ('cooldown_status', 'not_ready')],
            ('punch_prob', 'high'),
            weight=0.9
        ))
        self.rules.append(FuzzyRule(
            [('opponent_health', 'low'), ('ai_stamina', 'very_high'), ('cooldown_status', 'not_ready')],
            ('kick_prob', 'high'),
            weight=0.85
        ))
        
        
        self.rules.append(FuzzyRule(
            [('opponent_health', 'low'), ('health_differential', 'advantage'), ('ai_stamina', 'medium')],
            ('punch_prob', 'high'),
            weight=0.9
        ))
        self.rules.append(FuzzyRule(
            [('opponent_health', 'low'), ('health_differential', 'large_advantage'), ('ai_stamina', 'high')],
            ('kick_prob', 'high'),
            weight=0.9
        ))
    
    def fuzzify_inputs(self, ai_character, opponent_character, threat_level=0.5, 
                       pattern_strength=0.0, cooldown_ratio=1.0):
        """
        Convert crisp game state values to fuzzy membership values.
        
        Args:
            ai_character: AI character object
            opponent_character: Opponent character object
            threat_level: Threat level (0.0 to 1.0)
            pattern_strength: Pattern recognition strength (0.0 to 1.0)
            cooldown_ratio: Cooldown status (1.0 = ready, 0.0 = just used)
            
        Returns:
            dict: Fuzzy membership values for all input variables
        """
        from src.ai import fsm
        
        ai_health_pct = fsm.calculate_health_percentage(ai_character)
        ai_stam_pct = fsm.calculate_stamina_percentage(ai_character)
        opp_health_pct = fsm.calculate_health_percentage(opponent_character)
        opp_stam_pct = fsm.calculate_stamina_percentage(opponent_character)
        health_diff = fsm.calculate_health_differential(ai_character, opponent_character)
        
        fuzzy_values = {
            'ai_health': self.variables['ai_health'].fuzzify(ai_health_pct),
            'ai_stamina': self.variables['ai_stamina'].fuzzify(ai_stam_pct),
            'opponent_health': self.variables['opponent_health'].fuzzify(opp_health_pct),
            'opponent_stamina': self.variables['opponent_stamina'].fuzzify(opp_stam_pct),
            'health_differential': self.variables['health_differential'].fuzzify(health_diff),
            'threat': self.variables['threat'].fuzzify(threat_level),
            'pattern_strength': self.variables['pattern_strength'].fuzzify(pattern_strength),
            'cooldown_status': self.variables['cooldown_status'].fuzzify(cooldown_ratio)
        }
        
        return fuzzy_values
    
    def evaluate_rules(self, fuzzy_values):
        """
        Evaluate all fuzzy rules and get output membership values.
        
        Args:
            fuzzy_values: Dictionary of fuzzy input values
            
        Returns:
            dict: Dictionary of output membership values for each action
        """
        output_memberships = {
            'punch_prob': {},
            'kick_prob': {},
            'special_prob': {},
            'block_prob': {},
            'evade_prob': {},
            'rest_prob': {}
        }
        
        for rule in self.rules:
            firing_strength = rule.evaluate(fuzzy_values)
            if firing_strength > 0:
                var_name, func_name = rule.conclusion
                if var_name in output_memberships:
                    
                    current = output_memberships[var_name].get(func_name, 0.0)
                    output_memberships[var_name][func_name] = max(current, firing_strength)
        
        return output_memberships
    
    def defuzzify(self, output_memberships, method='centroid'):
        """
        Convert fuzzy output membership values to crisp probabilities.
        
        Args:
            output_memberships: Dictionary of output membership values
            method: Defuzzification method ('centroid' or 'max')
            
        Returns:
            dict: Dictionary of crisp probabilities for each action
        """
        results = {}
        
        for var_name, memberships in output_memberships.items():
            if not memberships:
                results[var_name] = 0.0
                continue
            
            if method == 'centroid':
                
                total_area = 0.0
                weighted_sum = 0.0
                
                var = self.variables[var_name]
                
                num_samples = 100
                step = (var.max_val - var.min_val) / num_samples
                
                for i in range(num_samples + 1):
                    x = var.min_val + i * step
                    
                    max_membership = 0.0
                    for func_name, membership_value in memberships.items():
                        membership = var.get_membership(x, func_name)
                        max_membership = max(max_membership, min(membership, membership_value))
                    
                    total_area += max_membership
                    weighted_sum += x * max_membership
                
                if total_area > 0:
                    results[var_name] = weighted_sum / total_area
                else:
                    results[var_name] = 0.0
            
            elif method == 'max':
                
                max_value = 0.0
                best_func = None
                for func_name, membership_value in memberships.items():
                    if membership_value > max_value:
                        max_value = membership_value
                        best_func = func_name
                
                if best_func:
                    
                    var = self.variables[var_name]
                    func = var.membership_functions[best_func]
                    if func['type'] == 'triangular':
                        _, center, _ = func['params']
                        results[var_name] = center
                    else:
                        results[var_name] = max_value
                else:
                    results[var_name] = 0.0
        
        return results
    
    def compute_action_probabilities(self, ai_character, opponent_character, 
                                     threat_level=0.5, last_player_move=None,
                                     pattern_strength=0.0, cooldown_ratio=1.0):
        """
        Compute action probabilities using fuzzy logic.
        
        Args:
            ai_character: AI character object
            opponent_character: Opponent character object
            threat_level: Threat level (0.0 to 1.0)
            last_player_move: Last move made by player (for threat calculation)
            pattern_strength: Pattern recognition strength (0.0 to 1.0)
            cooldown_ratio: Cooldown status (1.0 = ready, 0.0 = just used)
            
        Returns:
            dict: Dictionary of action probabilities
        """
        
        if last_player_move == 'special':
            threat_level = min(1.0, threat_level + 0.3)
        elif last_player_move == 'punch':
            threat_level = min(1.0, threat_level + 0.1)
        elif last_player_move == 'rest':
            threat_level = max(0.0, threat_level - 0.2)
        
        
        fuzzy_inputs = self.fuzzify_inputs(
            ai_character, opponent_character, threat_level,
            pattern_strength=pattern_strength,
            cooldown_ratio=cooldown_ratio
        )
        
        
        output_memberships = self.evaluate_rules(fuzzy_inputs)
        
        
        action_probs = self.defuzzify(output_memberships, method='centroid')
        
        
        total = sum(action_probs.values())
        if total > 0:
            for action in action_probs:
                action_probs[action] = action_probs[action] / total
        
        return {
            'punch': action_probs.get('punch_prob', 0.0),
            'kick': action_probs.get('kick_prob', 0.0),
            'special': action_probs.get('special_prob', 0.0),
            'block': action_probs.get('block_prob', 0.0),
            'evade': action_probs.get('evade_prob', 0.0),
            'rest': action_probs.get('rest_prob', 0.0)
        }



_fuzzy_system = None

def get_fuzzy_system():
    """Get or create the global fuzzy logic system instance."""
    global _fuzzy_system
    if _fuzzy_system is None:
        _fuzzy_system = FuzzyLogicSystem()
    return _fuzzy_system

