# Project Report

## Objective and architecture

CyberLab is a single Express application bound to `127.0.0.1`. `sql.js` holds fictional seeded users and products. The browser SPA provides a dashboard, variant controls, live output panels, and evidence guidance. State is intentionally small and resettable: comments and profile changes live only in process memory.

## Findings and mitigations

SQL injection occurs when a concatenated string is parsed as SQL. The vulnerable authentication and product-search routes execute the resulting query; prepared placeholders preserve input as data. Command injection occurs where shell parsing sees a semicolon in the constructed ping command; `execFile` supplies an argument vector without a shell. Stored/reflected XSS comes from assigning untrusted HTML to `innerHTML`; the secured demonstrations use `textContent`. CSRF routes demonstrate why a cookie alone does not prove user intent; the secure action checks a session-bound synchronizer token and state-changing GET is avoided.

## Alternatives and limits

Use allow-lists, least privilege, safe error handling, framework auto-escaping, HTML sanitization only where rich HTML is essential, CSP as defence in depth, restrictive SameSite cookies, and re-authentication for sensitive actions. This lab is intentionally not production-ready: its vulnerable routes exist only for local demonstration. Do not claim screenshots or browser observations that were not captured.
