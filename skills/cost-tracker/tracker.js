/**
 * Cost Tracker for OpenClaw
 * Tracks token usage and costs across sessions
 */

const fs = require('fs');
const path = require('path');

const DATA_FILE = path.join(__dirname, 'data.json');

// Pricing per 1K tokens (USD)
const PRICING = {
  'anthropic/claude-sonnet-4-6': { input: 0.003, output: 0.015, cacheRead: 0.0003 },
  'anthropic/claude-opus-4-6': { input: 0.015, output: 0.075, cacheRead: 0.0015 },
  'synthetic/hf:moonshotai/Kimi-K2.5': { input: 0.0003, output: 0.0006, cacheRead: 0 },
  'google/gemini-2.5-flash-exp': { input: 0.0001, output: 0.0004, cacheRead: 0 },
  'google/gemini-2.5-flash-lite': { input: 0.000075, output: 0.0003, cacheRead: 0 },
  'openai/gpt-5.2': { input: 0.005, output: 0.015, cacheRead: 0 },
  'default': { input: 0.003, output: 0.015, cacheRead: 0.0003 }
};

class CostTracker {
  constructor() {
    this.data = this.load();
  }

  load() {
    try {
      return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
    } catch {
      return {
        userId: '1813960285',
        created: new Date().toISOString(),
        totalSessions: 0,
        totalCostUSD: 0,
        totalTokens: { input: 0, output: 0 },
        byModel: {},
        sessions: []
      };
    }
  }

  save() {
    fs.writeFileSync(DATA_FILE, JSON.stringify(this.data, null, 2));
  }

  startSession() {
    this.currentSession = {
      id: `session_${Date.now()}`,
      started: new Date().toISOString(),
      tools: [],
      model: null,
      tokens: { input: 0, output: 0 },
      estCost: 0
    };
    return this.currentSession.id;
  }

  recordTool(toolName, model, inputTokens = 0, outputTokens = 0) {
    if (!this.currentSession) {
      this.startSession();
    }

    const pricing = PRICING[model] || PRICING.default;
    const cost = (inputTokens * pricing.input + outputTokens * pricing.output) / 1000;

    this.currentSession.tools.push({
      name: toolName,
      model,
      inputTokens,
      outputTokens,
      costUSD: cost,
      timestamp: new Date().toISOString()
    });

    this.currentSession.tokens.input += inputTokens;
    this.currentSession.tokens.output += outputTokens;
    this.currentSession.estCost += cost;
    this.currentSession.model = model;

    return cost;
  }

  endSession() {
    if (!this.currentSession) return null;

    this.currentSession.ended = new Date().toISOString();
    const session = this.currentSession; // Capture before clearing
    
    this.data.sessions.push(session);
    this.data.totalSessions++;
    this.data.totalCostUSD += session.estCost;
    this.data.totalTokens.input += session.tokens.input;
    this.data.totalTokens.output += session.tokens.output;

    // Update byModel breakdown
    const model = session.model || 'unknown';
    if (!this.data.byModel[model]) {
      this.data.byModel[model] = { calls: 0, cost: 0, tokens: { input: 0, output: 0 } };
    }
    this.data.byModel[model].calls++;
    this.data.byModel[model].cost += session.estCost;
    this.data.byModel[model].tokens.input += session.tokens.input;
    this.data.byModel[model].tokens.output += session.tokens.output;

    this.currentSession = null; // Clear after saving
    this.save();
    return session;
  }

  getReport() {
    const today = new Date().toISOString().split('T')[0];
    const todaySessions = this.data.sessions.filter(s => s.started.startsWith(today));
    const todayCost = todaySessions.reduce((sum, s) => sum + s.estCost, 0);

    return {
      total: {
        sessions: this.data.totalSessions,
        cost: this.data.totalCostUSD.toFixed(4),
        tokens: this.data.totalTokens
      },
      today: {
        sessions: todaySessions.length,
        cost: todayCost.toFixed(4)
      },
      byModel: this.data.byModel,
      current: this.currentSession ? {
        tools: this.currentSession.tools.length,
        cost: this.currentSession.estCost.toFixed(4),
        model: this.currentSession.model
      } : null
    };
  }

  formatReport() {
    const r = this.getReport();
    let out = `📊 Cost Report\n`;
    out += `━━━━━━━━━━━━━━━━━\n`;
    out += `Today: $${r.today.cost} (${r.today.sessions} sessions)\n`;
    out += `Total: $${r.total.cost} (${r.total.sessions} sessions)\n`;
    out += `Tokens: ${r.total.tokens.input.toLocaleString()} in / ${r.total.tokens.output.toLocaleString()} out\n`;
    if (r.current) {
      out += `Current: $${r.current.cost} (${r.current.tools} tools)\n`;
    }
    out += `━━━━━━━━━━━━━━━━━\n`;
    return out;
  }
}

// CLI usage
if (require.main === module) {
  const tracker = new CostTracker();
  const args = process.argv.slice(2);
  
  if (args[0] === 'report') {
    console.log(tracker.formatReport());
  } else if (args[0] === 'start') {
    const id = tracker.startSession();
    tracker.save();
    console.log(`Session started: ${id}`);
  } else if (args[0] === 'end') {
    const session = tracker.endSession();
    console.log(`Session ended: ${session.id}`);
    console.log(`Cost: $${session.estCost.toFixed(4)}`);
  } else {
    console.log('Usage: node tracker.js [start|end|report]');
  }
}

module.exports = { CostTracker, PRICING };
