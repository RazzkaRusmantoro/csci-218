"""
Move functions for the Turn-Based Fighter Game.
Implements the basic moves: Punch, Block, and Evade.
Special moves are handled in each character's class.
"""

import random
from src.utils import config


def punch(attacker, target):
    """
    Execute a punch attack.
    Now includes fatigue penalty and counter-attack risk.
    
    Args:
        attacker: Character performing the punch
        target: Character being attacked
        
    Returns:
        dict: Result of the punch with damage, message, etc.
    """
    # Check stamina
    if attacker.stamina < config.PUNCH_STAMINA_COST:
        return {
            'success': False,
            'message': f"{attacker.name} doesn't have enough stamina to punch!",
            'stamina_cost': 0
        }
    
    # Consume stamina
    attacker.stamina -= config.PUNCH_STAMINA_COST
    
    # Track consecutive punches (fatigue system)
    if attacker.last_move == 'punch':
        attacker.consecutive_punches += 1
    else:
        attacker.consecutive_punches = 1  # Reset if different move
    attacker.consecutive_kicks = 0  # Reset kicks when punching
    
    attacker.last_move = 'punch'
    
    # Check if target evades
    was_evading = target.is_evading
    evade_success = False
    if was_evading:
        evade_success = random.random() < config.EVADE_SUCCESS_CHANCE
        if evade_success:
            # Successful evade - target can counter-attack
            target.can_counter_attack = True
            # Recover stamina from successful evade
            target.restore_stamina(config.EVADE_STAMINA_RECOVERY)
            return {
                'success': False,
                'message': f"{target.name} evaded {attacker.name}'s punch! (+{config.EVADE_STAMINA_RECOVERY} stamina)",
                'stamina_cost': config.PUNCH_STAMINA_COST,
                'evaded': True,
                'counter_opportunity': True
            }
    
    # Calculate base damage
    base_damage = int(attacker.base_damage * config.PUNCH_DAMAGE_MULTIPLIER)
    
    # Apply fatigue penalty (repeated punching becomes less effective)
    # Fatigue applies from first consecutive punch
    fatigue_penalty = attacker.consecutive_punches * config.PUNCH_FATIGUE_PENALTY
    base_damage = int(base_damage * (1.0 - fatigue_penalty))
    
    # Apply momentum bonus (reward for move variety)
    momentum_bonus = attacker.move_variety_bonus
    
    # Apply evade bonus if attacker has it (from previous evade)
    evade_bonus = 0.0
    if attacker.has_status_effect('evade_bonus'):
        evade_bonus = attacker.status_effects['evade_bonus'].get('bonus', 0.0)
    
    base_damage = int(base_damage * (1.0 + momentum_bonus + evade_bonus))
    
    # Check for miss chance (10% per consecutive punch, stacks)
    miss_chance = attacker.consecutive_punches * config.PUNCH_MISS_CHANCE_PER_FATIGUE
    if miss_chance > 0 and random.random() < miss_chance:
        return {
            'success': False,
            'message': f"{attacker.name} punches but misses due to fatigue! ({int(miss_chance*100)}% miss chance)",
            'stamina_cost': config.PUNCH_STAMINA_COST,
            'missed': True
        }
    
    # Apply damage variance if enabled
    if config.DAMAGE_VARIANCE_ENABLED:
        variance = random.uniform(
            1 - config.DAMAGE_VARIANCE_PERCENT,
            1 + config.DAMAGE_VARIANCE_PERCENT
        )
        base_damage = int(base_damage * variance)
    
    # Check if target is blocking (before applying damage)
    was_blocking = target.is_blocking
    blocked_completely = False
    
    # Apply damage to target
    actual_damage = target.take_damage(base_damage)
    
    # Check if it was completely blocked
    if was_blocking and actual_damage == 0:
        blocked_completely = True
        # Successful block - target can counter-attack
        target.can_counter_attack = True
        # Recover stamina from successful block
        target.restore_stamina(config.BLOCK_STAMINA_RECOVERY)
    
    # Counter-attack risk (if target blocked/evaded but didn't completely avoid)
    counter_damage = 0
    counter_msg = ""
    if (was_blocking or was_evading) and not blocked_completely and not evade_success:
        if random.random() < config.PUNCH_COUNTER_RISK:
            # Target counter-attacks!
            counter_damage = int(target.base_damage * 0.8)  # 80% of base damage
            attacker.hp = max(0, attacker.hp - counter_damage)
            counter_msg = f" {target.name} counter-attacks for {counter_damage} damage!"
    
    # Check for critical hit (if enabled and not character-specific)
    is_crit = False
    if random.random() < config.CRITICAL_HIT_CHANCE:
        is_crit = True
        crit_damage = int(actual_damage * (config.CRITICAL_HIT_MULTIPLIER - 1))
        target.hp = max(0, target.hp - crit_damage)
        actual_damage += crit_damage
    
    crit_msg = " CRITICAL HIT!" if is_crit else ""
    fatigue_msg = f" (fatigued: -{int(fatigue_penalty*100)}%)" if fatigue_penalty > 0 else ""
    momentum_msg = f" (momentum: +{int(momentum_bonus*100)}%)" if momentum_bonus > 0 else ""
    
    # Build message based on block result
    if blocked_completely:
        damage_msg = f"{attacker.name} punches, but {target.name} completely blocks it! (+{config.BLOCK_STAMINA_RECOVERY} stamina){counter_msg}"
    elif was_blocking and actual_damage < base_damage:
        damage_msg = f"{attacker.name} punches {target.name} for {actual_damage} damage (blocked, reduced from {base_damage})!{fatigue_msg}{momentum_msg}{crit_msg}{counter_msg}"
    else:
        damage_msg = f"{attacker.name} punches {target.name} for {actual_damage} damage!{fatigue_msg}{momentum_msg}{crit_msg}{counter_msg}"
    
    return {
        'success': True,
        'damage': actual_damage,
        'message': damage_msg,
        'stamina_cost': config.PUNCH_STAMINA_COST,
        'critical': is_crit,
        'blocked': blocked_completely,
        'counter_damage': counter_damage,
        'fatigue_penalty': fatigue_penalty
    }


