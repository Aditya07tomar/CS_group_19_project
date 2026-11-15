# SQL Injection

Variant: authentication bypass. The vulnerable endpoint concatenates input into an `sql.js` query; the demonstration uses only seeded fictional accounts. The secure endpoint uses `?` placeholders. Demonstrate a normal login, the documented payload, the returned query result, the exact same payload against the secure endpoint, then a normal login again. Alternatives: allow-lists, least-privilege database accounts, and safe error handling.
