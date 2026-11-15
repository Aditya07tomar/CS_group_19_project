# Individual demonstration scripts

Use this 2–3 minute pattern for each category: “I am [name], demonstrating [variant]. First, this is the vulnerable code path. A normal request works. I now submit the documented harmless payload and the live output shows the effect. The root cause is that untrusted data is interpreted as instructions. Here is the secured path. I submit exactly the same payload: it is treated as data or rejected, while the normal request still works. Other defences include [relevant alternatives].”

For SQL, show authentication bypass or UNION records, then parameterization. For command injection, show `whoami` output or measured `sleep` delay, then `execFile`. For XSS, show the alert only in the vulnerable DOM sink, then literal text. For CSRF, establish a victim session over HTTPS, open the local attacker origin, then show the protected request rejects a missing token.
