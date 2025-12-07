

PUNCH_DAMAGE_MULTIPLIER = 1.0  
PUNCH_STAMINA_COST = 10  
PUNCH_FATIGUE_PENALTY = 0.1  
PUNCH_MISS_CHANCE_PER_FATIGUE = 0.10  
PUNCH_COUNTER_RISK = 0.15  


KICK_DAMAGE_MULTIPLIER = 1.3  
KICK_STAMINA_COST = 15  
KICK_BASE_MISS_CHANCE = 0.30  
KICK_FATIGUE_PENALTY = 0.1  
KICK_MISS_CHANCE_PER_FATIGUE = 0.10  
KICK_COUNTER_RISK = 0.20  


BLOCK_DAMAGE_REDUCTION = 0.7  
BLOCK_COMPLETE_BLOCK_CHANCE = 0.3  
BLOCK_STAMINA_COST = 5  
BLOCK_COUNTER_ATTACK_CHANCE = 0.4  
BLOCK_STAMINA_RECOVERY = 5  


EVADE_SUCCESS_CHANCE = 0.3  
EVADE_STAMINA_COST = 8  
EVADE_COUNTER_ATTACK_CHANCE = 0.5  
EVADE_STAMINA_RECOVERY = 3  
EVADE_NEXT_TURN_BONUS = 0.15  


SPECIAL_MOVE_MIN_STAMINA_COST = 20
SPECIAL_MOVE_MAX_STAMINA_COST = 40



SPECIAL_DAMAGE_MULTIPLIERS = {
    'warrior': 2.5,      
    'tank': 2.0,         
    'assassin': 2.0,     
    'mage': 2.2,         
    'samurai': 2.3,      
}


SPECIAL_STAMINA_COSTS = {
    'warrior': 30,
    'tank': 35,
    'assassin': 30,
    'mage': 35,
    'samurai': 28,
}


ASSASSIN_CRIT_CHANCE = 0.6  
ASSASSIN_CRIT_MULTIPLIER = 1.8
SAMURAI_HIT_CHANCE = 0.9  






POISON_DAMAGE_PER_TURN = 5
POISON_DURATION_TURNS = 3


STATUS_EFFECT_TYPES = {
    'POISON': 'poison',
    'BURN': 'burn',
    'STUN': 'stun',
    'BLEED': 'bleed'
}


AI_HEALTH_THRESHOLDS = {
    'WOUNDED': 0.5,        
    'DESPERATION': 0.2,    
    'FINISHER': 0.15       
}


AI_STAMINA_THRESHOLDS = {
    'EXHAUSTED': 0.25,     
    'LOW_STAMINA': 0.4     
}



DIFFICULTY_EASY = 'easy'
DIFFICULTY_MEDIUM = 'medium'
DIFFICULTY_HARD = 'hard'

DIFFICULTY_MODIFIERS = {
    DIFFICULTY_EASY: {
        
        'aggressive': {'punch': 0.5, 'kick': 0.4, 'special': 0.4, 'block': 1.6, 'evade': 1.5, 'rest': 1.5},  
        'defensive': {'punch': 0.3, 'kick': 0.2, 'special': 0.2, 'block': 1.8, 'evade': 1.6, 'rest': 1.4},
        'counter': {'punch': 0.4, 'kick': 0.3, 'special': 0.3, 'block': 1.5, 'evade': 1.3, 'rest': 1.3},
        'wounded': {'punch': 0.2, 'kick': 0.2, 'special': 0.2, 'block': 1.7, 'evade': 1.5, 'rest': 1.4},
        'desperation': {'punch': 0.3, 'kick': 0.3, 'special': 0.5, 'block': 1.3, 'evade': 1.2, 'rest': 1.2},  
        'exhausted': {'punch': 0.2, 'kick': 0.2, 'special': 0.1, 'block': 1.4, 'evade': 1.3, 'rest': 1.6},  
        'finisher': {'punch': 0.3, 'kick': 0.3, 'special': 0.5, 'block': 1.2, 'evade': 1.1, 'rest': 1.1}  
    },
    DIFFICULTY_MEDIUM: {
        
        'aggressive': {'punch': 1.0, 'kick': 1.0, 'special': 1.0, 'block': 1.0, 'evade': 1.0, 'rest': 1.0},
        'defensive': {'punch': 1.0, 'kick': 1.0, 'special': 1.0, 'block': 1.0, 'evade': 1.0, 'rest': 1.0},
        'counter': {'punch': 1.0, 'kick': 1.0, 'special': 1.0, 'block': 1.0, 'evade': 1.0, 'rest': 1.0},
        'wounded': {'punch': 1.0, 'kick': 1.0, 'special': 1.0, 'block': 1.0, 'evade': 1.0, 'rest': 1.0},
        'desperation': {'punch': 1.0, 'kick': 1.0, 'special': 1.0, 'block': 1.0, 'evade': 1.0, 'rest': 1.0},
        'exhausted': {'punch': 1.0, 'kick': 1.0, 'special': 1.0, 'block': 1.0, 'evade': 1.0, 'rest': 1.0},
        'finisher': {'punch': 1.0, 'kick': 1.0, 'special': 1.0, 'block': 1.0, 'evade': 1.0, 'rest': 1.0}
    },
    DIFFICULTY_HARD: {
        
        'aggressive': {'punch': 1.8, 'kick': 1.7, 'special': 1.6, 'block': 0.4, 'evade': 0.5, 'rest': 0.5},  
        'defensive': {'punch': 1.5, 'kick': 1.4, 'special': 1.3, 'block': 0.5, 'evade': 0.6, 'rest': 0.6},
        'counter': {'punch': 1.6, 'kick': 1.5, 'special': 1.5, 'block': 0.5, 'evade': 0.6, 'rest': 0.5},
        'wounded': {'punch': 1.4, 'kick': 1.3, 'special': 1.3, 'block': 0.6, 'evade': 0.7, 'rest': 0.6},
        'desperation': {'punch': 1.5, 'kick': 1.5, 'special': 1.8, 'block': 0.4, 'evade': 0.5, 'rest': 0.4},  
        'exhausted': {'punch': 1.3, 'kick': 1.2, 'special': 1.2, 'block': 0.6, 'evade': 0.7, 'rest': 0.5},  
        'finisher': {'punch': 1.4, 'kick': 1.4, 'special': 1.9, 'block': 0.3, 'evade': 0.4, 'rest': 0.3}  
    }
}


