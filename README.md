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

**Change battle format:**
```python
player = Local_AIPlayer(model="gemma3:12b", battle_format="gen9ou", team=your_team)
```

**Adjust log length:**
```python
player = Local_AIPlayer(model="gemma3:12b", log_length=50)  # default: 25
```

**Use different models:**
```python
local_player = Local_AIPlayer(model="mistral:7b", ...)
cloud_player = Router_AIPlayer(model="anthropic/claude-3-5-sonnet", ...)
```

## Troubleshooting

**Connection refused:** Ensure Showdown server is running with `--no-security`

**Model not found:** Run `ollama list` or check OpenRouter model names

**Invalid actions:** Bot falls back to random moves when LLM output is invalid

## Credits

- [Poke-Env](https://github.com/hsahovic/poke-env) - Python interface for Pokemon Showdown
- [Pokemon Showdown](https://github.com/smogon/pokemon-showdown) - Battle simulator
