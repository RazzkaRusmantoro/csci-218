# Quick Start Guide

## Running the Game

### Step 1: Start the Flask Backend

Open a terminal and run:

```bash
cd csci-218
python app/api/server.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

### Step 2: Start the Next.js Frontend

Open a **new** terminal window and run:

```bash
cd csci-218
npm install  # Only needed the first time
npm run dev
```

You should see:
```
  ▲ Next.js 16.0.7
  - Local:        http://localhost:3000
```

### Step 3: Play the Game!

1. Open your browser to `http://localhost:3000`
2. Select a difficulty (Easy, Medium, or Hard)
3. Choose your character
4. Click "START BATTLE"
5. Make your moves and fight!

## Troubleshooting

- **Backend won't start**: Make sure you have Flask installed: `pip install -r requirements.txt`
- **Frontend won't start**: Make sure you have Node.js installed and run `npm install` first
- **Connection errors**: Make sure both servers are running (Flask on port 5000, Next.js on port 3000)
- **Import errors**: Make sure you're running from the `csci-218` directory and that the `src` folder is in the parent directory

## Changing the API URL

If your Flask backend runs on a different port, edit `csci-218/app/page.js` and change:

```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
```

## Game Controls

- **👊 Punch**: Basic attack (10 stamina)
- **🦵 Kick**: Powerful attack, higher miss chance (15 stamina)
- **🛡️ Block**: Reduce incoming damage (5 stamina)
- **💨 Evade**: Chance to dodge attacks (8 stamina)
- **💤 Rest**: Recover stamina and HP (free)
- **✨ Special**: Character's unique powerful move (cooldown: 4 turns)

Enjoy the game! 🎮⚔️


