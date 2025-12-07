
class Character:

    def __init__(self, name, max_hp, max_stamina, base_damage, special_move_name):

        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.max_stamina = max_stamina
        self.stamina = max_stamina
        self.base_damage = base_damage
        self.special_move_name = special_move_name
        self.is_blocking = False
        self.is_evading = False
        self.status_effects = {} 
        self.special_move_cooldown = 0
        self.turns_since_special = 0
        self.consecutive_punches = 0
        self.consecutive_kicks = 0 
        self.last_move = None
        self.move_variety_bonus = 0.0
        self.can_counter_attack = False
    
    def reset_status(self):
        self.is_blocking = False
        self.is_evading = False
        self.can_counter_attack = False
    
    def can_use_special(self):
        return self.special_move_cooldown == 0
    
    def use_special_move_with_cooldown(self, target):
        if not self.can_use_special():
            return {
                'success': False,
                'message': f"{self.name}'s {self.special_move_name} is on cooldown! ({self.special_move_cooldown} turns remaining)"
            }
        
        result = self.use_special_move(target)
        
        if result.get('success', False):
            from src.utils import config
            self.special_move_cooldown = config.SPECIAL_MOVE_COOLDOWN_TURNS
            self.turns_since_special = 0
        
        return result
    
    def tick_cooldowns(self):
        if self.special_move_cooldown > 0:
            self.special_move_cooldown -= 1
        self.turns_since_special += 1
    
    def apply_status_effect(self, effect_type, damage=0, turns=0, **kwargs):
        self.status_effects[effect_type] = {
            'damage': damage,
            'turns': turns,
            **kwargs
        }
    
    def has_status_effect(self, effect_type):
        return effect_type in self.status_effects
    
    def process_status_effects(self):
        total_damage = 0
        expired_effects = []
        
        for effect_type, effect_data in list(self.status_effects.items()):
            if effect_data.get('damage', 0) > 0:
                damage = effect_data['damage']
                self.hp = max(0, self.hp - damage)
                total_damage += damage
            
            effect_data['turns'] -= 1
            
            if effect_data['turns'] <= 0:
                expired_effects.append(effect_type)
                del self.status_effects[effect_type]
        
        return {
            'damage': total_damage,
            'expired_effects': expired_effects,
            'active_effects': list(self.status_effects.keys())
        }
    
    def _apply_damage_with_block_check(self, target, damage, move_name):
        was_blocking = target.is_blocking
        actual_damage = target.take_damage(damage)
        
        if was_blocking and actual_damage == 0:
            return (0, True, f"{self.name} uses {move_name}, but {target.name} completely blocks it!")
        elif was_blocking and actual_damage < damage:
            return (actual_damage, False, f"{self.name} uses {move_name}! {target.name} blocks, takes {actual_damage} damage (reduced from {damage})!")
        else:
            return (actual_damage, False, f"{self.name} uses {move_name}! Deals {actual_damage} damage!")
    
    def use_special_move(self, target):
        raise NotImplementedError("Each character must implement use_special_move")
    
    def restore_stamina(self, amount):
        self.stamina = min(self.max_stamina, self.stamina + amount)
    
    def restore_hp(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)
    
    def take_damage(self, damage):
        if self.is_blocking:
            import random
            from src.utils import config
            
            if random.random() < config.BLOCK_COMPLETE_BLOCK_CHANCE:
                return 0  
            
            damage = int(damage * (1.0 - config.BLOCK_DAMAGE_REDUCTION))
        self.hp = max(0, self.hp - damage)
        return damage
    
    def is_alive(self):
        return self.hp > 0
    
    def get_stats(self):
        return {
            'name': self.name,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'stamina': self.stamina,
            'max_stamina': self.max_stamina,
            'special_move': self.special_move_name
        }


class Warrior(Character):
    
    def __init__(self):
        super().__init__(
            name="Warrior",
            max_hp=100,
            max_stamina=80,
            base_damage=15,
            special_move_name="Power Strike"
        )
    
    def use_special_move(self, target):
        stamina_cost = 30
        if self.stamina < stamina_cost:
            return {'success': False, 'message': f"{self.name} doesn't have enough stamina!"}
        
        self.stamina -= stamina_cost
        damage = int(self.base_damage * 2.5)
        
        if target.is_evading:
            return {'success': False, 'message': f"{target.name} evaded the attack!", 'stamina_cost': stamina_cost}

        actual_damage, blocked_completely, message = self._apply_damage_with_block_check(target, damage, "Power Strike")
        
        return {
            'success': True,
            'damage': actual_damage,
            'message': message,
            'stamina_cost': stamina_cost
        }


