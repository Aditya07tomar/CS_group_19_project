"""
CSRF through a state-changing GET request.
"""
from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = "demo-secret-key-not-for-production"

USERS = {}
HISTORY = []


def reset_state():
    USERS.clear()
    USERS.update({
        "victim":   {"password": "victim123",   "balance": 10000},
        "attacker": {"password": "attacker123", "balance": 0},
    })
    HISTORY.clear()


reset_state()

STYLE = """
<style>
 :root{font-family:Arial,Helvetica,sans-serif;color:#10243a;background:#f6f7fc;font-synthesis:none}
 *{box-sizing:border-box}
 body{margin:0;min-height:100vh;background:#f6f7fc}
 .demo-bar{display:flex;justify-content:space-between;gap:12px;padding:6px 16px;background:#ffe4d5;border-top:3px solid #6658ed;color:#6b392a;font:700 10px/1.3 Consolas,monospace;letter-spacing:.08em}
 .shell{width:min(100% - 28px,1180px);margin:0 auto}
 .topbar{display:flex;align-items:center;justify-content:space-between;min-height:62px;border-bottom:1px solid #e8ebf3}
 .brand{display:flex;align-items:center;gap:10px}
 .brand-mark,.user-mark{display:grid;place-items:center;width:34px;height:34px;border-radius:10px;background:#092137;color:white;font-size:17px}
 .brand-name{margin:0;font-size:15px;font-weight:700}
 .subline{margin:3px 0 0;color:#627187;font-size:11px}
 .subline strong{color:#315ca8}
 .account-actions{display:flex;align-items:center;gap:10px}
 .logout{color:#d64c4c;text-decoration:none;font:700 11px Consolas,monospace}
 .user-mark{width:30px;height:30px;border-radius:50%;font-size:14px}
 .module-row{display:flex;align-items:center;justify-content:space-between;padding:10px 0;color:#68758a;font:700 10px Consolas,monospace;letter-spacing:.08em}
 .status{padding:5px 8px;border-radius:5px;background:#fff0ef;color:#bf4747;font:700 9px Consolas,monospace;letter-spacing:.05em}
 .notice{display:flex;align-items:center;gap:10px;margin-bottom:12px;padding:11px 14px;border-radius:8px;background:#edf3ff;color:#203a5d;font-size:12px}
 .notice-icon{display:grid;place-items:center;flex:0 0 18px;height:18px;border:1px solid #3c72da;border-radius:50%;color:#2861c1;font-weight:700}
 .card{margin:12px 0;padding:16px;border:1px solid #edf0f6;border-radius:10px;background:#fff;box-shadow:0 2px 8px #1a2c4908}
 .balance-card{padding:17px 18px}
 .card-top,.section-heading{display:flex;align-items:center;justify-content:space-between;gap:12px}
 .eyebrow{color:#647187;font:700 10px Consolas,monospace;letter-spacing:.09em}
 .active-pill{padding:4px 8px;border-radius:99px;background:#e8edff;color:#334e9a;font:700 9px Consolas,monospace}
 .balance-line{display:flex;align-items:baseline;gap:6px;margin:5px 0 8px}
 .balance{font-size:22px;font-weight:700;letter-spacing:-.03em}
 .currency{color:#647187;font:700 9px Consolas,monospace}
 .account-label{margin:0;color:#718096;font-size:11px}
 .section-heading{margin:0 0 14px}
 .section-heading h2{margin:0;font-size:14px;font-weight:700}
 .heading-icon{margin-right:5px;color:#152d49}
 .section-note{color:#718096;font:9px Consolas,monospace;letter-spacing:.06em}
 .field{display:block;margin:12px 0}
 .field-label{display:block;margin-bottom:7px;font-size:11px;font-weight:600}
 input{display:block;width:100%;height:39px;padding:0 11px;border:1px solid #e5e9f1;border-radius:6px;background:#fff;color:#10243a;font:12px Arial,sans-serif;outline:none}
 input::placeholder{color:#9aa5b5}
 input:focus{border-color:#788ded;box-shadow:0 0 0 3px #7186e21c}
 button{width:100%;height:39px;margin-top:1px;border:0;border-radius:6px;background:#061b2e;color:#fff;font-size:12px;font-weight:700;cursor:pointer}
 button:hover{background:#102e48}
 .history-empty{display:grid;justify-items:center;gap:8px;min-height:116px;padding:18px;background:#eef3ff;text-align:center}
 .history-icon{display:grid;place-items:center;width:31px;height:31px;border-radius:10px;background:#dce7ff;color:#344d7a;font-size:16px}
 .history-empty p{margin:0;font-size:12px}
 .history-empty small{max-width:300px;color:#68758a;font-size:10px;line-height:1.5}
 .history-list{margin:0;padding:0;list-style:none}
 .history-list li{padding:10px 2px;border-top:1px solid #edf0f6;color:#41516a;font-size:12px}
 .error{margin:10px 0 0;color:#b42336;font-size:12px}
 .login-wrap{max-width:440px;margin:42px auto}
 .login-card{padding:22px}
 .login-card .section-heading{margin-bottom:18px}
 .demo-users{margin:15px 0 0;color:#718096;font-size:11px;line-height:1.6}
 @media(max-width:600px){.shell{width:min(100% - 20px,1180px)}.demo-bar{padding-inline:10px;font-size:9px}.topbar{min-height:58px}.card{padding:14px}.balance{font-size:20px}.module-row{font-size:9px}}
</style>
"""

