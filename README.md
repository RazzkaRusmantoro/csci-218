# Turn-Based Fighter Game - Web Version

A beautiful web-based version of the Turn-Based Fighter Game built with Next.js frontend and Flask backend.

## Features

- 🎮 5 unique characters with special moves
- 🤖 AI opponent with Fuzzy Logic decision-making
- ⚔️ Turn-based combat system
- 💪 HP and Stamina management
- 🎨 Beautiful, modern UI with gradient backgrounds
- 📜 Real-time battle log
- 🎯 Three difficulty levels (Easy, Medium, Hard)

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 18+ and npm
- Flask and flask-cors (install via requirements.txt)

### Backend Setup (Flask)

1. Navigate to the csci-218 directory:
```bash
cd csci-218
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start the Flask server:
```bash
python app/api/server.py
```

The Flask server will run on `http://localhost:5000`

### Frontend Setup (Next.js)

1. In a new terminal, navigate to the csci-218 directory:
```bash
cd csci-218
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the Next.js development server:
```bash
npm run dev
```

The Next.js app will run on `http://localhost:3000`

## How to Play

1. Make sure both Flask backend and Next.js frontend are running
2. Open your browser to `http://localhost:3000`
3. Select a difficulty level (Easy, Medium, or Hard)
4. Choose your character from the available fighters
5. Click "START BATTLE" to begin
6. Make moves by clicking the action buttons:
   - 👊 Punch: Basic attack
   - 🦵 Kick: Powerful attack with higher miss chance
   - 🛡️ Block: Reduce incoming damage
   - 💨 Evade: Chance to dodge attacks
   - 💤 Rest: Recover stamina and HP
   - ✨ Special: Character's unique powerful move (has cooldown)

## Game Characters

- **Warrior**: Balanced fighter with Power Strike
- **Tank**: High HP with Shield Slam
- **Assassin**: High crit chance with Shadow Strike
- **Mage**: Ranged attacks with Fireball
- **Samurai**: Precise attacks with Iaido Slash

## API Endpoints

The Flask backend provides these endpoints:

- `GET /api/characters` - Get list of available characters
- `POST /api/game/start` - Start a new game
- `GET /api/game/<game_id>/state` - Get current game state
- `POST /api/game/<game_id>/move` - Execute a player move
- `POST /api/game/<game_id>/process-turn` - Process turn effects
- `DELETE /api/game/<game_id>` - Delete a game
- `GET /api/health` - Health check

## Project Structure

```
csci-218/
├── app/
│   ├── api/
│   │   └── server.py       # Flask backend API
│   ├── page.js             # Next.js game UI
│   └── globals.css         # Global styles
├── requirements.txt        # Python dependencies
├── package.json           # Node.js dependencies
└── README.md             # This file
```

## Troubleshooting

- **Cannot connect to backend**: Make sure Flask server is running on port 5000
- **Module import errors**: Ensure you're running the Flask server from the csci-218 directory and the workspace root is in the Python path
- **CORS errors**: The Flask server has CORS enabled for localhost:3000

## Development

To modify the game logic, edit the files in the `src/` directory (outside csci-218). The Flask server imports these modules directly.
