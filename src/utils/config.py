
# Punch move
PUNCH_DAMAGE_MULTIPLIER = 1.0  # Base damage multiplier for punch
PUNCH_STAMINA_COST = 10  # Stamina cost for punch
PUNCH_FATIGUE_PENALTY = 0.1  # 10% damage reduction per consecutive punch
PUNCH_MISS_CHANCE_PER_FATIGUE = 0.10  # 10% miss chance per consecutive punch (stacks)
PUNCH_COUNTER_RISK = 0.15  # 15% chance to be counter-attacked if opponent blocked/evaded

# Kick move
KICK_DAMAGE_MULTIPLIER = 1.3  # 30% more damage than punch
KICK_STAMINA_COST = 15  # More stamina than punch
KICK_BASE_MISS_CHANCE = 0.30  # 30% base miss chance (higher than punch)
KICK_FATIGUE_PENALTY = 0.1  # 10% damage reduction per consecutive kick
KICK_MISS_CHANCE_PER_FATIGUE = 0.10  # 10% additional miss chance per consecutive kick
KICK_COUNTER_RISK = 0.20  # 20% chance to be counter-attacked (higher risk than punch)

# Block move
BLOCK_DAMAGE_REDUCTION = 0.7  # Block reduces damage by 70% (improved)
BLOCK_COMPLETE_BLOCK_CHANCE = 0.3  # 30% chance to completely block attack
BLOCK_STAMINA_COST = 5  # Stamina cost for block
BLOCK_COUNTER_ATTACK_CHANCE = 0.4  # 40% chance to counter-attack after blocking
BLOCK_STAMINA_RECOVERY = 5  # Recover 5 stamina when successfully blocking

# Evade move
EVADE_SUCCESS_CHANCE = 0.3  # 30% chance to completely avoid attack
EVADE_STAMINA_COST = 8  # Stamina cost for evade
EVADE_COUNTER_ATTACK_CHANCE = 0.5  # 50% chance to counter-attack after evading
EVADE_STAMINA_RECOVERY = 3  # Recover 3 stamina when successfully evading
EVADE_NEXT_TURN_BONUS = 0.15  # 15% damage bonus on next attack after successful evade

# Special move base costs (character-specific multipliers may apply)
SPECIAL_MOVE_MIN_STAMINA_COST = 20
SPECIAL_MOVE_MAX_STAMINA_COST = 40


# Damage multipliers for special moves
SPECIAL_DAMAGE_MULTIPLIERS = {
    'warrior': 2.5,      # Power Strike
    'tank': 2.0,         # Shield Slam
    'assassin': 2.0,     # Shadow Strike (base, with crit multiplier)
    'mage': 2.2,         # Fireball
    'samurai': 2.3,      # Iaido Slash
}

# Special move stamina costs
SPECIAL_STAMINA_COSTS = {
    'warrior': 30,
    'tank': 35,
    'assassin': 30,
    'mage': 35,
    'samurai': 28,
}

# Special move specific constants
ASSASSIN_CRIT_CHANCE = 0.6  # 60% crit chance
ASSASSIN_CRIT_MULTIPLIER = 1.8
SAMURAI_HIT_CHANCE = 0.9  # 90% accuracy even when evading

# ============================================================================
# STATUS EFFECT CONSTANTS
# ============================================================================

# Poison effect (for status effects system)
POISON_DAMAGE_PER_TURN = 5
POISON_DURATION_TURNS = 3

# Status effect types
STATUS_EFFECT_TYPES = {
    'POISON': 'poison',
    'BURN': 'burn',
    'STUN': 'stun',
    'BLEED': 'bleed'
}

# ============================================================================
# HEALING & RESTORATION CONSTANTS
# ============================================================================

# Healing constants (if needed for future characters)
# HP_RESTORE_PERCENT = 0.25  # 25% of max HP
# STAMINA_RESTORE_PERCENT = 0.3  # 30% of max stamina

# ============================================================================
# AI FSM CONSTANTS
# ============================================================================

# Health thresholds for AI state transitions (as percentage of max HP)
AI_HEALTH_THRESHOLDS = {
    'WOUNDED': 0.5,        # Below 50% HP -> Wounded state
    'DESPERATION': 0.2,    # Below 20% HP -> Desperation state
    'FINISHER': 0.15       # Opponent below 15% HP -> Finisher state
}

# Stamina thresholds for AI state transitions (as percentage of max stamina)
AI_STAMINA_THRESHOLDS = {
    'EXHAUSTED': 0.25,     # Below 25% stamina -> Exhausted state
    'LOW_STAMINA': 0.4     # Below 40% stamina -> Low stamina warning
}

# ============================================================================
# DIFFICULTY SETTINGS
# ============================================================================

# Difficulty levels
DIFFICULTY_EASY = 'easy'
DIFFICULTY_MEDIUM = 'medium'
DIFFICULTY_HARD = 'hard'

