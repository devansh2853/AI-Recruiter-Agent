import express from "express";
import path from 'path';
import { fileURLToPath } from 'url';
import bcrypt from 'bcrypt';
import { v4 as uuidv4 } from 'uuid';
import db from './db.js';
import composio from './config/composio.js';
import { getAuthConfigIdForProvider } from './config/authConfigs.js';

import multer from 'multer';
import { spawn } from 'child_process';


const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        console.log('Uploading to folder uploads')
    cb(null, 'uploads/'); // keep the folder in root
  },
  filename: (req, file, cb) => {
    // Use the default random name + .pdf
      const ext = '.pdf';
      const filename = file.fieldname + '-' + Date.now() + ext;
        console.log('Saving file as:', filename);
    cb(null, file.fieldname + '-' + Date.now() + ext);
  }
});


// const upload = multer({ dest: "uploads/" });
const upload = multer({storage: storage});


const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// Serve static frontend
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
app.use(express.static(path.join(__dirname, 'frontend')));
// Auth: signup
app.post('/auth/signup', async (req, res) => {
    try {
        const { username, password } = req.body;
        if (!username || !password) return res.status(400).json({ error: 'username and password required' });
        const userId = uuidv4();
        const passwordHash = await bcrypt.hash(password, 10);
        const stmt = db.prepare('INSERT INTO users (id, username, password_hash, created_at) VALUES (?, ?, ?, ?)');
        stmt.run(userId, username, passwordHash, Date.now());
        return res.json({ user_id: userId });
    } catch (err) {
        if (String(err.message).includes('UNIQUE')) return res.status(409).json({ error: 'username taken' });
        return res.status(500).json({ error: 'signup failed' });
    }
});

// Auth: login
app.post('/auth/login', async (req, res) => {
    try {
        const { username, password } = req.body;
        if (!username || !password) return res.status(400).json({ error: 'username and password required' });
        const row = db.prepare('SELECT id, username, password_hash FROM users WHERE username = ?').get(username);
        if (!row) return res.status(401).json({ error: 'invalid credentials' });
        const ok = await bcrypt.compare(password, row.password_hash);
        if (!ok) return res.status(401).json({ error: 'invalid credentials' });
        return res.json({ user_id: row.id, username: row.username });
    } catch (err) {
        return res.status(500).json({ error: 'login failed' });
    }
});

// Get user profile
app.get('/users/:userId', (req, res) => {
    const { userId } = req.params;
    const row = db.prepare('SELECT id, username FROM users WHERE id = ?').get(userId);
    if (!row) return res.status(404).json({ error: 'user not found' });
    return res.json(row);
});

// Get connection statuses for all providers
app.get('/users/:userId/connections/status', (req, res) => {
    const { userId } = req.params;
    const rows = db.prepare('SELECT provider, connection_id FROM user_connections WHERE user_id = ?').all(userId);
    const status = { gmail: false, docs: false};
    for (const r of rows) {
        if (r.provider in status) status[r.provider] = !!r.connection_id;
    }
    return res.json(status);
});


// Initiate a Composio connection for a provider using an authConfigId
app.post('/users/:userId/connections/initiate', async (req, res) => {
    const { userId } = req.params;
    const { provider } = req.body;
    if (!provider) return res.status(400).json({ error: 'provider required' });
    try {
        const authConfigId = getAuthConfigIdForProvider(provider);
        if (!authConfigId) return res.status(400).json({ error: 'unknown provider' });
        
        let cr;
        // For other providers, use OAuth flow
        const connections = db.prepare('SELECT connection_id, provider FROM user_connections WHERE user_id = ?').all(userId);
        //Delete existing connection
        for (const connection of connections) {
            if (connection.provider === provider) {
                await composio.connectedAccounts.delete(connection.connection_id);
                db.prepare('DELETE FROM user_connections WHERE user_id = ? AND provider = ?').run(userId, provider);
            }
        }

        //Create New Connection
        cr = await composio.connectedAccounts.initiate(userId, authConfigId);
        db.prepare('INSERT INTO pending_connections (user_id, provider, connection_request_id, created_at) VALUES (?, ?, ?, ?)').run(userId, provider, cr.id, Date.now());
        return res.json({ connection_request_id: cr.id, redirect_url: cr.redirectUrl });
    } catch (err) {
        console.log(err.message);
        return res.status(500).json({ error: 'failed to initiate connection' });
    }
});

// Finalize/poll and persist connection
app.post('/users/:userId/connections/finalize-latest', async (req, res) => {
    const { userId } = req.params;
    const { provider, timeout_ms } = req.body;
    if (!provider) return res.status(400).json({ error: 'provider required' });
    const pending = db.prepare('SELECT connection_request_id FROM pending_connections WHERE user_id = ? AND provider = ? ORDER BY created_at DESC LIMIT 1').get(userId, provider);
    try {
        if (!pending) return res.status(404).json({ error: 'no pending request found' });
        const timeout = Number(timeout_ms) || 300000;
        await composio.connectedAccounts.waitForConnection(pending.connection_request_id, timeout);
        const connected = await composio.connectedAccounts.get(pending.connection_request_id);
        const existing = db.prepare('SELECT connection_id FROM user_connections WHERE user_id = ? AND provider = ?').get(userId, provider);
        if (existing && existing.connection_id && existing.connection_id !== connected.id) {
            try { await composio.connectedAccounts.delete(existing.connection_id); } catch (e) { /* ignore cleanup errors */ }
        }

        db.prepare('INSERT INTO user_connections (user_id, provider, connection_id, created_at) VALUES (?, ?, ?, ?) ON CONFLICT(user_id, provider) DO UPDATE SET connection_id = excluded.connection_id').run(userId, provider, connected.id, Date.now());


        db.prepare('DELETE FROM pending_connections WHERE user_id = ? AND provider = ?').run(userId, provider);
        
        return res.json({ ok: true, connection_id: connected.id });
    } catch (err) {
        console.log(err.message);
        await composio.connectedAccounts.delete(pending.connection_request_id);
        return res.status(500).json({ error: 'failed to finalize connection' });
    }
});

//Handle File Upload
app.post('/users/:userId/resume', upload.single('resume'), (req, res) => {
    const { userId } = req.params;
    console.log(userId);
    if (!req.file) {
      return res.status(400).json({ ok: false, error: "No resume file uploaded" });
    }
    // Full path of uploaded resume
    const resumePath = req.file.path;
    const python = spawn('python3', ['src/python-llm/main.py', resumePath]);

    let output = '';
    let errorOutput = '';

    // Collect stdout data
    python.stdout.on('data', (data) => {
      output += data.toString();
    });

    // Collect stderr data
    python.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    python.on('close', (code) => {
        if (code !== 0) {
            console.log("Failed");
            return res.status(400).json({ok: false, error: `Python process exited with code ${code}: ${errorOutput}`})
      }
      try {
        const result = JSON.parse(output); // Expect JSON string from Python
          if (!result.successful) return res.status(400).json({ ok: false, error: result.error })
          return res.status(200).json({ok: true})
      } catch (err) {
        return res.status(400).json({ok: false, error: `Failed to parse python output: ${output}`})
      }
    });
});


const PORT = 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});
