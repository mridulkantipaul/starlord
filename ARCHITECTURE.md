# Architecture

## Overview
Star Lord is a local-first agent with pluggable IO, tools, and skills. The core **Agent** routes user input to a target skill based on intent, then produces a response (currently stubbed).

## Flow
1. **Input** (text or speech)
2. **Router** determines intent
3. **Skill** handles intent
4. **Tools** are called as needed
5. **Output** (text or speech)

## Key Modules
- `core/agent.py`: orchestrator
- `core/router.py`: intent routing
- `core/memory.py`: memory interface (stub)
- `io/`: speech/text IO adapters
- `tools/`: integrations
- `skills/`: domain skills
- `plugins/`: plugin interface

## Future Extensions
- Replace router with ML classifier
- Add vector memory
- Add event loop for background tasks