def block(character):
    """
    Execute a block action.
    Sets the character to blocking state for the next turn.
    
    Args:
        character: Character performing the block
        
    Returns:
        dict: Result of the block action
    """
    # Check stamina
    if character.stamina < config.BLOCK_STAMINA_COST:
        return {
            'success': False,
            'message': f"{character.name} doesn't have enough stamina to block!",
            'stamina_cost': 0
        }
    
    # Consume stamina
    character.stamina -= config.BLOCK_STAMINA_COST
    
    # Reset consecutive punches/kicks (blocking breaks fatigue)
    character.consecutive_punches = 0
    character.consecutive_kicks = 0
    character.last_move = 'block'
    
    # Update momentum (variety bonus)
    character.move_variety_bonus = min(
        config.MOMENTUM_MAX_BONUS,
        character.move_variety_bonus + config.MOMENTUM_BONUS_PER_UNIQUE_MOVE
    )
    
    # Set blocking state
    character.is_blocking = True
    
    return {
        'success': True,
        'damage': 0,
        'message': f"{character.name} raises guard! Next attack will be reduced by {int(config.BLOCK_DAMAGE_REDUCTION * 100)}% or completely blocked ({int(config.BLOCK_COMPLETE_BLOCK_CHANCE * 100)}% chance)!",
        'stamina_cost': config.BLOCK_STAMINA_COST,
        'blocking': True
    }


def evade(character):
    """
    Execute an evade action.
    Sets the character to evading state for the next turn.
    
    Args:
        character: Character performing the evade
        
    Returns:
        dict: Result of the evade action
    """
    # Check stamina
    if character.stamina < config.EVADE_STAMINA_COST:
        return {
            'success': False,
            'message': f"{character.name} doesn't have enough stamina to evade!",
            'stamina_cost': 0
        }
    
    # Consume stamina
    character.stamina -= config.EVADE_STAMINA_COST
    
    # Reset consecutive punches/kicks (evading breaks fatigue)
    character.consecutive_punches = 0
    character.consecutive_kicks = 0
    character.last_move = 'evade'
    
    # Update momentum (variety bonus)
    character.move_variety_bonus = min(
        config.MOMENTUM_MAX_BONUS,
        character.move_variety_bonus + config.MOMENTUM_BONUS_PER_UNIQUE_MOVE
    )
    
    # Set evading state
    character.is_evading = True
    
    # Apply next-turn damage bonus (stored in status effects)
    character.apply_status_effect('evade_bonus', damage=0, turns=1, bonus=config.EVADE_NEXT_TURN_BONUS)
    
    return {
        'success': True,
        'damage': 0,
        'message': f"{character.name} prepares to dodge the next attack! (Next attack: +{int(config.EVADE_NEXT_TURN_BONUS*100)}% damage)",
        'stamina_cost': config.EVADE_STAMINA_COST,
        'evading': True
    }