class Tank(Character):
    
    def __init__(self):
        super().__init__(
            name="Tank",
            max_hp=150,
            max_stamina=60,
            base_damage=18,
            special_move_name="Shield Slam"
        )
    
    def use_special_move(self, target):
        stamina_cost = 35
        if self.stamina < stamina_cost:
            return {'success': False, 'message': f"{self.name} doesn't have enough stamina!"}
        
        self.stamina -= stamina_cost
        self.is_blocking = True  
        
        damage = int(self.base_damage * 2.0) 

        if target.is_evading:
            return {'success': False, 'message': f"{target.name} evaded the attack!", 'stamina_cost': stamina_cost}
        
        actual_damage, blocked_completely, damage_msg = self._apply_damage_with_block_check(target, damage, "Shield Slam")
        
        return {
            'success': True,
            'damage': actual_damage,
            'message': f"{damage_msg} {self.name} also raises guard!",
            'stamina_cost': stamina_cost
        }


class Assassin(Character):
    """High crit chance, ignores block."""
    
    def __init__(self):
        super().__init__(
            name="Assassin",
            max_hp=75,
            max_stamina=90,
            base_damage=16,
            special_move_name="Shadow Strike"
        )
    
    def use_special_move(self, target):
        """Shadow Strike: High crit chance, ignores block."""
        stamina_cost = 30
        if self.stamina < stamina_cost:
            return {'success': False, 'message': f"{self.name} doesn't have enough stamina!"}
        
        self.stamina -= stamina_cost
        
        if target.is_evading:
            return {'success': False, 'message': f"{target.name} evaded the attack!", 'stamina_cost': stamina_cost}
        
        import random
        is_crit = random.random() < 0.6
        base_damage = int(self.base_damage * 2.0)
        
        if is_crit:
            damage = int(base_damage * 1.8)
            crit_msg = " CRITICAL HIT!"
        else:
            damage = base_damage
            crit_msg = ""

        was_blocking = target.is_blocking
        target.is_blocking = False
        actual_damage = target.take_damage(damage)
        target.is_blocking = was_blocking
        
        return {
            'success': True,
            'damage': actual_damage,
            'message': f"{self.name} uses Shadow Strike{crit_msg}! Deals {actual_damage} damage (ignores block)!",
            'stamina_cost': stamina_cost
        }


class Mage(Character):
    
    def __init__(self):
        super().__init__(
            name="Mage",
            max_hp=70,
            max_stamina=75,
            base_damage=17,
            special_move_name="Fireball"
        )
    
    def use_special_move(self, target):
        stamina_cost = 35
        if self.stamina < stamina_cost:
            return {'success': False, 'message': f"{self.name} doesn't have enough stamina!"}
        
        self.stamina -= stamina_cost
        
        
        was_evading = target.is_evading
        target.is_evading = False
        
        damage = int(self.base_damage * 2.2)  
        
        
        actual_damage, blocked_completely, damage_msg = self._apply_damage_with_block_check(target, damage, "Fireball")
        
        target.is_evading = was_evading
        
        if blocked_completely:
            return {
                'success': True,
                'damage': 0,
                'message': damage_msg,
                'stamina_cost': stamina_cost
            }
        else:
            return {
                'success': True,
                'damage': actual_damage,
                'message': f"{damage_msg} (ignores evade)",
                'stamina_cost': stamina_cost
            }


class Samurai(Character):
    
    def __init__(self):
        super().__init__(
            name="Samurai",
            max_hp=88,
            max_stamina=80,
            base_damage=16,
            special_move_name="Iaido Slash"
        )
    
    def use_special_move(self, target):
        stamina_cost = 28
        if self.stamina < stamina_cost:
            return {'success': False, 'message': f"{self.name} doesn't have enough stamina!"}
        
        self.stamina -= stamina_cost

        import random
        hit_chance = 0.9
        
        if target.is_evading and random.random() > hit_chance:
            return {'success': False, 'message': f"{target.name} evaded the attack!", 'stamina_cost': stamina_cost}
        
        damage = int(self.base_damage * 2.3)

        actual_damage, blocked_completely, damage_msg = self._apply_damage_with_block_check(target, damage, "Iaido Slash")
        
        return {
            'success': True,
            'damage': actual_damage,
            'message': damage_msg,
            'stamina_cost': stamina_cost
        }


CHARACTERS = {
    'warrior': Warrior,
    'tank': Tank,
    'assassin': Assassin,
    'mage': Mage,
    'samurai': Samurai
}


def get_character(name):
    name_lower = name.lower()
    if name_lower in CHARACTERS:
        return CHARACTERS[name_lower]()
    return None


def list_all_characters():
    return list(CHARACTERS.keys())