AI_ACTION_WEIGHTS = {
    'aggressive': {
        'punch': 0.55,      
        'special': 0.25,     
        'block': 0.05,       
        'evade': 0.08,       
        'rest': 0.07         
    },
    'defensive': {
        'punch': 0.10,       
        'special': 0.05,      
        'block': 0.50,       
        'evade': 0.25,       
        'rest': 0.10         
    },
    'counter': {
        'punch': 0.40,       
        'special': 0.30,     
        'block': 0.15,       
        'evade': 0.10,       
        'rest': 0.05         
    },
    'wounded': {
        'punch': 0.15,       
        'special': 0.10,     
        'block': 0.45,       
        'evade': 0.20,       
        'rest': 0.10         
    },
    'desperation': {
        'punch': 0.20,       
        'special': 0.60,     
        'block': 0.05,       
        'evade': 0.10,       
        'rest': 0.05         
    },
    'exhausted': {
        'punch': 0.10,       
        'special': 0.02,      
        'block': 0.20,       
        'evade': 0.15,       
        'rest': 0.53         
    },
    'finisher': {
        'punch': 0.15,       
        'special': 0.70,     
        'block': 0.03,       
        'evade': 0.08,       
        'rest': 0.04         
    }
}

PLAYER_TURN_FIRST = True  


MIN_HP = 0
MIN_STAMINA = 0


STAMINA_REGEN_PER_TURN = 5


REST_STAMINA_RESTORE_PERCENT = 0.3  
REST_STAMINA_COST = 0  
REST_HP_RESTORE_PERCENT = 0.05  
REST_FATIGUE_RECOVERY = True  


SPECIAL_MOVE_COOLDOWN_TURNS = 4  


MOMENTUM_BONUS_PER_UNIQUE_MOVE = 0.1  
MOMENTUM_MAX_BONUS = 0.3  
MOMENTUM_DECAY = 0.05  


HP_BAR_LENGTH = 20  
STAMINA_BAR_LENGTH = 15  


TURN_SEPARATOR = "=" * 60
ACTION_SEPARATOR = "-" * 60


VALID_MOVES = ['punch', 'kick', 'block', 'evade', 'special', 'rest']


VALID_CHARACTER_NAMES = [
    'warrior', 'tank', 'assassin', 'mage', 'samurai'
]


VALID_DIFFICULTY_LEVELS = [DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD]



DAMAGE_VARIANCE_ENABLED = False
DAMAGE_VARIANCE_PERCENT = 0.1  


BASE_ACCURACY = 1.0  
CRITICAL_HIT_CHANCE = 0.1  
CRITICAL_HIT_MULTIPLIER = 1.5  

DEBUG_MODE = False


LOG_LEVEL = 'INFO'  


SHOW_AI_DECISIONS = True


SHOW_DETAILED_CALCULATIONS = False