def rest(character):
    """
    Execute a rest action.
    Restores stamina and HP, resets fatigue, and provides strategic recovery.
    
    Args:
        character: Character performing the rest
        
    Returns:
        dict: Result of the rest action
    """
    # Restore stamina
    stamina_restored = int(character.max_stamina * config.REST_STAMINA_RESTORE_PERCENT)
    character.restore_stamina(stamina_restored)
    
    # Restore HP (strategic benefit)
    hp_restored = int(character.max_hp * config.REST_HP_RESTORE_PERCENT)
    character.restore_hp(hp_restored)
    
    # Reset fatigue (consecutive punches/kicks)
    character.consecutive_punches = 0
    character.consecutive_kicks = 0
    character.last_move = 'rest'
    
    # Update momentum (variety bonus)
    character.move_variety_bonus = min(
        config.MOMENTUM_MAX_BONUS,
        character.move_variety_bonus + config.MOMENTUM_BONUS_PER_UNIQUE_MOVE
    )
    
    hp_msg = f" and {hp_restored} HP" if hp_restored > 0 else ""
    return {
        'success': True,
        'damage': 0,
        'message': f"{character.name} rests and restores {stamina_restored} stamina{hp_msg}! (Fatigue reset)",
        'stamina_cost': config.REST_STAMINA_COST,
        'stamina_restored': stamina_restored,
        'hp_restored': hp_restored
    }


