# CyberLab – Web Server Security Playground

IIIT Allahabad · IT-30001 Cyber Security · Autumn 2026. A localhost-only, deliberately vulnerable training application for demonstrating SQL injection, OS command injection, XSS, and CSRF alongside their mitigations.

## Safety

Never deploy this application or bind it beyond loopback. It uses fictional records, harmless browser alerts, a mock profile, and a command allow-list limited to localhost with a controlled `whoami` demonstration.

## Start

```bash
npm install
npm run setup
npm start
```

Open http://127.0.0.1:3000. For the cross-origin CSRF demonstration, run `npm run cert`, restart, open `https://127.0.0.1:3000`, and accept the local certificate warning. The attacker page is deliberately served under `https://localhost:3000/attacker/get`, a distinct local origin.

## Modules

| Category | Variants | Mitigation |
|---|---|---|
| SQL injection | authentication bypass | parameterized SQLite queries |
| OS command injection | in-band command injection | `execFile` + localhost allow-list |
| XSS | stored, reflected | `textContent` safe DOM sink |
| CSRF | GET-based forged action | synchronizer token |

See `docs/` for report content, demonstration scripts, evidence guidance, and viva preparation.
