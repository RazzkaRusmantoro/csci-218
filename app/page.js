'use client';

import { useState, useEffect } from 'react';
import './globals.css';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export default function Game() {
  const [gameState, setGameState] = useState(null);
  const [characters, setCharacters] = useState([]);
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [difficulty, setDifficulty] = useState('medium');
  const [loading, setLoading] = useState(false);
  const [gameLog, setGameLog] = useState([]);
  const [gameId, setGameId] = useState(null);

  useEffect(() => {
    fetchCharacters();
  }, []);

  const fetchCharacters = async () => {
    try {
      const response = await fetch(`${API_URL}/api/characters`);
      const data = await response.json();
      setCharacters(data.characters || []);
    } catch (error) {
      console.error('Failed to fetch characters:', error);
      addLog('Error: Could not connect to game server. Make sure Flask backend is running.', 'error');
    }
  };

  const addLog = (message, type = 'info') => {
    setGameLog(prev => [...prev, { message, type, timestamp: new Date().toLocaleTimeString() }]);
  };

  const startGame = async () => {
    if (!selectedCharacter) {
      alert('Please select a character first!');
      return;
    }

    setLoading(true);
    const newGameId = `game_${Date.now()}`;
    setGameId(newGameId);
    setGameLog([]);

    try {
      const response = await fetch(`${API_URL}/api/game/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player_character: selectedCharacter,
          difficulty: difficulty,
          game_id: newGameId
        })
      });

      const data = await response.json();
      if (response.ok) {
        // Fetch full game state to get available moves
        const stateResponse = await fetch(`${API_URL}/api/game/${newGameId}/state`);
        const stateData = await stateResponse.json();
        setGameState(stateData);
        addLog(`Battle begins! ${data.player.name} vs ${data.ai.name}`, 'battle');
        addLog(`Difficulty: ${difficulty.toUpperCase()}`, 'info');
      } else {
        addLog(`Error: ${data.error}`, 'error');
      }
    } catch (error) {
      addLog(`Error starting game: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const makeMove = async (moveType) => {
    if (!gameState || gameState.game_over || loading) return;

    setLoading(true);

    try {
      // First process turn (status effects, cooldowns)
      const processResponse = await fetch(`${API_URL}/api/game/${gameId}/process-turn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const processData = await processResponse.json();

      if (processData.status_messages && processData.status_messages.length > 0) {
        processData.status_messages.forEach(msg => addLog(msg.message, 'status'));
      }

      if (processData.game_over) {
        setGameState(prev => ({
          ...prev,
          ...processData,
          player: processData.player,
          ai: processData.ai
        }));
        addLog(`${processData.winner} wins!`, 'victory');
        setLoading(false);
        return;
      }

      // Make player move
      const moveResponse = await fetch(`${API_URL}/api/game/${gameId}/move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ move: moveType })
      });

      const moveData = await moveResponse.json();

      if (moveResponse.ok) {
        if (moveData.player_move) {
          addLog(`${moveData.player_move.message}`, 'player');
        }

        if (moveData.ai_move) {
          addLog(`${moveData.ai_move.message}`, 'ai');
        }

        // Get updated game state with available moves and AI state
        const stateResponse = await fetch(`${API_URL}/api/game/${gameId}/state`);
        const stateData = await stateResponse.json();
        
        setGameState({
          ...stateData,
          ...moveData,
          player: moveData.player || stateData.player,
          ai: moveData.ai || stateData.ai,
          turn_number: moveData.turn_number || stateData.turn_number,
          ai_state: moveData.ai_state || stateData.ai_state
        });

        if (moveData.game_over) {
          addLog(`${moveData.winner} wins the battle!`, 'victory');
        }
      } else {
        addLog(`Error: ${moveData.error}`, 'error');
      }
    } catch (error) {
      addLog(`Error making move: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const resetGame = () => {
    setGameState(null);
    setGameLog([]);
    setGameId(null);
    setSelectedCharacter(null);
  };

  const HealthBar = ({ current, max, label, color = 'bg-red-500' }) => {
    const percentage = Math.max(0, Math.min(100, (current / max) * 100));
    const isLow = percentage < 30;
    const barColor = label === 'Health' 
      ? (isLow ? 'bg-red-600' : 'bg-red-500')
      : (isLow ? 'bg-blue-600' : 'bg-blue-500');
    
    return (
      <div className="w-full">
        <div className="flex justify-between mb-1.5">
          <span className="text-sm font-medium text-gray-300">{label}</span>
          <span className="text-sm font-medium text-gray-300">{current}/{max}</span>
        </div>
        <div className="w-full bg-gray-800 rounded-full h-4 overflow-hidden shadow-inner">
          <div
            className={`${barColor} h-4 transition-all duration-500 ease-out rounded-full shadow-sm ${
              isLow ? 'animate-pulse' : ''
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    );
  };

  if (!gameState) {
    return (
      <div className="min-h-screen bg-gray-950 text-gray-100 flex items-center justify-center p-4">
        <div className="max-w-5xl w-full bg-gray-900/90 backdrop-blur-sm rounded-xl shadow-2xl p-8 border border-gray-800/50">
          <h1 className="text-4xl font-bold text-center mb-3 text-white tracking-tight">
            TURN-BASED FIGHTER
          </h1>
          <p className="text-center text-gray-400 mb-10 text-lg">Choose your warrior and prepare for battle</p>

          <div className="mb-10">
            <label className="block text-gray-300 font-semibold mb-4 text-lg">Select Difficulty</label>
            <div className="grid grid-cols-3 gap-4">
              {['easy', 'medium', 'hard'].map((diff) => (
                <button
                  key={diff}
                  onClick={() => setDifficulty(diff)}
                  className={`px-6 py-4 rounded-lg border-2 font-semibold transition-all cursor-pointer ${
                    difficulty === diff
                      ? 'bg-gray-800 border-gray-500 text-white shadow-lg scale-105'
                      : 'bg-gray-950/50 border-gray-800 text-gray-400 hover:border-gray-700 hover:bg-gray-900/50 hover:text-gray-300'
                  }`}
                  style={{ cursor: 'pointer' }}
                >
                  {diff.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-10">
            <label className="block text-gray-300 font-semibold mb-4 text-lg">Select Your Character</label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {characters.map((char) => (
                <div
                  key={char.id}
                  onClick={() => setSelectedCharacter(char.id)}
                  className={`p-5 rounded-lg border-2 cursor-pointer transition-all transform ${
                    selectedCharacter === char.id
                      ? 'border-gray-500 bg-gray-800 shadow-lg scale-105 ring-2 ring-gray-600'
                      : 'border-gray-800 bg-gray-950/50 hover:border-gray-700 hover:bg-gray-900/70 hover:scale-102'
                  }`}
                  style={{ cursor: 'pointer' }}
                >
                  <h3 className="text-xl font-bold text-white mb-2">{char.name}</h3>
                  <p className="text-gray-400 text-sm mb-3 font-medium">{char.special_move}</p>
                  <div className="text-gray-500 text-sm space-y-1.5">
                    <div className="flex justify-between">
                      <span>HP:</span>
                      <span className="text-gray-400">{char.max_hp}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Stamina:</span>
                      <span className="text-gray-400">{char.max_stamina}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Damage:</span>
                      <span className="text-gray-400">{char.base_damage}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={startGame}
            disabled={!selectedCharacter || loading}
            className="w-full py-4 bg-gray-800 hover:bg-gray-700 active:bg-gray-600 text-white font-bold text-lg rounded-lg border-2 border-gray-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
            style={{ cursor: !selectedCharacter || loading ? 'not-allowed' : 'pointer' }}
          >
            {loading ? 'Starting Battle...' : 'START BATTLE'}
          </button>
        </div>
      </div>
    );
  }

  // Format FSM state name for display
  const formatFSMState = (stateObj) => {
    if (!stateObj) return 'Unknown';
    if (typeof stateObj === 'string') return stateObj;
    return stateObj.state || 'Unknown';
  };

  const getFSMStateDescription = (stateObj) => {
    if (!stateObj || typeof stateObj === 'string') return '';
    return stateObj.state_description || '';
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-3 tracking-tight">
            TURN {gameState.turn_number}
          </h1>
          {gameState.game_over && (
            <div className="mt-6 p-6 bg-gray-900/90 backdrop-blur-sm rounded-xl border-2 border-gray-700 shadow-xl">
              <p className="text-3xl font-bold text-white">{gameState.winner} WINS!</p>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Player Section */}
          <div className="bg-gray-900/90 backdrop-blur-sm rounded-xl p-6 border-2 border-gray-800 shadow-lg">
            <h2 className="text-2xl font-bold text-white mb-5 text-center">
              {gameState.player.name}
            </h2>
            <HealthBar
              current={gameState.player.hp}
              max={gameState.player.max_hp}
              label="Health"
            />
            <div className="mt-5">
              <HealthBar
                current={gameState.player.stamina}
                max={gameState.player.max_stamina}
                label="Stamina"
              />
            </div>
            {gameState.player.special_move_cooldown > 0 && (
              <div className="mt-4 text-center text-gray-400 text-sm bg-gray-800/50 rounded py-2">
                Special Cooldown: {gameState.player.special_move_cooldown} turns
              </div>
            )}
            {gameState.player.status_effects && Object.keys(gameState.player.status_effects).length > 0 && (
              <div className="mt-4 text-center">
                <div className="text-xs text-gray-400 font-semibold mb-2">Status Effects:</div>
                <div className="flex flex-wrap gap-2 justify-center">
                  {Object.entries(gameState.player.status_effects).map(([effect, data]) => (
                    <span key={effect} className="px-3 py-1 bg-gray-800 rounded-md text-xs text-gray-300 border border-gray-700">
                      {effect} ({data.turns})
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Battle Log */}
          <div className="bg-gray-900/90 backdrop-blur-sm rounded-xl p-6 border-2 border-gray-800 shadow-lg">
            <h2 className="text-xl font-bold text-white mb-5 text-center">Battle Log</h2>
            <div className="space-y-2 max-h-96 overflow-y-auto pr-2">
              {gameLog.map((log, idx) => (
                <div
                  key={idx}
                  className={`text-sm p-3 rounded-lg border ${
                    log.type === 'player' ? 'bg-gray-800/70 border-gray-700 text-gray-200' :
                    log.type === 'ai' ? 'bg-gray-800/70 border-gray-700 text-gray-300' :
                    log.type === 'victory' ? 'bg-gray-800/90 border-gray-600 text-white font-bold' :
                    log.type === 'error' ? 'bg-red-950/50 border-red-900 text-red-400' :
                    'bg-gray-800/70 border-gray-700 text-gray-400'
                  }`}
                >
                  <span className="text-xs text-gray-500">{log.timestamp}</span> {log.message}
                </div>
              ))}
            </div>
            <button
              onClick={resetGame}
              className="w-full mt-5 py-3 bg-gray-800 hover:bg-gray-700 active:bg-gray-600 text-white rounded-lg border-2 border-gray-700 transition-all font-semibold shadow-md hover:shadow-lg"
              style={{ cursor: 'pointer' }}
            >
              New Game
            </button>
          </div>

          {/* AI Section */}
          <div className="bg-gray-900/90 backdrop-blur-sm rounded-xl p-6 border-2 border-gray-800 shadow-lg">
            <h2 className="text-2xl font-bold text-white mb-5 text-center">
              {gameState.ai.name}
            </h2>
            
            {/* FSM State Display */}
            {gameState.ai_state && (
              <div className="mb-5 p-4 bg-gray-800/70 rounded-lg border-2 border-gray-700">
                <div className="text-xs text-gray-400 mb-2 uppercase tracking-wide font-semibold">FSM State</div>
                <div className="text-base font-bold text-white mb-1.5">
                  {formatFSMState(gameState.ai_state)}
                </div>
                {getFSMStateDescription(gameState.ai_state) && (
                  <div className="text-xs text-gray-400 italic leading-relaxed">
                    {getFSMStateDescription(gameState.ai_state)}
                  </div>
                )}
              </div>
            )}
            
            <HealthBar
              current={gameState.ai.hp}
              max={gameState.ai.max_hp}
              label="Health"
            />
            <div className="mt-5">
              <HealthBar
                current={gameState.ai.stamina}
                max={gameState.ai.max_stamina}
                label="Stamina"
              />
            </div>
            {gameState.ai.special_move_cooldown > 0 && (
              <div className="mt-4 text-center text-gray-400 text-sm bg-gray-800/50 rounded py-2">
                Special Cooldown: {gameState.ai.special_move_cooldown} turns
              </div>
            )}
            {gameState.ai.status_effects && Object.keys(gameState.ai.status_effects).length > 0 && (
              <div className="mt-4 text-center">
                <div className="text-xs text-gray-400 font-semibold mb-2">Status Effects:</div>
                <div className="flex flex-wrap gap-2 justify-center">
                  {Object.entries(gameState.ai.status_effects).map(([effect, data]) => (
                    <span key={effect} className="px-3 py-1 bg-gray-800 rounded-md text-xs text-gray-300 border border-gray-700">
                      {effect} ({data.turns})
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Move Buttons */}
        {!gameState.game_over && (
          <div className="mt-6 bg-gray-900/90 backdrop-blur-sm rounded-xl p-6 border-2 border-gray-800 shadow-lg">
            <h2 className="text-xl font-bold text-white mb-6 text-center">Your Moves</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {gameState.available_moves?.map((move) => (
                <button
                  key={move.type}
                  onClick={() => makeMove(move.type)}
                  disabled={!move.can_perform || loading}
                  className={`p-5 rounded-lg border-2 transition-all transform ${
                    move.can_perform
                      ? 'bg-gray-800 border-gray-600 text-white hover:bg-gray-700 hover:border-gray-500 hover:scale-105 active:scale-95 shadow-md hover:shadow-lg'
                      : 'bg-gray-950 border-gray-800 text-gray-600 cursor-not-allowed opacity-60'
                  }`}
                  title={move.reason || move.description}
                  style={{ cursor: move.can_perform && !loading ? 'pointer' : 'not-allowed' }}
                >
                  <div className="text-sm font-bold mb-2">{move.name}</div>
                  <div className="text-xs text-gray-400 mb-1">
                    Stamina: {move.stamina_cost === 0 ? 'Free' : move.stamina_cost === 'Varies' ? 'Varies' : move.stamina_cost}
                  </div>
                  {move.cooldown && (
                    <div className="text-xs text-yellow-400 mt-1 font-semibold">CD: {move.cooldown}</div>
                  )}
                </button>
              ))}
            </div>
            {loading && (
              <div className="text-center mt-6 text-gray-400 font-medium">Processing turn...</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
