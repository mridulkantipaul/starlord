# Mobile Scaffolding (Android/iOS)

This directory provides **starter scaffolding** and **design guidance** for building Star Lord on mobile devices. The core agent remains in Python; mobile apps will communicate with it via a local service or a bundled runtime (to be decided).

## Recommended Architecture (Phase 4)
**Option A — Local service bridge (recommended for MVP)**
- Run the Python agent as a **local service** on the device (or nearby host).
- Mobile app communicates via **localhost HTTP/WebSocket**.
- Pros: keeps Python core intact, simpler iteration.

**Option B — Embedded runtime**
- Embed Python (e.g., Python on Android / iOS via embedded runtime).
- Pros: fully on-device, offline-first.
- Cons: higher complexity.

## Directory Layout
```
mobile/
  android/
    README.md
  ios/
    README.md
```

## Next Steps
- Decide the mobile architecture (A or B).
- Add UI shell (voice input button, conversation timeline).
- Hook into device STT/TTS (native or via Python bridge).

See platform-specific notes in `mobile/android/README.md` and `mobile/ios/README.md`.
