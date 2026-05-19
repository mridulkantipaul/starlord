# Star Lord Interface Specification

Reference image: `ChatGPT Image May 19, 2026, 11_56_28 PM.png` (use this filename when adding the asset to the repo).

## Frontends

- **Primary:** PyQt (`src/starlord/gui_qt.py`)
- **Fallback:** Tkinter (`src/starlord/gui.py`)

Both frontends use the same modular command layer: `src/starlord/command_system.py`.

## UI Structure (mapped to the reference)

1. **Session rail (left):**
   - Session list
   - New Session button
2. **Main chat panel (center):**
   - Avatar/info header (`🤖 Star Lord | 🧑 Operator`)
   - Tool row
   - Chat transcript
   - Prompt input + Attach File + Send
3. **Utility tabs/panels:**
   - Files, Code, Tasks, Plugins, Settings
4. **Status + background agent area:**
   - Status bar messages for all actions
   - Qt system tray integration (show/quit)

## Button Mapping

| Button | Action |
|---|---|
| Listen | Start voice capture (`handle_voice`) |
| Type | Focus input box |
| Stop | Request stop flag on current command |
| Play | TTS playback generation for latest assistant response |
| Send | Send text to modular command system (`handle_text`) |
| Attach File / File Explorer | Load file and process through file command (`handle_file`) |
| Memory | Query vector memory with current input |
| Plugins | Open plugins tab |
| Settings | Open settings tab |
| New Session | Create and switch to a new chat session |

## Workflow

1. User enters text, speaks, or selects a file.
2. UI dispatches action to `AgentCommandSystem`.
3. Command system executes:
   - routes to `Agent` inference placeholder (`Agent.handle_input`)
   - persists memory (`FileMemoryStore`, `SimpleVectorMemory`)
   - updates current session history
4. UI receives async completion/error callback, updates transcript/status, and re-enables controls.

## Accessibility and Responsiveness

- Keyboard shortcuts in Qt for core controls (`Ctrl+L`, `Ctrl+T`, `Ctrl+P`, `Ctrl+Return`).
- Accessible names/descriptions on major controls in Qt.
- Background threading in both frontends for voice/file/inference paths to keep UI responsive.
- Error dialogs/status hints for failed actions.

## Extensibility

- Replace `Agent.handle_input` with real LLM calls without changing UI wiring.
- Swap voice adapters via existing settings (`vosk/whisper`, `piper`).
- Replace assets/avatars/style independently of command system logic.
