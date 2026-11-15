# Cross-Site Request Forgery

Variant: state-changing GET. Establish a local HTTPS victim session at `127.0.0.1`, then open the attacker page at `localhost` to create a distinct origin. The secure action requires a session-bound synchronizer token and rejects missing tokens. Alternatives: restrictive SameSite cookies, re-authentication, and avoiding state-changing GET endpoints.
