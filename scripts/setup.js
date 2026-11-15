const fs = require('fs');
const path = require('path');
for (const dir of ['data', 'evidence/sqli', 'evidence/command-injection', 'evidence/xss', 'evidence/csrf']) {
  fs.mkdirSync(path.join(process.cwd(), dir), { recursive: true });
}
console.log('CyberLab workspace initialized. Run npm run cert for the full CSRF browser demonstration, then npm start.');
