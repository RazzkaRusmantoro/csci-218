"""
Pattern Recognition System for AI.
Detects player move patterns and predicts future moves.
"""

from collections import deque, Counter


class PatternRecognizer:
    """Recognizes and predicts player move patterns."""
    
    def __init__(self, history_size=5):
        """
        Initialize pattern recognizer.
        
        Args:
            history_size: Number of recent moves to track
        """
        self.history_size = history_size
        self.move_history = deque(maxlen=history_size)
        self.pattern_strength = 0.0  
        self.predicted_next_move = None
        self.common_patterns = {
            'aggressive': ['punch', 'punch', 'special'],
            'defensive': ['block', 'evade', 'block'],
            'stamina_conserving': ['punch', 'rest', 'punch'],
            'special_spam': ['special', 'rest', 'special'],
            'counter': ['block', 'punch', 'block']
        }
    
    def record_move(self, move):
        """
        Record a player move.
        
        Args:
            move: Move type ('punch', 'block', etc.)
        """
        self.move_history.append(move)
        self._analyze_pattern()
    
    def _analyze_pattern(self):
        """Analyze move history for patterns."""
        if len(self.move_history) < 2:
            self.pattern_strength = 0.0
            self.predicted_next_move = None
            return
        
        
        move_list = list(self.move_history)
        
        
        if len(move_list) >= 3:
            
            last_two = tuple(move_list[-2:])
            count = 0
            for i in range(len(move_list) - 2):
                if tuple(move_list[i:i+2]) == last_two:
                    count += 1
            
            if count >= 2:
                
                self.pattern_strength = min(1.0, count / 3.0)
                
                
                next_moves = []
                for i in range(len(move_list) - 2):
                    if tuple(move_list[i:i+2]) == last_two and i + 2 < len(move_list):
                        next_moves.append(move_list[i + 2])
                
                if next_moves:
                    most_common = Counter(next_moves).most_common(1)[0]
                    self.predicted_next_move = most_common[0]
                    self.pattern_strength = min(1.0, most_common[1] / len(next_moves))
                else:
                    self.predicted_next_move = None
            else:
                self.pattern_strength = 0.0
                self.predicted_next_move = None
        
        
        history_str = ' -> '.join(move_list)
        for pattern_name, pattern_sequence in self.common_patterns.items():
            pattern_str = ' -> '.join(pattern_sequence)
            if pattern_str in history_str:
                self.pattern_strength = 0.8
                
                if len(move_list) < len(pattern_sequence):
                    idx = len(move_list)
                    if idx < len(pattern_sequence):
                        self.predicted_next_move = pattern_sequence[idx]
    
    def get_pattern_info(self):
        """
        Get current pattern information.
        
        Returns:
            dict: Pattern strength and predicted move
        """
        return {
            'pattern_strength': self.pattern_strength,
            'predicted_move': self.predicted_next_move,
            'recent_moves': list(self.move_history)
        }
    
    def should_counter(self, move_type):
        """
        Check if AI should counter a specific move type.
        
        Args:
            move_type: Move type to counter
            
        Returns:
            bool: True if counter is recommended
        """
        if not self.predicted_next_move:
            return False
        
        
        counter_map = {
            'punch': 'block',  
            'special': 'evade',  
            'block': 'special',  
            'evade': 'punch',  
        }
        
        return self.predicted_next_move == move_type and self.pattern_strength > 0.5