# Difficulty modifiers for action weights
# Values > 1.0 increase probability, < 1.0 decrease
# These modify the fuzzy logic probabilities, making AI easier/harder
DIFFICULTY_MODIFIERS = {
    DIFFICULTY_EASY: {
        # Easy: Significantly reduce aggressive actions, increase defensive actions
        'aggressive': {'punch': 0.5, 'kick': 0.4, 'special': 0.4, 'block': 1.6, 'evade': 1.5, 'rest': 1.5},  # Much less punch/kick/special, more defense
        'defensive': {'punch': 0.3, 'kick': 0.2, 'special': 0.2, 'block': 1.8, 'evade': 1.6, 'rest': 1.4},
        'counter': {'punch': 0.4, 'kick': 0.3, 'special': 0.3, 'block': 1.5, 'evade': 1.3, 'rest': 1.3},
        'wounded': {'punch': 0.2, 'kick': 0.2, 'special': 0.2, 'block': 1.7, 'evade': 1.5, 'rest': 1.4},
        'desperation': {'punch': 0.3, 'kick': 0.3, 'special': 0.5, 'block': 1.3, 'evade': 1.2, 'rest': 1.2},  # Less desperate
        'exhausted': {'punch': 0.2, 'kick': 0.2, 'special': 0.1, 'block': 1.4, 'evade': 1.3, 'rest': 1.6},  # Much more rest
        'finisher': {'punch': 0.3, 'kick': 0.3, 'special': 0.5, 'block': 1.2, 'evade': 1.1, 'rest': 1.1}  # Less finishing
    },
    DIFFICULTY_MEDIUM: {
        # Medium: No modifiers - use base fuzzy logic probabilities
        'aggressive': {'punch': 1.0, 'kick': 1.0, 'special': 1.0, 'block': 1.0, 'evade': 1.0, 'rest': 1.0},
        'defensive': {'punch': 1.0, 'kick': 1.0, 'special': 1.0, 'block': 1.0, 'evade': 1.0, 'rest': 1.0},
        'counter': {'punch': 1.0, 'kick': 1.0, 'special': 1.0, 'block': 1.0, 'evade': 1.0, 'rest': 1.0},
        'wounded': {'punch': 1.0, 'kick': 1.0, 'special': 1.0, 'block': 1.0, 'evade': 1.0, 'rest': 1.0},
        'desperation': {'punch': 1.0, 'kick': 1.0, 'special': 1.0, 'block': 1.0, 'evade': 1.0, 'rest': 1.0},
        'exhausted': {'punch': 1.0, 'kick': 1.0, 'special': 1.0, 'block': 1.0, 'evade': 1.0, 'rest': 1.0},
        'finisher': {'punch': 1.0, 'kick': 1.0, 'special': 1.0, 'block': 1.0, 'evade': 1.0, 'rest': 1.0}
    },
    DIFFICULTY_HARD: {
        # Hard: Significantly increase aggressive actions, reduce defensive actions
        'aggressive': {'punch': 1.8, 'kick': 1.7, 'special': 1.6, 'block': 0.4, 'evade': 0.5, 'rest': 0.5},  # Much more punch/kick/special
        'defensive': {'punch': 1.5, 'kick': 1.4, 'special': 1.3, 'block': 0.5, 'evade': 0.6, 'rest': 0.6},
        'counter': {'punch': 1.6, 'kick': 1.5, 'special': 1.5, 'block': 0.5, 'evade': 0.6, 'rest': 0.5},
        'wounded': {'punch': 1.4, 'kick': 1.3, 'special': 1.3, 'block': 0.6, 'evade': 0.7, 'rest': 0.6},
        'desperation': {'punch': 1.5, 'kick': 1.5, 'special': 1.8, 'block': 0.4, 'evade': 0.5, 'rest': 0.4},  # Very aggressive
        'exhausted': {'punch': 1.3, 'kick': 1.2, 'special': 1.2, 'block': 0.6, 'evade': 0.7, 'rest': 0.5},  # Less rest
        'finisher': {'punch': 1.4, 'kick': 1.4, 'special': 1.9, 'block': 0.3, 'evade': 0.4, 'rest': 0.3}  # Very likely to finish
    }
}


