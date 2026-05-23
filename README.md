# Sentinel

> Red-teaming agent. Not a tool. Not a script. An operator that thinks.

Sentinel is an AI-powered red-teaming agent built for the [Hermes Agent](https://hermes-agent.nousresearch.com) platform by Nous Research. Designed to assist security operators through every phase of an engagement — from recon to report — while staying sharp, honest, and tactically sound.

Model-agnostic by design. Runs on Hermes today. Works with Claude Code, Gemini CLI, or whatever runtime you're using tomorrow.

---

## What Sentinel is

- A **6-layer system prompt** (identity, conduct, decision tree, tone, security, meta-instructions)
- **12 native skills** covering the full attack lifecycle
- A **session state engine** that persists engagement context to SQLite
- A philosophy: **if confidence < 80%, search before you speak**

Sentinel doesn't improvise commands. Doesn't hallucinate flags. If it doesn't know, it says so — and looks it up.

---

## Skills

| Skill | Phase | Description |
|---|---|---|
| `/plan` | Planning | Define scope, objectives, attack surface |
| `/recon` | Recon | Passive + active reconnaissance |
| `/enum` | Enumeration | Deep service enumeration |
| `/exploit` | Exploitation | Vulnerability exploitation |
| `/post` | Post-exploitation | Persistence, lateral movement, pivoting |
| `/report` | Reporting | Generate structured engagement report |
| `/analyze` | Any | Analyze output, logs, or findings |
| `/rt-llm` | Red Team LLM | Adversarial testing of AI systems |
| `/state` | Any | Inspect current session state |
| `/checkpoint` | Any | Persist session state to SQLite |
| `/handoff` | Any | Transfer context between agents or sessions |

---

## Architecture

```
sentinel_soul_v1.3.md     ← system prompt (model-agnostic) — versión activa
skills/                   ← Hermes native skills
  plan/SKILL.md
  recon/SKILL.md
  enum/SKILL.md
  exploit/SKILL.md
  post/SKILL.md
  report/SKILL.md
  analyze/SKILL.md
  rt-llm/SKILL.md
  state/SKILL.md
  handoff/SKILL.md
  checkpoint/
    SKILL.md
    scripts/
      init_db.py          ← initialize sentinel.db
      checkpoint.py       ← parse agent output → write SQLite
      recover.py          ← reconstruct session state from DB
operator-guide.md         ← wiki structure, Obsidian conventions
```

The agent generates state in plain text. An external script writes to SQLite. The LLM never touches JSON directly. This is intentional.

---

## Requirements

- Python 3.10+
- [Hermes Agent](https://hermes-agent.nousresearch.com) — or any compatible agent runtime
- No external Python dependencies — stdlib only (`sqlite3`, `argparse`, `json`, `re`)

---

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/h4ckforge/Sentinel.git
cd Sentinel
```

### 2. Initialize the database

```bash
python skills/checkpoint/scripts/init_db.py
# OK: schema initialized
```

Default path: `./sentinel.db`. Custom path:

```bash
python skills/checkpoint/scripts/init_db.py --db /path/to/sentinel.db
```

### 3. Load the system prompt

Copy `sentinel_soul_v1.3.md` as the system prompt for your agent runtime.

**Hermes Agent:**
- Create a new agent in the Hermes dashboard
- Paste the contents of `sentinel_soul_v1.3.md` as the system prompt
- Load skills from the `skills/` directory

**Claude Code / other runtimes:**
- Use `sentinel_soul_v1.3.md` as your system prompt
- Reference skills manually or adapt to your runtime's skill format

### 4. Set database path (optional)

```bash
export SENTINEL_DB=/path/to/sentinel.db
```

---

## Usage

### Saving a checkpoint

When the agent outputs a CHECKPOINT block, persist it:

```bash
# From a file
python skills/checkpoint/scripts/checkpoint.py --file checkpoint_output.txt

# From stdin
python skills/checkpoint/scripts/checkpoint.py < checkpoint_output.txt

# OK: checkpoint saved (id=1, session=eng-2026-05-20-acme)
```

### Recovering session state

```bash
# Last checkpoint (any session)
python skills/checkpoint/scripts/recover.py

# Last checkpoint for a specific session
python skills/checkpoint/scripts/recover.py --session eng-2026-05-20-acme
```

Output is a valid CHECKPOINT block ready to inject back into the agent context.

### CHECKPOINT block format

The agent generates this format. The script parses it.

```
CHECKPOINT
session_id=eng-2026-05-20-acme
mode=recon
target=10.10.11.42
last_tool=nmap -sV -sC 10.10.11.42
user_level=operator
recon_done=true
phase_complete=false
active_skill=/recon
pending_actions=["run theHarvester", "enumerate port 445"]
explained_concepts=[]
findings=[{"host":"10.10.11.42","ports":[{"port":80,"service":"http","version":"Apache 2.4"}],"notes":"default page, no auth"}]
nota=Initial recon complete. SMB and HTTP open. Proceeding to enum.
END_CHECKPOINT
```

---

## Session state schema

Defined in `skills/recon/SKILL.md`. All skills read and extend this schema.

| Field | Type | Description |
|---|---|---|
| `session_id` | string | Unique engagement identifier |
| `mode` | string | Current phase: recon/enum/exploit/post/report |
| `target` | string | IP, domain, or application |
| `last_tool` | string | Last command executed |
| `user_level` | string | operator / beginner / expert |
| `recon_done` | bool | Recon phase completed |
| `phase_complete` | bool | Current phase completed |
| `active_skill` | string | Currently active skill |
| `pending_actions` | array | Queued actions |
| `explained_concepts` | array | Concepts already explained this session |
| `findings` | array | Accumulated findings with hosts/ports/notes |

---

## Philosophy

Sentinel is built on three principles:

**1. No improvisation under uncertainty**
If confidence is below 80%, Sentinel declares it and searches the wiki before answering. A correct "I don't know" is worth more than any hallucinated command.

**2. The operator leads**
Sentinel proposes. It never imposes. When it detects a tactical error or a skipped phase, it flags it and asks — it doesn't override.

**3. Model-agnostic**
The system prompt, skills, and persistence layer are designed to work with any model. The agent runtime is a detail. The operator and the methodology are what matter.

---

## Project status

| Component | Status |
|---|---|
| System prompt (6 layers) | Done — v1.3 |
| Heurísticas Operativas (13 rules) | Done — v1.3 |
| Dynamic Checklist Switching | Done — v1.3 |
| Skills (12 native) | Done |
| Pipeline paralelo (recon + enum) | Done |
| Session state persistence (SQLite) | Done |
| RAG / Obsidian wiki | In progress |
| Banco de pruebas (90 preguntas) | In progress |
| Hermes runtime integration | Planned |

---

## Part of QH4X

Sentinel is a component of **QH4X** — a personal cybersecurity research project by [@rockmetal](https://github.com/rockmetal).

---

## License

MIT
