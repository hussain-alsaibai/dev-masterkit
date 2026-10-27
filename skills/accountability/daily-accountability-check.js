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

// Discover every git repo on disk.
// The previous version only checked 3 fixed paths (workspace, workspace/dev-masterkit,
// ~/github/*). Real work is committed in workspace/tiny-* (top-level checkouts) and
// repos/* worktrees, which that scan never saw — producing false ZERO-COMMIT days.
function discoverRepos() {
  const found = new Set();
  const roots = [
    path.join(process.env.HOME, '.openclaw', 'workspace'),
    GITHUB_DIR,
  ];

  for (const root of roots) {
    if (!fs.existsSync(root)) continue;
    const stack = [[root, 0]];
    while (stack.length) {
      const [dir, depth] = stack.pop();
      if (depth > 4) continue;
      let entries;
      try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch (e) { continue; }
      for (const ent of entries) {
        if (!ent.isDirectory()) continue;
        const full = path.join(dir, ent.name);
        if (SKIP_DIRS.includes(ent.name)) continue;
        if (fs.existsSync(path.join(full, '.git'))) { found.add(full); continue; }
        stack.push([full, depth + 1]);
      }
    }
  }
  return [...found];
}

const SKIP_DIRS = ['node_modules', '.venv', 'venv', '__pycache__', '.cache', 'site-packages'];

function commitsInRepo(dir, todayStr) {
  try {
    const log = execSync(
      'cd "' + dir + '" && git log --since="' + todayStr + 'T00:00:00" --until="' + todayStr + 'T23:59:59" --oneline 2>/dev/null',
      { encoding: 'utf8', timeout: 15000 }
    );
    return log.trim() ? log.trim().split('\n').filter(l => l.length > 0) : [];
  } catch (e) {
    return [];
  }
}

function countCommitsToday() {
  const todayStr = todayAST();
  let totalCommits = 0;
  const repos = discoverRepos();
  const perRepo = [];

  for (const repo of repos) {
    const commits = commitsInRepo(repo, todayStr);
    if (commits.length) {
      perRepo.push({ repo, count: commits.length, commits });
      totalCommits += commits.length;
    }
  }

  return { total: totalCommits, repos, perRepo };
}

// --- Publish verification -------------------------------------------------
// The original check counted LOCAL commits only, so it reported PASS even while
// every push was failing on a dead PAT. A commit is not a ship until the remote
// has it. These helpers measure the real published state.

function upstreamOf(dir) {
  try {
    const ref = execSync('cd "' + dir + '" && git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null', {
      encoding: 'utf8', timeout: 10000,
    }).trim();
    return ref || null;
  } catch (e) {
    return null;
  }
}

// Commits on the current branch that the upstream does not have.
function unpushedInRepo(dir) {
  try {
    const n = parseInt(execSync(
      'cd "' + dir + '" && git rev-list --count @{u}..HEAD 2>/dev/null',
      { encoding: 'utf8', timeout: 15000 }
    ).trim(), 10);
    return Number.isFinite(n) ? n : 0;
  } catch (e) {
    return 0;
  }
}

function totalUnpushed(repos) {
  let total = 0;
  const offenders = [];
  for (const repo of repos) {
    if (!upstreamOf(repo)) continue;
    const n = unpushedInRepo(repo);
    if (n > 0) {
      total += n;
      offenders.push({ repo, count: n });
    }
  }
  offenders.sort((a, b) => b.count - a.count);
  return { total, offenders };
}

// Repos with no origin remote at all can never publish.
function reposWithoutRemote(repos) {
  const out = [];
  for (const repo of repos) {
    try {
      const remotes = execSync('cd "' + repo + '" && git remote 2>/dev/null', {
        encoding: 'utf8', timeout: 10000,
      }).trim();
      if (!remotes) out.push(repo);
    } catch (e) {
      out.push(repo);
    }
  }
  return out;
}

