/* LOCAL-ONLY EDUCATIONAL LAB. Never deploy this server. */
const express = require('express');
const cookieParser = require('cookie-parser');
const initSqlJs = require('sql.js');
const {
  exec,
  execFile
} = require('child_process');
const fs = require('fs');
const https = require('https');
const crypto = require('crypto');

const app = express();
app.use(express.json());
app.use(express.urlencoded({
  extended: false
}));
app.use(cookieParser());
app.use(express.static('public'));
const HOST = '127.0.0.1',
  PORT = 3000;
let db, comments = [{
  id: 1,
  text: 'Welcome to the seeded CyberLab discussion.'
}];
let profile = {
  displayName: 'Demo Student'
};
const sessions = new Map();
const safe = (fn) => (req, res) => Promise.resolve(fn(req, res)).catch(e => res.status(500).json({
  ok: false,
  error: e.message
}));
const rows = (stmt) => {
  const out = [];
  while (stmt.step()) out.push(stmt.getAsObject());
  stmt.free();
  return out;
};
const q = (sql, params) => rows(db.prepare(sql, params));

function session(req, res) {
  let id = req.cookies.cyberlab_session;
  if (!id || !sessions.has(id)) {
    id = crypto.randomUUID();
    sessions.set(id, {
      csrf: crypto.randomBytes(24).toString('hex')
    });
    res.cookie('cyberlab_session', id, {
      httpOnly: true,
      sameSite: 'none',
      secure: Boolean(app.locals.https)
    });
  }
  return sessions.get(id);
}

function validHost(host) {
  return /^(127\.0\.0\.1|localhost|::1)$/.test(host);
}

app.get('/api/dashboard', (req, res) => {
  res.json({
    variants: 5,
    profile,
    comments: comments.length
  });
});

// SQL injection: vulnerable paths deliberately concatenate data into sql.js queries.
app.post('/api/sqli/auth/:mode', safe((req, res) => {
  const {
    username = '', password = ''
  } = req.body;
  const sql = req.params.mode === 'vulnerable' ? `SELECT id, username, role FROM users WHERE username = '${username}' AND password = '${password}'` : 'SELECT id, username, role FROM users WHERE username = ? AND password = ?';
  const result = q(sql, req.params.mode === 'secure' ? [username, password] : undefined);
  res.json({
    ok: true,
    sql,
    authenticated: result.length > 0,
    records: result
  });
}));

// Command injection lab: the shell endpoint only allows the documented harmless suffix.
function command(req, res, blind) {
  const host = String(req.body.host || '');
  const mode = req.params.mode;
  const start = Date.now();
  if (mode === 'secure') {
    if (!validHost(host)) return res.json({
      ok: false,
      blocked: true,
      message: 'Allow-list rejected host; no command was run.',
      duration: Date.now() - start
    });
    return execFile('/sbin/ping', ['-c', '1', host], {
      timeout: 2500,
      maxBuffer: 8192
    }, (err, stdout, stderr) => res.json({
      ok: !err,
      blocked: false,
      duration: Date.now() - start,
      output: (stdout || stderr || '').slice(0, 2000)
    }));
  }
  if (!/^(127\.0\.0\.1|localhost)(; whoami)?$/.test(host)) return res.status(400).json({
    ok: false,
    error: 'Lab allows only localhost or the documented ; whoami demonstration.'
  });
  const cmd = `/sbin/ping -c 1 ${host}`;
  exec(cmd, {
    timeout: 5500,
    maxBuffer: 8192
  }, (err, stdout, stderr) => res.json({
    ok: !err,
    command: cmd,
    duration: Date.now() - start,
    output: blind ? '(Blind mode intentionally suppresses command output.)' : (stdout || stderr || '').slice(0, 2000),
    evidence: blind ? `Measured response duration: ${Date.now()-start} ms` : undefined
  }));
}
app.post('/api/command/inband/:mode', (req, res) => command(req, res, false));

app.get('/api/xss/comments', (req, res) => res.json(comments));
app.post('/api/xss/comments', (req, res) => {
  const text = String(req.body.text || '').slice(0, 500);
  comments.push({
    id: Date.now(),
    text
  });
  res.json({
    ok: true
  });
});
app.delete('/api/xss/comments', (req, res) => {
  comments = [{
    id: 1,
    text: 'Welcome to the seeded CyberLab discussion.'
  }];
  res.json({
    ok: true
  });
});

app.get('/api/csrf/profile', (req, res) => {
  const s = session(req, res);
  res.json({
    profile,
    token: s.csrf
  });
});

function csrfChange(req, res, secure) {
  const s = session(req, res);
  if (secure && req.body.csrfToken !== s.csrf) return res.status(403).json({
    ok: false,
    error: 'Invalid synchronizer token: request rejected.'
  });
  profile.displayName = String(req.body.displayName || req.query.name || '').slice(0, 60);
  res.json({
    ok: true,
    profile,
    secure
  });
}
app.get('/api/csrf/vulnerable/change-name', (req, res) => csrfChange(req, res, false));
app.post('/api/csrf/vulnerable/change-name', (req, res) => csrfChange(req, res, false));
app.post('/api/csrf/secure/change-name', (req, res) => csrfChange(req, res, true));
app.post('/api/csrf/reset', (req, res) => {
  profile.displayName = 'Demo Student';
  res.json({
    ok: true,
    profile
  });
});
app.get('/attacker/get', (req, res) => {
  const target = `${app.locals.https?'https':'http'}://127.0.0.1:${PORT}`;
  res.type('html').send(`<!doctype html><title>Local CSRF demo — GET</title><h1>Attacker GET page</h1><p>Local educational demonstration only.</p><img alt="forged request" src="${target}/api/csrf/vulnerable/change-name?name=Forged%20GET">`);
});

initSqlJs().then(SQL => {
  db = new SQL.Database();
  db.run(`CREATE TABLE users (id INTEGER, username TEXT, password TEXT, role TEXT); CREATE TABLE products (id INTEGER, name TEXT, price TEXT); INSERT INTO users VALUES (1,'admin','demo-admin-password','administrator'),(2,'learner','learning-only','student'); INSERT INTO products VALUES (1,'Packet Sentinel','299'),(2,'Blue Team Notebook','149');`);
  const cert = 'certs/cert.pem',
    key = 'certs/key.pem';
  if (fs.existsSync(cert) && fs.existsSync(key)) {
    app.locals.https = true;
    https.createServer({
      cert: fs.readFileSync(cert),
      key: fs.readFileSync(key)
    }, app).listen(PORT, HOST, () => console.log(`CyberLab HTTPS: https://${HOST}:${PORT} (attacker: https://localhost:${PORT}/attacker/get)`));
  } else app.listen(PORT, HOST, () => console.log(`CyberLab HTTP: http://${HOST}:${PORT} — run npm run cert for HTTPS CSRF demo.`));
});
