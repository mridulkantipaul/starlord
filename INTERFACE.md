# Star Lord Interface Specification

Reference design image: [`ChatGPT Image May 19, 2026, 11_56_28 PM.png`](https://github.com/user-attachments/assets/05cbde08-6b48-46f4-884c-5b8c2fe9ca67).

The current UI is structured to match that design language: session rail, central chat deck, right-side command tools, avatar/agent zone, and persistent status feedback.

## Frontends

- **Primary:** PyQt (`src/starlord/gui_qt.py`)
- **Fallback:** Tkinter (`src/starlord/gui.py`)

Both frontends call the same modular workflow layer: `src/starlord/command_system.py`.

## Layout Mapping

### PyQt layout

1. **Left session rail**
   - session list
   - new session button
2. **Central command deck**
   - Star Lord header
   - chat/history transcript
   - prompt entry
   - attach file button
   - send button
3. **Lower utility workspace**
   - Files
   - Code
   - Tasks
   - Plugins
   - Settings
4. **Right tool rail**
   - avatar/agent zone
   - listen
   - type
   - send
   - stop
   - play
   - file explorer
   - memory
   - plugins
   - settings
5. **Indicators**
   - agent state label
   - system/tray indicator
   - current session indicator
   - status bar for transient feedback

### Tk fallback layout

- central chat deck
- prompt/send row
- right-side avatar/tool rail
- status footer

## Button Responses

| Control | Primary behavior | User feedback |
|---|---|---|
| Listen | Calls `handle_voice()` asynchronously | Status bar shows running/captured state, prompt is filled on success |
| Type | Focuses prompt input | Status text reports type mode and agent state changes to `Typing` |
| Send | Calls `handle_text()` asynchronously | User prompt is echoed to transcript, result/error is appended |
| Stop | Calls `request_stop()` | Status shows stop request and agent state changes to `Stopped` |
| Play | Calls `play_last_response()` asynchronously | Status shows playback generation or friendly error |
| Attach File | Opens picker and routes file into `handle_file()` | Transcript/status update on completion or file error |
| File Explorer | Opens Files workspace tab | Status confirms the workspace is ready |
| Memory | Queries vector memory using current input | Transcript shows matches or `No matches`, status shows result count |
| Plugins | Opens Plugins workspace tab | Status confirms plugin manager is ready |
| Settings | Opens Settings workspace tab | Status confirms settings panel is ready |
| New Session | Creates a fresh session and activates it | Session indicator and status bar update immediately |

## Workflow

1. User provides text, voice, or file input.
2. The UI dispatches work into `AgentCommandSystem`.
3. `AgentCommandSystem` routes the request into:
   - `Agent.handle_input()` for AI response generation
   - `FileMemoryStore` and `SimpleVectorMemory` for persistence/search
   - session state for transcript continuity
4. The frontend receives success/error callbacks and:
   - re-enables controls
   - updates transcript
   - updates the status bar
   - updates the visible agent state

## Error Handling

- Missing voice/TTS dependencies surface as friendly dependency warnings.
- Bad file paths surface as user-fixable file warnings.
- Send failures append a safe assistant apology line to the transcript.
- Empty prompt, empty memory search, empty task entry, and empty code analysis input all show immediate status guidance.

## Accessibility and Responsiveness

- Qt keyboard shortcuts: `Ctrl+L`, `Ctrl+T`, `Ctrl+P`, `Ctrl+Return`
- accessible names/descriptions on major Qt controls
- threaded action execution to keep the interface responsive
- status-driven feedback for every major button action

## Usage

```bash
python -m starlord.app --gui-qt
python -m starlord.app --gui
```

## Extension Points

- swap the `Agent.handle_input()` placeholder for a real LLM/backend
- extend plugin discovery via `starlord.plugins`
- replace voice adapters without changing the desktop interface wiring
