#!/usr/bin/env node
/**
 * Enhanced Daily Repo Monitor
 * Uses python3 for JSON parsing
 * Checks: stars, forks, open issues, new issues/PRs (7d), new comments, mentions
 */

import { execSync } from 'child_process';

const REPOS = [
  { owner: 'hussain-alsaibai', name: 'context-bridge', label: 'Context Bridge' },
  { owner: 'hussain-alsaibai', name: 'dev-masterkit', label: 'Dev MasterKit' }
];

const SEVEN_DAYS_AGO = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();

function run(cmd, timeout = 15000) {
  try {
    return execSync(cmd, { encoding: 'utf-8', timeout }).trim();
  } catch (e) {
    return '';
  }
}

function parseJSON(jsonStr) {
  try {
    return JSON.parse(jsonStr || '{}');
  } catch {
    return {};
  }
}

function checkRepoStats(owner, name) {
  const url = `https://api.github.com/repos/${owner}/${name}`;
  const cmd = `curl -s "${url}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps({'stars':d.get('stargazers_count',0),'forks':d.get('forks_count',0),'issues':d.get('open_issues_count',0),'name':d.get('name',''),'url':d.get('html_url',''),'updated':d.get('updated_at',''),'pushed':d.get('pushed_at','')}))"`;
  return parseJSON(run(cmd));
}

function checkRecentIssues(owner, name) {
  const url = `https://api.github.com/repos/${owner}/${name}/issues?state=all&since=${SEVEN_DAYS_AGO}&per_page=50`;
  const cmd = `curl -s "${url}" | python3 -c "
import sys,json
d=json.load(sys.stdin)
arr=d if isinstance(d,list) else []
issues = [x for x in arr if not x.get('pull_request')]
prs = [x for x in arr if x.get('pull_request')]
print(json.dumps({'new_issues': len(issues), 'new_prs': len(prs), 'total_recent': len(arr)}))
"`;
  return parseJSON(run(cmd));
}

function checkRecentComments(owner, name) {
  // Get comments from issues in last 7 days
  const url = `https://api.github.com/repos/${owner}/${name}/issues/comments?since=${SEVEN_DAYS_AGO}&per_page=50`;
  const cmd = `curl -s "${url}" | python3 -c "
import sys,json
d=json.load(sys.stdin)
arr=d if isinstance(d,list) else []
comments = []
for c in arr:
    comments.append({
        'user': c.get('user',{}).get('login',''),
        'body_preview': c.get('body','')[:100],
        'created': c.get('created_at',''),
        'url': c.get('html_url','')
    })
print(json.dumps({'count': len(comments), 'comments': comments[:5]}))
"`;
  return parseJSON(run(cmd));
}

function checkOpenPRs(owner, name) {
  const url = `https://api.github.com/repos/${owner}/${name}/pulls?state=open&per_page=50`;
  const cmd = `curl -s "${url}" | python3 -c "
import sys,json
d=json.load(sys.stdin)
arr=d if isinstance(d,list) else []
prs = []
for p in arr:
    prs.append({
        'title': p.get('title',''),
        'author': p.get('user',{}).get('login',''),
        'created': p.get('created_at',''),
        'url': p.get('html_url',''),
        'draft': p.get('draft',False)
    })
print(json.dumps({'count': len(prs), 'prs': prs}))
"`;
  return parseJSON(run(cmd));
}

function formatDate(isoStr) {
  if (!isoStr) return 'N/A';
  const d = new Date(isoStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function main() {
  const reports = [];
  const actionItems = [];
  
  const now = new Date();
  const dateStr = now.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  reports.push('═══════════════════════════════════════════');
  reports.push(`📋 DAILY REPO REPORT — ${dateStr}`);
  reports.push('═══════════════════════════════════════════');
  reports.push('');

  for (const repo of REPOS) {
    const stats = checkRepoStats(repo.owner, repo.name);
    const recent = checkRecentIssues(repo.owner, repo.name);
    const comments = checkRecentComments(repo.owner, repo.name);
    const openPRs = checkOpenPRs(repo.owner, repo.name);

    if (stats.error || !stats.name) {
      reports.push(`⚠️ ${repo.label}: Error fetching data`);
      continue;
    }

    reports.push(`📦 ${repo.label} (${stats.name})`);
    reports.push(`   ⭐ Stars: ${stats.stars} | 🍴 Forks: ${stats.forks}`);
    reports.push(`   📋 Open Issues: ${stats.issues} | 🔀 Open PRs: ${openPRs.count || 0}`);
    reports.push(`   🕐 Last Push: ${formatDate(stats.pushed)}`);
    reports.push(`   🔗 ${stats.url}`);
    reports.push('');

    // Recent activity
    const hasNewIssues = recent.new_issues > 0;
    const hasNewPRs = recent.new_prs > 0;
    const hasComments = comments.count > 0;
    const hasOpenPRs = openPRs.count > 0;

    if (hasNewIssues || hasNewPRs || hasComments) {
      reports.push(`   🔥 RECENT ACTIVITY (Last 7 Days):`);
      
      if (hasNewIssues) {
        reports.push(`      📥 ${recent.new_issues} new issue(s)`);
        actionItems.push(`[${repo.label}] Review ${recent.new_issues} new issue(s)`);
      }
      
      if (hasNewPRs) {
        reports.push(`      🔀 ${recent.new_prs} new PR(s)`);
        actionItems.push(`[${repo.label}] Review ${recent.new_prs} new PR(s)`);
      }
      
      if (hasComments) {
        reports.push(`      💬 ${comments.count} new comment(s)`);
        actionItems.push(`[${repo.label}] Check ${comments.count} new comment(s) for responses needed`);
      }
      
      reports.push('');
    } else {
      reports.push(`   ✅ No new activity in last 7 days`);
      reports.push('');
    }

    // Open PRs section
    if (hasOpenPRs && openPRs.prs) {
      reports.push(`   🔀 OPEN PULL REQUESTS:`);
      for (const pr of openPRs.prs.slice(0, 5)) {
        const draftMark = pr.draft ? ' [DRAFT]' : '';
        reports.push(`      • "${pr.title}"${draftMark} — @${pr.author} (${formatDate(pr.created)})`);
        reports.push(`        ${pr.url}`);
      }
      if (openPRs.prs.length > 5) {
        reports.push(`      ... and ${openPRs.prs.length - 5} more`);
      }
      reports.push('');
      actionItems.push(`[${repo.label}] Review ${openPRs.count} open PR(s)`);
    }

    reports.push('───────────────────────────────────────────');
    reports.push('');
  }

  // Action Items Section
  if (actionItems.length > 0) {
    reports.push('═══════════════════════════════════════════');
    reports.push('⚡ ACTION ITEMS');
    reports.push('═══════════════════════════════════════════');
    reports.push('');
    for (let i = 0; i < actionItems.length; i++) {
      reports.push(`${i + 1}. ${actionItems[i]}`);
    }
    reports.push('');
  } else {
    reports.push('═══════════════════════════════════════════');
    reports.push('✅ NO ACTION ITEMS');
    reports.push('═══════════════════════════════════════════');
    reports.push('');
    reports.push('All repos are quiet. Nothing needs your attention today.');
    reports.push('');
  }

  return { 
    report: reports.join('\n'), 
    hasAction: actionItems.length > 0,
    actionItems 
  };
}

if (process.argv[1] === import.meta.url.slice(7)) {
  const result = main();
  console.log(result.report);
}

export { main };
