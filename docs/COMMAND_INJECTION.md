# OS Command Injection

Variant: in-band command injection using the controlled `127.0.0.1; whoami` payload. The vulnerable local route deliberately uses a shell but only permits this documented localhost demonstration, with a timeout and output cap. The secure route validates the host through an allow-list before using `execFile` without a shell. Alternatives: native functionality, avoid shell parsing, and least-privilege process execution.
