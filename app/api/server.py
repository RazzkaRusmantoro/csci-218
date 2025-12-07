"""
Flask API server for the Turn-Based Fighter Game.
Provides REST API endpoints for game initialization, moves, and state management.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__)) 
csci218_root = os.path.abspath(os.path.join(current_dir, '../..'))
sys.path.insert(0, csci218_root)

from src.core import characters, game_engine
from src.core import moves as moves_module

app = Flask(__name__)
CORS(app)

active_games = {}

def character_to_dict(char):
    """Convert character object to dictionary."""
    return {
        'name': char.name,
        'hp': max(0, char.hp),
        'max_hp': char.max_hp,
        'stamina': max(0, char.stamina),
        'max_stamina': char.max_stamina,
        'base_damage': char.base_damage,
        'special_move_name': char.special_move_name,
        'special_move_cooldown': char.special_move_cooldown,
        'status_effects': {
            k: {
                'damage': v.get('damage', 0),
                'turns': v.get('turns', 0),
                **{k2: v2 for k2, v2 in v.items() if k2 not in ['damage', 'turns']}
            }
            for k, v in char.status_effects.items()
        }
    }

@app.route('/api/characters', methods=['GET'])
def get_characters():
    """Get list of available characters."""
    char_list = characters.list_all_characters()
    char_info = []
    
    for char_name in char_list:
        char = characters.get_character(char_name)
        if char:
            char_info.append({
                'name': char.name,
                'special_move': char.special_move_name,
                'max_hp': char.max_hp,
                'max_stamina': char.max_stamina,
                'base_damage': char.base_damage,
                'id': char_name.lower()
            })
    
    return jsonify({'characters': char_info})

@app.route('/api/game/start', methods=['POST'])
def start_game():
    """Start a new game."""
    data = request.json
    player_char_name = data.get('player_character')
    difficulty = data.get('difficulty', 'medium')
    game_id = data.get('game_id', f'game_{len(active_games)}')
    
    if not player_char_name:
        return jsonify({'error': 'Player character is required'}), 400
    
    try:
        game = game_engine.create_game(player_char_name, difficulty=difficulty)
        game.turn_number = 0
        game.game_over = False
        
        if hasattr(game.ai_controller, 'update_state'):
            game.ai_controller.update_state(game.player)
        
        # Store game
        active_games[game_id] = game
        
        # Get available moves for initial state
        available_moves = moves_module.get_available_moves(game.player)
        moves_info = []
        for move in available_moves:
            move_info = moves_module.get_move_info(move)
            can_perform, reason = moves_module.can_perform_move(game.player, move)
            
            move_data = {
                'type': move,
                'name': move_info['name'],
                'description': move_info['description'],
                'can_perform': can_perform,
                'reason': reason if not can_perform else None
            }
            
            if move == 'special':
                move_data['name'] = f"{move_info['name']} ({game.player.special_move_name})"
                if game.player.special_move_cooldown > 0:
                    move_data['cooldown'] = game.player.special_move_cooldown
            
            moves_info.append(move_data)
        
        # Get initial AI state info
        if hasattr(game.ai_controller, 'get_state_info'):
            ai_state_info = game.ai_controller.get_state_info()
        else:
            # Fallback: use FSM helper directly
            from src.ai import fsm
            ai_state_info = fsm.get_state_info_dict(
                game.ai_controller.current_state if hasattr(game.ai_controller, 'current_state') else fsm.DEFAULT_STATE,
                game.ai_char,
                game.player
            )
        
        return jsonify({
            'game_id': game_id,
            'player': character_to_dict(game.player),
            'ai': character_to_dict(game.ai_char),
            'difficulty': difficulty,
            'turn_number': game.turn_number,
            'game_over': game.game_over,
            'available_moves': moves_info,
            'ai_state': {
                'state': ai_state_info.get('state', 'Unknown'),
                'state_description': ai_state_info.get('state_description', 'Unknown'),
                'health_percentage': ai_state_info.get('health_percentage', 0),
                'stamina_percentage': ai_state_info.get('stamina_percentage', 0)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/game/<game_id>/state', methods=['GET'])
def get_game_state(game_id):
    """Get current game state."""
    if game_id not in active_games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = active_games[game_id]
    
    # Get available moves for player
    available_moves = moves_module.get_available_moves(game.player)
    moves_info = []
    for move in available_moves:
        move_info = moves_module.get_move_info(move)
        can_perform, reason = moves_module.can_perform_move(game.player, move)
        
        move_data = {
            'type': move,
            'name': move_info['name'],
            'description': move_info['description'],
            'stamina_cost': move_info.get('stamina_cost', 0),
            'can_perform': can_perform,
            'reason': reason if not can_perform else None
        }
        
        if move == 'special':
            move_data['name'] = f"{move_info['name']} ({game.player.special_move_name})"
            # Get actual stamina cost for special move from config
            from src.utils import config
            move_data['stamina_cost'] = config.SPECIAL_STAMINA_COSTS.get(game.player.name.lower(), 'Varies')
            if game.player.special_move_cooldown > 0:
                move_data['cooldown'] = game.player.special_move_cooldown
        
        moves_info.append(move_data)
    
    # Get AI state info - update state first to get current FSM state
    if hasattr(game.ai_controller, 'update_state'):
        game.ai_controller.update_state(game.player)
    
    # Get state info using the AI controller's method
    if hasattr(game.ai_controller, 'get_state_info'):
        ai_state_info = game.ai_controller.get_state_info()
    else:
        # Fallback: use FSM helper directly
        from src.ai import fsm
        ai_state_info = fsm.get_state_info_dict(
            game.ai_controller.current_state if hasattr(game.ai_controller, 'current_state') else fsm.DEFAULT_STATE,
            game.ai_char,
            game.player
        )
    
    return jsonify({
        'game_id': game_id,
        'player': character_to_dict(game.player),
        'ai': character_to_dict(game.ai_char),
        'turn_number': game.turn_number,
        'game_over': game.game_over,
        'winner': game.winner.name if game.winner else None,
        'available_moves': moves_info,
        'ai_state': {
            'state': ai_state_info.get('state', 'Unknown'),
            'state_description': ai_state_info.get('state_description', 'Unknown'),
            'health_percentage': ai_state_info.get('health_percentage', 0),
            'stamina_percentage': ai_state_info.get('stamina_percentage', 0)
        }
    })

@app.route('/api/game/<game_id>/move', methods=['POST'])
def make_move(game_id):
    """Execute a player move."""
    if game_id not in active_games:
        return jsonify({'error': 'Game not found'}), 404
    
    data = request.json
    move_type = data.get('move')
    
    if not move_type:
        return jsonify({'error': 'Move is required'}), 400
    
    game = active_games[game_id]
    
    if game.game_over:
        return jsonify({'error': 'Game is over'}), 400
    
    try:
        # Execute player move
        result = moves_module.execute_move(move_type, game.player, game.ai_char)
        
        player_message = result.get('message', '')
        
        # Check if AI is defeated
        if not game.ai_char.is_alive():
            game.game_over = True
            game.winner = game.player
            return jsonify({
                'player_move': {
                    'type': move_type,
                    'success': result.get('success', False),
                    'message': player_message,
                    'damage': result.get('damage', 0)
                },
                'ai_move': None,
                'game_over': True,
                'winner': game.player.name,
                'player': character_to_dict(game.player),
                'ai': character_to_dict(game.ai_char)
            })
        
        # Process status effects
        status_messages = []
        player_effects = game.player.process_status_effects()
        if player_effects['damage'] > 0:
            status_messages.append({
                'type': 'status',
                'character': game.player.name,
                'message': f"{game.player.name} takes {player_effects['damage']} damage from status effects!"
            })
        
        ai_effects = game.ai_char.process_status_effects()
        if ai_effects['damage'] > 0:
            status_messages.append({
                'type': 'status',
                'character': game.ai_char.name,
                'message': f"{game.ai_char.name} takes {ai_effects['damage']} damage from status effects!"
            })
        
        # Check if game over from status effects
        if not game.player.is_alive():
            game.game_over = True
            game.winner = game.ai_char
        elif not game.ai_char.is_alive():
            game.game_over = True
            game.winner = game.player
        
        if game.game_over:
            return jsonify({
                'player_move': {
                    'type': move_type,
                    'success': result.get('success', False),
                    'message': player_message,
                    'damage': result.get('damage', 0)
                },
                'status_messages': status_messages,
                'ai_move': None,
                'game_over': True,
                'winner': game.winner.name if game.winner else None,
                'player': character_to_dict(game.player),
                'ai': character_to_dict(game.ai_char)
            })
        
        # Tick cooldowns and reset status
        game.tick_cooldowns()
        game.reset_turn_status()
        
        # Record player move for AI
        if move_type == 'special':
            game.ai_controller.record_player_move('special')
        elif move_type in ['punch', 'kick']:
            game.ai_controller.record_player_move(move_type)
        else:
            game.ai_controller.record_player_move(move_type)
        
        # Update AI state before AI makes move
        if hasattr(game.ai_controller, 'update_state'):
            game.ai_controller.update_state(game.player)
        
        # AI's turn
        ai_result = game.ai_controller.make_move(game.player)
        ai_message = ai_result.get('message', '')
        
        # Check if player is defeated
        if not game.player.is_alive():
            game.game_over = True
            game.winner = game.ai_char
        
        # Increment turn number after both moves are complete
        if not game.game_over:
            game.turn_number += 1
        
        # Get updated AI state info after move
        if hasattr(game.ai_controller, 'update_state'):
            game.ai_controller.update_state(game.player)
        
        # Get state info using the AI controller's method
        if hasattr(game.ai_controller, 'get_state_info'):
            ai_state_info = game.ai_controller.get_state_info()
        else:
            # Fallback: use FSM helper directly
            from src.ai import fsm
            ai_state_info = fsm.get_state_info_dict(
                game.ai_controller.current_state if hasattr(game.ai_controller, 'current_state') else fsm.DEFAULT_STATE,
                game.ai_char,
                game.player
            )
        
        ai_state_obj = {
            'state': ai_state_info.get('state', 'Unknown'),
            'state_description': ai_state_info.get('state_description', 'Unknown state'),
            'health_percentage': ai_state_info.get('health_percentage', 0),
            'stamina_percentage': ai_state_info.get('stamina_percentage', 0)
        }
        
        return jsonify({
            'player_move': {
                'type': move_type,
                'success': result.get('success', False),
                'message': player_message,
                'damage': result.get('damage', 0)
            },
            'status_messages': status_messages,
            'ai_move': {
                'type': ai_result.get('action_type', 'unknown'),
                'success': ai_result.get('success', False),
                'message': ai_message,
                'damage': ai_result.get('damage', 0)
            },
            'game_over': game.game_over,
            'winner': game.winner.name if game.winner else None,
            'turn_number': game.turn_number,
            'player': character_to_dict(game.player),
            'ai': character_to_dict(game.ai_char),
            'ai_state': ai_state_obj
        })
    
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/game/<game_id>/process-turn', methods=['POST'])
def process_turn(game_id):
    """Process status effects and cooldowns at start of turn."""
    if game_id not in active_games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = active_games[game_id]
    
    if game.game_over:
        return jsonify({'error': 'Game is over'}), 400
    
    try:
        # Process status effects
        status_messages = []
        player_effects = game.player.process_status_effects()
        if player_effects['damage'] > 0:
            status_messages.append({
                'type': 'status',
                'character': game.player.name,
                'message': f"{game.player.name} takes {player_effects['damage']} damage from status effects!"
            })
        
        ai_effects = game.ai_char.process_status_effects()
        if ai_effects['damage'] > 0:
            status_messages.append({
                'type': 'status',
                'character': game.ai_char.name,
                'message': f"{game.ai_char.name} takes {ai_effects['damage']} damage from status effects!"
            })
        
        # Check if game over from status effects
        if not game.player.is_alive():
            game.game_over = True
            game.winner = game.ai_char
        elif not game.ai_char.is_alive():
            game.game_over = True
            game.winner = game.player
        
        # Tick cooldowns and reset status
        game.tick_cooldowns()
        game.reset_turn_status()
        
        return jsonify({
            'status_messages': status_messages,
            'game_over': game.game_over,
            'winner': game.winner.name if game.winner else None,
            'player': character_to_dict(game.player),
            'ai': character_to_dict(game.ai_char)
        })
    
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/game/<game_id>', methods=['DELETE'])
def delete_game(game_id):
    """Delete a game."""
    if game_id in active_games:
        del active_games[game_id]
        return jsonify({'message': 'Game deleted'})
    return jsonify({'error': 'Game not found'}), 404

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