// Credential sources in trust order. The gateway process env can hold a STALE
// token (e.g. a revoked fine-grained PAT) while the live classic PAT sits in the
// workspace .env, ~/.git-credentials, or gh hosts.yml. Probing process.env only
// produced false "auth BROKEN" verdicts and hid the fact that pushes would work.
function credentialCandidates() {
  const out = [];
  const seen = new Set();
  const add = (label, token) => {
    const tok = (token || '').trim();
    if (!tok || seen.has(tok)) return;
    seen.add(tok);
    out.push({ label, token: tok });
  };

  add('process.env.GitHUB_PAT', process.env.GitHUB_PAT);

  try {
    const envFile = path.join(process.env.HOME, '.openclaw', 'workspace', '.env');
    const m = fs.readFileSync(envFile, 'utf8').match(/^GitHUB_PAT=(.*)$/m);
    if (m) add('workspace .env', m[1].replace(/^["']|["']$/g, ''));
  } catch (e) { /* optional source */ }

  try {
    const cred = fs.readFileSync(path.join(process.env.HOME, '.git-credentials'), 'utf8');
    const m = cred.match(/https:\/\/[^:]*:([^@\s]+)@github\.com/);
    if (m) add('~/.git-credentials', m[1]);
  } catch (e) { /* optional source */ }

  try {
    const hosts = fs.readFileSync(path.join(process.env.HOME, '.config', 'gh', 'hosts.yml'), 'utf8');
    const m = hosts.match(/oauth_token:\s*(\S+)/);
    if (m) add('gh hosts.yml', m[1]);
  } catch (e) { /* optional source */ }

  return out;
}

// One API call tells us whether GitHub auth works at all.
// The token travels through the child process env, never through the command
// string, so it never lands in a transcript, log, or the process list.
function githubAuthStatus() {
  const candidates = credentialCandidates();
  if (!candidates.length) {
    return { ok: false, reason: 'no GitHub credential found (env, .env, .git-credentials, gh hosts.yml)', source: null };
  }
  const failures = [];
  for (const c of candidates) {
    try {
      const res = execSync(
        'curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $ACCT_GH_TOKEN" https://api.github.com/user',
        { encoding: 'utf8', timeout: 20000, shell: '/bin/bash',
          env: Object.assign({}, process.env, { ACCT_GH_TOKEN: c.token }) }
      ).trim();
      if (res === '200') {
        return { ok: true, reason: 'GitHub auth OK via ' + c.label + ' (HTTP 200)', source: c.label };
      }
      failures.push(c.label + ' -> HTTP ' + res);
    } catch (e) {
      failures.push(c.label + ' -> ' + e.message);
    }
  }
  return { ok: false, reason: 'all credential candidates rejected: ' + failures.join('; '), source: null };
}

function main() {
  console.log(`[${new Date().toISOString()}] === Daily Accountability Check ===`);
  console.log(`Checking commits for ${todayAST()} (AST)`);

  const { total: commitCount, repos, perRepo } = countCommitsToday();
  console.log(`Repos scanned: ${repos.length}`);
  console.log(`Commits today: ${commitCount}`);
  for (const p of perRepo) {
    console.log(`  [${p.count}] ${p.repo.replace(process.env.HOME, '~')}`);
    for (const c of p.commits) console.log(`       ${c}`);
  }

  // Publish state — a local commit is not a ship until the remote has it.
  const auth = githubAuthStatus();
  const { total: unpushedTotal, offenders } = totalUnpushed(repos);
  const noRemote = reposWithoutRemote(repos);
  console.log(`GitHub auth: ${auth.ok ? 'OK' : 'BROKEN'} — ${auth.reason}`);
  console.log(`Unpushed commits: ${unpushedTotal}`);
  for (const o of offenders.slice(0, 15)) {
    console.log(`  [${o.count}] ${o.repo.replace(process.env.HOME, '~')}`);
  }
  if (offenders.length > 15) console.log(`  ... and ${offenders.length - 15} more repo(s)`);
  if (noRemote.length) {
    console.log(`Repos with NO origin remote (can never publish): ${noRemote.length}`);
    for (const r of noRemote.slice(0, 10)) console.log(`  ${r.replace(process.env.HOME, '~')}`);
  }
  const published = commitCount > 0 && unpushedTotal === 0 && auth.ok;
  console.log(`Publish status: ${published ? 'PUBLISHED' : 'NOT FULLY PUBLISHED'}`);

  // Log to daily file
  if (!fs.existsSync(MEMORY_DIR)) fs.mkdirSync(MEMORY_DIR, { recursive: true });
  const dailyFile = path.join(MEMORY_DIR, `${today()}.md`);
  const status = commitCount > 0 ? '✅ PASS' : '🚨 ZERO-COMMIT DAY';
  const publishStatus = published ? '✅ PUBLISHED' : '🚨 NOT FULLY PUBLISHED';
  const publishSummary = offenders.length
    ? '\n- Unpushed by repo:\n' + offenders.map(o => `  - ${o.repo.replace(process.env.HOME, '~')}: ${o.count}`).join('\n')
    : '';
  const repoSummary = perRepo.length
    ? '\n' + perRepo.map(p => `- ${p.repo.replace(process.env.HOME, '~')}: ${p.count}`).join('\n')
    : '';
  const entry = `\n## Accountability Check — ${todayAST()}\n- Repos scanned: ${repos.length}\n- Commits today: ${commitCount}\n- Status: ${status}\n- Publish status: ${publishStatus}\n- GitHub auth: ${auth.reason}\n- Unpushed commits: ${unpushedTotal}${publishSummary}\n`;
  try {
    fs.appendFileSync(dailyFile, entry);
  } catch (e) {
    console.log('Could not append to daily file:', e.message);
  }

  if (commitCount === 0) {
    console.log('🚨 ZERO-COMMIT DAY — triggering emergency work session');

    const emergencyMsg = `🚨 **ZERO-COMMIT DAY ALERT**\n\nNo commits shipped today (${todayAST()}).\n\n**Emergency Protocol:**\n1. Run bounty scanner immediately\n2. Pick smallest non-scam issue\n3. Fix and commit within 30 minutes\n4. Report back\n\nThis is an automated accountability check.\n`;
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

    const publishLine = published
      ? '\n\nAll commits reached the remote.'
      : `\n\n⚠️ **${unpushedTotal} commit(s) are NOT published.** ${auth.reason}.\n` +
        (offenders.length
          ? 'Top blocked repos: ' + offenders.slice(0, 5).map(o => `${o.repo.replace(process.env.HOME, '~')} (+${o.count})`).join(', ')
          : '') +
        (noRemote.length ? `\n\n${noRemote.length} repo(s) have no origin remote at all.` : '');
    const successMsg = `✅ **Accountability Check — ${todayAST()}**\n\n${commitCount} commit(s) shipped today across ${perRepo.length} repo(s).\n\nPublish status: **${published ? 'PUBLISHED' : 'NOT FULLY PUBLISHED'}**${publishLine}\n\nKeep the streak alive! 🔥`;
    console.log('\n---TELEGRAM---\n' + successMsg + '\n---END---');
  }
}

main();