LOGIN_HTML = STYLE + """
<div class="demo-bar"><span>△ DEMO MODE: SIMULATED ENVIRONMENT</span><span>SANDBOX V1.0</span></div>
<main class="shell login-wrap">
  <header class="topbar">
    <div class="brand"><div class="brand-mark" aria-hidden="true">⌂</div><div><h1 class="brand-name">Campus Demo Bank</h1><p class="subline">Secure learning environment</p></div></div>
    <span class="status">CSRF TARGET</span>
  </header>
  <div class="notice"><span class="notice-icon" aria-hidden="true">i</span><span>Simulation only — no real money is involved in this environment.</span></div>
  <section class="card login-card">
    <div class="section-heading"><h2>Sign in to your account</h2><span class="section-note">DEMO ACCESS</span></div>
    <form method="POST" action="{{ url_for('login') }}">
      <label class="field"><span class="field-label">Username</span><input name="username" autocomplete="username" placeholder="Enter your username" required></label>
      <label class="field"><span class="field-label">Password</span><input name="password" type="password" autocomplete="current-password" placeholder="Enter your password" required></label>
      <button type="submit">Sign in</button>
    </form>
    {% if error %}<p class="error" role="alert">{{ error }}</p>{% endif %}
    <p class="demo-users">Demo accounts: <strong>victim / victim123</strong><br><strong>attacker / attacker123</strong></p>
  </section>
</main>
"""

DASH_HTML = STYLE + """
<div class="demo-bar"><span>△ DEMO MODE: SIMULATED ENVIRONMENT</span><span>SANDBOX V1.0</span></div>
<main class="shell">
  <header class="topbar">
    <div class="brand"><div class="brand-mark" aria-hidden="true">⌂</div><div><h1 class="brand-name">Campus Demo Bank</h1><p class="subline">Logged in as: <strong>{{ user }}</strong></p></div></div>
    <div class="account-actions"><a class="logout" href="{{ url_for('logout') }}">Logout</a><div class="user-mark" aria-hidden="true">●</div></div>
  </header>
  <div class="module-row"><span>ACTIVE MODULE: ACCOUNT DASHBOARD</span><span class="status">CSRF TARGET</span></div>
  <div class="notice"><span class="notice-icon" aria-hidden="true">i</span><span>Simulation only — no real money is involved in this environment.</span></div>

  <section class="card balance-card">
    <div class="card-top"><span class="eyebrow">AVAILABLE BALANCE</span><span class="active-pill">Demo Active</span></div>
    <div class="balance-line"><span class="balance">Rs. {{ "{:,}".format(balance) }}</span><span class="currency">INR</span></div>
    <p class="account-label">◇ Demo checking account</p>
  </section>

  <section class="card">
    <div class="section-heading"><h2><span class="heading-icon" aria-hidden="true">↪</span>Transfer money</h2><span class="section-note">SIMULATED TRANSFER</span></div>
    <form method="GET" action="{{ url_for('transfer') }}">
      <label class="field"><span class="field-label">Recipient Username</span><input name="to" placeholder="e.g., attacker or classmate" required></label>
      <label class="field"><span class="field-label">Amount (Rs.)</span><input name="amount" type="number" min="1" placeholder="e.g., 500" required></label>
      <button type="submit">➜ &nbsp; Send transfer</button>
    </form>
  </section>

  <section class="card">
    <div class="section-heading"><h2><span class="heading-icon" aria-hidden="true">◷</span>Transaction history</h2><span class="section-note">{{ history|length }} ENTRIES</span></div>
    {% if history %}
      <ul class="history-list">{% for h in history %}<li>{{ h }}</li>{% endfor %}</ul>
    {% else %}
      <div class="history-empty"><span class="history-icon" aria-hidden="true">▤</span><p>No transactions yet.</p><small>Transfers made in this simulation session will appear here in chronological order.</small></div>
    {% endif %}
  </section>
</main>
"""


@app.route("/")
def index():
    return redirect(url_for("dashboard" if "user" in session else "login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        if u in USERS and USERS[u]["password"] == p:
            session["user"] = u
            return redirect(url_for("dashboard"))
        error = "Invalid credentials"
    return render_template_string(LOGIN_HTML, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    mine = [h for h in HISTORY if user in h]
    return render_template_string(DASH_HTML, user=user,
                                  balance=USERS[user]["balance"], history=mine)


# ---------------------------------------------------------------------------
# VULNERABLE CODE PATH (item a)
# State-changing action exposed on GET. The only check is "is there a valid
# session cookie?". The browser attaches that cookie automatically to ANY
# request to this site, including ones triggered by <img src=...> on another
# page. There is no CSRF token and no proof the user intended the action.
# ---------------------------------------------------------------------------
@app.route("/transfer")
def transfer():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))

    to = request.args.get("to", "")
    try:
        amount = int(request.args.get("amount", "0"))
    except ValueError:
        return "Invalid amount", 400

    if to not in USERS or to == user or amount <= 0 or amount > USERS[user]["balance"]:
        return "Transfer failed", 400

    USERS[user]["balance"] -= amount
    USERS[to]["balance"] += amount
    HISTORY.append(f"{user} -> {to}: Rs. {amount}")
    return redirect(url_for("dashboard"))


# Demo helper: resets balances between takes while recording the video.
@app.route("/reset")
def reset():
    reset_state()
    session.clear()
    return "State reset. <a href='/login'>Login</a>"


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=False)