# AI action weights (probabilities) for each state
# These are base weights - heavily weighted towards the most logical action for each state
# Used for FSM state tracking and as reference for difficulty modifiers
AI_ACTION_WEIGHTS = {
    'aggressive': {
        'punch': 0.55,      # Aggressive = mostly punch (55%)
        'special': 0.25,     # Special when opportunity arises (25%)
        'block': 0.05,       # Rarely block when aggressive (5%)
        'evade': 0.08,       # Occasionally evade (8%)
        'rest': 0.07         # Rarely rest when aggressive (7%)
    },
    'defensive': {
        'punch': 0.10,       # Rarely attack when defensive (10%)
        'special': 0.05,      # Very rarely special (5%)
        'block': 0.50,       # Defensive = mostly block (50%)
        'evade': 0.25,       # Evade is important defense (25%)
        'rest': 0.10         # Occasionally rest (10%)
    },
    'counter': {
        'punch': 0.40,       # Counter = attack after defense (40%)
        'special': 0.30,     # Special for strong counter (30%)
        'block': 0.15,       # Still block sometimes (15%)
        'evade': 0.10,       # Less evade in counter (10%)
        'rest': 0.05         # Rarely rest (5%)
    },
    'wounded': {
        'punch': 0.15,       # Less attack when wounded (15%)
        'special': 0.10,     # Rarely special (10%)
        'block': 0.45,       # Wounded = mostly block (45%)
        'evade': 0.20,       # Evade to avoid damage (20%)
        'rest': 0.10         # Occasionally rest (10%)
    },
    'desperation': {
        'punch': 0.20,       # Still attack but less (20%)
        'special': 0.60,     # Desperation = all-out special attacks (60%)
        'block': 0.05,       # Rarely block (5%)
        'evade': 0.10,       # Some evade (10%)
        'rest': 0.05         # Rarely rest (5%)
    },
    'exhausted': {
        'punch': 0.10,       # Very little attack (10%)
        'special': 0.02,      # Almost never special (2%)
        'block': 0.20,       # Block for cheap defense (20%)
        'evade': 0.15,       # Some evade (15%)
        'rest': 0.53         # Exhausted = mostly rest (53%)
    },
    'finisher': {
        'punch': 0.15,       # Some punch (15%)
        'special': 0.70,     # Finisher = mostly special to finish (70%)
        'block': 0.03,       # Almost never block (3%)
        'evade': 0.08,       # Some evade (8%)
        'rest': 0.04         # Almost never rest (4%)
    }
}

# ============================================================================
# GAME MECHANICS CONSTANTS
# ============================================================================

# Turn order
PLAYER_TURN_FIRST = True  # Player goes first by default

# Minimum values
MIN_HP = 0
MIN_STAMINA = 0

# Default stamina regeneration per turn (if implemented)
STAMINA_REGEN_PER_TURN = 5

# Rest move
REST_STAMINA_RESTORE_PERCENT = 0.3  # Restores 30% of max stamina
REST_STAMINA_COST = 0  # Rest costs no stamina
REST_HP_RESTORE_PERCENT = 0.05  # Restores 5% of max HP when resting
REST_FATIGUE_RECOVERY = True  # Rest resets fatigue/consecutive punch counter

# Special move cooldown
SPECIAL_MOVE_COOLDOWN_TURNS = 4  # Special moves can only be used every 4 turns

# Momentum system (reward move variety)
MOMENTUM_BONUS_PER_UNIQUE_MOVE = 0.1  # 10% damage bonus per unique move in last 3 turns
MOMENTUM_MAX_BONUS = 0.3  # Maximum 30% bonus for variety
MOMENTUM_DECAY = 0.05  # Momentum decays 5% per turn if not maintained

# ============================================================================
# DISPLAY & UI CONSTANTS
# ============================================================================

# Display formatting
HP_BAR_LENGTH = 20  # Length of HP bar in characters
STAMINA_BAR_LENGTH = 15  # Length of stamina bar in characters

# Message formatting
TURN_SEPARATOR = "=" * 60
ACTION_SEPARATOR = "-" * 60

# ============================================================================
# VALIDATION CONSTANTS
# ============================================================================

# Valid move types
VALID_MOVES = ['punch', 'kick', 'block', 'evade', 'special', 'rest']

# Valid character names (for validation)
VALID_CHARACTER_NAMES = [
    'warrior', 'tank', 'assassin', 'mage', 'samurai'
]

# Valid difficulty levels
VALID_DIFFICULTY_LEVELS = [DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD]

# ============================================================================
# GAME BALANCE CONSTANTS
# ============================================================================

# Damage variance (if you want to add randomness to damage)
DAMAGE_VARIANCE_ENABLED = False
DAMAGE_VARIANCE_PERCENT = 0.1  # ±10% damage variance

# Accuracy system (if implemented)
BASE_ACCURACY = 1.0  # 100% base accuracy
CRITICAL_HIT_CHANCE = 0.1  # 10% base crit chance (if not character-specific)
CRITICAL_HIT_MULTIPLIER = 1.5  # 1.5x damage on crit

# ============================================================================
# DEBUG & TESTING CONSTANTS
# ============================================================================

# Debug mode
DEBUG_MODE = False

# Logging level
LOG_LEVEL = 'INFO'  # Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR'

# Show AI decision process
SHOW_AI_DECISIONS = True

# Show detailed move calculations
SHOW_DETAILED_CALCULATIONS = False

