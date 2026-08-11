#!/usr/bin/env node
/**
 * Daily Repo Monitor + Trend Research
 * Uses python3 for JSON parsing (no jq dependency)
 * Uses hussain-alsaibai for dev-masterkit
 */

import { execSync } from 'child_process';
import { existsSync, readFileSync, writeFileSync } from 'fs';

const REPOS = [
  { owner: 'hussain-alsaibai', name: 'context-bridge', label: 'Context Bridge' },
  { owner: 'hussain-alsaibai', name: 'dev-masterkit', label: 'Dev MasterKit' }
];

function run(cmd, timeout = 15000) {
  try {
    return execSync(cmd, { encoding: 'utf-8', timeout }).trim();
  } catch (e) {
    return '';
  }
}

function checkRepo(owner, name) {
  const url = `https://api.github.com/repos/${owner}/${name}`;
  const cmd = `curl -s "${url}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps({'stars':d.get('stargazers_count',0),'forks':d.get('forks_count',0),'issues':d.get('open_issues_count',0),'name':d.get('name',''),'url':d.get('html_url',''),'error':d.get('message','')}))"`;
  const result = run(cmd);
  try {
    return JSON.parse(result || '{"stars":0,"forks":0,"issues":0}');
  } catch {
    return { stars: 0, forks: 0, issues: 0, error: 'parse_error' };
  }
}

function checkRecentIssues(owner, name) {
  const since = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
  const url = `https://api.github.com/repos/${owner}/${name}/issues?state=all&since=${since}&per_page=20`;
  const cmd = `curl -s "${url}" | python3 -c "import sys,json; d=json.load(sys.stdin); arr=d if isinstance(d,list) else []; print(len([x for x in arr if not x.get('pull_request')]))"`;
  const count = parseInt(run(cmd) || '0');
  return { recentIssues: count };
}

function main() {
  const reports = [];
  let hasAction = false;

  for (const repo of REPOS) {
    const stats = checkRepo(repo.owner, repo.name);
    const recent = checkRecentIssues(repo.owner, repo.name);
    
    if (stats.error && stats.error.includes('Not Found')) {
      reports.push(`⚠️ ${repo.label}: Repo not found or private`);
      continue;
    }
    
    reports.push(`📊 ${repo.label}`);
    reports.push(`  ⭐ Stars: ${stats.stars} | 🍴 Forks: ${stats.forks} | 📋 Open Issues: ${stats.issues}`);
    reports.push(`  🔥 Recent (7d): ${recent.recentIssues} issues/PRs`);
    reports.push(`  🔗 ${stats.url || `https://github.com/${repo.owner}/${repo.name}`}`);
    reports.push('');
    
    if (recent.recentIssues > 0) hasAction = true;
  }

  return { report: reports.join('\n'), hasAction };
}

if (process.argv[1] === import.meta.url.slice(7)) {
  const result = main();
  console.log(result.report);
}

export { main, checkRepo };
