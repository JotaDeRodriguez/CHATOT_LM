# CHATOT_LM

LLM-based Pokemon Showdown bot using Poke-Env. Supports local models via Ollama and cloud models via OpenRouter.

## How It Works

1. Bot receives battle state (logs, active pokemon, team status, available actions)
2. Sends state to LLM which returns reasoning + action
3. Executes action via Poke-Env

## Requirements

- Python 3.12+
- UV package manager
- Node.js (for local Showdown server)
- Ollama (for local models) or OpenRouter API key (for cloud models)

## Installation

```bash
git clone https://github.com/JotaDeRodriguez/CHATOT_LM
cd CHATOT_LM
uv sync
```

**For local models:**
```bash
ollama pull gemma3:12b
ollama pull qwen3:14b
```

**For cloud models:**
```bash
export OPENROUTER_API_KEY="your-api-key"
```

**Start Showdown server:**
```bash
git clone https://github.com/smogon/pokemon-showdown.git
cd pokemon-showdown
npm install
node pokemon-showdown start --no-security
```

## Usage

**Single battle:**
```bash
uv run python main.py
```

**Battle against the bot:**

Uncomment line 104 in [main.py](main.py):
```python
await gemma_player.accept_challenges(opponent=None, n_challenges=1)
```

**Round robin tournament:**
```bash
uv run python round_robin.py
```

## Configuration

**Creating players:**

Use factory methods to create AI players:

```python
from ai_players import AIPlayer
from poke_env import AccountConfiguration

# Local Ollama models
local_player = AIPlayer.local(
    model="gemma3:12b",
    verbosity=True,
    account_configuration=AccountConfiguration("bot_name", None),
    battle_format="gen3ubers",
    log_length=25,  # default: 25 for local
    team=your_team
)

# OpenRouter cloud models
cloud_player = AIPlayer.router(
    model="anthropic/claude-3-5-sonnet",
    verbosity=True,
    account_configuration=AccountConfiguration("bot_name", None),
    battle_format="gen3ubers",
    log_length=100,  # default: 100 for router
    team=your_team
)
```

**Change battle format:**
```python
player = AIPlayer.local(model="gemma3:12b", battle_format="gen9ou", team=your_team)
```

**Adjust log length:**
```python
player = AIPlayer.local(model="gemma3:12b", log_length=50)
```

## Troubleshooting

**Connection refused:** Ensure Showdown server is running with `--no-security`

**Model not found:** Run `ollama list` or check OpenRouter model names

**Invalid actions:** Bot falls back to random moves when LLM output is invalid

## Credits

- [Poke-Env](https://github.com/hsahovic/poke-env) - Python interface for Pokemon Showdown
- [Pokemon Showdown](https://github.com/smogon/pokemon-showdown) - Battle simulator
