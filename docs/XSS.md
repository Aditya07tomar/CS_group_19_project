# Cross-Site Scripting

Variants: stored comments and reflected search. The vulnerable browser rendering uses `innerHTML`; submit the harmless alert-only payload and observe browser execution. The secured path uses `textContent`, where the exact payload renders literally. Alternatives: framework auto-escaping, carefully configured HTML sanitization, CSP, HttpOnly cookies, and safe DOM sinks.