def kick(attacker, target):
    """
    Execute a kick attack.
    Higher damage and stamina cost than punch, but higher miss chance.
    
    Args:
        attacker: Character performing the kick
        target: Character being attacked
        
    Returns:
        dict: Result of the kick with damage, message, etc.
    """
    # Check stamina
    if attacker.stamina < config.KICK_STAMINA_COST:
        return {
            'success': False,
            'message': f"{attacker.name} doesn't have enough stamina to kick!",
            'stamina_cost': 0
        }
    
    # Consume stamina
    attacker.stamina -= config.KICK_STAMINA_COST
    
    # Track consecutive kicks (fatigue system)
    if attacker.last_move == 'kick':
        attacker.consecutive_kicks += 1
    else:
        attacker.consecutive_kicks = 1  # Reset if different move
    attacker.consecutive_punches = 0  # Reset punches when kicking
    
    attacker.last_move = 'kick'
    
    # Check if target evades
    was_evading = target.is_evading
    evade_success = False
    if was_evading:
        evade_success = random.random() < config.EVADE_SUCCESS_CHANCE
        if evade_success:
            # Successful evade - target can counter-attack
            target.can_counter_attack = True
            # Recover stamina from successful evade
            target.restore_stamina(config.EVADE_STAMINA_RECOVERY)
            return {
                'success': False,
                'message': f"{target.name} evaded {attacker.name}'s kick! (+{config.EVADE_STAMINA_RECOVERY} stamina)",
                'stamina_cost': config.KICK_STAMINA_COST,
                'evaded': True,
                'counter_opportunity': True
            }
    
    # Calculate base damage (higher than punch)
    base_damage = int(attacker.base_damage * config.KICK_DAMAGE_MULTIPLIER)
    
    # Apply fatigue penalty (repeated kicking becomes less effective)
    fatigue_penalty = attacker.consecutive_kicks * config.KICK_FATIGUE_PENALTY
    base_damage = int(base_damage * (1.0 - fatigue_penalty))
    
    # Apply momentum bonus (reward for move variety)
    momentum_bonus = attacker.move_variety_bonus
    
    # Apply evade bonus if attacker has it (from previous evade)
    evade_bonus = 0.0
    if attacker.has_status_effect('evade_bonus'):
        evade_bonus = attacker.status_effects['evade_bonus'].get('bonus', 0.0)
    
    base_damage = int(base_damage * (1.0 + momentum_bonus + evade_bonus))
    
    # Check for miss chance (base 30% + 10% per consecutive kick)
    total_miss_chance = config.KICK_BASE_MISS_CHANCE + (attacker.consecutive_kicks * config.KICK_MISS_CHANCE_PER_FATIGUE)
    if random.random() < total_miss_chance:
        return {
            'success': False,
            'message': f"{attacker.name} kicks but misses! ({int(total_miss_chance*100)}% miss chance)",
            'stamina_cost': config.KICK_STAMINA_COST,
            'missed': True
        }
    
    # Apply damage variance if enabled
    if config.DAMAGE_VARIANCE_ENABLED:
        variance = random.uniform(
            1 - config.DAMAGE_VARIANCE_PERCENT,
            1 + config.DAMAGE_VARIANCE_PERCENT
        )
        base_damage = int(base_damage * variance)
    
    # Check if target is blocking (before applying damage)
    was_blocking = target.is_blocking
    blocked_completely = False
    
    # Apply damage to target
    actual_damage = target.take_damage(base_damage)
    
    # Check if it was completely blocked
    if was_blocking and actual_damage == 0:
        blocked_completely = True
        # Successful block - target can counter-attack
        target.can_counter_attack = True
        # Recover stamina from successful block
        target.restore_stamina(config.BLOCK_STAMINA_RECOVERY)
    
    # Counter-attack risk (if target blocked/evaded but didn't completely avoid)
    counter_damage = 0
    counter_msg = ""
    if (was_blocking or was_evading) and not blocked_completely and not evade_success:
        if random.random() < config.KICK_COUNTER_RISK:
            # Target counter-attacks!
            counter_damage = int(target.base_damage * 0.8)  # 80% of base damage
            attacker.hp = max(0, attacker.hp - counter_damage)
            counter_msg = f" {target.name} counter-attacks for {counter_damage} damage!"
    
    # Check for critical hit (if enabled and not character-specific)
    is_crit = False
    if random.random() < config.CRITICAL_HIT_CHANCE:
        is_crit = True
        crit_damage = int(actual_damage * (config.CRITICAL_HIT_MULTIPLIER - 1))
        target.hp = max(0, target.hp - crit_damage)
        actual_damage += crit_damage
    
    crit_msg = " CRITICAL HIT!" if is_crit else ""
    fatigue_msg = f" (fatigued: -{int(fatigue_penalty*100)}%)" if fatigue_penalty > 0 else ""
    momentum_msg = f" (momentum: +{int(momentum_bonus*100)}%)" if momentum_bonus > 0 else ""
    
    # Build message based on block result
    if blocked_completely:
        damage_msg = f"{attacker.name} kicks, but {target.name} completely blocks it! (+{config.BLOCK_STAMINA_RECOVERY} stamina){counter_msg}"
    elif was_blocking and actual_damage < base_damage:
        damage_msg = f"{attacker.name} kicks {target.name} for {actual_damage} damage (blocked, reduced from {base_damage})!{fatigue_msg}{momentum_msg}{crit_msg}{counter_msg}"
    else:
        damage_msg = f"{attacker.name} kicks {target.name} for {actual_damage} damage!{fatigue_msg}{momentum_msg}{crit_msg}{counter_msg}"
    
    return {
        'success': True,
        'damage': actual_damage,
        'message': damage_msg,
        'stamina_cost': config.KICK_STAMINA_COST,
        'critical': is_crit,
        'blocked': blocked_completely,
        'counter_damage': counter_damage,
        'fatigue_penalty': fatigue_penalty
    }


def execute_move(move_type, attacker, target=None):
    """
    Execute a move based on move type.
    Universal function to call the appropriate move function.
    
    Args:
        move_type: Type of move ('punch', 'block', 'evade', 'special', 'rest')
        attacker: Character performing the move
        target: Target character (required for punch and special, None for block/evade/rest)
        
    Returns:
        dict: Result of the move execution
    """
    move_type = move_type.lower()
    
    if move_type == 'punch':
        if target is None:
            return {
                'success': False,
                'message': "Punch requires a target!",
                'damage': 0
            }
        return punch(attacker, target)
    
    elif move_type == 'kick':
        if target is None:
            return {
                'success': False,
                'message': "Kick requires a target!",
                'damage': 0
            }
        return kick(attacker, target)
    
    elif move_type == 'block':
        return block(attacker)
    
    elif move_type == 'evade':
        return evade(attacker)
    
    elif move_type == 'rest':
        return rest(attacker)
    
    elif move_type == 'special':
        if target is None:
            return {
                'success': False,
                'message': "Special move requires a target!",
                'damage': 0
            }
        # Use special move with cooldown check
        return attacker.use_special_move_with_cooldown(target)
    
    else:
        return {
            'success': False,
            'message': f"Unknown move type: {move_type}",
            'damage': 0
        }


