# Working Memory Skill

**Purpose:** Session-scoped volatile memory for tracking current task state, loaded context, and next steps.

**Pattern:** Fast memory (recent, volatile) separate from slow memory (persistent, curated).

**Research:** Based on Continuum Memory (arXiv 2601.09913) and StreamingLLM attention sink patterns.

---

## Usage

### Initialize Session
```javascript
const wm = require('./working-memory.js');
await wm.init({
  session_id: 'main-2026-02-13',
  task: 'LLM context management research'
});
```

### Update State
```javascript
await wm.update({
  current_task: 'Bug hunting on huntr.com',
  active_files: ['/data/.openclaw/workspace/bug-reports/DBGPT-RCE.md'],
  next_steps: ['Monitor validation', 'Research Gitcoin tasks']
});
```

### Add Metrics
```javascript
await wm.addMetric('web_searches', 13);
await wm.addMetric('sources_analyzed', 80);
```

### Read State
```javascript
const state = await wm.read();
console.log(state.current_task); // "Bug hunting on huntr.com"
```

### Checkpoint (Save for Next Session)
```javascript
await wm.checkpoint({
  summary: 'Completed LLM context research, documented 10 techniques',
  next_action: 'Implement working memory + resume income work'
});
```

### Restore (Load Previous Session)
```javascript
const checkpoint = await wm.restore();
// Returns last checkpoint if exists, null otherwise
```

---

## File Locations

- **Working Memory:** `/tmp/working_memory.json` (session-scoped, volatile)
- **Checkpoint:** `/tmp/session_checkpoint.json` (persists across restarts)
- **Archive:** `/data/.openclaw/workspace/memory/checkpoints/YYYY-MM-DD.json` (optional)

---

## Benefits

1. **Separation of Concerns**
   - Working memory: Current task, ephemeral state
   - Long-term memory: MEMORY.md, daily files
   
2. **Cheaper to Read**
   - JSON (50-200 tokens) vs full markdown (2K-10K tokens)
   
3. **Session Recovery**
   - "Where was I?" after restarts
   - Resume context, reduce re-explanation
   
4. **Clear State Tracking**
   - Active task, loaded files, next steps
   - Metrics (searches, files created, time spent)

---

## Example Working Memory

```json
{
  "session_id": "main-2026-02-13",
  "session_started": "2026-02-13T20:30:00Z",
  "current_task": "LLM context management research",
  "context_loaded": [
    "SOUL.md",
    "USER.md",
    "AGENTS.md",
    "MEMORY.md",
    "memory/2026-02-13.md"
  ],
  "active_files": [
    "/data/.openclaw/workspace/LLM_CONTEXT_MANAGEMENT_PRACTICAL_GUIDE.md"
  ],
  "next_steps": [
    "Implement working memory pattern",
    "Research Gitcoin guaranteed-income tasks",
    "Monitor huntr validation updates"
  ],
  "metrics": {
    "web_searches": 13,
    "sources_analyzed": 80,
    "documents_created": 1,
    "time_spent_minutes": 120
  },
  "state": {
    "bug_bounties_pending": 2,
    "estimated_earnings": "$2000-$3700",
    "validation_deadline": "2026-02-16T12:00:00Z"
  }
}
```

---

## Integration with OpenClaw

Add to session initialization (main session):

```javascript
// At session start
const wm = require('./skills/working-memory/working-memory.js');
const checkpoint = await wm.restore();

if (checkpoint) {
  console.log(`Resuming: ${checkpoint.active_task}`);
  console.log(`Progress: ${checkpoint.context_summary}`);
  console.log(`Next: ${checkpoint.next_action}`);
}

await wm.init({
  session_id: sessionKey,
  task: checkpoint?.next_action || 'New session'
});
```

At critical points (task completion, before long operation):

```javascript
await wm.update({
  current_task: 'New task started',
  next_steps: ['Step 1', 'Step 2']
});
```

At session end (or every hour):

```javascript
await wm.checkpoint({
  summary: 'What I accomplished this session',
  next_action: 'What to do next session'
});
```

---

## Best Practices

1. **Update Frequently** - After each major step (every 15-30 min)
2. **Checkpoint Hourly** - So session crashes don't lose progress
3. **Clear Next Steps** - So next session knows where to start
4. **Track Metrics** - Token usage, API calls, files created, time spent
5. **Archive Old Checkpoints** - Move to memory/checkpoints/ weekly

---

*Based on research: Continuum Memory (long-horizon agents), StreamingLLM (attention sinks), Memory OS (fast/slow memory hierarchy)*
