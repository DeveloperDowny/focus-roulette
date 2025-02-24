# FocusRoulette

## Why I Built This

Life is unpredictable. You never know what’s coming next. Instead of getting lost in endless choices and analysis paralysis, I decided to fight randomness with randomness.

**Enter FocusRoulette.**

Every week, I spin the wheel. One area gets my full attention. No second-guessing. No overthinking. Just pure execution.

## How It Works

FocusRoulette uses an **adaptive weighted random selection** to pick my focus area. Each category has a base weight, which changes dynamically based on past selections and cooldowns.

- More important areas have **higher base weights**, making them more likely to be picked.
- Recently selected areas **get a temporary weight reduction**, so I don’t keep picking the same thing.
- **Cooldowns ensure balance**, allowing weights to recover over time.
- The randomness keeps me **engaged, challenged, and moving forward.**

## Example Task Pool

```json
{
  "tasks": {
    "Leader in Community": { "base_weight": 1.0, "current_weight": 1.0, "cooldown": 2 },
    "DSA": { "base_weight": 5.0, "current_weight": 0.5, "cooldown": 2 },
    "Indie Hacking": { "base_weight": 4.0, "current_weight": 4.0, "cooldown": 2 },
    "Chill": { "base_weight": 1.0, "current_weight": 1.0, "cooldown": 3 },
    "Showcasing": { "base_weight": 2.0, "current_weight": 0.2, "cooldown": 2 },
    "Hobbies": { "base_weight": 1.0, "current_weight": 1.0, "cooldown": 3 },
    "Marketing": { "base_weight": 2.0, "current_weight": 2.0, "cooldown": 2 }
  },
  "history": [
    { "task": "DSA", "timestamp": "2025-02-25T00:22:44.051442", "weight_used": 5.0 },
    { "task": "Showcasing", "timestamp": "2025-02-25T00:23:07.981900", "weight_used": 2.0 }
  ]
}
```

## Features

✅ **Randomly selects a focus area each week**  
✅ **Balances priority and fairness** with adaptive weights  
✅ **Prevents burnout** by rotating between different types of tasks  
✅ **Tracks history** so I can review past focus areas  
✅ **Simple UI** with a clear task selection system

## How to Use

1. **Run the app** and view your task list.
2. **Click “Select Random Task”** to pick your focus for the week.
3. **Trust the process. Execute.**
4. **See what happens.** No regrets, no overthinking.

## Tech Stack

- **Python** (for logic and task selection)
- **Tkinter** (for the user interface)
- **JSON storage** (to save tasks and history)

## Installation

```bash
# Clone the repository
git clone https://github.com/DeveloperDowny/focus-roulette.git

# Navigate into the directory
cd focus-roulette

# Run the application
python main.py
```

## Why It Works

We often waste **more energy deciding what to do** than actually doing the thing. FocusRoulette eliminates that decision fatigue. It forces me to **commit to a path** and go all in, making real progress instead of getting stuck in endless “what should I do?” loops.

It’s **structured enough** to ensure I focus on the right things. But it’s also **random enough** to keep life interesting.

## The Challenge

Try it for a month. **Let go. Let randomness decide.** See how much you can achieve when you stop second-guessing and just start moving.

### 🚀 Spin the wheel. Focus. Achieve.