def get_move_info(move_type):
    """
    Get information about a move type.
    
    Args:
        move_type: Type of move ('punch', 'kick', 'block', 'evade', 'rest', 'special')
        
    Returns:
        dict: Information about the move (stamina cost, description, etc.)
    """
    move_type = move_type.lower()
    
    move_info = {
        'punch': {
            'name': 'Punch',
            'stamina_cost': config.PUNCH_STAMINA_COST,
            'description': 'Basic attack that deals moderate damage.',
            'requires_target': True
        },
        'kick': {
            'name': 'Kick',
            'stamina_cost': config.KICK_STAMINA_COST,
            'description': f'Powerful attack: {int(config.KICK_DAMAGE_MULTIPLIER * 100)}% damage but {int(config.KICK_BASE_MISS_CHANCE * 100)}% miss chance.',
            'requires_target': True
        },
        'block': {
            'name': 'Block',
            'stamina_cost': config.BLOCK_STAMINA_COST,
            'description': f'Defensive move: {int(config.BLOCK_DAMAGE_REDUCTION * 100)}% damage reduction or {int(config.BLOCK_COMPLETE_BLOCK_CHANCE * 100)}% chance to completely block.',
            'requires_target': False
        },
        'evade': {
            'name': 'Evade',
            'stamina_cost': config.EVADE_STAMINA_COST,
            'description': f'Dodge move with {int(config.EVADE_SUCCESS_CHANCE * 100)}% chance to avoid next attack.',
            'requires_target': False
        },
        'special': {
            'name': 'Special',
            'stamina_cost': 'Varies',
            'description': 'Character-specific unique move with high impact.',
            'requires_target': True
        },
        'rest': {
            'name': 'Rest',
            'stamina_cost': 0,
            'description': f'Rest and restore {int(config.REST_STAMINA_RESTORE_PERCENT * 100)}% of max stamina.',
            'requires_target': False
        }
    }
    
    return move_info.get(move_type, {
        'name': 'Unknown',
        'stamina_cost': 0,
        'description': 'Unknown move type.',
        'requires_target': False
    })


def can_perform_move(character, move_type):
    """
    Check if a character can perform a specific move.
    
    Args:
        character: Character to check
        move_type: Type of move to check
        
    Returns:
        tuple: (can_perform: bool, reason: str)
    """
    move_type = move_type.lower()
    
    if move_type == 'punch':
        if character.stamina < config.PUNCH_STAMINA_COST:
            return False, f"Not enough stamina (need {config.PUNCH_STAMINA_COST}, have {character.stamina})"
        return True, "Can perform punch"
    
    elif move_type == 'kick':
        if character.stamina < config.KICK_STAMINA_COST:
            return False, f"Not enough stamina (need {config.KICK_STAMINA_COST}, have {character.stamina})"
        return True, "Can perform kick"
    
    elif move_type == 'block':
        if character.stamina < config.BLOCK_STAMINA_COST:
            return False, f"Not enough stamina (need {config.BLOCK_STAMINA_COST}, have {character.stamina})"
        return True, "Can perform block"
    
    elif move_type == 'evade':
        if character.stamina < config.EVADE_STAMINA_COST:
            return False, f"Not enough stamina (need {config.EVADE_STAMINA_COST}, have {character.stamina})"
        return True, "Can perform evade"
    
    elif move_type == 'rest':
        # Rest is always available (costs no stamina)
        return True, "Can rest"
    
    elif move_type == 'special':
        # Check cooldown
        if not character.can_use_special():
            return False, f"On cooldown ({character.special_move_cooldown} turns remaining)"
        # Special moves have character-specific costs, so we can't check stamina here
        return True, "Special move available"
    
    else:
        return False, f"Unknown move type: {move_type}"


def get_available_moves(character):
    """
    Get a list of moves available to a character based on their stamina.
    
    Args:
        character: Character to check
        
    Returns:
        list: List of available move types
    """
    available = []
    
    if character.stamina >= config.PUNCH_STAMINA_COST:
        available.append('punch')
    
    if character.stamina >= config.KICK_STAMINA_COST:
        available.append('kick')
    
    if character.stamina >= config.BLOCK_STAMINA_COST:
        available.append('block')
    
    if character.stamina >= config.EVADE_STAMINA_COST:
        available.append('evade')
    
    # Rest is always available
    available.append('rest')
    
    # Special moves are always listed (they check their own stamina and cooldown)
    available.append('special')
    
    return available

