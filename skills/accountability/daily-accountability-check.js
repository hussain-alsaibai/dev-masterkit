#!/usr/bin/env node
/**
 * Daily Accountability Check — verify commits, flag zero days
 * Usage: node daily-accountability-check.js
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const MEMORY_DIR = path.join(__dirname, '..', '..', 'memory');
const GITHUB_DIR = path.join(process.env.HOME, 'github');

function runCommand(cmd, timeout = 10000) {
  try {
    return execSync(cmd, { timeout, encoding: 'utf8' }).trim();
  } catch (e) {
    return null;
  }
}

function today() {
  return new Date().toISOString().split('T')[0];
}

function todayAST() {
  // AST is UTC+3, so "today" in AST may be different from UTC
  const now = new Date();
  const astOffset = 3 * 60 * 60 * 1000;
  const astTime = new Date(now.getTime() + astOffset);
  return astTime.toISOString().split('T')[0];
}

function countCommitsToday() {
  const todayStr = todayAST();
  let totalCommits = 0;
  
  // Check workspace
  const workspaceDir = path.join(process.env.HOME, '.openclaw', 'workspace');
  try {
    const log = execSync(
      `cd "${workspaceDir}" && git log --since="${todayStr}T00:00:00" --until="${todayStr}T23:59:59" --oneline`,
      { encoding: 'utf8' }
    );
    const lines = log.trim().split('\n').filter(l => l.length > 0);
    totalCommits += lines.length;
  } catch (e) {}

  // Check dev-masterkit
  const devkitDir = path.join(workspaceDir, 'dev-masterkit');
  try {
    const log = execSync(
      `cd "${devkitDir}" && git log --since="${todayStr}T00:00:00" --until="${todayStr}T23:59:59" --oneline`,
      { encoding: 'utf8' }
    );
    const lines = log.trim().split('\n').filter(l => l.length > 0);
    totalCommits += lines.length;
  } catch (e) {}

  // Check all github repos
  if (fs.existsSync(GITHUB_DIR)) {
    const repos = fs.readdirSync(GITHUB_DIR).filter(d => {
      return fs.statSync(path.join(GITHUB_DIR, d)).isDirectory() &&
             fs.existsSync(path.join(GITHUB_DIR, d, '.git'));
    });
    
    for (const repo of repos) {
      try {
        const log = execSync(
          `cd "${path.join(GITHUB_DIR, repo)}" && git log --since="${todayStr}T00:00:00" --until="${todayStr}T23:59:59" --oneline`,
          { encoding: 'utf8' }
        );
        const lines = log.trim().split('\n').filter(l => l.length > 0);
        totalCommits += lines.length;
      } catch (e) {}
    }
  }

  return totalCommits;
}

function main() {
  console.log(`[${new Date().toISOString()}] === Daily Accountability Check ===`);
  console.log(`Checking commits for ${todayAST()} (AST)`);

  const commitCount = countCommitsToday();
  console.log(`Commits today: ${commitCount}`);

  // Log to daily file
  const dailyFile = path.join(MEMORY_DIR, `${today()}.md`);
  const status = commitCount > 0 ? '✅ PASS' : '🚨 ZERO-COMMIT DAY';
  const entry = `
## Accountability Check — ${todayAST()}
- Commits today: ${commitCount}
- Status: ${status}
`;
  fs.appendFileSync(dailyFile, entry);

  if (commitCount === 0) {
    console.log('🚨 ZERO-COMMIT DAY — triggering emergency work session');
    
    const emergencyMsg = `🚨 **ZERO-COMMIT DAY ALERT**

No commits shipped today (${todayAST()}).

**Emergency Protocol:**
1. Run bounty scanner immediately
2. Pick smallest non-scam issue
3. Fix and commit within 30 minutes
4. Report back

This is an automated accountability check.
`;
    console.log('\n---TELEGRAM---\n' + emergencyMsg + '\n---END---');
    
    // Try to trigger immediate bounty work
    try {
      execSync('node ' + path.join(__dirname, '..', 'bounty-scanner', 'daily-bounty-work.js'), {
        timeout: 180000,
        stdio: 'inherit'
      });
    } catch (e) {
      console.log('Emergency work session failed:', e.message);
    }
  } else {
    console.log(`✅ ${commitCount} commit(s) shipped today. Good work.`);
    
    const successMsg = `✅ **Accountability Check — ${todayAST()}**

${commitCount} commit(s) shipped today.

Keep the streak alive! 🔥`;
    console.log('\n---TELEGRAM---\n' + successMsg + '\n---END---');
  }
}

main();
